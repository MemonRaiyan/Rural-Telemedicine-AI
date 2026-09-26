import os
import json
import hashlib
import uuid
from backend.app.database.database import get_db, init_db, query_one

def hash_password(password: str) -> str:
    salt = "gramcare_salt_secure_2026"
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()

def seed_database():
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT count(*) as count FROM users")
        if cursor.fetchone()[0] > 0:
            print("Database already contains data. Skipping initial seeding or refreshing demo records.")
            return

        print("Seeding GramCare AI demo database...")
        pwd_hash = hash_password("password123")

        # 1. Users
        users_data = [
            ("usr_patient", "patient@gramcare.in", pwd_hash, "PATIENT", "Ramesh Patel", "+91 98765 43210", "gu"),
            ("usr_doc_anjali", "anjali@gramcare.in", pwd_hash, "DOCTOR", "Dr. Anjali Patel", "+91 98222 11001", "gu"),
            ("usr_doc_vikram", "vikram@gramcare.in", pwd_hash, "DOCTOR", "Dr. Vikram Singh", "+91 98333 22002", "hi"),
            ("usr_doc_priya", "priya@gramcare.in", pwd_hash, "DOCTOR", "Dr. Priya Sharma", "+91 98444 33003", "en"),
            ("usr_doc_meera", "meera@gramcare.in", pwd_hash, "DOCTOR", "Dr. Meera Desai", "+91 98555 44004", "gu"),
            ("usr_hospital", "hospital@gramcare.in", pwd_hash, "HOSPITAL", "Shakti Community Hospital", "+91 2762 234567", "en"),
            ("usr_village", "village@gramcare.in", pwd_hash, "COMMUNITY_REP", "Bhavesh Patel (Sarpanch)", "+91 98799 55443", "gu"),
            ("usr_admin", "admin@gramcare.in", pwd_hash, "ADMIN", "GramCare Administrator", "+91 11 2345 6789", "en")
        ]
        cursor.executemany("""
            INSERT INTO users (id, email, password_hash, role, full_name, phone, preferred_language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, users_data)

        # 2. Patients
        cursor.execute("""
            INSERT INTO patients (id, user_id, age, gender, village, district, state, pin_code, emergency_contact, blood_group, allergies, chronic_conditions, abha_id, abha_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "pat_ramesh", "usr_patient", 38, "Male", "Rampura", "Mehsana", "Gujarat", "384001",
            "+91 98765 43211 (Brother)", "B+", "Penicillin", "Mild Hypertension", "14-2394-3948-2938", "LINKED"
        ))

        # 3. Doctors
        doctors_data = [
            ("doc_anjali", "usr_doc_anjali", "MBBS, MD (General Medicine)", "GMC-GJ-48291", "General Physician", 8,
             json.dumps(["Gujarati", "Hindi", "English"]), 0.0, "Shakti Community Hospital & Rural Outreach",
             "Dedicated rural healthcare physician with 8 years of teleconsultation and primary care experience.",
             "👩🏽‍⚕️", "VERIFIED", "gmc_reg_48291.pdf", 4.8, 126,
             json.dumps(["09:00 AM - 12:00 PM", "02:00 PM - 05:00 PM", "06:00 PM - 08:00 PM"])),
            
            ("doc_vikram", "usr_doc_vikram", "MBBS, DCH (Pediatrics)", "DMC-DL-39102", "Pediatrician", 6,
             json.dumps(["Hindi", "English"]), 0.0, "North Gujarat Child Wellness Center",
             "Specialized in child immunization, acute pediatric infections, and maternal-child health.",
             "👨🏽‍⚕️", "VERIFIED", "dmc_reg_39102.pdf", 4.9, 89,
             json.dumps(["10:00 AM - 01:00 PM", "03:00 PM - 06:00 PM"])),

            ("doc_priya", "usr_doc_priya", "MBBS, MD (Dermatology)", "MMC-MH-58201", "Dermatologist", 5,
             json.dumps(["English", "Hindi"]), 50.0, "Civil Hospital Ahmedabad (Honorary)",
             "Expert in tropical dermatology, fungal infections, allergic contact dermatitis, and tele-derm screening.",
             "👩🏻‍⚕️", "VERIFIED", "mmc_reg_58201.pdf", 4.7, 64,
             json.dumps(["11:00 AM - 02:00 PM", "05:00 PM - 07:00 PM"])),

            ("doc_meera", "usr_doc_meera", "MBBS, MS (Obstetrics & Gynecology)", "GMC-GJ-61928", "Gynecologist", 10,
             json.dumps(["Gujarati", "Hindi", "English"]), 0.0, "Mehsana District Women's Hospital",
             "Passionate about rural women's health screening, anemia management, and antenatal care.",
             "👩🏽‍⚕️", "VERIFIED", "gmc_reg_61928.pdf", 4.9, 142,
             json.dumps(["09:00 AM - 01:00 PM"]))
        ]
        cursor.executemany("""
            INSERT INTO doctors (id, user_id, qualification, license_number, specialization, experience_years,
                                languages_spoken, consultation_fee, hospital_affiliation, bio, avatar_emoji,
                                verification_status, verification_document, rating_avg, reviews_count, availability_schedule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, doctors_data)

        # 4. Organization
        cursor.execute("""
            INSERT INTO organizations (id, user_id, org_name, org_type, registration_number, contact_person,
                                      contact_phone, address, district, state, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "org_shakti", "usr_hospital", "Shakti Community Hospital", "HOSPITAL", "GJ-MEH-HOSP-2018",
            "Dr. K. N. Dave (Medical Superintendent)", "+91 2762 234567", "Station Road, Mehsana", "Mehsana", "Gujarat", 1
        ))

        # 5. Appointments & Completed Consultations
        # A completed appointment for Ramesh with Dr. Anjali (so patient can review or view past record)
        cursor.execute("""
            INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, time_slot, consultation_mode, status, chief_complaint, symptoms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "apt_comp_01", "pat_ramesh", "doc_anjali", "2026-08-25", "10:00 AM - 10:30 AM", "VIDEO", "COMPLETED",
            "Seasonal cough and intermittent fever", "Dry cough for 4 days, mild body ache, temperature 99.8F"
        ))

        cursor.execute("""
            INSERT INTO consultations (id, appointment_id, patient_id, doctor_id, mode, status, start_time, end_time,
                                      clinical_notes, diagnosis, follow_up_advice, follow_up_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "cns_comp_01", "apt_comp_01", "pat_ramesh", "doc_anjali", "VIDEO", "COMPLETED",
            "2026-08-25 10:02:15", "2026-08-25 10:21:40",
            "Patient reports dry cough for 4 days following exposure to dust and seasonal change. No chest pain or dyspnea. Pharynx congested. Chest clear on bilateral auscultation.",
            "Acute Upper Respiratory Tract Viral Infection",
            "Hydration, warm saline gargles, rest. Re-visit if fever persists over 3 days.",
            "2026-09-01"
        ))

        cursor.execute("""
            INSERT INTO prescriptions (id, consultation_id, patient_id, doctor_id, medications_json, general_advice)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "rx_comp_01", "cns_comp_01", "pat_ramesh", "doc_anjali",
            json.dumps([
                {"name": "Paracetamol 500mg", "dosage": "1 tablet", "timing": "SOS / After meals", "duration": "3 days", "instructions": "Take if temperature exceeds 99.5F"},
                {"name": "Cetirizine 10mg", "dosage": "1 tablet", "timing": "At bedtime", "duration": "5 days", "instructions": "For cough & nasal congestion"},
                {"name": "Warm Saline Gargle", "dosage": "Twice daily", "timing": "Morning and Night", "duration": "5 days", "instructions": "Soothes throat irritation"}
            ]),
            "Drink plenty of lukewarm water. Avoid cold food and dusty areas."
        ))

        # An upcoming appointment for demonstration
        cursor.execute("""
            INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, time_slot, consultation_mode, status, chief_complaint, symptoms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "apt_up_01", "pat_ramesh", "doc_anjali", "2026-09-22", "04:00 PM - 04:30 PM", "VIDEO", "CONFIRMED",
            "Follow-up for seasonal cough and allergy check", "Mild lingering cough after morning walks."
        ))

        # 6. Health Records
        records_data = [
            ("rec_01", "pat_ramesh", "Teleconsultation Prescription - Dr. Anjali Patel", "PRESCRIPTION",
             "/static/uploads/rx_sample.pdf", "2026-08-25", "Dr. Anjali Patel", "Upper Respiratory Infection medications", 1),
            ("rec_02", "pat_ramesh", "Complete Blood Count (CBC) Report", "LAB_REPORT",
             "/static/uploads/cbc_sample.pdf", "2026-08-10", "Shakti Hospital Diagnostic Lab", "Hb: 13.8 g/dL, TLC: 7,400 /mcL, Platelets normal", 1),
            ("rec_03", "pat_ramesh", "Community Health Camp Screening Summary", "CLINICAL_NOTE",
             "/static/uploads/camp_vitals.pdf", "2026-07-15", "Rampura Village Health Camp", "BP: 124/82 mmHg, Random Blood Sugar: 104 mg/dL", 1)
        ]
        cursor.executemany("""
            INSERT INTO health_records (id, patient_id, title, record_type, file_path, date_recorded, uploaded_by, notes, is_abha_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records_data)

        # 7. Doctor Reviews
        reviews_data = [
            ("rev_01", "doc_anjali", "pat_ramesh", "cns_comp_01", "R.P.", 5, 5, 5, 5,
             "Dr. Anjali explained everything very patiently in Gujarati. I felt comfortable and the medicines worked within two days.", 1, 0),
            ("rev_02", "doc_anjali", "pat_ramesh", None, "M.S.", 5, 5, 4, 5,
             "Very helpful doctor for rural patients. Prompt tele-consultation.", 1, 0),
            ("rev_03", "doc_anjali", "pat_ramesh", None, "K.B.", 4, 4, 4, 4,
             "Listened carefully to my elder mother's complaints and advised simple home care.", 1, 0)
        ]
        cursor.executemany("""
            INSERT INTO doctor_reviews (id, doctor_id, patient_id, consultation_id, patient_initials, rating,
                                       communication_score, punctuality_score, explanation_score, review_text, is_verified, is_moderated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, reviews_data)

        # 8. Health Camps
        camps_data = [
            ("camp_01", "Free General & Eye Health Screening Camp", "General",
             "Comprehensive health screening for all age groups including free vision test, blood pressure, blood glucose, and doctor consultations.",
             "Shakti Community Hospital", "HOSPITAL", "org_shakti", "Rampura Community Hall, Near Panchayat Office",
             "Rampura", "Mehsana", "Gujarat", "2026-09-28", "09:00 AM - 02:00 PM", 150, 94,
             json.dumps(["General Checkup", "Eye Screening", "Blood Pressure", "Diabetes Screening", "Free Medicines"]),
             json.dumps(["Vision Chart", "Tonometer", "Glucometers", "BP Apparatus", "Emergency First Aid Kit"]),
             3, 1, "REGISTRATION_OPEN", None),
            
            ("camp_02", "Maternal & Child Wellness Health Camp", "Women",
             "Specialized screening for pregnant women, adolescent girls, and pediatric immunizations with pediatricians and gynecologists.",
             "North Gujarat Health Mission & Shakti Hospital", "NGO", "org_shakti", "Kadi Primary Health Center Ground",
             "Kadi", "Mehsana", "Gujarat", "2026-10-05", "10:00 AM - 03:00 PM", 120, 68,
             json.dumps(["Antenatal Screening", "Pediatric Checkup", "Anemia Screening", "Nutrition Counseling"]),
             json.dumps(["Hemoglobinometer", "Ultrasound Portable", "Pediatric Scales", "Folic Acid / Iron Tablets"]),
             2, 1, "REGISTRATION_OPEN", None),

            ("camp_03", "Rural Diabetes & Hypertension Screening Camp (Completed)", "Diabetes",
             "Conducted screening camp covering elderly villagers for cardiovascular risk factors and diabetic retinopathy.",
             "Shakti Community Hospital", "HOSPITAL", "org_shakti", "Visnagar Gram Panchayat Hall",
             "Visnagar", "Mehsana", "Gujarat", "2026-08-15", "09:00 AM - 01:00 PM", 100, 100,
             json.dumps(["Random Blood Sugar", "HbA1c Spot Test", "ECG Screening", "Doctor Consultation"]),
             json.dumps(["HbA1c Analyzers", "Portable 12-lead ECG", "Glucometers"]),
             2, 1, "COMPLETED",
             json.dumps({
                 "patients_attended": 118,
                 "screenings_completed": 118,
                 "hypertension_detected": 28,
                 "diabetes_detected": 19,
                 "referrals_to_hospital": 14,
                 "medicines_distributed": 92
             }))
        ]
        cursor.executemany("""
            INSERT INTO health_camps (id, title, camp_type, description, organizer_name, organizer_type, organizer_id,
                                     location, village, district, state, date, time, capacity, registered_count,
                                     services_json, equipment_json, doctors_needed, is_free, status, impact_report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, camps_data)

        # 9. Camp Registrations
        cursor.execute("""
            INSERT INTO camp_registrations (id, camp_id, patient_id, patient_name, phone, age, gender, village, attended)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "reg_01", "camp_01", "pat_ramesh", "Ramesh Patel", "+91 98765 43210", 38, "Male", "Rampura", 0
        ))

        # 10. Camp Requests from Village Community Reps
        camp_requests_data = [
            ("req_01", "usr_village", "Bhavesh Patel (Sarpanch)", "Village Representative", "Rampura", "Mehsana", "Gujarat",
             "Bhavesh Patel", "+91 98799 55443", 160, "2026-10-12", "09:00 AM", "General & Eye Camp",
             json.dumps(["General Physician", "Eye Specialist", "Blood Pressure", "Diabetes Check"]),
             "Normal", "Many elderly farm workers have eye strain and joint pains. Nearest sub-center is 9 km away.",
             "PENDING", None, None),
            
            ("req_02", "usr_village", "Gram Seva NGO", "NGO", "Unjha Rural", "Mehsana", "Gujarat",
             "Hasmukh Shah", "+91 94280 11223", 200, "2026-10-20", "10:00 AM", "Women & Child Care Camp",
             json.dumps(["Pediatrician", "Gynecologist", "Anemia Test"]),
             "Urgent", "High prevalence of nutritional anemia among adolescent girls and farm working mothers.",
             "REVIEWED", None, None)
        ]
        cursor.executemany("""
            INSERT INTO camp_requests (id, requester_id, requester_name, requester_type, village, district, state,
                                      contact_person, contact_phone, expected_patients, preferred_date, preferred_time,
                                      camp_type, required_services_json, urgency, description, status, accepted_by_id, accepted_by_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, camp_requests_data)

        # 11. ABDM Consents
        cursor.execute("""
            INSERT INTO abdm_consents (id, patient_id, doctor_id, purpose, records_requested, consent_status, granted_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "cst_01", "pat_ramesh", "doc_anjali", "Teleconsultation & Continuity of Care",
            "Prescriptions, Diagnostic Reports, Discharge Summary", "GRANTED", "2026-08-25 10:00:00", "2026-09-25 10:00:00"
        ))

        # 12. In-App Notifications
        notifs_data = [
            ("notif_01", "usr_patient", "Upcoming Consultation Reminder", "You have a confirmed teleconsultation with Dr. Anjali Patel today at 04:00 PM.", "APPOINTMENT", 0, "/#consultation"),
            ("notif_02", "usr_patient", "Camp Registration Confirmed", "Your seat is reserved for Free General & Eye Health Screening Camp on 28 Sep.", "CAMP", 0, "/#health-camps"),
            ("notif_03", "usr_doc_anjali", "New Patient Scheduled", "Patient Ramesh Patel booked an appointment for 04:00 PM today.", "APPOINTMENT", 0, "/#doctor-queue"),
            ("notif_04", "usr_hospital", "New Village Camp Request", "Sarpanch Bhavesh Patel requested a General & Eye Camp for Rampura Village (160 expected patients).", "CAMP", 0, "/#camp-requests")
        ]
        cursor.executemany("""
            INSERT INTO notifications (id, user_id, title, message, type, is_read, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, notifs_data)

        # 13. Audit Logs
        audit_data = [
            ("aud_01", "usr_patient", "USER_LOGIN", "AUTH", "Successful login via Demo Authentication", "127.0.0.1", "SUCCESS"),
            ("aud_02", "usr_doc_anjali", "ABDM_RECORD_ACCESS", "HEALTH_RECORD", "Doctor Dr. Anjali Patel accessed CBC report rec_02 under consent cst_01", "127.0.0.1", "SUCCESS"),
            ("aud_03", "usr_admin", "DOCTOR_VERIFICATION", "DOCTORS", "Admin verified Dr. Anjali Patel (GMC-GJ-48291)", "127.0.0.1", "SUCCESS")
        ]
        cursor.executemany("""
            INSERT INTO audit_logs (id, user_id, action, resource, details, ip_address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, audit_data)

        conn.commit()
        print("Demo database seeded successfully with realistic healthcare scenarios!")

if __name__ == "__main__":
    seed_database()
