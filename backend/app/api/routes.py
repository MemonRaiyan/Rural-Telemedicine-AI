import os
import secrets
import json
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from pydantic import BaseModel, EmailStr

from backend.app.database.database import query_one, query_all, execute_query, get_db
from backend.app.auth.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_optional_user, require_role, log_audit
)
from backend.app.ai.triage import perform_nlp_triage
from backend.app.ai.emergency import check_emergency_red_flags
from backend.app.ai.image_screening import screen_medical_image
from backend.app.ai.doctor_assistant import generate_clinical_summary
from backend.app.services.abdm import AbhaService, ConsentService, HealthRecordExchangeService

api_router = APIRouter()

# ----------------- SCHEMAS -----------------
class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str # PATIENT, DOCTOR, HOSPITAL, COMMUNITY_REP
    full_name: str
    phone: Optional[str] = None
    preferred_language: Optional[str] = "en"
    # Patient fields
    age: Optional[int] = 30
    gender: Optional[str] = "Other"
    village: Optional[str] = "Rampura"
    district: Optional[str] = "Mehsana"
    # Doctor fields
    specialization: Optional[str] = "General Physician"
    qualification: Optional[str] = "MBBS"
    license_number: Optional[str] = None
    consultation_fee: Optional[float] = 0.0

class LoginRequest(BaseModel):
    email: str
    password: str

class DoctorProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    languages_spoken: Optional[List[str]] = None
    consultation_fee: Optional[float] = None
    hospital_affiliation: Optional[str] = None
    bio: Optional[str] = None
    availability_schedule: Optional[List[str]] = None
    avatar_emoji: Optional[str] = None

class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    preferred_language: Optional[str] = None

class AppointmentStatusUpdate(BaseModel):
    status: str # CONFIRMED, CANCELLED, REJECTED, COMPLETED

class TriageInput(BaseModel):
    symptoms: str
    age: Optional[int] = 30
    gender: Optional[str] = "Other"
    severity: Optional[str] = "Moderate"
    duration: Optional[str] = None
    existing_conditions: Optional[str] = None

class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_date: str # YYYY-MM-DD
    time_slot: str
    consultation_mode: Optional[str] = "VIDEO"
    chief_complaint: str
    symptoms: Optional[str] = None

class ConsultationCompleteRequest(BaseModel):
    clinical_notes: str
    diagnosis: str
    follow_up_advice: Optional[str] = None
    follow_up_date: Optional[str] = None
    medications: Optional[List[dict]] = []

class ReviewCreate(BaseModel):
    doctor_id: str
    consultation_id: str
    rating: int
    communication_score: Optional[int] = 5
    punctuality_score: Optional[int] = 5
    explanation_score: Optional[int] = 5
    review_text: Optional[str] = ""

class CampCreate(BaseModel):
    title: str
    camp_type: str
    description: str
    location: str
    village: str
    district: str
    date: str
    time: str
    capacity: int = 100
    services: List[str] = []
    is_free: bool = True

class CampRequestCreate(BaseModel):
    village: str
    district: str
    contact_person: str
    contact_phone: str
    expected_patients: int = 100
    preferred_date: str
    camp_type: str
    required_services: List[str] = []
    urgency: Optional[str] = "Normal"
    description: Optional[str] = ""

class ConsentRequestInput(BaseModel):
    patient_id: str
    purpose: str
    records_requested: str

# ----------------- AUTH ENDPOINTS -----------------
@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    existing = query_one("SELECT id FROM users WHERE email = ?", (req.email,))
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    user_id = f"usr_{secrets.token_hex(6)}"
    pwd_hash = hash_password(req.password)
    
    execute_query("""
        INSERT INTO users (id, email, password_hash, role, full_name, phone, preferred_language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, req.email, pwd_hash, req.role.upper(), req.full_name, req.phone, req.preferred_language))

    if req.role.upper() == "PATIENT":
        pat_id = f"pat_{secrets.token_hex(6)}"
        execute_query("""
            INSERT INTO patients (id, user_id, age, gender, village, district)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pat_id, user_id, req.age, req.gender, req.village, req.district))
    elif req.role.upper() == "DOCTOR":
        doc_id = f"doc_{secrets.token_hex(6)}"
        license_num = req.license_number or f"MED-REG-{secrets.token_hex(3).upper()}"
        execute_query("""
            INSERT INTO doctors (id, user_id, qualification, license_number, specialization, consultation_fee, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
        """, (doc_id, user_id, req.qualification, license_num, req.specialization, req.consultation_fee))
    elif req.role.upper() == "HOSPITAL":
        org_id = f"org_{secrets.token_hex(6)}"
        execute_query("""
            INSERT INTO organizations (id, user_id, org_name, org_type, district, is_verified)
            VALUES (?, ?, ?, 'HOSPITAL', ?, 1)
        """, (org_id, user_id, req.full_name, req.district))

    token = create_access_token({"sub": user_id, "role": req.role.upper(), "name": req.full_name})
    log_audit(user_id, "USER_REGISTER", "AUTH", f"New {req.role} registered: {req.email}")
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": req.email, "role": req.role.upper(), "full_name": req.full_name}
    }

