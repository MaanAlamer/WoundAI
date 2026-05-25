import os
import uuid
import sqlite3
from urllib.parse import urlparse
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, jsonify, session)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image

import database
import models_loader
import i18n  # EN / AR scaffolding (Step 1: structure only, no translations yet)

app = Flask(__name__)
app.secret_key = 'wound-classifier-2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # 16 MB limit

SESSION_PATIENT_ID = 'patient_id'
SESSION_PATIENT_NAME = 'patient_name'
SESSION_DOCTOR_ID = 'doctor_id'
SESSION_DOCTOR_NAME = 'doctor_name'
SESSION_LANG_KEY = 'lang'
REVIEW_STATUS_OPTIONS = (
    'Stable',
    'Needs Follow-up',
    'Urgent Review Recommended',
)
REVIEW_STATUS_SET = set(REVIEW_STATUS_OPTIONS)

UPLOAD_FOLDER  = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
OVERLAY_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'overlays')
ALLOWED_EXT    = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(OVERLAY_FOLDER, exist_ok=True)


def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


# --------------------------------------------------------------------------
# Language (EN / AR) — Step 1 scaffolding only.
# Adds: session-stored language preference, a context processor that exposes
# `current_lang`, `text_direction`, `is_rtl`, and a translation helper `t()`
# to every template, plus a dedicated route to switch languages.
# This block is intentionally self-contained and does NOT touch ML, /predict,
# authentication, the database, or patient isolation.
# --------------------------------------------------------------------------

def _get_current_language():
    """Read the current language from the session, falling back to English."""
    return i18n.normalize_language(session.get(SESSION_LANG_KEY))


@app.context_processor
def inject_language_context():
    """Make language info available to every template automatically."""
    lang = _get_current_language()
    return {
        'current_lang': lang,
        'text_direction': i18n.text_direction_for(lang),
        'is_rtl': i18n.is_rtl(lang),
        'supported_languages': i18n.SUPPORTED_LANGUAGES,
        'language_labels': i18n.LANGUAGE_LABELS,
        # Templates can call `{{ t('some.key') }}` — safe even if missing.
        't': lambda key: i18n.t(key, lang),
    }


def is_patient_logged_in():
    return session.get(SESSION_PATIENT_ID) is not None


def is_doctor_logged_in():
    return session.get(SESSION_DOCTOR_ID) is not None


def require_patient_login(flash_message='Please log in to access this page.'):
    if not is_patient_logged_in():
        flash(flash_message, 'error')
        return False
    return True


def require_doctor_login(flash_message='Please log in as doctor to access this page.'):
    if not is_doctor_logged_in():
        flash(flash_message, 'error')
        return False
    return True


@app.route('/')
def index():
    recent = database.get_all_predictions(limit=5)
    return render_template('index.html', recent=recent)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


def _is_safe_redirect_target(url):
    """Return True only for same-origin redirect targets.

    Accepts:
      - app-relative paths starting with a single forward slash
        (e.g. ``/user-dashboard`` or ``/history?filter=foo``).
      - absolute URLs on this host (matches ``request.host_url``).

    Rejects protocol-relative URLs (``//evil.com/...``), backslash
    tricks, javascript: and data: schemes, etc.
    """
    if not url or not isinstance(url, str):
        return False
    if url.startswith('/'):
        if url.startswith('//') or url.startswith('/\\'):
            return False
        parsed = urlparse(url)
        if parsed.scheme or parsed.netloc:
            return False
        return True
    return url.startswith(request.host_url)


