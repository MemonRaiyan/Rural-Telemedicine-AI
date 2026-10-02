import pytest
import io
from fastapi.testclient import TestClient
from PIL import Image
from backend.app.main import app
from backend.app.database.database import init_db
from backend.app.database.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    seed_database()

# 1. Health Endpoint Test
def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "GramCare" in data["service"]

# 2. Authentication & 1-Click Demo Login
def test_demo_logins():
    for role in ["patient", "doctor", "hospital", "admin"]:
        res = client.post(f"/api/auth/demo-login/{role}")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["user"]["role"].lower() == role

def test_manual_auth_failure():
    res = client.post("/api/auth/login", json={"email": "patient@gramcare.in", "password": "wrongpassword"})
    assert res.status_code == 401

# 3. AI NLP Symptom Triage Tests
def test_nlp_triage_respiratory():
    res = client.post("/api/ai/triage", json={
        "symptoms": "I have had a mild fever and dry cough for 3 days",
        "age": 35,
        "severity": "Moderate"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["urgency"] in ["MODERATE", "LOW"]
    assert data["suggested_department"] == "General Physician"
    assert "preliminary" in data["disclaimer"].lower() or "triage" in data["disclaimer"].lower()
    assert len(data["symptoms"]) > 0

def test_nlp_triage_vernacular_gujarati():
    res = client.post("/api/ai/triage", json={
        "symptoms": "મને 2 દિવસથી તાવ અને ખાંસી છે",
        "age": 40
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["language_detected"] == "gu"
    assert "fever" in data["symptoms"] or "cough" in data["symptoms"]

# 4. Emergency Red-Flag Engine Test
def test_emergency_red_flag_detection():
    res = client.post("/api/ai/triage", json={
        "symptoms": "Severe acute chest pain radiating to left arm and difficulty breathing",
        "age": 55,
        "severity": "Severe"
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["urgency"] == "EMERGENCY"
    assert data["emergency_alert"] is not None
    assert "108" in data["emergency_helpline"]

# 5. Medical Image Screening Test
def test_medical_image_screening():
    # Create synthetic test image
    img = Image.new("RGB", (256, 256), color=(120, 120, 120))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    res = client.post(
        "/api/ai/image-screening",
        files={"image": ("test_xray.png", buf, "image/png")},
        data={"image_type": "CHEST_XRAY"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "detected_finding" in data
    assert "prototype" in data["disclaimer"].lower() or "screening" in data["disclaimer"].lower()

# 6. Doctor Search & Directory Tests
def test_doctor_search_and_filters():
    res = client.get("/api/doctors")
    assert res.status_code == 200
    docs = res.json()["data"]
    assert len(docs) >= 3

    # Filter by specialty
    res_ped = client.get("/api/doctors?specialty=Pediatrician")
    assert res_ped.status_code == 200
    peds = res_ped.json()["data"]
    assert any("Pediatrician" in p["specialization"] for p in peds)

# 7. Appointment Booking & Conflict Prevention Test
def test_appointment_booking_and_conflict():
    # Login as patient
    login_res = client.post("/api/auth/demo-login/patient").json()
    token = login_res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    import time
    unique_date = f"2026-11-{int(time.time()) % 28 + 1:02d}"
    # Book slot
    booking_payload = {
        "doctor_id": "doc_anjali",
        "appointment_date": unique_date,
        "time_slot": "11:00 AM - 11:30 AM",
        "chief_complaint": "Seasonal wellness check"
    }
    # Clean any previous record for this slot to guarantee 200
    from backend.app.database.database import execute_query
    execute_query("DELETE FROM appointments WHERE doctor_id = 'doc_anjali' AND appointment_date = ? AND time_slot = '11:00 AM - 11:30 AM'", (unique_date,))
    res1 = client.post("/api/appointments", json=booking_payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["success"] is True

    # Try duplicate booking for same doctor & slot (Conflict test)
    res2 = client.post("/api/appointments", json=booking_payload, headers=headers)
    assert res2.status_code == 409
    assert "already booked" in res2.json()["detail"]

# 8. Health Camp Network & Registration Test
def test_camp_registration_and_requests():
    # Login as patient
    login_res = client.post("/api/auth/demo-login/patient").json()
    token = login_res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register for camp
    res_reg = client.post("/api/camps/camp_02/register", headers=headers)
    assert res_reg.status_code in [200, 400] # 200 on first try, 400 if already registered

    # Village Camp Request
    res_req = client.post("/api/camp-requests", json={
        "village": "Bhandu",
        "district": "Mehsana",
        "contact_person": "Panchayat Head",
        "contact_phone": "+91 98222 33445",
        "expected_patients": 180,
        "preferred_date": "2026-11-15",
        "camp_type": "Eye Care Camp",
        "required_services": ["Ophthalmologist", "Vision Test"]
    })
    assert res_req.status_code == 200
    req_id = res_req.json()["request_id"]

    # Hospital accepts request
    hosp_login = client.post("/api/auth/demo-login/hospital").json()
    h_headers = {"Authorization": f"Bearer {hosp_login['access_token']}"}
    res_accept = client.post(f"/api/camp-requests/{req_id}/accept", headers=h_headers)
    assert res_accept.status_code == 200
    assert "camp_id" in res_accept.json()

# 9. ABDM Consent Flow Test
def test_abdm_consent_flow():
    # Doctor requests consent
    doc_login = client.post("/api/auth/demo-login/doctor").json()
    d_headers = {"Authorization": f"Bearer {doc_login['access_token']}"}

    res_cst = client.post("/api/abdm/request-consent", json={
        "patient_id": "pat_ramesh",
        "purpose": "Teleconsultation Review",
        "records_requested": "Prescription, DiagnosticReport"
    }, headers=d_headers)
    assert res_cst.status_code == 200
    cid = res_cst.json()["consent_id"]

    # Patient approves consent
    pat_login = client.post("/api/auth/demo-login/patient").json()
    p_headers = {"Authorization": f"Bearer {pat_login['access_token']}"}
    res_grant = client.patch(f"/api/abdm/consents/{cid}", json={"status": "GRANTED"}, headers=p_headers)
    assert res_grant.status_code == 200

    # Doctor accesses records under consent
    res_rec = client.get("/api/abdm/patient-records/pat_ramesh", headers=d_headers)
    assert res_rec.status_code == 200
    data = res_rec.json()["data"]
    assert data["authorized"] is True
    assert len(data["records"]) > 0

# 10. Admin Analytics & Audit Log Test
def test_admin_stats_and_audit():
    adm_login = client.post("/api/auth/demo-login/admin").json()
    headers = {"Authorization": f"Bearer {adm_login['access_token']}"}

    res = client.get("/api/admin/stats", headers=headers)
    assert res.status_code == 200
    stats = res.json()["data"]
    assert stats["total_patients"] >= 1
    assert stats["total_doctors"] >= 1

    res_audit = client.get("/api/admin/audit-logs", headers=headers)
    assert res_audit.status_code == 200
    assert len(res_audit.json()["data"]) > 0

# 11. Security & Object-Level Authorization Tests
def test_cross_user_consultation_isolation():
    import time
    ts = int(time.time() * 1000)
    # 1. Register two distinct patients
    r1 = client.post("/api/auth/register", json={
        "email": f"pat1_sec_{ts}@test.in",
        "password": "Password123!",
        "role": "PATIENT",
        "full_name": "Patient Alpha"
    })
    assert r1.status_code == 200
    token1 = r1.json()["access_token"]
    
    r2 = client.post("/api/auth/register", json={
        "email": f"pat2_sec_{ts}@test.in",
        "password": "Password123!",
        "role": "PATIENT",
        "full_name": "Patient Beta"
    })
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]
    
    # 2. Patient 1 books an appointment with Dr. Anjali
    appt_date = f"2026-12-{(ts % 28) + 1:02d}"
    from backend.app.database.database import execute_query
    execute_query("DELETE FROM appointments WHERE doctor_id = 'doc_anjali' AND appointment_date = ? AND time_slot = '09:00 AM - 09:30 AM'", (appt_date,))
    book_res = client.post("/api/appointments", json={
        "doctor_id": "doc_anjali",
        "appointment_date": appt_date,
        "time_slot": "09:00 AM - 09:30 AM",
        "chief_complaint": "Alpha private health complaint"
    }, headers={"Authorization": f"Bearer {token1}"}).json()
    appt_id = book_res["appointment_id"]
    
    # 3. Patient 1 starts consultation
    start_res = client.post(f"/api/consultations/{appt_id}/start", headers={"Authorization": f"Bearer {token1}"}).json()
    cns_id = start_res["data"]["id"]
    
    # 4. Patient 2 attempts to read Patient 1's consultation (must be 403 Forbidden)
    unauth_res = client.get(f"/api/consultations/{cns_id}", headers={"Authorization": f"Bearer {token2}"})
    assert unauth_res.status_code == 403
    assert "Access denied" in unauth_res.json()["detail"]
    
    # 5. Patient 1 can legitimately read their own consultation
    auth_res = client.get(f"/api/consultations/{cns_id}", headers={"Authorization": f"Bearer {token1}"})
    assert auth_res.status_code == 200
    assert auth_res.json()["data"]["id"] == cns_id

# 12. Doctor Profile Lifecycle & Persistence Test
def test_doctor_profile_lifecycle_and_update():
    import time
    ts = int(time.time() * 1000)
    # Register a new doctor
    doc_reg = client.post("/api/auth/register", json={
        "email": f"dr.vikram_{ts}@test.in",
        "password": "DocPassword123!",
        "role": "DOCTOR",
        "full_name": "Dr. Vikram Seth",
        "specialization": "Cardiologist",
        "qualification": "MBBS, MD",
        "consultation_fee": 150.0
    })
    assert doc_reg.status_code == 200
    doc_token = doc_reg.json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    
    # Verify doctor profile update
    update_res = client.patch("/api/doctors/profile", json={
        "qualification": "MBBS, MD, DM Cardiology",
        "specialization": "Interventional Cardiology",
        "experience_years": 14,
        "bio": "Specialist in rural preventative cardiology and hypertension.",
        "consultation_fee": 200.0,
        "languages_spoken": ["English", "Hindi", "Gujarati"]
    }, headers=doc_headers)
    assert update_res.status_code == 200
    updated = update_res.json()["data"]
    assert updated["qualification"] == "MBBS, MD, DM Cardiology"
    assert updated["experience_years"] == 14
    assert updated["consultation_fee"] == 200.0
    
    # Patient cannot update doctor profile (403 Forbidden)
    pat_login = client.post("/api/auth/demo-login/patient").json()
    pat_headers = {"Authorization": f"Bearer {pat_login['access_token']}"}
    forbidden_res = client.patch("/api/doctors/profile", json={"qualification": "Fake Degree"}, headers=pat_headers)
    assert forbidden_res.status_code == 403

# 13. Patient Profile Update Test
def test_patient_profile_update():
    pat_login = client.post("/api/auth/demo-login/patient").json()
    pat_headers = {"Authorization": f"Bearer {pat_login['access_token']}"}
    
    update_res = client.patch("/api/patients/profile", json={
        "village": "Viramgam",
        "blood_group": "O+",
        "allergies": "Penicillin allergy",
        "chronic_conditions": "Hypertension"
    }, headers=pat_headers)
    assert update_res.status_code == 200
    p = update_res.json()["data"]
    assert p["village"] == "Viramgam"
    assert p["blood_group"] == "O+"
    assert p["allergies"] == "Penicillin allergy"

# 14. Image Screening Validation Test
def test_image_screening_validation():
    # Attempt to upload corrupted/invalid bytes
    corrupted_buf = io.BytesIO(b"not an image file data")
    res = client.post(
        "/api/ai/image-screening",
        files={"image": ("bad.png", corrupted_buf, "image/png")},
        data={"image_type": "CHEST_XRAY"}
    )
    assert res.status_code == 400
    assert "Unable to decode" in res.json()["detail"] or "Invalid" in res.json()["detail"]