# ----------------- PROFILE MANAGEMENT -----------------
@api_router.patch("/doctors/profile")
async def update_doctor_profile(req: DoctorProfileUpdate, user: dict = Depends(require_role(["DOCTOR"]))):
    doc = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor profile not found.")
    
    if req.full_name or req.phone:
        if req.full_name and req.phone:
            execute_query("UPDATE users SET full_name = ?, phone = ? WHERE id = ?", (req.full_name, req.phone, user["id"]))
        elif req.full_name:
            execute_query("UPDATE users SET full_name = ? WHERE id = ?", (req.full_name, user["id"]))
        elif req.phone:
            execute_query("UPDATE users SET phone = ? WHERE id = ?", (req.phone, user["id"]))
            
    updates = []
    params = []
    if req.qualification is not None:
        updates.append("qualification = ?")
        params.append(req.qualification)
    if req.specialization is not None:
        updates.append("specialization = ?")
        params.append(req.specialization)
    if req.experience_years is not None:
        updates.append("experience_years = ?")
        params.append(req.experience_years)
    if req.languages_spoken is not None:
        updates.append("languages_spoken = ?")
        params.append(json.dumps(req.languages_spoken))
    if req.consultation_fee is not None:
        updates.append("consultation_fee = ?")
        params.append(req.consultation_fee)
    if req.hospital_affiliation is not None:
        updates.append("hospital_affiliation = ?")
        params.append(req.hospital_affiliation)
    if req.bio is not None:
        updates.append("bio = ?")
        params.append(req.bio)
    if req.availability_schedule is not None:
        updates.append("availability_schedule = ?")
        params.append(json.dumps(req.availability_schedule))
    if req.avatar_emoji is not None:
        updates.append("avatar_emoji = ?")
        params.append(req.avatar_emoji)
        
    if updates:
        params.append(doc["id"])
        execute_query(f"UPDATE doctors SET {', '.join(updates)} WHERE id = ?", params)
        
    log_audit(user["id"], "DOCTOR_PROFILE_UPDATE", "DOCTOR", f"Doctor profile {doc['id']} updated.")
    
    updated_doc = query_one("""
        SELECT d.*, u.full_name, u.email, u.phone
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    """, (doc["id"],))
    return {"success": True, "message": "Doctor profile updated successfully.", "data": updated_doc}

@api_router.patch("/patients/profile")
async def update_patient_profile(req: PatientProfileUpdate, user: dict = Depends(require_role(["PATIENT"]))):
    pat = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
    if not pat:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
        
    if req.full_name or req.phone or req.preferred_language:
        u_updates = []
        u_params = []
        if req.full_name:
            u_updates.append("full_name = ?")
            u_params.append(req.full_name)
        if req.phone:
            u_updates.append("phone = ?")
            u_params.append(req.phone)
        if req.preferred_language:
            u_updates.append("preferred_language = ?")
            u_params.append(req.preferred_language)
        u_params.append(user["id"])
        execute_query(f"UPDATE users SET {', '.join(u_updates)} WHERE id = ?", u_params)
        
    updates = []
    params = []
    if req.age is not None:
        updates.append("age = ?")
        params.append(req.age)
    if req.gender is not None:
        updates.append("gender = ?")
        params.append(req.gender)
    if req.village is not None:
        updates.append("village = ?")
        params.append(req.village)
    if req.district is not None:
        updates.append("district = ?")
        params.append(req.district)
    if req.state is not None:
        updates.append("state = ?")
        params.append(req.state)
    if req.pin_code is not None:
        updates.append("pin_code = ?")
        params.append(req.pin_code)
    if req.emergency_contact is not None:
        updates.append("emergency_contact = ?")
        params.append(req.emergency_contact)
    if req.blood_group is not None:
        updates.append("blood_group = ?")
        params.append(req.blood_group)
    if req.allergies is not None:
        updates.append("allergies = ?")
        params.append(req.allergies)
    if req.chronic_conditions is not None:
        updates.append("chronic_conditions = ?")
        params.append(req.chronic_conditions)
        
    if updates:
        params.append(pat["id"])
        execute_query(f"UPDATE patients SET {', '.join(updates)} WHERE id = ?", params)
        
    log_audit(user["id"], "PATIENT_PROFILE_UPDATE", "PATIENT", f"Patient profile {pat['id']} updated.")
    
    updated_pat = query_one("""
        SELECT p.*, u.full_name, u.email, u.phone, u.preferred_language
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    """, (pat["id"],))
    return {"success": True, "message": "Patient profile updated successfully.", "data": updated_pat}

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    user = query_one("SELECT id, email, password_hash, role, full_name, preferred_language, is_active FROM users WHERE email = ?", (req.email,))
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is suspended.")

    token = create_access_token({"sub": user["id"], "role": user["role"], "name": user["full_name"]})
    log_audit(user["id"], "USER_LOGIN", "AUTH", f"User logged in: {req.email}")
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
            "preferred_language": user["preferred_language"]
        }
    }

@api_router.post("/auth/demo-login/{role}")
async def demo_login(role: str):
    role_map = {
        "patient": "patient@gramcare.in",
        "doctor": "anjali@gramcare.in",
        "hospital": "hospital@gramcare.in",
        "community_rep": "village@gramcare.in",
        "admin": "admin@gramcare.in"
    }
    email = role_map.get(role.lower())
    if not email:
        raise HTTPException(status_code=400, detail=f"Invalid demo role. Available: {list(role_map.keys())}")
    
    user = query_one("SELECT id, email, role, full_name, preferred_language FROM users WHERE email = ?", (email,))
    if not user:
        raise HTTPException(status_code=404, detail="Demo user account not found. Please re-seed database.")
    
    token = create_access_token({"sub": user["id"], "role": user["role"], "name": user["full_name"]})
    log_audit(user["id"], "DEMO_LOGIN", "AUTH", f"1-Click Demo Login as {user['role']}")
    
    # Fetch sub-profile ID
    profile_id = None
    if user["role"] == "PATIENT":
        p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
        profile_id = p["id"] if p else None
    elif user["role"] == "DOCTOR":
        d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
        profile_id = d["id"] if d else None
    elif user["role"] == "HOSPITAL":
        o = query_one("SELECT id FROM organizations WHERE user_id = ?", (user["id"],))
        profile_id = o["id"] if o else None

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "profile_id": profile_id,
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
            "preferred_language": user["preferred_language"]
        }
    }

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    extra = {}
    if user["role"] == "PATIENT":
        p = query_one("SELECT * FROM patients WHERE user_id = ?", (user["id"],))
        extra["patient_profile"] = p
    elif user["role"] == "DOCTOR":
        d = query_one("SELECT * FROM doctors WHERE user_id = ?", (user["id"],))
        extra["doctor_profile"] = d
    elif user["role"] == "HOSPITAL":
        o = query_one("SELECT * FROM organizations WHERE user_id = ?", (user["id"],))
        extra["org_profile"] = o
        
    return {"success": True, "user": user, **extra}

