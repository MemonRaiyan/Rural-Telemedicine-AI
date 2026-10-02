import re
from typing import Dict, Any, List, Optional
from backend.app.ai.emergency import check_emergency_red_flags

# Vernacular dictionary mapping Gujarati and Hindi terms to standardized clinical entities
VERNACULAR_SYMPTOM_MAP = {
    # Gujarati terms
    "તાવ": "fever",
    "બુખાર": "fever",
    "ખાંસી": "cough",
    "ઉધરસ": "cough",
    "શરદી": "cold/rhinorrhea",
    "ગળું દુખવું": "sore throat",
    "માથું દુખવું": "headache",
    "માથાનો દુખાવો": "headache",
    "પેટમાં દુખાવો": "abdominal pain",
    "ઝાડા": "diarrhea",
    "ઊલટી": "vomiting",
    "ચક્કર": "dizziness",
    "થાક": "fatigue",
    "કમળો": "jaundice",
    "સાંધાનો દુખાવો": "joint pain",
    "કમરનો દુખાવો": "back pain",
    "આંખોમાં બળતરા": "eye burning/redness",
    "આંખમાં લાલાશ": "eye redness",
    "ત્વચા પર ફોલ્લી": "skin rash",
    "ખંજવાળ": "itching",
    "શ્વાસ ચડવો": "shortness of breath",
    
    # Hindi terms
    "बुखार": "fever",
    "खांसी": "cough",
    "सर्दी": "cold",
    "जुकाम": "common cold",
    "गले में खराश": "sore throat",
    "सिरदर्द": "headache",
    "पेट दर्द": "abdominal pain",
    "दस्त": "diarrhea",
    "उल्टी": "vomiting",
    "चक्कर आना": "dizziness",
    "थकान": "fatigue",
    "जोड़ों का दर्द": "joint pain",
    "कमर दर्द": "backache",
    "आंखों में जलन": "eye irritation",
    "खुजली": "itching",
    "त्वचा पर चकत्ते": "skin rash",
    "सांस फूलना": "breathlessness"
}

DEPARTMENT_KEYWORDS = {
    "Pediatrician": [
        "child", "baby", "infant", "toddler", "vaccine", "teething", "બાળક", "નાનું બાળક", "बच्चा", "शिशु", "टीका"
    ],
    "Gynecologist": [
        "pregnancy", "period", "menstrual", "pregnant", "uterus", "cramps", "vaginal", "ગર્ભાવસ્થા", "માસિક", "સગર્ભા", "गर्भावस्था", "माहवारी"
    ],
    "Dermatologist": [
        "skin", "rash", "itching", "eczema", "fungal", "pimples", "acne", "boils", "ત્વચા", "ખંજવાળ", "દાહ", "ખીલ", "त्वचा", "खुजली", "दाद"
    ],
    "Ophthalmologist": [
        "eye", "vision", "blur", "cornea", "cataract", "burning eye", "આંખ", "દ્રષ્ટિ", "મોતિયો", "આંખો", "आंख", "धुंधला", "मोतियाबिंद"
    ],
    "Cardiologist": [
        "chest pain", "palpitation", "heart beat", "hypertension", "bp high", "છાતીમાં દુખાવો", "ધબકારા", "छाती में दर्द", "धड़कन"
    ],
    "Orthopedic": [
        "bone", "joint pain", "fracture", "knee pain", "back pain", "arthritis", "હાડકાં", "સાંધાનો દુખાવો", "ઢીંચણ", "हड्डी", "जोड़ों का दर्द", "घुटने"
    ],
    "ENT Specialist": [
        "ear pain", "ear discharge", "throat", "sinus", "tonsil", "hearing", "કાન", "ગળું", "નાક", "कान", "गला", "नाक"
    ]
}

