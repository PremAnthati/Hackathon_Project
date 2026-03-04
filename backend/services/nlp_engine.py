import re
from typing import List

# A more comprehensive rule-based extraction for ML integration
SYMPTOM_MAPPING = {
    "fever": ["fever", "high temperature", "hot", "high fever", "low-grade fever"],
    "chest_pain": ["chest pain", "pain in chest", "chest hurting", "heart hurting"],
    "difficulty_breathing": ["difficulty breathing", "breathless", "shortness of breath", "can't breathe"],
    "vomiting": ["vomiting", "throw up", "puking"],
    "severe_headache": ["severe headache", "head hurting bad", "migraine", "headache"],
    "dizziness": ["dizzy", "dizziness", "lightheaded", "faint"],
    "rash": ["rash", "rashes", "red spots"],
    "runny_nose": ["runny nose", "sniffles", "stuffy nose", "nasal discharge"],
    "swollen_lymph_nodes": ["swollen lymph nodes", "swollen glands", "neck glands"],
    "sore_throat": ["sore throat", "throat hurts", "scratchy throat"],
    "cough": ["cough", "coughing"],
    "diarrhea": ["diarrhea", "loose motion", "watery stool"],
    "fatigue": ["fatigue", "tiredness", "exhaustion", "feeling tired", "weak"],
    "headache": ["headache", "head hurts"],
    "loss_of_appetite": ["loss of appetite", "not hungry", "can't eat"],
    "abdominal_pain": ["abdominal pain", "stomach pain", "stomach cramps", "belly ache"],
    "body_aches": ["body aches", "muscle aches", "sore muscles"],
    "chills": ["chills", "shivering", "feeling cold"],
    "red_eyes": ["red eyes", "sore eyes", "watery eyes"]
}

def extract_symptoms(text: str) -> List[str]:
    text_lower = text.lower()
    detected = []
    
    for symptom_key, keywords in SYMPTOM_MAPPING.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                detected.append(symptom_key)
                break # Move to next symptom key once found
                
    return detected