# ----------------- AI CLINICAL WORKFLOWS -----------------
@api_router.post("/ai/triage")
async def ai_triage(req: TriageInput, user: Optional[dict] = Depends(get_optional_user)):
    triage_result = perform_nlp_triage(
        symptoms_text=req.symptoms,
        age=req.age or 30,
        gender=req.gender or "Other",
        user_severity=req.severity,
        existing_conditions=req.existing_conditions
    )
    
    patient_id = None
    if user and user["role"] == "PATIENT":
        p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
        patient_id = p["id"] if p else None
        
    # Save assessment record
    record_id = f"triage_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO ai_triage_assessments (id, patient_id, symptoms_input, language, duration, severity, urgency, suggested_department, red_flags_json, summary, recommended_action, confidence, disclaimer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id, patient_id, req.symptoms, triage_result["language_detected"],
        triage_result["duration"], triage_result["severity"], triage_result["urgency"],
        triage_result["suggested_department"], json.dumps(triage_result["red_flags"]),
        triage_result["summary"], triage_result["recommended_next_step"],
        triage_result["confidence"], triage_result["disclaimer"]
    ))
    
    triage_result["assessment_id"] = record_id
    return {"success": True, "data": triage_result}

@api_router.post("/ai/image-screening")
async def ai_image_screening(
    image: UploadFile = File(...),
    image_type: str = Form("CHEST_XRAY"),
    user: Optional[dict] = Depends(get_optional_user)
):
    content = await image.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file exceeds 10MB limit.")
        
    screening_result = screen_medical_image(content, image_type)
    if screening_result.get("status") == "FAILED":
        raise HTTPException(status_code=400, detail=screening_result.get("error"))

    # Save image to upload folder
    filename = f"{secrets.token_hex(6)}_{image.filename}"
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    patient_id = None
    if user and user["role"] == "PATIENT":
        p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
        patient_id = p["id"] if p else None

    rec_id = f"img_scr_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO medical_image_screenings (id, patient_id, image_type, image_filename, detected_finding, confidence, red_flag, analysis_summary, disclaimer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rec_id, patient_id, image_type, filename,
        screening_result["detected_finding"], screening_result["confidence"],
        screening_result["red_flag"], screening_result["recommended_action"],
        screening_result["disclaimer"]
    ))
    
    screening_result["id"] = rec_id
    screening_result["image_url"] = f"/static/uploads/{filename}"
    return {"success": True, "data": screening_result}

@api_router.post("/ai/clinical-summary")
async def ai_clinical_summary(req: dict, user: dict = Depends(require_role(["DOCTOR", "ADMIN"]))):
    summary = generate_clinical_summary(
        patient_name=req.get("patient_name", "Patient"),
        age=req.get("age", 35),
        gender=req.get("gender", "Other"),
        chief_complaint=req.get("chief_complaint", "General Malaise"),
        symptoms=req.get("symptoms", "Fever, Cough"),
        duration=req.get("duration", "3 days"),
        doctor_raw_notes=req.get("doctor_raw_notes", ""),
        provisional_diagnosis=req.get("provisional_diagnosis", "")
    )
    return {"success": True, "data": summary}

# ----------------- DOCTOR SEARCH & DIRECTORY -----------------
@api_router.get("/doctors")
async def get_doctors(specialty: Optional[str] = None, language: Optional[str] = None, min_rating: Optional[float] = None):
    sql = """
        SELECT d.*, u.full_name, u.email, u.phone
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.verification_status = 'VERIFIED'
    """
    params = []
    if specialty and specialty.lower() != "all":
        sql += " AND LOWER(d.specialization) LIKE ?"
        params.append(f"%{specialty.lower()}%")
    if language and language.lower() != "all":
        sql += " AND LOWER(d.languages_spoken) LIKE ?"
        params.append(f"%{language.lower()}%")
    if min_rating:
        sql += " AND d.rating_avg >= ?"
        params.append(min_rating)
        
    sql += " ORDER BY d.rating_avg DESC"
    docs = query_all(sql, params)
    for doc in docs:
        if doc.get("languages_spoken"):
            try:
                doc["languages_list"] = json.loads(doc["languages_spoken"])
            except Exception:
                doc["languages_list"] = [doc["languages_spoken"]]
        else:
            doc["languages_list"] = ["English"]
    return {"success": True, "data": docs}

@api_router.get("/doctors/{doctor_id}")
async def get_doctor_detail(doctor_id: str):
    doc = query_one("""
        SELECT d.*, u.full_name, u.email, u.phone
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    """, (doctor_id,))
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    
    reviews = query_all("""
        SELECT r.*, p.age, p.gender
        FROM doctor_reviews r
        JOIN patients p ON r.patient_id = p.id
        WHERE r.doctor_id = ? AND r.is_moderated = 0
        ORDER BY r.created_at DESC LIMIT 10
    """, (doctor_id,))
    
    if doc.get("languages_spoken"):
        try:
            doc["languages_list"] = json.loads(doc["languages_spoken"])
        except Exception:
            doc["languages_list"] = [doc["languages_spoken"]]
    if doc.get("availability_schedule"):
        try:
            doc["schedule_list"] = json.loads(doc["availability_schedule"])
        except Exception:
            doc["schedule_list"] = ["09:00 AM - 12:00 PM", "04:00 PM - 07:00 PM"]
            
    return {"success": True, "data": doc, "reviews": reviews}

