import sqlite3
import os
import re
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'wound_app.db')

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         TEXT    DEFAULT (datetime('now', 'localtime')),
            original_filename TEXT    NOT NULL,
            original_path     TEXT    NOT NULL,
            overlay_path      TEXT    NOT NULL,
            prediction        TEXT    NOT NULL,
            confidence        REAL    NOT NULL,
            infected_prob     REAL    NOT NULL,
            non_infected_prob REAL    NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name      TEXT    NOT NULL,
            email          TEXT    NOT NULL UNIQUE,
            password_hash  TEXT    NOT NULL,
            created_at     TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name      TEXT    NOT NULL,
            email          TEXT    NOT NULL UNIQUE,
            password_hash  TEXT    NOT NULL,
            created_at     TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)
    _ensure_predictions_patient_id_column(conn)
    _ensure_predictions_review_columns(conn)
    conn.commit()
    conn.close()
    print(f"[DB] Initialized: {DB_PATH}")


def _ensure_predictions_patient_id_column(conn):
    """Add patient_id to predictions for existing SQLite databases."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(predictions)").fetchall()}
    if 'patient_id' not in cols:
        conn.execute(
            "ALTER TABLE predictions ADD COLUMN patient_id INTEGER REFERENCES patients(id)"
        )


def _ensure_predictions_review_columns(conn):
    """Add doctor review columns to predictions for existing SQLite databases."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(predictions)").fetchall()}
    if 'doctor_comment' not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN doctor_comment TEXT")
    if 'doctor_recommendation' not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN doctor_recommendation TEXT")
    if 'review_status' not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN review_status TEXT")
    if 'reviewed_by' not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN reviewed_by INTEGER REFERENCES doctors(id)")
    if 'reviewed_at' not in cols:
        conn.execute("ALTER TABLE predictions ADD COLUMN reviewed_at TEXT")


