import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from backend.app.database.database import query_one, query_all, execute_query
from backend.app.auth.auth import log_audit

ABDM_ENV = os.environ.get("ABDM_ENV", "sandbox")
ABDM_CLIENT_ID = os.environ.get("ABDM_CLIENT_ID", "SBX_GRAMCARE_AI_2026")
ABDM_BASE_URL = os.environ.get("ABDM_BASE_URL", "https://dev.abdm.gov.in/gateway/v0.5")

class AbhaService:
    @staticmethod
    def verify_or_generate_abha(phone: str, aadhaar_last4: str = "4928") -> Dict[str, Any]:
        """
        Simulates ABDM Sandbox ABHA creation / lookup via OTP flow.
        """
        abha_number = f"14-{secrets.randbelow(8999)+1000}-{secrets.randbelow(8999)+1000}-{secrets.randbelow(8999)+1000}"
        abha_address = f"ruraluser.{phone[-4:]}@abdm"
        return {
            "environment": f"ABDM Sandbox ({ABDM_ENV})",
            "status": "SUCCESS",
            "abha_number": abha_number,
            "abha_address": abha_address,
            "kyc_verified": True,
            "message": "ABHA ID successfully linked via ABDM Sandbox Gateway."
        }

class ConsentService:
    @staticmethod
    def create_consent_request(patient_id: str, doctor_id: str, purpose: str, records_requested: str) -> str:
        consent_id = f"cst_{secrets.token_hex(6)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        execute_query("""
            INSERT INTO abdm_consents (id, patient_id, doctor_id, purpose, records_requested, consent_status, expires_at)
            VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
        """, (consent_id, patient_id, doctor_id, purpose, records_requested, expires_at))
        
        # Notify patient
        patient_user = query_one("SELECT user_id FROM patients WHERE id = ?", (patient_id,))
        if patient_user:
            notif_id = f"notif_{secrets.token_hex(6)}"
            execute_query("""
                INSERT INTO notifications (id, user_id, title, message, type, link)
                VALUES (?, ?, ?, ?, 'CONSENT', '/#health-records')
            """, (notif_id, patient_user["user_id"], "New ABDM Consent Request",
                  f"A doctor has requested access to your health records for {purpose}. Please review.", ))
        
        log_audit(doctor_id, "ABDM_CONSENT_REQUEST_CREATED", "ABDM_CONSENT", f"Consent ID: {consent_id} for Patient {patient_id}")
        return consent_id

    @staticmethod
    def update_consent_status(consent_id: str, user_id: str, new_status: str) -> bool:
        # new_status: GRANTED, DENIED, REVOKED
        consent = query_one("SELECT * FROM abdm_consents WHERE id = ?", (consent_id,))
        if not consent:
            return False
        
        granted_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if new_status == "GRANTED" else None
        execute_query("""
            UPDATE abdm_consents SET consent_status = ?, granted_at = ? WHERE id = ?
        """, (new_status, granted_at, consent_id))
        
        log_audit(user_id, f"ABDM_CONSENT_{new_status}", "ABDM_CONSENT", f"Consent ID: {consent_id}")
        return True

class HealthRecordExchangeService:
    @staticmethod
    def get_authorized_records(doctor_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Retrieves health records only if a valid, unexpired GRANTED consent exists.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        valid_consent = query_one("""
            SELECT * FROM abdm_consents 
            WHERE patient_id = ? AND doctor_id = ? AND consent_status = 'GRANTED' AND (expires_at > ? OR expires_at IS NULL)
        """, (patient_id, doctor_id, now_str))
        
        if not valid_consent:
            log_audit(doctor_id, "ABDM_RECORD_ACCESS_DENIED", "HEALTH_RECORD", f"Unauthorized attempt for patient {patient_id}", status_str="DENIED")
            return {
                "authorized": False,
                "reason": "No active GRANTED ABDM consent found or consent expired.",
                "records": []
            }
            
        records = query_all("SELECT * FROM health_records WHERE patient_id = ?", (patient_id,))
        log_audit(doctor_id, "ABDM_RECORD_ACCESS_GRANTED", "HEALTH_RECORD", f"Retrieved {len(records)} records under consent {valid_consent['id']}")
        
        return {
            "authorized": True,
            "consent_id": valid_consent["id"],
            "purpose": valid_consent["purpose"],
            "expires_at": valid_consent["expires_at"],
            "records": records
        }
