import re
from typing import Dict, Any, List

EMERGENCY_RED_FLAGS = [
    {
        "pattern": r"(chest\s*pain|heart\s*attack|छाती\s*में\s*दर्द|છાતીમાં\s*દુખાવો|pressure\s*in\s*chest|radiating\s*to\s*arm|left\s*arm\s*pain)",
        "condition": "Acute Coronary Syndrome / Suspected Cardiac Event",
        "guidance": "Rest immediately in a comfortable seated position. Call 108 (National Emergency Ambulance) or proceed to the nearest emergency room."
    },
    {
        "pattern": r"(difficulty\s*breathing|cannot\s*breathe|severe\s*shortness\s*of\s*breath|breathlessness|सांस\s*लेने\s*में\s*दिक्कत|શ્વાસ\s*લેવામાં\s*તકલીફ|gasping|blue\s*lips)",
        "condition": "Acute Respiratory Distress / Severe Dyspnea",
        "guidance": "Sit upright, do not lie flat. Loosen tight clothing. Call emergency services (108) immediately."
    },
    {
        "pattern": r"(unconscious|fainted|passed\s*out|loss\s*of\s*consciousness|बेहोश|બેભાન|not\s*responding|unresponsive)",
        "condition": "Syncope / Loss of Consciousness",
        "guidance": "Lay the person on their side in the recovery position. Check breathing. Do not give anything by mouth. Call 108 immediately."
    },
    {
        "pattern": r"(stroke|face\s*droop|slurred\s*speech|one\s*side\s*paralysis|paralysis|लकवा|લકવો|sudden\s*weakness|sudden\s*numbness)",
        "condition": "Suspected Acute Stroke (FAST Protocol)",
        "guidance": "Urgent brain ischemia window. Do not delay. Transport patient immediately to the nearest stroke-ready hospital."
    },
    {
        "pattern": r"(severe\s*bleeding|uncontrolled\s*bleeding|hemorrhage|खून\s*बहना|લોહી\s*વહેવું|deep\s*cut|spurting\s*blood)",
        "condition": "Severe Acute Hemorrhage",
        "guidance": "Apply firm, continuous pressure with a clean cloth or bandage directly to the wound. Elevate the injured area. Seek immediate emergency care."
    },
    {
        "pattern": r"(seizure|convulsion|fitting|दौरा|ખેંચ|epilepsy\s*attack)",
        "condition": "Acute Seizure / Convulsions",
        "guidance": "Protect from surrounding hazards. Do not hold the patient down or place objects in mouth. Turn onto side when twitching stops. Seek emergency care."
    },
    {
        "pattern": r"(anaphylaxis|severe\s*allergy|swollen\s*throat|swollen\s*tongue|allergy\s*attack)",
        "condition": "Severe Acute Allergic Reaction (Anaphylaxis)",
        "guidance": "Administer epinephrine autoinjector if prescribed. Call emergency ambulance (108) immediately."
    },
    {
        "pattern": r"(suicid|self\s*harm|harm\s*myself|આત્મહત્યા|आत्महत्या)",
        "condition": "Psychiatric Emergency / Crisis Support",
        "guidance": "Please reach out immediately. Contact the National Tele-MANAS Mental Health Helpline at 14416 or 1800-891-4416 (toll-free 24x7)."
    }
]

def check_emergency_red_flags(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    detected_flags: List[Dict[str, str]] = []
    
    for flag in EMERGENCY_RED_FLAGS:
        if re.search(flag["pattern"], text_lower, re.IGNORECASE):
            detected_flags.append({
                "condition": flag["condition"],
                "guidance": flag["guidance"]
            })
            
    is_emergency = len(detected_flags) > 0
    
    return {
        "is_emergency": is_emergency,
        "flags_detected": detected_flags,
        "emergency_alert": (
            "🚨 URGENT MEDICAL ATTENTION REQUIRED: The symptoms you reported may indicate a critical medical emergency. "
            "Do not wait for an online appointment. Please contact emergency services (Dial 108 or 112) or visit the nearest hospital casualty immediately."
            if is_emergency else None
        ),
        "emergency_helpline": "108 (National Ambulance) / 112 (National Emergency)" if is_emergency else None
    }