@app.route('/set-language/<lang_code>')
def set_language(lang_code):
    """
    Persist the user's preferred language in the session and redirect back
    to the SAME page the user was on when they clicked the toggle.

    Resolution order for the redirect target:
      1. ``?next=<path>`` — the toggle include in templates passes the
         current page path here. Validated as same-origin.
      2. ``Referer`` header — fallback when ``next`` is missing or
         unsafe (e.g. browsers/policies that strip Referer).
      3. Homepage — last-resort fallback.

    Auth/session, ML, /predict, and patient ownership are unaffected.
    """
    if i18n.is_supported(lang_code):
        session[SESSION_LANG_KEY] = lang_code

    next_arg = request.args.get('next')
    if next_arg and _is_safe_redirect_target(next_arg):
        return redirect(next_arg)

    referrer = request.referrer
    if referrer and _is_safe_redirect_target(referrer):
        return redirect(referrer)

    return redirect(url_for('index'))


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        flash('No file part in the request.', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('index'))

    if not allowed(file.filename):
        flash('Unsupported file type. Please upload JPG, PNG, BMP, or WEBP.', 'error')
        return redirect(url_for('index'))

    try:
        img = Image.open(file).convert('RGB')
    except Exception:
        flash('Could not open the image. Please try a different file.', 'error')
        return redirect(url_for('index'))

    uid              = uuid.uuid4().hex
    orig_filename    = f'{uid}_original.jpg'
    overlay_filename = f'{uid}_overlay.jpg'
    orig_path        = os.path.join(UPLOAD_FOLDER,  orig_filename)
    overlay_path     = os.path.join(OVERLAY_FOLDER, overlay_filename)

    img.save(orig_path, 'JPEG', quality=92)

    try:
        overlay_img = models_loader.apply_overlay(img)
        overlay_img.save(overlay_path, 'JPEG', quality=92)
    except Exception as e:
        flash(f'Segmentation failed: {e}', 'error')
        return redirect(url_for('index'))

    try:
        label, inf_prob, noninf_prob = models_loader.classify(overlay_img)
        confidence = max(inf_prob, noninf_prob)
    except Exception as e:
        flash(f'Classification failed: {e}', 'error')
        return redirect(url_for('index'))

    patient_row_id = session.get(SESSION_PATIENT_ID)
    record_id = database.save_prediction(
        original_filename = secure_filename(file.filename),
        original_path     = f'uploads/{orig_filename}',
        overlay_path      = f'overlays/{overlay_filename}',
        prediction        = label,
        confidence        = round(confidence, 6),
        infected_prob     = round(inf_prob, 6),
        non_infected_prob = round(noninf_prob, 6),
        patient_id        = patient_row_id,
    )

    return redirect(url_for('result', record_id=record_id))


@app.route('/result/<int:record_id>')
def result(record_id):
    record = database.get_prediction_with_patient(record_id)
    if record is None:
        flash('Record not found.', 'error')
        return redirect(url_for('index'))
    session_patient_id = session.get(SESSION_PATIENT_ID)
    if session_patient_id is not None:
        owner_id = record.get('patient_id')
        if owner_id != session_patient_id:
            flash('You do not have access to this analysis.', 'error')
            return redirect(url_for('history'))

    # Patient-facing display number (oldest = 1, newest = N).
    # Routes, deletion, and DB relations still use record['id'] — this is
    # purely the value rendered in the UI ("Record #N").
    owner_id = record.get('patient_id')
    display_number = database.get_patient_analysis_number(
        record_id, owner_id) if owner_id is not None else None
    if display_number is None:
        display_number = record['id']

    return render_template(
        'result.html',
        record=record,
        display_number=display_number,
        patient_name=(session.get(SESSION_PATIENT_NAME)
                      if session.get(SESSION_PATIENT_ID) else None),
    )


