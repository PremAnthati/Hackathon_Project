import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 1. REAL DATASET LOADER, PRE-PROCESSING & ML TRAINING
# ==========================================

TRAINING_DATA_PATH = r"/Users/premanthati/Desktop/Hackathon/training_data.csv"

def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans up raw datasets issues like trailing underscores, weird spacings, and unneeded columns."""
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Strip whitespace from string values in the dataset
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    
    # Some datasets contain a trailing unnamed column full of NaNs. Discard it.
    df = df.dropna(axis=1, how='all')
    
    # Replace weird intra-string spaces in the symptom columns (e.g. 'foul_smell_of urine' -> 'foul_smell_of_urine')
    clean_columns = {}
    for col in df.columns:
        # Lowercase, replace internal spaces with underscores, and strip edges
        clean_name = col.lower().strip().replace('  ', ' ').replace(' ', '_')
        
        # Specific dataset typo corrections from raw inspection
        clean_name = clean_name.replace("foul_smell_of_urine", "foul_smell_of_urine")
        clean_name = clean_name.replace("dischromic__patches", "dischromic_patches")
        clean_name = clean_name.replace("spotting__urination", "spotting_urination")
        clean_name = clean_name.replace("toxic_look_(typhos)", "toxic_look_typhos")
        
        clean_columns[col] = clean_name

    df = df.rename(columns=clean_columns)
    
    return df

def generate_dynamic_clinical_rules(feature_columns: List[str]) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Parses the 132 symptom columns and assigns a clinical baseline score 
    and a critical override score based on keyword detection.
    """
    base_scores = {}
    critical_symptoms = {}
    
    # Heuristics to identify severe keywords in the 132 columns
    critical_keywords = ['bleeding', 'coma', 'breathlessness', 'chest_pain', 'failure', 'paralysis']
    high_keywords = ['fever', 'pain', 'vomiting', 'vision', 'weight_loss', 'blood', 'sensorium']
    
    for symptom in feature_columns:
        score = 5.0 # Low-risk baseline default
        
        if any(keyword in symptom for keyword in critical_keywords):
            score = 15.0
            critical_symptoms[symptom] = 30.0 # Huge bonus for immediate attention
            
        elif any(keyword in symptom for keyword in high_keywords):
            score = 10.0
            
        base_scores[symptom] = score
        
    return base_scores, critical_symptoms


def train_disease_classifier():
    """Trains a Random Forest model on the real training_data.csv dataset."""
    print("[SYSTEM] Loading real dataset, preprocessing, and training ML...")
    try:
        raw_df = pd.read_csv(TRAINING_DATA_PATH)
        df = preprocess_dataset(raw_df)
        
        # Features and Targets
        X = df.drop(columns=["prognosis"])
        y = df["prognosis"]
        
        # Train Random Forest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        print("[SYSTEM] ML Model trained successfully on pre-processed data.\n")
        
        # Generate Dynamic Rule logic maps based exactly on dataset features
        features_list = X.columns.tolist()
        base_rules, crit_rules = generate_dynamic_clinical_rules(features_list)
        
        return model, features_list, model.classes_, base_rules, crit_rules
        
    except FileNotFoundError:
        print("[ERROR] Dataset not found. Please ensure training_data.csv is in Downloads.")
        return None, [], [], {}, {}

# Initialize system globally
ML_MODEL, FEATURE_COLS, TARGET_CLASSES, SYMPTOM_BASE_SCORES, CRITICAL_SYMPTOMS = train_disease_classifier()


# ==========================================
# 2. CONFIGURATION & RULE-BASED SCORING ENGINE
# ==========================================

SEVERITY_MULTIPLIERS = {
    "mild": 1.0,
    "moderate": 1.5,
    "severe": 2.0
}

HIGH_RISK_CONDITIONS = {
    "diabetes": 15.0,
    "hypertension": 15.0,
    "heart_disease": 25.0,
    "copd": 20.0,
    "asthma": 10.0
}

def calculate_duration_score(symptom_name: str, days: int) -> Tuple[float, str]:
    if days >= 7:
        return 15.0, f"{symptom_name.replace('_', ' ')} lasting {days} days suggests prolonged illness or serious infection"
    elif days >= 3:
        return 10.0, f"{symptom_name.replace('_', ' ')} lasting several days indicates infection"
    return 0.0, ""

def calculate_patient_risk_factor(age: int, conditions: List[str]) -> Tuple[float, List[str]]:
    score = 0.0
    explanations = []
    
    if age >= 60:
        score += 12.0
        explanations.append("age above 60 increases complication risk")
    elif age > 50:
        score += 8.0
        explanations.append(f"age {age} moderately increases complication risk")
        
    for condition in conditions:
        cond_lower = condition.lower()
        if cond_lower in HIGH_RISK_CONDITIONS:
            score += HIGH_RISK_CONDITIONS[cond_lower]
            explanations.append(f"existing condition '{condition}' increases baseline risk")
            
    return score, explanations

def get_critical_symptom_bonus(symptom_name: str) -> Tuple[float, str]:
    bonus = CRITICAL_SYMPTOMS.get(symptom_name, 0.0)
    explanation = ""
    if bonus > 0:
        name_clean = symptom_name.replace("_", " ")
        explanation = f"{name_clean} is a critical symptom indicating severe distress"
    return bonus, explanation