# ----------------- APPOINTMENTS & TELECONSULTATION -----------------
@api_router.get("/appointments")
async def get_appointments(user: dict = Depends(get_current_user)):
    if user["role"] == "PATIENT":
        p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
        if not p:
            return {"success": True, "data": []}
        appts = query_all("""
            SELECT a.*, d.specialization, d.avatar_emoji, d.consultation_fee, u.full_name as doctor_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE a.patient_id = ?
            ORDER BY a.appointment_date DESC, a.created_at DESC
        """, (p["id"],))
    elif user["role"] == "DOCTOR":
        d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
        if not d:
            return {"success": True, "data": []}
        appts = query_all("""
            SELECT a.*, p.age, p.gender, p.village, p.district, p.blood_group, u.full_name as patient_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE a.doctor_id = ?
            ORDER BY a.appointment_date DESC, a.created_at DESC
        """, (d["id"],))
    else:
        appts = query_all("""
            SELECT a.*, u_p.full_name as patient_name, u_d.full_name as doctor_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN users u_p ON p.user_id = u_p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u_d ON d.user_id = u_d.id
            ORDER BY a.created_at DESC LIMIT 50
        """)
    return {"success": True, "data": appts}

@api_router.post("/appointments")
async def create_appointment(req: AppointmentCreate, user: dict = Depends(require_role(["PATIENT"]))):
    p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
    if not p:
        raise HTTPException(status_code=400, detail="Patient profile not found.")
        
    # Check for slot double-booking
    conflict = query_one("""
        SELECT id FROM appointments 
        WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ? AND status IN ('CONFIRMED', 'UPCOMING', 'IN_PROGRESS')
    """, (req.doctor_id, req.appointment_date, req.time_slot))
    if conflict:
        raise HTTPException(status_code=409, detail="Selected time slot is already booked. Please choose another slot.")

    appt_id = f"apt_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, time_slot, consultation_mode, status, chief_complaint, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, ?)
    """, (appt_id, p["id"], req.doctor_id, req.appointment_date, req.time_slot, req.consultation_mode, req.chief_complaint, req.symptoms))
    
    # Notify doctor
    doc = query_one("SELECT user_id FROM doctors WHERE id = ?", (req.doctor_id,))
    if doc:
        notif_id = f"notif_{secrets.token_hex(6)}"
        execute_query("""
            INSERT INTO notifications (id, user_id, title, message, type, link)
            VALUES (?, ?, ?, ?, 'APPOINTMENT', '/#doctor-queue')
        """, (notif_id, doc["user_id"], "New Appointment Booked",
              f"Patient {user['full_name']} scheduled a consultation for {req.appointment_date} at {req.time_slot}."))

    log_audit(user["id"], "APPOINTMENT_BOOKED", "APPOINTMENT", f"Appointment {appt_id} with Doctor {req.doctor_id}")
    return {"success": True, "message": "Appointment confirmed successfully!", "appointment_id": appt_id}

@api_router.patch("/appointments/{appointment_id}/status")
async def update_appointment_status(appointment_id: str, req: AppointmentStatusUpdate, user: dict = Depends(get_current_user)):
    appt = query_one("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found.")
        
    user_role = user.get("role")
    user_id = user.get("id")
    
    # Object-level authorization check
    if user_role != "ADMIN":
        if user_role == "PATIENT":
            p = query_one("SELECT id FROM patients WHERE user_id = ?", (user_id,))
            if not p or p["id"] != appt["patient_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the patient on this appointment.")
        elif user_role == "DOCTOR":
            d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user_id,))
            if not d or d["id"] != appt["doctor_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the assigned doctor on this appointment.")
        else:
            raise HTTPException(status_code=403, detail="Access denied: Unauthorized role.")
            
    execute_query("UPDATE appointments SET status = ? WHERE id = ?", (req.status.upper(), appointment_id))
    log_audit(user_id, "APPOINTMENT_STATUS_UPDATE", "APPOINTMENT", f"Appointment {appointment_id} status changed to {req.status.upper()}")
    
    # Notify other party
    if user_role == "DOCTOR":
        pat_user = query_one("SELECT user_id FROM patients WHERE id = ?", (appt["patient_id"],))
        if pat_user:
            notif_id = f"notif_{secrets.token_hex(6)}"
            execute_query("""
                INSERT INTO notifications (id, user_id, title, message, type, link)
                VALUES (?, ?, ?, ?, 'APPOINTMENT', '/#patient-home')
            """, (notif_id, pat_user["user_id"], f"Appointment {req.status.capitalize()}",
                  f"Doctor updated your appointment status for {appt['appointment_date']} to {req.status.upper()}."))
    elif user_role == "PATIENT":
        doc_user = query_one("SELECT user_id FROM doctors WHERE id = ?", (appt["doctor_id"],))
        if doc_user:
            notif_id = f"notif_{secrets.token_hex(6)}"
            execute_query("""
                INSERT INTO notifications (id, user_id, title, message, type, link)
                VALUES (?, ?, ?, ?, 'APPOINTMENT', '/#doctor-queue')
            """, (notif_id, doc_user["user_id"], "Appointment Cancelled by Patient",
                  f"Patient has updated their appointment for {appt['appointment_date']}."))
                  
    return {"success": True, "message": f"Appointment status updated to {req.status.upper()}."}

@api_router.post("/consultations/{appointment_id}/start")
async def start_consultation(appointment_id: str, user: dict = Depends(get_current_user)):
    appt = query_one("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found.")
        
    user_role = user.get("role")
    user_id = user.get("id")
    if user_role != "ADMIN":
        if user_role == "PATIENT":
            pat = query_one("SELECT id FROM patients WHERE user_id = ?", (user_id,))
            if not pat or pat["id"] != appt["patient_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the patient on this appointment.")
        elif user_role == "DOCTOR":
            doc = query_one("SELECT id FROM doctors WHERE user_id = ?", (user_id,))
            if not doc or doc["id"] != appt["doctor_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the assigned doctor on this appointment.")
        else:
            raise HTTPException(status_code=403, detail="Access denied: Unauthorized role.")
        
    # Check if consultation already exists
    existing = query_one("SELECT * FROM consultations WHERE appointment_id = ?", (appointment_id,))
    if existing:
        return {"success": True, "data": existing}
        
    cns_id = f"cns_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO consultations (id, appointment_id, patient_id, doctor_id, mode, status, clinical_notes)
        VALUES (?, ?, ?, ?, ?, 'IN_PROGRESS', ?)
    """, (cns_id, appointment_id, appt["patient_id"], appt["doctor_id"], appt["consultation_mode"], appt["chief_complaint"]))
    
    execute_query("UPDATE appointments SET status = 'IN_PROGRESS' WHERE id = ?", (appointment_id,))
    log_audit(user["id"], "CONSULTATION_STARTED", "CONSULTATION", f"Consultation {cns_id}")
    
    cns = query_one("SELECT * FROM consultations WHERE id = ?", (cns_id,))
    return {"success": True, "data": cns}

