import re
from typing import List

# A more comprehensive rule-based extraction tailored to training_data.csv features
SYMPTOM_MAPPING = {
    # Match these names exactly with columns in the dataset where possible
    "high_fever": ["fever", "high temperature", "hot", "high fever", "low-grade fever"],
    "chest_pain": ["chest pain", "pain in chest", "chest hurting", "heart hurting"],
    "breathlessness": ["breathing difficulty", "difficulty breathing", "breathless", "shortness of breath", "can't breathe"],
    "vomiting": ["vomiting", "throw up", "puking"],
    "headache": ["severe headache", "head hurting bad", "migraine", "headache", "head hurts"],
    "dizziness": ["dizzy", "dizziness", "lightheaded", "faint"],
    "skin_rash": ["rash", "rashes", "red spots", "skin rash"],
    "runny_nose": ["runny nose", "sniffles", "stuffy nose", "nasal discharge"],
    "swelled_lymph_nodes": ["swollen lymph nodes", "swollen glands", "neck glands"],
    "throat_irritation": ["sore throat", "throat hurts", "scratchy throat", "throat irritation"],
    "cough": ["cough", "coughing"],
    "diarrhoea": ["diarrhea", "loose motion", "watery stool", "diarrhoea"],
    "fatigue": ["fatigue", "tiredness", "exhaustion", "feeling tired", "weak"],
    "loss_of_appetite": ["loss of appetite", "not hungry", "can't eat"],
    "abdominal_pain": ["abdominal pain", "stomach pain", "stomach cramps", "belly ache"],
    "muscle_pain": ["body aches", "muscle aches", "sore muscles", "muscle pain"],
    "chills": ["chills", "shivering", "feeling cold"],
    "redness_of_eyes": ["red eyes", "sore eyes", "watery eyes", "redness of eyes"]
}

from typing import List, Dict, Any

def extract_symptoms(text: str) -> List[Dict[str, Any]]:
    text_lower = text.lower()
    detected = []
    
    for symptom_key, keywords in SYMPTOM_MAPPING.items():
        for keyword in keywords:
            # Find the keyword match
            match = re.search(r'\b' + re.escape(keyword) + r'\b', text_lower)
            if match:
                end_idx = match.end()
                
                # Check for "since X days" or "for X days" up to 30 characters after the symptom
                context_after = text_lower[end_idx:end_idx+30]
                days_match = re.search(r'(?:since|for|lasting)\s+(\d+)\s+days?', context_after)
                
                days = 1
                if days_match:
                    try:
                        days = int(days_match.group(1))
                    except ValueError:
                        pass
                        
                detected.append({
                    "name": symptom_key,
                    "days": days,
                    "severity": "moderate" # Default placeholder
                })
                break # Move to next symptom key once found
                
    return detected
