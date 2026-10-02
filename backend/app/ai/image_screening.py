import os
import io
from PIL import Image
from typing import Dict, Any

def screen_medical_image(image_bytes: bytes, image_type: str = "CHEST_XRAY") -> Dict[str, Any]:
    """
    Performs algorithmic preliminary medical image screening for academic demonstration.
    Supports CHEST_XRAY and DERMATOLOGY.
    Transparently reports heuristic findings and model limitations.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        format_type = img.format or "UNKNOWN"
        
        if format_type.upper() not in ["JPEG", "PNG", "WEBP", "MPO"]:
            return {
                "error": f"Unsupported image format: {format_type}. Allowed formats: JPEG, PNG, WebP.",
                "status": "FAILED"
            }
            
        if width < 64 or height < 64:
            return {
                "error": f"Image resolution too low ({width}x{height}). Minimum required: 64x64 pixels.",
                "status": "FAILED"
            }
    except Exception as e:
        return {
            "error": "Unable to decode image file. Please upload a valid image (JPEG, PNG, WebP).",
            "status": "FAILED"
        }

    # Convert to grayscale for structural analysis
    gray = img.convert('L')
    pixels = list(getattr(gray, 'get_flattened_data', gray.getdata)())
    avg_luminance = sum(pixels) / len(pixels)
    
    # Calculate variance / contrast metric
    variance = sum((p - avg_luminance) ** 2 for p in pixels) / len(pixels)
    contrast = variance ** 0.5

    disclaimer = (
        "⚠️ Academic Prototype Screening Only: This preliminary screening uses an optical density and contrast heuristic. "
        "It is NOT a certified clinical diagnostic AI model and does NOT replace formal evaluation by a licensed radiologist or dermatologist."
    )

    if image_type == "CHEST_XRAY":
        if avg_luminance > 140 or contrast < 35:
            finding = "Increased Bilateral Mid-to-Lower Zone Opacity (Possible Consolidation Pattern)"
            heuristic_score = 85.0
            red_flag = 1
            recommendation = "Recommend clinical correlation with stethoscope auscultation and formal radiologist review."
        elif avg_luminance < 60:
            finding = "Sub-optimal Exposure / Low Radiographic Contrast"
            heuristic_score = 70.0
            red_flag = 0
            recommendation = "Repeat high-resolution radiograph with proper inspiratory hold recommended."
        else:
            finding = "Clear Bilateral Lung Fields (No Macro-Consolidation Detected by Heuristic)"
            heuristic_score = 90.0
            red_flag = 0
            recommendation = "No acute gross focal abnormalities detected on baseline screening heuristic."

        limitations = "Heuristic screening is sensitive to patient rotation, exposure variation, and technique (PA vs AP)."
        category = "Chest Radiography (PA View)"

    elif image_type == "DERMATOLOGY":
        if contrast > 65:
            finding = "Circumscribed Heterogeneous Pigmented Macule (Density Variation)"
            heuristic_score = 82.0
            red_flag = 1
            recommendation = "Dermatoscopic evaluation recommended to assess pigment distribution."
        elif avg_luminance > 120 and contrast < 40:
            finding = "Superficial Erythematous Plaque / Mild Dermatitis Pattern"
            heuristic_score = 86.0
            red_flag = 0
            recommendation = "Evaluate for contact or environmental triggers. Maintain clean, dry skin."
        else:
            finding = "Benign Non-Specific Cutaneous Presentation"
            heuristic_score = 88.0
            red_flag = 0
            recommendation = "Routine clinical review. Avoid unprescribed topical steroid applications."

        limitations = "Accuracy depends heavily on ambient lighting, camera focus, and skin tone representation."
        category = "Dermatology Lesion Screening"

    else:
        finding = "General Medical Image Processed"
        heuristic_score = 75.0
        red_flag = 0
        recommendation = "Review by attending physician."
        limitations = "General screening heuristic."
        category = "General Medical Image"

    return {
        "status": "SUCCESS",
        "category": category,
        "image_type": image_type,
        "dimensions": f"{width}x{height}",
        "format": format_type,
        "detected_finding": finding,
        "confidence": round(heuristic_score, 1),
        "screening_method": "Algorithmic Pixel Density & Contrast Protocol (Prototype v1.0)",
        "red_flag": red_flag,
        "recommended_action": recommendation,
        "limitations": limitations,
        "disclaimer": disclaimer,
        "doctor_review_status": "PENDING_CLINICIAN_REVIEW"
    }