@api_router.get("/consultations/{consultation_id}")
async def get_consultation(consultation_id: str, user: dict = Depends(get_current_user)):
    cns = query_one("""
        SELECT c.*, a.appointment_date, a.time_slot, a.chief_complaint,
               p.age, p.gender, p.blood_group, p.village, p.district, p.allergies, p.chronic_conditions, p.abha_id,
               u_p.full_name as patient_name, u_d.full_name as doctor_name,
               d.specialization, d.qualification
        FROM consultations c
        JOIN appointments a ON c.appointment_id = a.id
        JOIN patients p ON c.patient_id = p.id
        JOIN users u_p ON p.user_id = u_p.id
        JOIN doctors d ON c.doctor_id = d.id
        JOIN users u_d ON d.user_id = u_d.id
        WHERE c.id = ?
    """, (consultation_id,))
    if not cns:
        raise HTTPException(status_code=404, detail="Consultation not found.")
        
    user_role = user.get("role")
    user_id = user.get("id")
    if user_role != "ADMIN":
        if user_role == "PATIENT":
            pat = query_one("SELECT id FROM patients WHERE user_id = ?", (user_id,))
            if not pat or pat["id"] != cns["patient_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the authorized patient in this consultation.")
        elif user_role == "DOCTOR":
            doc = query_one("SELECT id FROM doctors WHERE user_id = ?", (user_id,))
            if not doc or doc["id"] != cns["doctor_id"]:
                raise HTTPException(status_code=403, detail="Access denied: You are not the assigned doctor in this consultation.")
        else:
            raise HTTPException(status_code=403, detail="Access denied: Unauthorized role.")
        
    # Messages
    msgs = query_all("SELECT * FROM consultation_messages WHERE consultation_id = ? ORDER BY timestamp ASC", (consultation_id,))
    # Prescription if exists
    rx = query_one("SELECT * FROM prescriptions WHERE consultation_id = ?", (consultation_id,))
    
    return {"success": True, "data": cns, "messages": msgs, "prescription": rx}

