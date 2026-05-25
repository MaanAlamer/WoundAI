"""
i18n.py — lightweight EN / AR scaffolding for WoundSense AI.

Step 1 (this commit): structure only.
    - SUPPORTED_LANGUAGES whitelist
    - English remains the default
    - Arabic is registered as RTL but NO strings are translated yet
    - Translation tables are intentionally empty so layout/text never
      changes until we deliberately fill them page-by-page later.

Design goals:
    - Pure standard library, no extra dependencies.
    - Safe by construction: an unknown language code falls back to
      English, and a missing translation key returns the key itself
      so a template that uses {{ t('foo') }} never crashes.
    - Independent of Flask: this module can be imported and unit
      tested on its own without the app context.

Does NOT touch backend logic, ML, /predict, authentication,
database, or patient isolation.
"""

# --- Public configuration -------------------------------------------------

SUPPORTED_LANGUAGES = ('en', 'ar')
DEFAULT_LANGUAGE = 'en'
RTL_LANGUAGES = frozenset({'ar'})

# Human-readable labels for UI elements (e.g., the language toggle).
LANGUAGE_LABELS = {
    'en': 'EN',
    'ar': 'العربية',
}


# --- Translation tables ---------------------------------------------------
# Page-by-page translations.
#   - Step 2 (this commit): homepage (templates/index.html) only.
#   - Other pages remain English; their templates do not use t() yet.
#   - Keys are namespaced ("home.hero.title", "nav.patient_login", ...) so
#     adding more pages later is a clean append, not a rewrite.
#   - Brand names ("WoundSense AI") stay in Latin in both languages.
TRANSLATIONS = {
    'en': {
        # ---- Splash (only shown on first visit) ----
        'splash.tagline': 'AI-assisted wound monitoring',

        # ---- Header / nav (shared by homepage + auth pages) ----
        'nav.menu_button': 'Menu',
        'nav.menu_open_aria': 'Open menu',
        'nav.account_aria': 'Account',
        'nav.language_aria': 'Language',
        'nav.site_aria': 'Site',
        'nav.home': 'Home',
        'nav.patient_login': 'Patient Login',
        'nav.patient_signup': 'Patient Sign Up',
        'nav.doctor_login': 'Doctor Login',

        # ---- Homepage: hero ----
        'home.hero.title': 'AI-Powered Wound Infection Detection & Healing Tracking',
        'home.hero.lead': (
            'WoundSense AI helps patients and doctors monitor wound healing, '
            'detect infection risk early, and support better follow-up using '
            'AI-assisted wound image analysis.'
        ),
        'home.hero.learn_link': 'Learn about the project',

        # ---- Homepage: how it works ----
        'home.works.heading': 'How WoundSense AI Works',
        'home.works.card1.title': 'Upload Wound Image',
        'home.works.card1.text': (
            'Securely upload high-resolution images of the wound directly '
            'from your device.'
        ),
        'home.works.card2.title': 'AI Analysis & Risk Detection',
        'home.works.card2.text': (
            'Our AI engine analyzes images to flag infection risk signals '
            'and support assessment of healing progress.'
        ),
        'home.works.card3.title': 'Track Healing Over Time',
        'home.works.card3.text': (
            'Monitor changes with clearer context, confidence-oriented '
            'insight, and history to support recovery follow-up.'
        ),

        # ---- Homepage: empower ----
        'home.empower.heading': 'Empowering Care for Everyone',
        'home.empower.patients.title': 'For Patients',
        'home.empower.patients.item1': (
            'Gain peace of mind with early infection risk awareness.'
        ),
        'home.empower.patients.item2': (
            'Understand your healing journey with clearer, structured insight.'
        ),
        'home.empower.patients.item3': (
            'Visualize progress over time with chronological history.'
        ),
        'home.empower.patients.item4': (
            'Easily share updates with your healthcare provider.'
        ),
        'home.empower.doctors.title': 'For Doctors',
        'home.empower.doctors.item1': (
            'Enhance clinical context with AI-assisted wound insights.'
        ),
        'home.empower.doctors.item2': (
            'Monitor cases efficiently with trends and organized history.'
        ),
        'home.empower.doctors.item3': (
            'Facilitate patient communication and education at follow-up.'
        ),
        'home.empower.doctors.item4': (
            'Support documentation and treatment planning workflows.'
        ),

        # ---- Homepage: about ----
        'home.about.heading': 'About WoundSense AI',
        'home.about.text': (
            'WoundSense AI is a smart medical support platform designed to '
            'assist with wound infection detection and healing progress '
            'monitoring. It combines wound image analysis, infection-risk '
            'prediction, and history tracking to support patients and '
            'healthcare professionals.'
        ),
        'home.about.feature1': 'Early Infection Detection',
        'home.about.feature2': 'Healing Progress Monitoring',
        'home.about.feature3': 'Patient and Doctor Support',

        # ---- Footer ----
        'footer.tagline': (
            'AI-assisted wound monitoring for clearer follow-up and safer '
            'clinical insight.'
        ),
        'footer.copyright': '© 2026 WoundSense AI. All rights reserved.',

        # ---- Authentication pages (login / signup / doctor login) ----
        # Browser tab titles
        'auth.page_title.login': 'Patient Login | WoundSense AI',
        'auth.page_title.signup': 'Patient Sign Up | WoundSense AI',
        'auth.page_title.doctor_login': 'Doctor Login | WoundSense AI',

        # Shared form labels
        'auth.label.email': 'Email',
        'auth.label.password': 'Password',
        'auth.label.full_name': 'Full Name',
        'auth.label.confirm_password': 'Confirm Password',

        # Shared placeholders. Email/format examples stay in Latin in
        # both languages (universal email convention).
        'auth.placeholder.email_example': 'name@example.com',
        'auth.placeholder.email_doctor_example': 'doctor@hospital.org',
        'auth.placeholder.password_enter': 'Enter password',
        'auth.placeholder.password_create': 'Create a password (8+ characters)',
        'auth.placeholder.password_confirm': 'Confirm your password',
        'auth.placeholder.full_name': 'Enter your full name',

        # Patient login card
        'auth.login.title': 'Patient Login',
        'auth.login.lead': (
            'Access your wound reports, follow-up timeline, and care '
            'guidance in one place.'
        ),
        'auth.login.submit': 'Continue to Patient Dashboard',
        'auth.login.helper_prefix': 'No account yet?',
        'auth.login.helper_link': 'Create a patient account',

        # Patient signup card
        'auth.signup.title': 'Create Patient Account',
        'auth.signup.lead': (
            'Create an account to access wound reports, healing timeline, '
            'and follow-up support.'
        ),
        'auth.signup.submit': 'Create Patient Account',
        'auth.signup.helper_prefix': 'Already have an account?',
        # The link text reuses nav.patient_login.

        # Doctor login card
        'auth.doctor_login.title': 'Doctor Login',
        'auth.doctor_login.lead': (
            'Access patient wound progress, AI-assisted insights, and '
            'follow-up records.'
        ),
        'auth.doctor_login.submit': 'Continue to Doctor Dashboard',
        'auth.doctor_login.helper_prefix': 'Patient? Go to',
        # The link text reuses nav.patient_login.

        # ---- Patient dashboard (user-dashboard.html) ----
        'dashboard.page_title': 'Patient Dashboard | WoundSense AI',

        # Sidebar (patient_sidebar.html include)
        'dashboard.sidebar.aria': 'Patient navigation',
        'dashboard.sidebar.signed_in': 'Signed in',
        'dashboard.nav.dashboard': 'Dashboard',
        'dashboard.nav.start_analysis': 'Start New Analysis',
        'dashboard.nav.history': 'Healing History',
        'dashboard.nav.logout': 'Logout',

        # Welcome row. The patient name itself is dynamic and not translated.
        'dashboard.welcome_prefix': 'Welcome, ',

        # Upload card
        'dashboard.upload.lead': (
            'Upload a wound image for AI-assisted analysis. Results are '
            'saved to your private history.'
        ),
        'dashboard.upload.dropzone_title': 'Click to upload or drag image here',
        'dashboard.upload.dropzone_hint': (
            'Accepted: JPG, PNG, BMP, WEBP (max 16 MB)'
        ),
        'dashboard.upload.submit': 'Upload & analyze',
        'dashboard.upload.preview_alt': 'Selected wound preview',
        'dashboard.upload.progress_text': (
            'AI analysis is in progress. Please wait.'
        ),
        # Strings consumed by main.js via data-msg-* attributes.
        'dashboard.upload.msg_unsupported': (
            'Unsupported file type. Please select JPG, PNG, BMP, or WEBP.'
        ),
        'dashboard.upload.msg_selected': (
            'Image selected. Ready for AI analysis.'
        ),
        'dashboard.upload.msg_choose_first': (
            'Please choose an image before starting analysis.'
        ),
        'dashboard.upload.btn_analyzing': 'Analyzing image...',

        # Recent submissions
        'dashboard.recent.heading': 'Recent Submissions',
        'dashboard.recent.empty': (
            'No wound analyses yet. Upload a wound image to start tracking '
            'your healing progress.'
        ),

        # Status pills (also reused inline as bold inside summary copy)
        'dashboard.status.infection_risk': 'Infection risk',
        'dashboard.status.lower_risk': 'Lower risk',
        'dashboard.status.infection_flagged': 'Infection risk flagged',
        'dashboard.status.favoring_non_infected': 'Favoring non-infected',

        # Confidence label used in recent card row.
        'dashboard.field.confidence_label': 'Confidence: ',

        # Latest status summary section
        'dashboard.summary.heading': 'Latest Status Summary',
        'dashboard.summary.current_status_label': 'Current status',
        'dashboard.summary.last_analysis_label': 'Last analysis: ',
        'dashboard.summary.confidence_sub': 'Confidence',
        # The two copy strings include <strong>...</strong>; rendered with
        # the |safe filter in the template. These strings are fully
        # controlled here and are NOT user input — safe for |safe.
        'dashboard.summary.copy_inf': (
            'Our model suggests visual patterns associated with '
            '<strong>infection risk</strong>. Use this as supportive '
            'information only and follow up with a clinician for any '
            'concerning symptoms.'
        ),
        'dashboard.summary.copy_noninf': (
            'Your latest image aligns more strongly with '
            '<strong>non-infected</strong> patterns in the model. Continue '
            'monitoring and seek care if the wound worsens.'
        ),
        'dashboard.summary.view_full_result_prefix': 'View full result #',
        'dashboard.summary.empty': (
            'Your latest summary will appear here after you complete your '
            'first analysis.'
        ),

        # ---- Result page (result.html) ----
        'result.page_title': 'Analysis Result | WoundSense AI',
        'result.heading': 'AI Analysis Result',
        'result.subtitle_record_prefix': 'Record #',

        # Summary cards
        'result.label.prediction_status': 'Prediction status',
        'result.status.infected_model': 'Infected (model estimate)',
        'result.status.non_infected_model': 'Non-Infected (model estimate)',
        'result.label.confidence_score': 'Confidence score',

        # Image panels
        'result.panel.uploaded_image': 'Uploaded wound image',
        'result.panel.segmentation_overlay': 'AI segmentation overlay',
        'result.alt.model_overlay': 'Model overlay',

        # Interpretation. The two copy strings include <strong>...</strong>
        # and are rendered with |safe in the template. Both come exclusively
        # from this dictionary — never from user input.
        'result.interpretation.heading': 'Interpretation',
        'result.interpretation.copy_inf': (
            'The AI analysis suggests signs consistent with '
            '<strong>infection risk</strong> for this image. This is '
            'decision support only and not a diagnosis; clinical review '
            'is recommended, especially if symptoms are worsening.'
        ),
        'result.interpretation.copy_noninf': (
            'The AI analysis suggests features more consistent with '
            '<strong>healthy healing progression</strong> and lower '
            'infection risk on this image. Continue monitoring and follow '
            'your care plan.'
        ),

        # Suggested next steps
        'result.next_steps.heading': 'Suggested next steps',
        'result.next_steps.always': (
            'Monitor the wound regularly and capture images in consistent '
            'lighting.'
        ),
        'result.next_steps.inf1': (
            'Contact a healthcare professional promptly for medical '
            'assessment.'
        ),
        'result.next_steps.inf2': (
            'Seek urgent care if severe pain, fever, spreading redness, or '
            'discharge increases.'
        ),
        'result.next_steps.noninf1': (
            'Continue your wound care routine and follow prescribed '
            'treatment guidance.'
        ),
        'result.next_steps.noninf2': (
            'Consult your healthcare professional if symptoms worsen or '
            'healing stalls.'
        ),

        # Doctor review block. Free-text fields (comment/recommendation/name)
        # are intentionally NOT translated — they are entered by the doctor.
        # Only labels and the fixed enum review_status values get translated
        # at DISPLAY time; the database keeps the original English enum.
        'result.doctor_review.heading': 'Doctor Review',
        'result.doctor_review.status_label': 'Status:',
        'result.doctor_review.comment_label': 'Comment:',
        'result.doctor_review.recommendation_label': 'Recommendation:',
        'result.doctor_review.reviewed_by_label': 'Reviewed by:',
        'result.doctor_review.reviewed_at_label': 'Reviewed at:',
        'result.doctor_review.doctor_fallback': 'Doctor',
        'result.doctor_review.pending': 'Pending doctor review.',
        # Display-only translations of REVIEW_STATUS_OPTIONS in app.py.
        'result.doctor_review.status.stable': 'Stable',
        'result.doctor_review.status.needs_followup': 'Needs Follow-up',
        'result.doctor_review.status.urgent': 'Urgent Review Recommended',

        # Action row at the bottom of the page
        'result.meta.file_label': 'File: ',
        'result.action.back_dashboard': 'Back to Dashboard',
        'result.action.view_history': 'View Healing History',
        'result.action.delete_record': 'Delete record',
        'result.delete_confirm': (
            'Delete this record and its stored images?'
        ),

        # ---- Healing History page (history.html) ----
        # Display-only translation. The route still uses record.id for
        # /result/<id> and /delete/<id>; only the visible "#" column uses
        # the patient-facing display_number assigned in app.py.
        'history.page_title': 'Healing History | WoundSense AI',
        'history.heading': 'Healing History Timeline',
        'history.subtitle': 'Your analyses, newest first.',

        # Inline stats and filter
        'history.stats.total': 'Total',
        'history.stats.flagged': 'Flagged',
        'history.stats.non_infected_lean': 'Non-infected lean',
        'history.filter.label': 'Filter',
        'history.filter.placeholder': 'Search filename, number, or status',

        # Table headers (display)
        'history.table.number': '#',
        'history.table.original': 'Original',
        'history.table.overlay': 'Overlay',
        'history.table.file': 'File',
        'history.table.status': 'Status',
        'history.table.confidence': 'Confidence',
        'history.table.date': 'Date',
        'history.table.actions': 'Actions',

        # Status pill (DB still stores raw 'infected' / 'non-infected')
        'history.status.infected': 'Infected',
        'history.status.non_infected': 'Non-infected',

        # Row actions and confirmation dialog
        'history.action.view': 'View',
        'history.action.delete': 'Delete',
        'history.delete_confirm_prefix': 'Delete record #',
        'history.delete_confirm_suffix': '?',

        # Empty state (no patient records yet)
        'history.empty.title': 'No analyses yet',
        'history.empty.copy': (
            'No wound analyses yet. Upload a wound image from your patient '
            'dashboard to start tracking your healing progress.'
        ),
        'history.empty.action': 'Go to Patient Dashboard',

        # ---- Doctor portal (doctor-dashboard, doctor-report, includes) ----
        # Display-only; DB review_status values and form option values stay
        # English (REVIEW_STATUS_OPTIONS in app.py). Prediction labels in DB
        # stay 'infected' / 'non-infected'; only UI labels translate.

        # Sidebar (includes/doctor_sidebar.html)
        'doctor.sidebar.aria': 'Doctor navigation',
        'doctor.sidebar.role_label': 'Doctor',
        'doctor.nav.dashboard': 'Dashboard',
        'doctor.nav.patients': 'Patients',
        'doctor.nav.reports': 'Reports / Analysis Records',
        'doctor.nav.logout': 'Logout',

        # Footer (includes/doctor_footer.html)
        'doctor.footer.tagline': (
            'Clinical monitoring workspace for reviewing patient analyses and '
            'AI-assisted wound records.'
        ),

        # Model prediction display (raw values: infected | non-infected)
        'doctor.prediction.infected': 'Infected',
        'doctor.prediction.non_infected': 'Non-infected',

        # ---- Doctor dashboard (doctor-dashboard.html) ----
        'doctor.dash.page_title': 'Doctor Dashboard | WoundSense AI',
        'doctor.dash.welcome_prefix': 'Welcome, Dr. ',
        'doctor.dash.subtitle': (
            'Monitor patient analyses and prioritize follow-up safely.'
        ),
        'doctor.dash.link_view_all_patients': 'View All Patients',
        'doctor.dash.section.overview': 'Overview Analytics',
        'doctor.dash.kpi.total_cases': 'Total Cases Analyzed',
        'doctor.dash.kpi.active_infection_rate': 'Active Infection Rate',
        'doctor.dash.kpi.avg_ai_accuracy': 'Average AI Accuracy',
        'doctor.dash.kpi.patients_under_care': 'Patients Under Care',
        'doctor.dash.section.recent_analyses': 'Recent Patient Analyses',
        'doctor.dash.table.th.patient_name': 'Patient Name',
        'doctor.dash.table.th.wound_image': 'Wound Image',
        'doctor.dash.table.th.submission_date': 'Submission Date',
        'doctor.dash.table.th.status': 'Status',
        'doctor.dash.table.th.confidence': 'Confidence',
        'doctor.dash.table.th.action': 'Action',
        'doctor.dash.table.action_view_report': 'View Report',
        'doctor.dash.empty.title': 'No patient analyses yet',
        'doctor.dash.empty.text': (
            'Patient analysis records will appear here as patients upload '
            'wound images.'
        ),
        'doctor.dash.section.analytics': 'Analytics',
        'doctor.dash.chart.infection_trends': 'Infection Trends (Last 6 Months)',
        'doctor.dash.chart.ai_performance': 'AI Performance (Last 6 Months)',
        'doctor.dash.chart.not_enough_trend': (
            'Not enough real data yet to render trend values.'
        ),
        'doctor.dash.chart.not_enough_performance': (
            'Not enough real data yet to render performance values.'
        ),

        # ---- Doctor report (doctor-report.html) ----
        'doctor.report.page_title': 'Doctor Report | WoundSense AI',
        'doctor.report.heading': 'Patient Analysis Report',
        'doctor.report.back_dashboard': 'Back to dashboard',
        'doctor.report.card.patient': 'Patient',
        'doctor.report.label.name': 'Name:',
        'doctor.report.unassigned_patient': 'Unassigned patient',
        'doctor.report.label.email': 'Email:',
        'doctor.report.na': 'N/A',
        'doctor.report.label.submission_date': 'Submission date:',
        'doctor.report.card.model_result': 'Model result',
        'doctor.report.label.status': 'Status:',
        'doctor.report.label.confidence': 'Confidence:',
        'doctor.report.label.infected_prob': 'Infected probability:',
        'doctor.report.label.non_infected_prob': 'Non-infected probability:',
        'doctor.report.section.review': 'Doctor Review',
        'doctor.report.current_review.title': 'Current review',
        'doctor.report.current_review.none': (
            'No doctor review has been submitted yet.'
        ),
        'doctor.report.form_card.title': 'Add / Update review',
        'doctor.report.form.review_status': 'Review status',
        'doctor.report.form.select_status': 'Select status',
        'doctor.report.form.clinical_comment': 'Clinical comment',
        'doctor.report.form.placeholder.comment': (
            'Add professional clinical follow-up comment...'
        ),
        'doctor.report.form.recommendation': 'Recommendation',
        'doctor.report.form.placeholder.recommendation': (
            'Add guidance for patient follow-up...'
        ),
        'doctor.report.form.submit': 'Save Doctor Review',
        'doctor.report.panel.segmentation_overlay': 'Segmentation overlay',
        'doctor.report.interpretation.heading': 'Interpretation',
        'doctor.report.interpretation.copy_inf': (
            'The model indicates higher probability for infected-associated '
            'wound patterns. This should be reviewed as clinical decision '
            'support and correlated with examination findings.'
        ),
        'doctor.report.interpretation.copy_noninf': (
            'The model indicates higher probability for non-infected patterns. '
            'Continue follow-up based on wound evolution and patient symptoms.'
        ),
        'doctor.report.next_steps.heading': 'Suggested next steps',
        'doctor.report.next_steps.inf1': (
            'Prioritize clinical reassessment and evaluate for antimicrobial '
            'treatment needs.'
        ),
        'doctor.report.next_steps.inf2': (
            'Compare with prior images for progression of redness, swelling, '
            'or tissue changes.'
        ),
        'doctor.report.next_steps.inf3': (
            'Escalate care if systemic symptoms are present.'
        ),
        'doctor.report.next_steps.noninf1': (
            'Continue routine wound-care protocol and periodic image monitoring.'
        ),
        'doctor.report.next_steps.noninf2': (
            'Document progress trend and reassess if symptoms worsen.'
        ),
        'doctor.report.next_steps.noninf3': (
            'Maintain follow-up schedule per care plan.'
        ),
        'doctor.report.section.history': 'Patient Submission History',
        'doctor.report.table.th.id': 'ID',
        'doctor.report.table.th.date': 'Date',
        'doctor.report.table.th.status': 'Status',
        'doctor.report.table.th.confidence': 'Confidence',
        'doctor.report.table.th.action': 'Action',
        'doctor.report.table.action_open': 'Open',
        'doctor.report.history.empty': (
            'No additional submissions found for this patient yet.'
        ),
    },
    'ar': {
        # ---- Splash (only shown on first visit) ----
        'splash.tagline': 'مراقبة الجروح بمساعدة الذكاء الاصطناعي',

        # ---- Header / nav (shared by homepage + auth pages) ----
        'nav.menu_button': 'القائمة',
        'nav.menu_open_aria': 'فتح القائمة',
        'nav.account_aria': 'الحساب',
        'nav.language_aria': 'اللغة',
        'nav.site_aria': 'الموقع',
        'nav.home': 'الرئيسية',
        'nav.patient_login': 'دخول المريض',
        'nav.patient_signup': 'إنشاء حساب مريض',
        'nav.doctor_login': 'دخول الطبيب',

        # ---- Homepage: hero ----
        'home.hero.title': 'كشف عدوى الجروح وتتبّع التعافي بدعم الذكاء الاصطناعي',
        'home.hero.lead': (
            'يساعد WoundSense AI المرضى والأطباء على متابعة التئام الجروح، '
            'والكشف المبكر عن مخاطر العدوى، ودعم متابعة أفضل عبر تحليل صور '
            'الجروح بمساعدة الذكاء الاصطناعي.'
        ),
        'home.hero.learn_link': 'تعرّف على المشروع',

        # ---- Homepage: how it works ----
        'home.works.heading': 'كيف يعمل WoundSense AI',
        'home.works.card1.title': 'رفع صورة الجرح',
        'home.works.card1.text': (
            'ارفع صور الجرح بدقة عالية بأمان مباشرة من جهازك.'
        ),
        'home.works.card2.title': 'تحليل بالذكاء الاصطناعي وكشف المخاطر',
        'home.works.card2.text': (
            'يحلّل محرك الذكاء الاصطناعي الصور لرصد إشارات احتمال العدوى '
            'ودعم تقييم تقدّم التعافي.'
        ),
        'home.works.card3.title': 'تتبّع التعافي عبر الزمن',
        'home.works.card3.text': (
            'راقب التغيّرات برؤية أوضح، وتحليل قائم على درجة الثقة، وسجلّ '
            'زمني يدعم متابعة التعافي.'
        ),

        # ---- Homepage: empower ----
        'home.empower.heading': 'رعاية أفضل للجميع',
        'home.empower.patients.title': 'للمرضى',
        'home.empower.patients.item1': (
            'اطمئنان أكبر من خلال الوعي المبكر بمخاطر العدوى.'
        ),
        'home.empower.patients.item2': (
            'فهم رحلة التعافي بمعلومات منظَّمة وأكثر وضوحًا.'
        ),
        'home.empower.patients.item3': (
            'متابعة التقدّم بمرور الوقت عبر سجلّ زمني واضح.'
        ),
        'home.empower.patients.item4': (
            'مشاركة المستجدّات بسهولة مع مقدّم الرعاية الصحية.'
        ),
        'home.empower.doctors.title': 'للأطباء',
        'home.empower.doctors.item1': (
            'تعزيز السياق السريري برؤى مدعومة بالذكاء الاصطناعي.'
        ),
        'home.empower.doctors.item2': (
            'متابعة الحالات بكفاءة عبر اتجاهات وسجلّات منظَّمة.'
        ),
        'home.empower.doctors.item3': (
            'تسهيل التواصل والتثقيف مع المرضى أثناء المتابعة.'
        ),
        'home.empower.doctors.item4': (
            'دعم سير عمل التوثيق والتخطيط العلاجي.'
        ),

        # ---- Homepage: about ----
        'home.about.heading': 'حول WoundSense AI',
        'home.about.text': (
            'WoundSense AI منصّة طبية ذكية مصمَّمة للمساعدة في كشف عدوى '
            'الجروح ومراقبة تقدّم التعافي. تجمع المنصّة بين تحليل صور الجروح، '
            'والتنبّؤ بمخاطر العدوى، وتتبّع السجلّات لدعم المرضى والكوادر '
            'الصحية.'
        ),
        'home.about.feature1': 'الكشف المبكر عن العدوى',
        'home.about.feature2': 'متابعة تقدّم التعافي',
        'home.about.feature3': 'دعم المريض والطبيب',

        # ---- Footer ----
        'footer.tagline': (
            'مراقبة الجروح بمساعدة الذكاء الاصطناعي لمتابعة أوضح ورؤى '
            'سريرية أكثر أمانًا.'
        ),
        'footer.copyright': '© 2026 WoundSense AI. جميع الحقوق محفوظة.',

        # ---- Authentication pages (login / signup / doctor login) ----
        # Browser tab titles
        'auth.page_title.login': 'دخول المريض | WoundSense AI',
        'auth.page_title.signup': 'إنشاء حساب مريض | WoundSense AI',
        'auth.page_title.doctor_login': 'دخول الطبيب | WoundSense AI',

        # Shared form labels
        'auth.label.email': 'البريد الإلكتروني',
        'auth.label.password': 'كلمة المرور',
        'auth.label.full_name': 'الاسم الكامل',
        'auth.label.confirm_password': 'تأكيد كلمة المرور',

        # Shared placeholders. Email/format examples stay in Latin in
        # both languages (universal email convention).
        'auth.placeholder.email_example': 'name@example.com',
        'auth.placeholder.email_doctor_example': 'doctor@hospital.org',
        'auth.placeholder.password_enter': 'أدخل كلمة المرور',
        'auth.placeholder.password_create': 'أنشئ كلمة مرور (٨ أحرف فأكثر)',
        'auth.placeholder.password_confirm': 'أكِّد كلمة المرور',
        'auth.placeholder.full_name': 'أدخل اسمك الكامل',

        # Patient login card
        'auth.login.title': 'دخول المريض',
        'auth.login.lead': (
            'اطّلع على تقارير الجروح، والجدول الزمني للمتابعة، وإرشادات '
            'الرعاية في مكان واحد.'
        ),
        'auth.login.submit': 'متابعة إلى لوحة المريض',
        'auth.login.helper_prefix': 'ليس لديك حساب؟',
        'auth.login.helper_link': 'إنشاء حساب مريض',

        # Patient signup card
        'auth.signup.title': 'إنشاء حساب مريض',
        'auth.signup.lead': (
            'أنشئ حسابًا للوصول إلى تقارير الجروح، والجدول الزمني للتعافي، '
            'ودعم المتابعة.'
        ),
        'auth.signup.submit': 'إنشاء حساب مريض',
        'auth.signup.helper_prefix': 'لديك حساب بالفعل؟',
        # The link text reuses nav.patient_login.

        # Doctor login card
        'auth.doctor_login.title': 'دخول الطبيب',
        'auth.doctor_login.lead': (
            'اطّلع على تقدّم جروح المرضى، والرؤى المدعومة بالذكاء '
            'الاصطناعي، وسجلات المتابعة.'
        ),
        'auth.doctor_login.submit': 'متابعة إلى لوحة الطبيب',
        'auth.doctor_login.helper_prefix': 'هل أنت مريض؟ انتقل إلى',
        # The link text reuses nav.patient_login.

        # ---- Patient dashboard (user-dashboard.html) ----
        'dashboard.page_title': 'لوحة المريض | WoundSense AI',

        # Sidebar (patient_sidebar.html include)
        'dashboard.sidebar.aria': 'تنقّل المريض',
        'dashboard.sidebar.signed_in': 'تسجيل الدخول كـ',
        'dashboard.nav.dashboard': 'اللوحة',
        'dashboard.nav.start_analysis': 'بدء تحليل جديد',
        'dashboard.nav.history': 'سجلّ التعافي',
        'dashboard.nav.logout': 'تسجيل الخروج',

        # Welcome row. The patient name itself is dynamic and not translated.
        'dashboard.welcome_prefix': 'أهلاً، ',

        # Upload card
        'dashboard.upload.lead': (
            'ارفع صورة الجرح للتحليل بمساعدة الذكاء الاصطناعي. تُحفظ '
            'النتائج في سجلّك الخاص.'
        ),
        'dashboard.upload.dropzone_title': 'اضغط للرفع أو اسحب الصورة هنا',
        'dashboard.upload.dropzone_hint': (
            'الصيغ المقبولة: JPG، PNG، BMP، WEBP (الحد الأقصى ١٦ ميغابايت)'
        ),
        'dashboard.upload.submit': 'رفع وتحليل',
        'dashboard.upload.preview_alt': 'معاينة صورة الجرح المختارة',
        'dashboard.upload.progress_text': (
            'جاري التحليل بالذكاء الاصطناعي. يُرجى الانتظار.'
        ),
        # Strings consumed by main.js via data-msg-* attributes.
        'dashboard.upload.msg_unsupported': (
            'نوع ملف غير مدعوم. يُرجى اختيار JPG أو PNG أو BMP أو WEBP.'
        ),
        'dashboard.upload.msg_selected': (
            'تم اختيار الصورة. جاهزة للتحليل بالذكاء الاصطناعي.'
        ),
        'dashboard.upload.msg_choose_first': (
            'يُرجى اختيار صورة قبل بدء التحليل.'
        ),
        'dashboard.upload.btn_analyzing': 'جاري تحليل الصورة...',

        # Recent submissions
        'dashboard.recent.heading': 'آخر التحليلات',
        'dashboard.recent.empty': (
            'لا توجد تحليلات للجروح بعد. ارفع صورة جرح لبدء تتبّع تقدّم '
            'التعافي.'
        ),

        # Status pills (also reused inline as bold inside summary copy)
        'dashboard.status.infection_risk': 'احتمال عدوى',
        'dashboard.status.lower_risk': 'احتمال أقل',
        'dashboard.status.infection_flagged': 'تنبيه باحتمال عدوى',
        'dashboard.status.favoring_non_infected': 'ترجيح عدم وجود عدوى',

        # Confidence label used in recent card row.
        'dashboard.field.confidence_label': 'درجة الثقة: ',

        # Latest status summary section
        'dashboard.summary.heading': 'ملخّص آخر حالة',
        'dashboard.summary.current_status_label': 'الحالة الراهنة',
        'dashboard.summary.last_analysis_label': 'آخر تحليل: ',
        'dashboard.summary.confidence_sub': 'الثقة',
        # The two copy strings include <strong>...</strong>; rendered with
        # the |safe filter in the template. These strings are fully
        # controlled here and are NOT user input — safe for |safe.
        'dashboard.summary.copy_inf': (
            'يُشير النموذج إلى أنماط بصرية تتوافق مع '
            '<strong>احتمال عدوى</strong>. استخدم هذه المعلومات كدعم فقط '
            'وراجع طبيبًا في حال ظهور أي أعراض مقلقة.'
        ),
        'dashboard.summary.copy_noninf': (
            'تتوافق آخر صورة لك بشكل أوضح مع أنماط '
            '<strong>غير مصابة بالعدوى</strong> وفق النموذج. تابع المراقبة '
            'واطلب رعاية طبية في حال تفاقم الجرح.'
        ),
        'dashboard.summary.view_full_result_prefix': 'عرض النتيجة الكاملة رقم ',
        'dashboard.summary.empty': (
            'سيظهر آخر ملخّص هنا بعد إتمام أوّل تحليل لك.'
        ),

        # ---- Result page (result.html) ----
        'result.page_title': 'نتيجة التحليل | WoundSense AI',
        'result.heading': 'نتيجة تحليل الذكاء الاصطناعي',
        'result.subtitle_record_prefix': 'السجل رقم ',

        # Summary cards
        'result.label.prediction_status': 'حالة التنبّؤ',
        'result.status.infected_model': 'مصابة (تقدير النموذج)',
        'result.status.non_infected_model': 'غير مصابة (تقدير النموذج)',
        'result.label.confidence_score': 'درجة الثقة',

        # Image panels
        'result.panel.uploaded_image': 'صورة الجرح المرفوعة',
        'result.panel.segmentation_overlay': 'تجزئة الجرح بالذكاء الاصطناعي',
        'result.alt.model_overlay': 'تراكب النموذج',

        # Interpretation
        'result.interpretation.heading': 'التفسير',
        'result.interpretation.copy_inf': (
            'يُشير تحليل الذكاء الاصطناعي إلى علامات متوافقة مع '
            '<strong>احتمال عدوى</strong> في هذه الصورة. هذه نتيجة دعم '
            'قرار وليست تشخيصًا؛ يُنصح بالمراجعة الطبية، خاصةً عند تفاقم '
            'الأعراض.'
        ),
        'result.interpretation.copy_noninf': (
            'يُشير تحليل الذكاء الاصطناعي إلى ملامح أكثر توافقًا مع '
            '<strong>تقدّم تعافٍ سليم</strong> واحتمال أقل للعدوى في هذه '
            'الصورة. تابع المراقبة واستمر على خطّة الرعاية.'
        ),

        # Suggested next steps
        'result.next_steps.heading': 'الخطوات التالية المقترحة',
        'result.next_steps.always': (
            'راقب الجرح بانتظام والتقط الصور في إضاءة موحَّدة.'
        ),
        'result.next_steps.inf1': (
            'تواصل سريعًا مع كادر صحي لإجراء التقييم الطبي.'
        ),
        'result.next_steps.inf2': (
            'اطلب رعاية عاجلة عند ظهور ألم شديد أو حمى أو احمرار منتشر أو '
            'زيادة في الإفرازات.'
        ),
        'result.next_steps.noninf1': (
            'استمرّ في روتين العناية بالجرح واتّبع الإرشادات العلاجية '
            'الموصوفة.'
        ),
        'result.next_steps.noninf2': (
            'استشر الكادر الصحي إذا تفاقمت الأعراض أو توقّف التعافي.'
        ),

        # Doctor review
        'result.doctor_review.heading': 'مراجعة الطبيب',
        'result.doctor_review.status_label': 'الحالة:',
        'result.doctor_review.comment_label': 'التعليق:',
        'result.doctor_review.recommendation_label': 'التوصية:',
        'result.doctor_review.reviewed_by_label': 'تمت المراجعة من قِبَل:',
        'result.doctor_review.reviewed_at_label': 'تاريخ المراجعة:',
        'result.doctor_review.doctor_fallback': 'الطبيب',
        'result.doctor_review.pending': 'في انتظار مراجعة الطبيب.',
        'result.doctor_review.status.stable': 'مستقرّة',
        'result.doctor_review.status.needs_followup': 'تحتاج إلى متابعة',
        'result.doctor_review.status.urgent': 'يُوصى بمراجعة عاجلة',

        # Action row at the bottom of the page
        'result.meta.file_label': 'الملف: ',
        'result.action.back_dashboard': 'العودة إلى اللوحة',
        'result.action.view_history': 'عرض سجلّ التعافي',
        'result.action.delete_record': 'حذف السجل',
        'result.delete_confirm': (
            'هل تريد حذف هذا السجل والصور المخزَّنة معه؟'
        ),

        # ---- Healing History page (history.html) ----
        'history.page_title': 'سجلّ التعافي | WoundSense AI',
        'history.heading': 'الخط الزمني لسجلّ التعافي',
        'history.subtitle': 'تحليلاتك، الأحدث أولاً.',

        'history.stats.total': 'الإجمالي',
        'history.stats.flagged': 'المُعلَّمة',
        'history.stats.non_infected_lean': 'تميل لعدم الإصابة',
        'history.filter.label': 'تصفية',
        'history.filter.placeholder': 'ابحث باسم الملف أو الرقم أو الحالة',

        'history.table.number': '#',
        'history.table.original': 'الصورة الأصلية',
        'history.table.overlay': 'الطبقة التحليلية',
        'history.table.file': 'الملف',
        'history.table.status': 'الحالة',
        'history.table.confidence': 'الثقة',
        'history.table.date': 'التاريخ',
        'history.table.actions': 'الإجراءات',

        'history.status.infected': 'مصاب',
        'history.status.non_infected': 'غير مصاب',

        'history.action.view': 'عرض',
        'history.action.delete': 'حذف',
        'history.delete_confirm_prefix': 'حذف السجل رقم ',
        'history.delete_confirm_suffix': '؟',

        'history.empty.title': 'لا توجد تحليلات بعد',
        'history.empty.copy': (
            'لا توجد تحليلات للجروح بعد. ارفع صورة من لوحة المريض لبدء '
            'متابعة تقدّم تعافيك.'
        ),
        'history.empty.action': 'الذهاب إلى لوحة المريض',

        # ---- Doctor portal (doctor-dashboard, doctor-report, includes) ----
        'doctor.sidebar.aria': 'تنقّل الطبيب',
        'doctor.sidebar.role_label': 'طبيب',
        'doctor.nav.dashboard': 'لوحة الطبيب',
        'doctor.nav.patients': 'المرضى',
        'doctor.nav.reports': 'التقارير / سجلّ التحليلات',
        'doctor.nav.logout': 'تسجيل الخروج',

        'doctor.footer.tagline': (
            'مساحة عمل سريرية لمراجعة تحليلات المرضى وسجلات الجروح المدعومة '
            'بالذكاء الاصطناعي.'
        ),

        'doctor.prediction.infected': 'مصابة',
        'doctor.prediction.non_infected': 'غير مصابة',

        'doctor.dash.page_title': 'لوحة الطبيب | WoundSense AI',
        'doctor.dash.welcome_prefix': 'أهلاً، د. ',
        'doctor.dash.subtitle': (
            'راقب تحليلات المرضى ونظّم المتابعة بأمان.'
        ),
        'doctor.dash.link_view_all_patients': 'عرض جميع المرضى',
        'doctor.dash.section.overview': 'نظرة تحليلية عامة',
        'doctor.dash.kpi.total_cases': 'إجمالي الحالات المحلّلة',
        'doctor.dash.kpi.active_infection_rate': 'معدّل العدوى النشطة',
        'doctor.dash.kpi.avg_ai_accuracy': 'متوسط دقة الذكاء الاصطناعي',
        'doctor.dash.kpi.patients_under_care': 'مرضى تحت المتابعة',
        'doctor.dash.section.recent_analyses': 'آخر تحليلات المرضى',
        'doctor.dash.table.th.patient_name': 'اسم المريض',
        'doctor.dash.table.th.wound_image': 'صورة الجرح',
        'doctor.dash.table.th.submission_date': 'تاريخ الإرسال',
        'doctor.dash.table.th.status': 'الحالة',
        'doctor.dash.table.th.confidence': 'الثقة',
        'doctor.dash.table.th.action': 'إجراء',
        'doctor.dash.table.action_view_report': 'عرض التقرير',
        'doctor.dash.empty.title': 'لا توجد تحليلات للمرضى بعد',
        'doctor.dash.empty.text': (
            'ستظهر سجلات تحليل المرضى هنا عند رفعهم لصور الجروح.'
        ),
        'doctor.dash.section.analytics': 'التحليلات',
        'doctor.dash.chart.infection_trends': 'اتجاهات العدوى (آخر ٦ أشهر)',
        'doctor.dash.chart.ai_performance': 'أداء الذكاء الاصطناعي (آخر ٦ أشهر)',
        'doctor.dash.chart.not_enough_trend': (
            'لا تتوفر بيانات كافية بعد لعرض اتجاهات العدوى.'
        ),
        'doctor.dash.chart.not_enough_performance': (
            'لا تتوفر بيانات كافية بعد لعرض قيم الأداء.'
        ),

        'doctor.report.page_title': 'تقرير الطبيب | WoundSense AI',
        'doctor.report.heading': 'تقرير تحليل المريض',
        'doctor.report.back_dashboard': 'العودة إلى لوحة الطبيب',
        'doctor.report.card.patient': 'المريض',
        'doctor.report.label.name': 'الاسم:',
        'doctor.report.unassigned_patient': 'مريض غير مرتبط',
        'doctor.report.label.email': 'البريد الإلكتروني:',
        'doctor.report.na': 'غير متوفر',
        'doctor.report.label.submission_date': 'تاريخ الإرسال:',
        'doctor.report.card.model_result': 'نتيجة النموذج',
        'doctor.report.label.status': 'الحالة:',
        'doctor.report.label.confidence': 'الثقة:',
        'doctor.report.label.infected_prob': 'احتمال العدوى:',
        'doctor.report.label.non_infected_prob': 'احتمال عدم العدوى:',
        'doctor.report.section.review': 'مراجعة الطبيب',
        'doctor.report.current_review.title': 'المراجعة الحالية',
        'doctor.report.current_review.none': (
            'لم تُرسَل مراجعة طبيب بعد.'
        ),
        'doctor.report.form_card.title': 'إضافة / تحديث المراجعة',
        'doctor.report.form.review_status': 'حالة المراجعة',
        'doctor.report.form.select_status': 'اختر الحالة',
        'doctor.report.form.clinical_comment': 'تعليق سريري',
        'doctor.report.form.placeholder.comment': (
            'أضف تعليقًا سريريًا للمتابعة...'
        ),
        'doctor.report.form.recommendation': 'التوصية',
        'doctor.report.form.placeholder.recommendation': (
            'أضف إرشادات لمتابعة المريض...'
        ),
        'doctor.report.form.submit': 'حفظ مراجعة الطبيب',
        'doctor.report.panel.segmentation_overlay': 'تراكب التجزئة',
        'doctor.report.interpretation.heading': 'التفسير',
        'doctor.report.interpretation.copy_inf': (
            'يُشير النموذج إلى احتمال أعلى لأنماط جروح مرتبطة بالعدوى. يُرجى '
            'استخدام ذلك كدعم قرار سريري ومطابقته مع نتائج الفحص.'
        ),
        'doctor.report.interpretation.copy_noninf': (
            'يُشير النموذج إلى احتمال أعلى لأنماط غير مصابة بالعدوى. تابع '
            'المتابعة وفق تطوّر الجرح وأعراض المريض.'
        ),
        'doctor.report.next_steps.heading': 'الخطوات التالية المقترحة',
        'doctor.report.next_steps.inf1': (
            'أعِد التقييم السريري بأولوية وقيّم الحاجة إلى علاج مضاد للميكروبات.'
        ),
        'doctor.report.next_steps.inf2': (
            'قارِن مع الصور السابقة لتقدّم الاحمرار أو التورّم أو تغيّر الأنسجة.'
        ),
        'doctor.report.next_steps.inf3': (
            'صعّد مستوى الرعاية عند وجود أعراض جهازية.'
        ),
        'doctor.report.next_steps.noninf1': (
            'استمرّ في بروتوكول العناية بالجرح والمراقبة الدورية بالصور.'
        ),
        'doctor.report.next_steps.noninf2': (
            'وثّق اتجاه التحسّن وأعد التقييم عند تفاقم الأعراض.'
        ),
        'doctor.report.next_steps.noninf3': (
            'حافظ على جدول المتابعة وفق خطة الرعاية.'
        ),
        'doctor.report.section.history': 'سجلّ إرسالات المريض',
        'doctor.report.table.th.id': 'المعرّف',
        'doctor.report.table.th.date': 'التاريخ',
        'doctor.report.table.th.status': 'الحالة',
        'doctor.report.table.th.confidence': 'الثقة',
        'doctor.report.table.th.action': 'إجراء',
        'doctor.report.table.action_open': 'فتح',
        'doctor.report.history.empty': (
            'لا توجد إرسالات إضافية لهذا المريض بعد.'
        ),
    },
}


# --- Helpers --------------------------------------------------------------

def is_supported(lang):
    """Return True if `lang` is a known language code."""
    return lang in SUPPORTED_LANGUAGES


def normalize_language(lang):
    """Coerce any value to a supported language code, defaulting to English."""
    if lang in SUPPORTED_LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE


def text_direction_for(lang):
    """Return 'rtl' for RTL languages, 'ltr' otherwise."""
    return 'rtl' if lang in RTL_LANGUAGES else 'ltr'


def is_rtl(lang):
    """Convenience boolean for templates."""
    return lang in RTL_LANGUAGES


def t(key, lang=DEFAULT_LANGUAGE):
    """
    Translate `key` for the given language.

    Resolution order:
        1. Exact match in TRANSLATIONS[lang]
        2. Exact match in TRANSLATIONS[DEFAULT_LANGUAGE]
        3. The key itself (so missing keys never break rendering)
    """
    table = TRANSLATIONS.get(lang) or {}
    if key in table:
        return table[key]
    fallback = TRANSLATIONS.get(DEFAULT_LANGUAGE) or {}
    return fallback.get(key, key)
