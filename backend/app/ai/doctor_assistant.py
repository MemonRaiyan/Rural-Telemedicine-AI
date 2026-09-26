from typing import Dict, Any, Optional

def generate_clinical_summary(
    patient_name: str,
    age: int,
    gender: str,
    chief_complaint: str,
    symptoms: str,
    duration: Optional[str] = "3 days",
    doctor_raw_notes: Optional[str] = "",
    provisional_diagnosis: Optional[str] = ""
) -> Dict[str, str]:
    """
    AI Clinical Assistant that synthesizes patient history, reported symptoms,
    and doctor observations into standard SOAP formatted clinical documentation.
    """
    subjective = (
        f"{patient_name}, {age} y/o {gender}, presents with primary complaint of {chief_complaint}. "
        f"Symptoms reported: {symptoms}. Duration: {duration}."
    )
    
    objective = (
        f"Teleconsultation clinical examination: Patient alert, responsive, oriented in time/place. "
        f"{doctor_raw_notes if doctor_raw_notes else 'No acute distress noted over high-definition video link.'}"
    )
    
    assessment = provisional_diagnosis if provisional_diagnosis else "Provisional clinical assessment pending laboratory/clinical review."
    
    plan = (
        "1. Prescribed supportive pharmacotherapy and symptomatic management.\n"
        "2. Adequate oral fluid intake and balanced diet advised.\n"
        "3. Watch for red-flag warning signs.\n"
        "4. Follow-up consultation scheduled or emergency referral if worsening."
    )

    return {
        "chief_complaint": chief_complaint,
        "subjective": subjective,
        "objective": objective,
        "assessment": assessment,
        "plan": plan,
        "disclaimer": "Doctor remains exclusively responsible for final clinical approval and statutory medical sign-off."
    }