@api_router.post("/consultations/{consultation_id}/complete")
async def complete_consultation(consultation_id: str, req: ConsultationCompleteRequest, user: dict = Depends(require_role(["DOCTOR", "ADMIN"]))):
    cns = query_one("SELECT * FROM consultations WHERE id = ?", (consultation_id,))
    if not cns:
        raise HTTPException(status_code=404, detail="Consultation session not found.")
        
    if user.get("role") == "DOCTOR":
        doc = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
        if not doc or doc["id"] != cns["doctor_id"]:
            raise HTTPException(status_code=403, detail="Access denied: You are not the assigned doctor for this consultation.")
        
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    execute_query("""
        UPDATE consultations 
        SET status = 'COMPLETED', end_time = ?, clinical_notes = ?, diagnosis = ?, follow_up_advice = ?, follow_up_date = ?
        WHERE id = ?
    """, (now_str, req.clinical_notes, req.diagnosis, req.follow_up_advice, req.follow_up_date, consultation_id))
    
    if cns.get("appointment_id"):
        execute_query("UPDATE appointments SET status = 'COMPLETED' WHERE id = ?", (cns["appointment_id"],))

    # Save prescription
    if req.medications:
        rx_id = f"rx_{secrets.token_hex(6)}"
        execute_query("""
            INSERT INTO prescriptions (id, consultation_id, patient_id, doctor_id, medications_json, general_advice)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rx_id, consultation_id, cns["patient_id"], cns["doctor_id"], json.dumps(req.medications), req.follow_up_advice))
        
        # Add to patient health records
        rec_id = f"rec_{secrets.token_hex(6)}"
        doc_user = query_one("SELECT full_name FROM users WHERE id = ?", (user["id"],))
        doc_name = doc_user["full_name"] if doc_user else "Doctor"
        execute_query("""
            INSERT INTO health_records (id, patient_id, title, record_type, date_recorded, uploaded_by, notes)
            VALUES (?, ?, ?, 'PRESCRIPTION', ?, ?, ?)
        """, (rec_id, cns["patient_id"], f"Prescription: {req.diagnosis}", now_str[:10], doc_name, req.follow_up_advice))

    # Notify patient to rate doctor
    patient_user = query_one("SELECT user_id FROM patients WHERE id = ?", (cns["patient_id"],))
    if patient_user:
        notif_id = f"notif_{secrets.token_hex(6)}"
        execute_query("""
            INSERT INTO notifications (id, user_id, title, message, type, link)
            VALUES (?, ?, ?, ?, 'RATING', '/#rate-consultation')
        """, (notif_id, patient_user["user_id"], "Rate Your Consultation",
              f"Your consultation is completed. Please rate your experience to strengthen trust in rural healthcare."))

    log_audit(user["id"], "CONSULTATION_COMPLETED", "CONSULTATION", f"Consultation {consultation_id} completed with diagnosis: {req.diagnosis}")
    return {"success": True, "message": "Consultation successfully finalized and prescription generated."}

# ----------------- DOCTOR RATINGS & TRUST -----------------
@api_router.post("/reviews")
async def create_review(req: ReviewCreate, user: dict = Depends(require_role(["PATIENT"]))):
    p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
    if not p:
        raise HTTPException(status_code=400, detail="Patient profile not found.")
        
    # Check that consultation exists, belongs to patient, and is completed
    cns = query_one("SELECT * FROM consultations WHERE id = ? AND patient_id = ? AND status = 'COMPLETED'", (req.consultation_id, p["id"]))
    if not cns:
        raise HTTPException(status_code=400, detail="Reviews can only be submitted for completed verified consultations.")
        
    # Prevent duplicate review for same consultation
    dup = query_one("SELECT id FROM doctor_reviews WHERE consultation_id = ?", (req.consultation_id,))
    if dup:
        raise HTTPException(status_code=400, detail="You have already submitted a review for this consultation.")
        
    # Format initials to protect patient privacy in rural setting
    name_parts = user["full_name"].strip().split()
    initials = f"{name_parts[0][0]}.{name_parts[-1][0]}." if len(name_parts) > 1 else f"{name_parts[0][0]}."

    rev_id = f"rev_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO doctor_reviews (id, doctor_id, patient_id, consultation_id, patient_initials, rating,
                                   communication_score, punctuality_score, explanation_score, review_text, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (rev_id, req.doctor_id, p["id"], req.consultation_id, initials, req.rating,
          req.communication_score, req.punctuality_score, req.explanation_score, req.review_text))
          
    # Update doctor's aggregate rating
    all_revs = query_all("SELECT rating FROM doctor_reviews WHERE doctor_id = ? AND is_moderated = 0", (req.doctor_id,))
    avg_score = round(sum(r["rating"] for r in all_revs) / len(all_revs), 1)
    execute_query("UPDATE doctors SET rating_avg = ?, reviews_count = ? WHERE id = ?", (avg_score, len(all_revs), req.doctor_id))
    
    log_audit(user["id"], "DOCTOR_REVIEW_SUBMITTED", "DOCTOR_REVIEWS", f"Review for doctor {req.doctor_id}, score {req.rating}")
    return {"success": True, "message": "Thank you! Your verified rating has been published.", "new_doctor_rating": avg_score}

# ----------------- HEALTH CAMPS & COMMUNITY NETWORK -----------------
@api_router.get("/camps")
async def get_camps():
    camps = query_all("SELECT * FROM health_camps ORDER BY date ASC")
    for c in camps:
        if c.get("services_json"):
            try:
                c["services_list"] = json.loads(c["services_json"])
            except Exception:
                c["services_list"] = [c["services_json"]]
        if c.get("impact_report_json"):
            try:
                c["impact_report"] = json.loads(c["impact_report_json"])
            except Exception:
                c["impact_report"] = None
    return {"success": True, "data": camps}

@api_router.post("/camps")
async def create_camp(req: CampCreate, user: dict = Depends(require_role(["DOCTOR", "HOSPITAL", "ADMIN"]))):
    camp_id = f"camp_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO health_camps (id, title, camp_type, description, organizer_name, organizer_type, location, village, district, date, time, capacity, services_json, is_free, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'REGISTRATION_OPEN')
    """, (camp_id, req.title, req.camp_type, req.description, user["full_name"], user["role"], req.location, req.village, req.district, req.date, req.time, req.capacity, json.dumps(req.services), 1 if req.is_free else 0))
    
    log_audit(user["id"], "CAMP_PUBLISHED", "HEALTH_CAMPS", f"New health camp published: {req.title}")
    return {"success": True, "message": "Health camp successfully scheduled and published!", "camp_id": camp_id}

@api_router.post("/camps/{camp_id}/register")
async def register_for_camp(camp_id: str, user: dict = Depends(require_role(["PATIENT"]))):
    camp = query_one("SELECT * FROM health_camps WHERE id = ?", (camp_id,))
    if not camp:
        raise HTTPException(status_code=404, detail="Camp not found.")
    if camp["registered_count"] >= camp["capacity"]:
        raise HTTPException(status_code=400, detail="Camp registration is full.")
        
    p = query_one("SELECT * FROM patients WHERE user_id = ?", (user["id"],))
    pat_id = p["id"] if p else None
    
    # Check duplicate
    dup = query_one("SELECT id FROM camp_registrations WHERE camp_id = ? AND (patient_id = ? OR phone = ?)", (camp_id, pat_id, user.get("phone")))
    if dup:
        raise HTTPException(status_code=400, detail="You are already registered for this health camp.")
        
    reg_id = f"reg_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO camp_registrations (id, camp_id, patient_id, patient_name, phone, age, gender, village)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (reg_id, camp_id, pat_id, user["full_name"], user.get("phone"), p["age"] if p else 30, p["gender"] if p else "Other", p["village"] if p else camp["village"]))
    
    execute_query("UPDATE health_camps SET registered_count = registered_count + 1 WHERE id = ?", (camp_id,))
    
    notif_id = f"notif_{secrets.token_hex(6)}"
    execute_query("""
        INSERT INTO notifications (id, user_id, title, message, type, link)
        VALUES (?, ?, ?, ?, 'CAMP', '/#health-camps')
    """, (notif_id, user["id"], "Camp Registration Confirmed",
          f"Your seat for '{camp['title']}' on {camp['date']} at {camp['location']} is confirmed."))

    log_audit(user["id"], "CAMP_REGISTRATION", "CAMP_REGISTRATIONS", f"Patient registered for camp {camp_id}")
    return {"success": True, "message": "Seat successfully reserved at community health camp!", "registration_id": reg_id}

