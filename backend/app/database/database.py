import sqlite3
import os
import json
from contextlib import contextmanager

DB_PATH = os.environ.get("GRAMCARE_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "gramcare.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def query_one(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def query_all(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def execute_query(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.lastrowid

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- PATIENT, DOCTOR, HOSPITAL, COMMUNITY_REP, ADMIN
            full_name TEXT NOT NULL,
            phone TEXT,
            preferred_language TEXT DEFAULT 'en', -- en, hi, gu
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Patients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            age INTEGER,
            gender TEXT,
            village TEXT,
            district TEXT,
            state TEXT DEFAULT 'Gujarat',
            pin_code TEXT,
            emergency_contact TEXT,
            blood_group TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            abha_id TEXT,
            abha_status TEXT DEFAULT 'NOT_LINKED', -- NOT_LINKED, PENDING, LINKED
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Doctors table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            qualification TEXT,
            license_number TEXT UNIQUE,
            specialization TEXT NOT NULL,
            experience_years INTEGER DEFAULT 0,
            languages_spoken TEXT, -- JSON string or comma-separated
            consultation_fee REAL DEFAULT 0.0,
            hospital_affiliation TEXT,
            bio TEXT,
            avatar_emoji TEXT DEFAULT '👨🏽‍⚕️',
            verification_status TEXT DEFAULT 'PENDING', -- PENDING, VERIFIED, REJECTED, SUSPENDED
            verification_document TEXT,
            rating_avg REAL DEFAULT 5.0,
            reviews_count INTEGER DEFAULT 0,
            availability_schedule TEXT, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Organizations / Hospitals table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            org_name TEXT NOT NULL,
            org_type TEXT NOT NULL, -- HOSPITAL, NGO, GOVT, CSR
            registration_number TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            address TEXT,
            district TEXT,
            state TEXT DEFAULT 'Gujarat',
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Appointments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            doctor_id TEXT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            appointment_date TEXT NOT NULL, -- YYYY-MM-DD
            time_slot TEXT NOT NULL, -- e.g. 10:00 AM - 10:30 AM
            consultation_mode TEXT DEFAULT 'VIDEO', -- VIDEO, AUDIO, CHAT
            status TEXT DEFAULT 'CONFIRMED', -- REQUESTED, CONFIRMED, UPCOMING, IN_PROGRESS, COMPLETED, CANCELLED, NO_SHOW
            chief_complaint TEXT,
            symptoms TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 6. Consultations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id TEXT PRIMARY KEY,
            appointment_id TEXT UNIQUE REFERENCES appointments(id) ON DELETE SET NULL,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            doctor_id TEXT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            mode TEXT DEFAULT 'VIDEO',
            status TEXT DEFAULT 'IN_PROGRESS', -- IN_PROGRESS, COMPLETED
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            clinical_notes TEXT,
            diagnosis TEXT,
            follow_up_advice TEXT,
            follow_up_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. Consultation Messages (Chat)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultation_messages (
            id TEXT PRIMARY KEY,
            consultation_id TEXT NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
            sender_id TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            sender_role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 8. Prescriptions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id TEXT PRIMARY KEY,
            consultation_id TEXT NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            doctor_id TEXT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            medications_json TEXT NOT NULL, -- List of {name, dosage, timing, duration, instructions}
            general_advice TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 9. Health Records / Documents
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            record_type TEXT NOT NULL, -- PRESCRIPTION, LAB_REPORT, SCAN, CLINICAL_NOTE, VACCINATION
            file_path TEXT,
            date_recorded TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            notes TEXT,
            is_abha_synced INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 10. AI Triage Assessments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_triage_assessments (
            id TEXT PRIMARY KEY,
            patient_id TEXT REFERENCES patients(id) ON DELETE SET NULL,
            symptoms_input TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            duration TEXT,
            severity TEXT,
            urgency TEXT NOT NULL, -- LOW, MODERATE, HIGH, EMERGENCY
            suggested_department TEXT NOT NULL,
            red_flags_json TEXT,
            summary TEXT NOT NULL,
            recommended_action TEXT,
            confidence REAL DEFAULT 0.90,
            disclaimer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 11. Medical Image Screenings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_image_screenings (
            id TEXT PRIMARY KEY,
            patient_id TEXT REFERENCES patients(id) ON DELETE SET NULL,
            image_type TEXT NOT NULL, -- CHEST_XRAY, DERMATOLOGY, GENERAL
            image_filename TEXT NOT NULL,
            detected_finding TEXT NOT NULL,
            confidence REAL NOT NULL,
            red_flag INTEGER DEFAULT 0,
            analysis_summary TEXT,
            doctor_review_status TEXT DEFAULT 'PENDING_REVIEW', -- PENDING_REVIEW, REVIEWED
            doctor_notes TEXT,
            disclaimer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 12. Health Camps
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_camps (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            camp_type TEXT NOT NULL, -- General, Eye Care, Women, Pediatric, Diabetes, Dental, Vaccination
            description TEXT,
            organizer_name TEXT NOT NULL,
            organizer_type TEXT DEFAULT 'HOSPITAL', -- HOSPITAL, NGO, DOCTOR, GOVT
            organizer_id TEXT,
            location TEXT NOT NULL,
            village TEXT NOT NULL,
            district TEXT NOT NULL,
            state TEXT DEFAULT 'Gujarat',
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            capacity INTEGER NOT NULL DEFAULT 100,
            registered_count INTEGER NOT NULL DEFAULT 0,
            services_json TEXT, -- JSON array of services
            equipment_json TEXT,
            doctors_needed INTEGER DEFAULT 2,
            is_free INTEGER DEFAULT 1,
            status TEXT DEFAULT 'SCHEDULED', -- SCHEDULED, REGISTRATION_OPEN, ONGOING, COMPLETED, CANCELLED
            impact_report_json TEXT, -- patients_attended, consultations, referrals, medicines_given
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 13. Camp Requests (from village / community reps)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS camp_requests (
            id TEXT PRIMARY KEY,
            requester_id TEXT REFERENCES users(id) ON DELETE SET NULL,
            requester_name TEXT NOT NULL,
            requester_type TEXT NOT NULL, -- Village Representative, NGO, School, Society, Individual
            village TEXT NOT NULL,
            district TEXT NOT NULL,
            state TEXT DEFAULT 'Gujarat',
            contact_person TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            expected_patients INTEGER DEFAULT 100,
            preferred_date TEXT NOT NULL,
            preferred_time TEXT DEFAULT 'Morning 9:00 AM',
            camp_type TEXT NOT NULL,
            required_services_json TEXT,
            urgency TEXT DEFAULT 'Normal', -- Normal, Urgent
            description TEXT,
            status TEXT DEFAULT 'PENDING', -- PENDING, REVIEWED, ACCEPTED, REJECTED, SCHEDULED, COMPLETED
            accepted_by_id TEXT,
            accepted_by_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 14. Camp Registrations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS camp_registrations (
            id TEXT PRIMARY KEY,
            camp_id TEXT NOT NULL REFERENCES health_camps(id) ON DELETE CASCADE,
            patient_id TEXT REFERENCES patients(id) ON DELETE SET NULL,
            patient_name TEXT NOT NULL,
            phone TEXT,
            age INTEGER,
            gender TEXT,
            village TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            attended INTEGER DEFAULT 0,
            notes TEXT
        );
        """)

        # 15. Doctor Reviews & Ratings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_reviews (
            id TEXT PRIMARY KEY,
            doctor_id TEXT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            consultation_id TEXT UNIQUE REFERENCES consultations(id) ON DELETE CASCADE,
            patient_initials TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            communication_score INTEGER DEFAULT 5,
            punctuality_score INTEGER DEFAULT 5,
            explanation_score INTEGER DEFAULT 5,
            review_text TEXT,
            is_verified INTEGER DEFAULT 1,
            is_moderated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 16. ABDM / ABHA Consents
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS abdm_consents (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            doctor_id TEXT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            purpose TEXT NOT NULL, -- Care Management, Teleconsultation, Emergency
            records_requested TEXT NOT NULL, -- Prescription, DiagnosticReport, OPDRecord
            consent_status TEXT DEFAULT 'PENDING', -- PENDING, GRANTED, DENIED, EXPIRED, REVOKED
            granted_at TIMESTAMP,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 17. In-App Notifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL, -- APPOINTMENT, CAMP, RATING, CONSENT, SYSTEM
            is_read INTEGER DEFAULT 0,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 18. Audit Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT NOT NULL,
            resource TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            status TEXT DEFAULT 'SUCCESS',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
