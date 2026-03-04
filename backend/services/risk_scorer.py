from typing import List, Dict, Any

# Predefined weights as per requirements
SYMPTOM_WEIGHTS = {
    "fever": 20,
    "chest_pain": 35,
    "difficulty_breathing": 40,
    "vomiting": 10,
    "severe_headache": 15,
    "dizziness": 10
}

def compute_risk(detected_symptoms: List[str], age: int = None) -> Dict[str, Any]:
    score = 0
    selected_symptoms_names = []
    
    for sym in detected_symptoms:
        selected_symptoms_names.append(sym.replace("_", " ").title())
        if sym in SYMPTOM_WEIGHTS:
            score += SYMPTOM_WEIGHTS[sym]
        else:
            # Add a small baseline risk for other generic symptoms (configurable)
            score += 2
            
    # Age base risk adjustment (Bonus feature)
    if age and age > 65:
        score += 10 # Seniors have slightly higher baseline risk
        
    # Clamp to 0-100
    final_score = max(0, min(100, score))
    
    # Classification
    if final_score <= 25:
        level = "LOW"
        recommendation = "Self-care advice: Hydration, rest, and monitoring."
    elif final_score <= 50:
        level = "MODERATE"
        recommendation = "Recommend teleconsultation. Suggest contacting local health worker."
    elif final_score <= 75:
        level = "HIGH"
        recommendation = "Visit hospital within 24 hours."
    else:
        level = "CRITICAL"
        recommendation = "Emergency medical attention immediately!"

    return {
        "risk_score": final_score,
        "risk_level": level,
        "recommendation": recommendation,
        "detected_symptoms": selected_symptoms_names
    }