def extract_duration(text: str) -> str:
    patterns = [
        r"(\d+\s*(?:days?|weeks?|months?|hours?|years?))",
        r"(\d+\s*(?:દિવસ|અઠવાડિયા|મહિના|કલાક))",
        r"(\d+\s*(?:दिन|हफ्ते|महीने|घंटे))"
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "Not specified (Recent onset)"

def extract_severity(text: str, user_severity: Optional[str] = None) -> str:
    if user_severity and user_severity in ["Mild", "Moderate", "Severe"]:
        return user_severity
    text_lower = text.lower()
    if any(w in text_lower for w in ["severe", "unbearable", "very high", "તીવ્ર", "ખૂબ વધારે", "गंभीर", "अत्यधिक"]):
        return "Severe"
    if any(w in text_lower for w in ["mild", "slight", "little", "હળવું", "થોડું", "हल्का", "थोड़ा"]):
        return "Mild"
    return "Moderate"

def detect_language(text: str) -> str:
    for char in text:
        # Gujarati unicode range: 0x0A80 - 0x0AFF
        if '\u0a80' <= char <= '\u0aff':
            return 'gu'
        # Devanagari (Hindi) range: 0x0900 - 0x097F
        if '\u0900' <= char <= '\u097f':
            return 'hi'
    return 'en'

def perform_nlp_triage(
    symptoms_text: str,
    age: int = 30,
    gender: str = "Other",
    user_severity: Optional[str] = None,
    existing_conditions: Optional[str] = None
) -> Dict[str, Any]:
    
    # 1. First run Emergency Red-Flag Engine
    emergency_check = check_emergency_red_flags(symptoms_text)
    
    lang = detect_language(symptoms_text)
    duration = extract_duration(symptoms_text)
    severity = extract_severity(symptoms_text, user_severity)
    
    # 2. Extract standardized entities
    identified_entities = []
    text_lower = symptoms_text.lower()
    
    # Map vernacular keywords
    for key, entity in VERNACULAR_SYMPTOM_MAP.items():
        if key in text_lower or key in symptoms_text:
            if entity not in identified_entities:
                identified_entities.append(entity)
                
    # Check common english symptoms
    english_symptoms = ["fever", "cough", "cold", "headache", "vomiting", "diarrhea", "pain", "fatigue", "rash", "dizziness"]
    for s in english_symptoms:
        if s in text_lower and s not in identified_entities:
            identified_entities.append(s)
            
    if not identified_entities:
        identified_entities.append("General constitutional symptoms")

    # 3. Urgency Determination
    if emergency_check["is_emergency"]:
        urgency = "EMERGENCY"
    elif severity == "Severe" or (age < 5 and "fever" in identified_entities) or (age > 65 and "fever" in identified_entities):
        urgency = "HIGH"
    elif severity == "Moderate" or len(identified_entities) > 2:
        urgency = "MODERATE"
    else:
        urgency = "LOW"

    # 4. Department Recommendation
    suggested_dept = "General Physician"
    if age < 14:
        suggested_dept = "Pediatrician"
    else:
        for dept, keywords in DEPARTMENT_KEYWORDS.items():
            if any(k in text_lower or k in symptoms_text for k in keywords):
                suggested_dept = dept
                break

    # 5. Symptom Clinical Summary & Recommended Action
    red_flag_list = [f["condition"] for f in emergency_check.get("flags_detected", [])]
    
    if urgency == "EMERGENCY":
        summary = f"CRITICAL: Symptoms indicate possible acute medical emergency ({', '.join(red_flag_list)}). Immediate emergency intervention required."
        recommended_action = "Seek immediate in-person emergency hospital care or dial 108 for ambulance."
    elif urgency == "HIGH":
        summary = f"Patient presents with {severity.lower()} {', '.join(identified_entities)} persisting for {duration}. Close clinical monitoring required."
        recommended_action = f"Consult a {suggested_dept} within 24 hours. If symptoms deteriorate, visit nearest health center."
    elif urgency == "MODERATE":
        summary = f"Patient exhibits {', '.join(identified_entities)} of moderate intensity (reported duration: {duration}). Likely self-limiting or early-stage infection/ailment."
        recommended_action = f"Schedule a telemedicine or in-person consultation with a {suggested_dept} for evaluation and guidance."
    else:
        summary = f"Mild symptoms reported: {', '.join(identified_entities)}. No acute distress observed."
        recommended_action = "Rest, adequate hydration, and monitor. Book a routine consultation if symptoms persist beyond 3 days."

    # Questions for Doctor
    questions_for_doctor = [
        f"What is the expected recovery timeline for {identified_entities[0] if identified_entities else 'these symptoms'}?",
        "Are there any warning signs I should watch out for at home?",
        "Should I continue normal diet and daily farm/work activities?"
    ]

    disclaimer = (
        "⚠️ Academic Prototype Preliminary Triage: This clinical entity extraction protocol provides preliminary urgency stratification. "
        "It does NOT constitute a certified medical diagnosis, prescription, or clinical treatment advice. "
        "In case of severe or deteriorating symptoms, immediately consult a qualified physician or contact emergency medical services (108)."
    )

    return {
        "urgency": urgency,
        "suggested_department": suggested_dept,
        "symptoms": identified_entities,
        "duration": duration,
        "severity": severity,
        "summary": summary,
        "red_flags": red_flag_list,
        "emergency_alert": emergency_check.get("emergency_alert"),
        "emergency_helpline": emergency_check.get("emergency_helpline"),
        "recommended_next_step": recommended_action,
        "questions_for_doctor": questions_for_doctor,
        "confidence": 0.88,
        "confidence_level": "Protocol-Based Clinical Match",
        "protocol_version": "Vernacular Clinical Entity Extraction Protocol v1.0 (Academic Prototype)",
        "language_detected": lang,
        "disclaimer": disclaimer
    }