def standardize_symptom_name(name: str) -> str:
    """Takes user JSON strings and force maps them to the exact pre-processed dataset names."""
    name = name.lower().strip().replace(" ", "_")
    # Quick common synonyms mapped to exact dataset column strings
    synonyms = {
        "breathing_difficulty": "breathlessness",
        "muscle_ache": "muscle_pain",
        "tummy_ache": "stomach_pain",
        "fever": "high_fever" # Assumes standard high fever if severe
    }
    return synonyms.get(name, name)

def analyze_symptom_rules(symptom_data: Dict[str, Any]) -> Tuple[float, List[str], str]:
    """Evaluates rule-based risk score for a single symptom using Dynamic rules."""
    raw_name = symptom_data.get("name", "")
    
    # Formulate against dataset terminology
    mapped_name = standardize_symptom_name(raw_name)
    
    severity = symptom_data.get("severity", "mild").lower()
    days = symptom_data.get("days", 0)
    
    # Dynamic Database matching OR fallback to 5.0
    base_score = SYMPTOM_BASE_SCORES.get(mapped_name, 5.0)
    multiplier = SEVERITY_MULTIPLIERS.get(severity, 1.0)
    symptom_score = base_score * multiplier
    
    # If the user put "severe fever" we override mapped dimension if required
    if raw_name == "fever" and severity == "mild":
        mapped_name = "mild_fever"
        base_score = SYMPTOM_BASE_SCORES.get(mapped_name, 5.0)
        symptom_score = base_score * multiplier
        
    duration_score, dur_expl = calculate_duration_score(mapped_name, days)
    critical_bonus, crit_expl = get_critical_symptom_bonus(mapped_name)
    
    total_score = symptom_score + duration_score + critical_bonus
    
    explanations = []
    if dur_expl: explanations.append(dur_expl)
    if crit_expl: explanations.append(crit_expl)
        
    return total_score, explanations, mapped_name

def determine_triage_level(score: int) -> Tuple[str, str]:
    if score <= 25:
        return "Low", "Self care"
    elif score <= 50:
        return "Moderate", "Teleconsultation"
    elif score <= 75:
        return "High", "Visit hospital within 24 hours"
    else:
        return "Critical", "Emergency care"

# ==========================================
# 3. HYBRID PIPELINE
# ==========================================

def extract_ml_features(resolved_symptoms: List[str]) -> pd.DataFrame:
    """Converts the internally mapped resolved symptom list into the 132-dim feature vector."""
    features = {col: 0 for col in FEATURE_COLS}
    for symp in resolved_symptoms:
        if symp in features:
            features[symp] = 1

    return pd.DataFrame([features])

def predict_conditions_ml(resolved_symptoms: List[str]) -> List[str]:
    """Uses the trained Random Forest model to predict likely conditions based on standardized features."""
    if not ML_MODEL:
        return ["ML Model Unavailable"]
        
    features_df = extract_ml_features(resolved_symptoms)
    prediction_proba = ML_MODEL.predict_proba(features_df)[0]
    
    predicted_labels = []
    for idx, prob in enumerate(prediction_proba):
        if prob > 0.10:  # 10% threshold probability flag
            predicted_labels.append(TARGET_CLASSES[idx])
            
    return predicted_labels

def hybrid_clinical_triage_engine(patient_data: Dict[str, Any]) -> str:
    """
    Main triage coordinator using Dynamic Dataset Features + Rule-based logic for risk,
    and Machine Learning for intelligent condition prediction.
    """
    symptoms = patient_data.get("symptoms", [])
    age = patient_data.get("age", 0)
    conditions = patient_data.get("existing_conditions", [])
    
    total_risk_score = 0.0
    explanations = []
    
    # 1. Standardize Patient Risks
    patient_score, patient_expls = calculate_patient_risk_factor(age, conditions)
    total_risk_score += patient_score
    explanations.extend(patient_expls)
    
    # 2. Evaluate dynamically mapped symptoms
    resolved_symptom_list = []
    
    for symptom_obj in symptoms:
        symp_score, symp_expls, mapped_feature_name = analyze_symptom_rules(symptom_obj)
        total_risk_score += symp_score
        explanations.extend(symp_expls)
        resolved_symptom_list.append(mapped_feature_name)
        
    final_score = int(min(max(total_risk_score, 0), 100))
    risk_level, recommendation = determine_triage_level(final_score)
    
    # 3. Machine Learning Disease Suggestion 
    # (Passed normalized list so it 1:1 tracks database)
    predicted_conditions = predict_conditions_ml(resolved_symptom_list)
    
    # 4. Standardized Standardized Output Structure
    result = {
        "risk_score": final_score,
        "risk_level": risk_level,
        "possible_conditions": predicted_conditions,
        "recommendation": recommendation,
        "explanations": explanations,
        "_internal_mapped_features": resolved_symptom_list # Helpful debug output
    }
    
    return json.dumps(result, indent=2)

# --- Example Runner ---
if __name__ == "__main__":
    patient_json = '''{
        "symptoms":[
            {"name": "fever", "severity": "moderate", "days": 3},
            {"name": "cough", "severity": "moderate", "days": 2},
            {"name": "breathing_difficulty", "severity": "severe", "days": 1}
        ],
        "age": 45,
        "existing_conditions":["diabetes"]
    }'''
    
    input_data = json.loads(patient_json)
    
    print("--- Dynamic Dataset Hybrid Clinical Assessment ---")
    print("\n[INPUT DATA]:")
    print(json.dumps(input_data, indent=2))
    
    # Process
    output_data_json = hybrid_clinical_triage_engine(input_data)
    
    print("\n[TRIAGE OUTPUT]:")
    print(output_data_json)