def save_prediction(original_filename, original_path, overlay_path,
                    prediction, confidence, infected_prob, non_infected_prob,
                    patient_id=None):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO predictions
           (original_filename, original_path, overlay_path,
            prediction, confidence, infected_prob, non_infected_prob, patient_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (original_filename, original_path, overlay_path,
         prediction, confidence, infected_prob, non_infected_prob, patient_id),
    )
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_prediction(record_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM predictions WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_predictions(limit=200):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_predictions_for_patient(patient_id, limit=200):
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM predictions
           WHERE patient_id = ?
           ORDER BY id DESC LIMIT ?""",
        (patient_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------------
# Patient-facing analysis numbering (DISPLAY ONLY)
# --------------------------------------------------------------------------
# These helpers compute a per-patient chronological rank for an analysis
# (oldest = 1, newest = N) so each patient sees their own #1, #2, ...
# instead of the global database primary key.
#
# IMPORTANT: this is purely a display value.
#   - The database schema is NOT changed.
#   - record.id is still the canonical identifier used by /result/<id>,
#     /delete/<id>, and any DB relations.
#   - ML logic, /predict, auth/session, and patient ownership/security
#     are unaffected.
# --------------------------------------------------------------------------

def count_predictions_for_patient(patient_id):
    """Return the total number of analyses owned by a patient."""
    if patient_id is None:
        return 0
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id = ?",
        (patient_id,),
    ).fetchone()[0]
    conn.close()
    return int(n or 0)


def get_patient_analysis_number(record_id, patient_id):
    """
    Return the patient-facing display rank of a single record among the
    records owned by ``patient_id``.

    Ordering matches the patient-facing UI: the newest analysis is #1,
    the next-newest is #2, and the oldest is #N. This is computed by
    counting the records owned by the same patient that are at least as
    new as ``record_id`` (i.e. ``id >= record_id``).

    Returns ``None`` if the rank cannot be computed (e.g. unowned
    legacy record or unknown patient). Callers should fall back to
    ``record.id`` for display in that case.
    """
    if patient_id is None or record_id is None:
        return None
    conn = get_conn()
    row = conn.execute(
        """SELECT COUNT(*) FROM predictions
           WHERE patient_id = ? AND id >= ?""",
        (patient_id, record_id),
    ).fetchone()
    conn.close()
    if not row:
        return None
    rank = int(row[0] or 0)
    return rank if rank > 0 else None


def get_prediction_with_patient(record_id):
    conn = get_conn()
    row = conn.execute(
        """SELECT p.*,
                  pt.full_name AS patient_name,
                  pt.email AS patient_email,
                  d.full_name AS reviewed_by_name
           FROM predictions p
           LEFT JOIN patients pt ON p.patient_id = pt.id
           LEFT JOIN doctors d ON p.reviewed_by = d.id
           WHERE p.id = ?""",
        (record_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_doctor_review(record_id, doctor_id, review_status,
                         doctor_comment, doctor_recommendation):
    conn = get_conn()
    conn.execute(
        """UPDATE predictions
           SET doctor_comment = ?,
               doctor_recommendation = ?,
               review_status = ?,
               reviewed_by = ?,
               reviewed_at = datetime('now', 'localtime')
           WHERE id = ?""",
        (doctor_comment, doctor_recommendation, review_status, doctor_id, record_id),
    )
    conn.commit()
    conn.close()


def prediction_belongs_to_patient(record_id, patient_id):
    rec = get_prediction(record_id)
    if not rec:
        return False
    return rec.get('patient_id') == patient_id


def delete_prediction(record_id):
    conn = get_conn()
    conn.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def normalize_patient_email(email):
    if not email or not isinstance(email, str):
        return ''
    return email.strip().lower()


def email_format_valid(email):
    return bool(email and _EMAIL_RE.match(email))


def get_patient_by_email(email):
    email_n = normalize_patient_email(email)
    if not email_n:
        return None
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM patients WHERE email = ?", (email_n,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_patient_by_id(patient_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM patients WHERE id = ?", (patient_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_patient(full_name, email, password_hash):
    """Insert a new patient. Raises sqlite3.IntegrityError if email exists."""
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO patients (full_name, email, password_hash)
               VALUES (?, ?, ?)""",
            (full_name.strip(), normalize_patient_email(email), password_hash),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_doctor_by_email(email):
    email_n = normalize_patient_email(email)
    if not email_n:
        return None
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM doctors WHERE email = ?", (email_n,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_doctor_by_id(doctor_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_doctor(full_name, email, password_hash):
    """Insert a new doctor. Raises sqlite3.IntegrityError if email exists."""
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO doctors (full_name, email, password_hash)
               VALUES (?, ?, ?)""",
            (full_name.strip(), normalize_patient_email(email), password_hash),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_recent_patient_predictions(limit=12):
    conn = get_conn()
    rows = conn.execute(
        """SELECT p.*, pt.full_name AS patient_name
           FROM predictions p
           JOIN patients pt ON p.patient_id = pt.id
           ORDER BY p.id DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient_predictions_with_names(limit=5000):
    conn = get_conn()
    rows = conn.execute(
        """SELECT p.*, pt.full_name AS patient_name
           FROM predictions p
           JOIN patients pt ON p.patient_id = pt.id
           ORDER BY p.id DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_doctor_overview_stats():
    conn = get_conn()
    total_cases = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id IS NOT NULL"
    ).fetchone()[0]
    infected_cases = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE patient_id IS NOT NULL AND prediction = 'infected'"
    ).fetchone()[0]
    avg_conf_raw = conn.execute(
        "SELECT AVG(confidence) FROM predictions WHERE patient_id IS NOT NULL"
    ).fetchone()[0]
    patients_under_care = conn.execute(
        "SELECT COUNT(DISTINCT patient_id) FROM predictions WHERE patient_id IS NOT NULL"
    ).fetchone()[0]
    conn.close()

    infection_rate = (infected_cases / total_cases * 100) if total_cases else 0.0
    avg_accuracy = ((avg_conf_raw or 0.0) * 100) if avg_conf_raw is not None else 0.0
    return {
        'total_cases': int(total_cases or 0),
        'active_infection_rate': round(infection_rate, 1),
        'avg_ai_accuracy': round(avg_accuracy, 1),
        'patients_under_care': int(patients_under_care or 0),
    }


def get_monthly_chart_points(months=6):
    """Return month labels + infection% + avg confidence% for recent months."""
    now = datetime.now().replace(day=1)
    month_keys = []
    month_labels = []

    year = now.year
    month = now.month
    for i in range(months - 1, -1, -1):
        y = year
        m = month - i
        while m <= 0:
            m += 12
            y -= 1
        key = f"{y:04d}-{m:02d}"
        label = datetime(y, m, 1).strftime('%b')
        month_keys.append(key)
        month_labels.append(label)

    conn = get_conn()
    rows = conn.execute(
        """SELECT strftime('%Y-%m', timestamp) AS ym,
                  COUNT(*) AS total,
                  SUM(CASE WHEN prediction='infected' THEN 1 ELSE 0 END) AS infected,
                  AVG(confidence) AS avg_conf
           FROM predictions
           WHERE patient_id IS NOT NULL
           GROUP BY ym"""
    ).fetchall()
    conn.close()
    stats = {row['ym']: dict(row) for row in rows}

    infection = []
    accuracy = []
    for key in month_keys:
        row = stats.get(key)
        if not row or not row.get('total'):
            infection.append(None)
            accuracy.append(None)
            continue
        infection.append(round((row['infected'] / row['total']) * 100, 1))
        accuracy.append(round((row['avg_conf'] or 0.0) * 100, 1))

    return {
        'labels': month_labels,
        'infection_rate': infection,
        'ai_accuracy': accuracy,
    }