# Village / Community requests
@api_router.get("/camp-requests")
async def get_camp_requests():
    reqs = query_all("SELECT * FROM camp_requests ORDER BY created_at DESC")
    for r in reqs:
        if r.get("required_services_json"):
            try:
                r["required_services"] = json.loads(r["required_services_json"])
            except Exception:
                r["required_services"] = [r["required_services_json"]]
    return {"success": True, "data": reqs}

@api_router.post("/camp-requests")
async def create_camp_request(req: CampRequestCreate, user: Optional[dict] = Depends(get_optional_user)):
    req_id = f"req_{secrets.token_hex(6)}"
    requester_id = user["id"] if user else None
    requester_name = user["full_name"] if user else req.contact_person
    requester_type = user["role"] if user else "Village Representative"
    
    execute_query("""
        INSERT INTO camp_requests (id, requester_id, requester_name, requester_type, village, district, contact_person, contact_phone, expected_patients, preferred_date, camp_type, required_services_json, urgency, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (req_id, requester_id, requester_name, requester_type, req.village, req.district, req.contact_person, req.contact_phone, req.expected_patients, req.preferred_date, req.camp_type, json.dumps(req.required_services), req.urgency, req.description))
    
    log_audit(requester_id, "CAMP_REQUEST_CREATED", "CAMP_REQUESTS", f"Village camp request for {req.village} ({req.expected_patients} patients)")
    return {"success": True, "message": "Health camp request submitted! Nearby hospitals and doctors will be notified.", "request_id": req_id}

@api_router.post("/camp-requests/{request_id}/accept")
async def accept_camp_request(request_id: str, user: dict = Depends(require_role(["DOCTOR", "HOSPITAL", "ADMIN"]))):
    req = query_one("SELECT * FROM camp_requests WHERE id = ?", (request_id,))
    if not req:
        raise HTTPException(status_code=404, detail="Camp request not found.")
        
    execute_query("""
        UPDATE camp_requests 
        SET status = 'ACCEPTED', accepted_by_id = ?, accepted_by_name = ?
        WHERE id = ?
    """, (user["id"], user["full_name"], request_id))

    # Proactively schedule a camp in health_camps
    camp_id = f"camp_{secrets.token_hex(6)}"
    title = f"Community Camp: {req['camp_type']} - {req['village']}"
    execute_query("""
        INSERT INTO health_camps (id, title, camp_type, description, organizer_name, organizer_type, organizer_id, location, village, district, date, time, capacity, services_json, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'REGISTRATION_OPEN')
    """, (camp_id, title, req["camp_type"], req["description"], user["full_name"], user["role"], user["id"],
          f"{req['village']} Gram Panchayat Community Hall", req["village"], req["district"], req["preferred_date"], req["preferred_time"], req["expected_patients"], req["required_services_json"]))

    log_audit(user["id"], "CAMP_REQUEST_ACCEPTED", "CAMP_REQUESTS", f"Request {request_id} accepted by {user['full_name']}")
    return {"success": True, "message": "Camp request accepted and scheduled on the public directory!", "camp_id": camp_id}

@api_router.post("/camps/{camp_id}/complete")
async def complete_camp(camp_id: str, report: dict, user: dict = Depends(require_role(["DOCTOR", "HOSPITAL", "ADMIN"]))):
    camp = query_one("SELECT * FROM health_camps WHERE id = ?", (camp_id,))
    if not camp:
        raise HTTPException(status_code=404, detail="Camp not found.")
        
    execute_query("""
        UPDATE health_camps 
        SET status = 'COMPLETED', impact_report_json = ?
        WHERE id = ?
    """, (json.dumps(report), camp_id))
    
    log_audit(user["id"], "CAMP_COMPLETED", "HEALTH_CAMPS", f"Camp {camp_id} marked completed with impact report.")
    return {"success": True, "message": "Health camp completed and Social Impact Report generated!"}

# ----------------- ABDM / ABHA SANDBOX -----------------
@api_router.post("/abdm/link-abha")
async def link_abha(req: dict, user: dict = Depends(require_role(["PATIENT"]))):
    res = AbhaService.verify_or_generate_abha(phone=user.get("phone", "9876543210"))
    execute_query("""
        UPDATE patients 
        SET abha_id = ?, abha_status = 'LINKED'
        WHERE user_id = ?
    """, (res["abha_number"], user["id"]))
    
    log_audit(user["id"], "ABDM_ABHA_LINKED", "PATIENT", f"Linked ABHA ID: {res['abha_number']}")
    return {"success": True, "data": res}

@api_router.post("/abdm/request-consent")
async def request_consent(req: ConsentRequestInput, user: dict = Depends(require_role(["DOCTOR"]))):
    d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
    if not d:
        raise HTTPException(status_code=400, detail="Doctor profile not found.")
        
    cid = ConsentService.create_consent_request(
        patient_id=req.patient_id,
        doctor_id=d["id"],
        purpose=req.purpose,
        records_requested=req.records_requested
    )
    return {"success": True, "consent_id": cid, "message": "ABDM Consent Request sent to patient via HIE-CM Gateway."}

@api_router.get("/abdm/consents")
async def get_consents(user: dict = Depends(get_current_user)):
    if user["role"] == "PATIENT":
        p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
        consents = query_all("""
            SELECT c.*, u.full_name as doctor_name, d.specialization
            FROM abdm_consents c
            JOIN doctors d ON c.doctor_id = d.id
            JOIN users u ON d.user_id = u.id
            WHERE c.patient_id = ?
            ORDER BY c.created_at DESC
        """, (p["id"],)) if p else []
    elif user["role"] == "DOCTOR":
        d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
        consents = query_all("""
            SELECT c.*, u.full_name as patient_name
            FROM abdm_consents c
            JOIN patients p ON c.patient_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE c.doctor_id = ?
            ORDER BY c.created_at DESC
        """, (d["id"],)) if d else []
    else:
        consents = query_all("SELECT * FROM abdm_consents ORDER BY created_at DESC LIMIT 50")
    return {"success": True, "data": consents}

@api_router.patch("/abdm/consents/{consent_id}")
async def update_consent(consent_id: str, req: dict, user: dict = Depends(require_role(["PATIENT"]))):
    new_status = req.get("status", "DENIED")
    success = ConsentService.update_consent_status(consent_id, user["id"], new_status)
    if not success:
        raise HTTPException(status_code=404, detail="Consent record not found.")
    return {"success": True, "message": f"ABDM Consent status updated to {new_status}."}

@api_router.get("/abdm/patient-records/{patient_id}")
async def get_patient_records_under_consent(patient_id: str, user: dict = Depends(require_role(["DOCTOR"]))):
    d = query_one("SELECT id FROM doctors WHERE user_id = ?", (user["id"],))
    if not d:
        raise HTTPException(status_code=400, detail="Doctor profile not found.")
    result = HealthRecordExchangeService.get_authorized_records(doctor_id=d["id"], patient_id=patient_id)
    return {"success": True, "data": result}

# ----------------- HEALTH RECORDS -----------------
@api_router.get("/health-records")
async def get_health_records(user: dict = Depends(require_role(["PATIENT"]))):
    p = query_one("SELECT id FROM patients WHERE user_id = ?", (user["id"],))
    if not p:
        return {"success": True, "data": []}
    records = query_all("SELECT * FROM health_records WHERE patient_id = ? ORDER BY date_recorded DESC", (p["id"],))
    return {"success": True, "data": records}

# ----------------- IN-APP NOTIFICATIONS -----------------
@api_router.get("/notifications")
async def get_notifications(user: dict = Depends(get_current_user)):
    notifs = query_all("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user["id"],))
    unread_count = sum(1 for n in notifs if not n.get("is_read"))
    return {"success": True, "data": notifs, "unread_count": unread_count}

@api_router.patch("/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: str, user: dict = Depends(get_current_user)):
    execute_query("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, user["id"]))
    return {"success": True}

# ----------------- ADMIN DASHBOARD & ANALYTICS -----------------
@api_router.get("/admin/stats")
async def get_admin_stats(user: dict = Depends(require_role(["ADMIN"]))):
    total_patients = query_one("SELECT count(*) as count FROM patients")["count"]
    total_doctors = query_one("SELECT count(*) as count FROM doctors WHERE verification_status = 'VERIFIED'")["count"]
    pending_doctors = query_one("SELECT count(*) as count FROM doctors WHERE verification_status = 'PENDING'")["count"]
    total_camps = query_one("SELECT count(*) as count FROM health_camps")["count"]
    total_appts = query_one("SELECT count(*) as count FROM appointments")["count"]
    comp_cns = query_one("SELECT count(*) as count FROM consultations WHERE status = 'COMPLETED'")["count"]
    avg_rating = query_one("SELECT ROUND(AVG(rating), 1) as avg_score FROM doctor_reviews WHERE is_moderated = 0")["avg_score"] or 4.8
    total_camp_reg = query_one("SELECT count(*) as count FROM camp_registrations")["count"]
    
    urgency_dist = query_all("""
        SELECT urgency, count(*) as count 
        FROM ai_triage_assessments 
        GROUP BY urgency
    """)
    
    return {
        "success": True,
        "data": {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "pending_doctors": pending_doctors,
            "total_camps": total_camps,
            "total_appointments": total_appts,
            "completed_consultations": comp_cns,
            "average_doctor_rating": avg_rating,
            "camp_registrations": total_camp_reg,
            "urgency_distribution": urgency_dist
        }
    }

@api_router.get("/admin/audit-logs")
async def get_audit_logs(user: dict = Depends(require_role(["ADMIN"]))):
    logs = query_all("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50")
    return {"success": True, "data": logs}

@api_router.post("/admin/reset-demo")
async def reset_demo_data(user: dict = Depends(require_role(["ADMIN"]))):
    from backend.app.database.seed_data import seed_database
    # Clear tables and reseed
    with get_db() as conn:
        cursor = conn.cursor()
        for t in ["audit_logs", "notifications", "abdm_consents", "doctor_reviews", "camp_registrations",
                  "camp_requests", "health_camps", "medical_image_screenings", "ai_triage_assessments",
                  "health_records", "prescriptions", "consultation_messages", "consultations",
                  "appointments", "organizations", "doctors", "patients", "users"]:
            cursor.execute(f"DELETE FROM {t};")
        conn.commit()
    seed_database()
    return {"success": True, "message": "Demo database successfully reset to official academic seed state."}