@app.route('/history')
def history():
    if session.get(SESSION_PATIENT_ID) is None:
        flash('Please log in to view your analysis history.', 'error')
        return redirect(url_for('login'))
    pid = session[SESSION_PATIENT_ID]
    records = database.get_predictions_for_patient(pid, limit=200)

    # Attach a per-patient display number for the UI ONLY.
    # ``records`` is returned newest-first, so the topmost row becomes
    # #1, the next #2, and so on. ``record['id']`` is left untouched and
    # continues to drive routes (/result/<id>, /delete/<id>) and DB
    # relations.
    for i, rec in enumerate(records):
        rec['display_number'] = i + 1

    return render_template(
        'history.html',
        records=records,
        patient_name=session.get(SESSION_PATIENT_NAME) or 'Patient',
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        email_n = database.normalize_patient_email(email)
        if not database.email_format_valid(email_n):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
        patient = database.get_patient_by_email(email_n)
        if not patient or not check_password_hash(
                patient['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
        session.pop(SESSION_DOCTOR_ID, None)
        session.pop(SESSION_DOCTOR_NAME, None)
        session[SESSION_PATIENT_ID] = patient['id']
        session[SESSION_PATIENT_NAME] = patient['full_name']
        return redirect(url_for('user_dashboard'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullName', '').strip()
        email = request.form.get('signupEmail', '')
        password = request.form.get('signupPassword', '')
        confirm = request.form.get('confirmPassword', '')
        if not full_name or not email or not password or not confirm:
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('signup.html')
        email_n = database.normalize_patient_email(email)
        if not database.email_format_valid(email_n):
            flash('Please enter a valid email address.', 'error')
            return render_template('signup.html')
        phash = generate_password_hash(password)
        try:
            database.create_patient(full_name, email_n, phash)
        except sqlite3.IntegrityError:
            flash('An account with this email already exists.', 'error')
            return render_template('signup.html')
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/doctor-login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('doctorEmail', '')
        password = request.form.get('doctorPassword', '')
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('doctor-login.html')
        email_n = database.normalize_patient_email(email)
        if not database.email_format_valid(email_n):
            flash('Invalid email or password.', 'error')
            return render_template('doctor-login.html')
        doctor = database.get_doctor_by_email(email_n)
        if not doctor or not check_password_hash(doctor['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('doctor-login.html')
        session.pop(SESSION_PATIENT_ID, None)
        session.pop(SESSION_PATIENT_NAME, None)
        session[SESSION_DOCTOR_ID] = doctor['id']
        session[SESSION_DOCTOR_NAME] = doctor['full_name']
        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor-login.html')


@app.route('/doctor-dashboard')
def doctor_dashboard():
    if not require_doctor_login():
        return redirect(url_for('doctor_login'))

    stats = database.get_doctor_overview_stats()
    recent_records = database.get_recent_patient_predictions(limit=12)
    chart_data = database.get_monthly_chart_points(months=6)
    return render_template(
        'doctor-dashboard.html',
        doctor_name=session.get(SESSION_DOCTOR_NAME) or 'Doctor',
        stats=stats,
        recent_records=recent_records,
        chart_data=chart_data,
    )


@app.route('/doctor/reports/<int:record_id>')
def doctor_report(record_id):
    if not require_doctor_login():
        return redirect(url_for('doctor_login'))
    record = database.get_prediction_with_patient(record_id)
    if not record:
        flash('Record not found.', 'error')
        return redirect(url_for('doctor_dashboard'))
    if record.get('patient_id') is None:
        flash('This analysis is not linked to a patient account.', 'error')
        return redirect(url_for('doctor_dashboard'))
    patient_history = []
    if record.get('patient_id') is not None:
        patient_history = database.get_predictions_for_patient(record['patient_id'], limit=10)
    return render_template(
        'doctor-report.html',
        doctor_name=session.get(SESSION_DOCTOR_NAME) or 'Doctor',
        record=record,
        patient_history=patient_history,
        review_status_options=REVIEW_STATUS_OPTIONS,
    )


@app.route('/doctor/reports/<int:record_id>/review', methods=['POST'])
def doctor_save_review(record_id):
    if not require_doctor_login():
        return redirect(url_for('doctor_login'))
    record = database.get_prediction_with_patient(record_id)
    if not record or record.get('patient_id') is None:
        flash('Record not found for doctor review.', 'error')
        return redirect(url_for('doctor_dashboard'))

    review_status = (request.form.get('review_status') or '').strip()
    doctor_comment = (request.form.get('doctor_comment') or '').strip()
    doctor_recommendation = (request.form.get('doctor_recommendation') or '').strip()

    if review_status not in REVIEW_STATUS_SET:
        flash('Please select a valid review status.', 'error')
        return redirect(url_for('doctor_report', record_id=record_id))
    if not doctor_comment:
        flash('Doctor comment is required.', 'error')
        return redirect(url_for('doctor_report', record_id=record_id))
    if not doctor_recommendation:
        flash('Doctor recommendation is required.', 'error')
        return redirect(url_for('doctor_report', record_id=record_id))

    database.update_doctor_review(
        record_id=record_id,
        doctor_id=session[SESSION_DOCTOR_ID],
        review_status=review_status,
        doctor_comment=doctor_comment,
        doctor_recommendation=doctor_recommendation,
    )
    flash('Doctor review saved successfully.', 'success')
    return redirect(url_for('doctor_report', record_id=record_id))


@app.route('/doctor/logout', methods=['GET', 'POST'])
def doctor_logout():
    session.pop(SESSION_DOCTOR_ID, None)
    session.pop(SESSION_DOCTOR_NAME, None)
    flash('Doctor session ended.', 'success')
    return redirect(url_for('doctor_login'))


@app.route('/user-dashboard')
def user_dashboard():
    if session.get(SESSION_PATIENT_ID) is None:
        flash('Please log in to access the patient dashboard.', 'error')
        return redirect(url_for('login'))
    patient_name = session.get(SESSION_PATIENT_NAME) or 'Patient'
    pid = session[SESSION_PATIENT_ID]
    patient_records = database.get_predictions_for_patient(pid, limit=200)

    # Attach a per-patient display number for the UI ONLY.
    # The list is newest-first, so the latest analysis becomes #1, the
    # next #2, etc. record['id'] is preserved and still used for every
    # route (/result/<id>, /delete/<id>) and DB lookup.
    for i, rec in enumerate(patient_records):
        rec['display_number'] = i + 1

    return render_template(
        'user-dashboard.html',
        patient_name=patient_name,
        patient_records=patient_records,
    )


@app.route('/patient/logout', methods=['GET', 'POST'])
def patient_logout():
    session.pop(SESSION_PATIENT_ID, None)
    session.pop(SESSION_PATIENT_NAME, None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    if session.get(SESSION_PATIENT_ID) is None:
        flash('Please log in to manage your analyses.', 'error')
        return redirect(url_for('login'))
    if not database.prediction_belongs_to_patient(
            record_id, session[SESSION_PATIENT_ID]):
        flash('You cannot delete this record.', 'error')
        return redirect(url_for('history'))
    record = database.get_prediction(record_id)
    if record:
        for path_key in ('original_path', 'overlay_path'):
            full = os.path.join(os.path.dirname(__file__), 'static', record[path_key])
            if os.path.exists(full):
                os.remove(full)
        database.delete_prediction(record_id)
    return redirect(url_for('history'))


@app.route('/api/stats')
def api_stats():
    records = database.get_all_predictions(limit=10000)
    total    = len(records)
    infected = sum(1 for r in records if r['prediction'] == 'infected')
    avg_conf = round(sum(r['confidence'] for r in records) / total, 4) if total else 0
    return jsonify({'total': total, 'infected': infected,
                    'non_infected': total - infected, 'avg_confidence': avg_conf})


# Render/gunicorn import this module without running __main__; PORT is set at runtime.
if os.environ.get('PORT'):
    database.init_db()
    models_loader.load_models()


if __name__ == '__main__':
    print("[Startup] Initializing database...")
    database.init_db()
    print("[Startup] Loading models...")
    models_loader.load_models()
    print("[Startup] Server starting at http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
