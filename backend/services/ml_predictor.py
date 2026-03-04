import joblib
import os
import pandas as pd
import numpy as np
from typing import List, Optional

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')
MODEL_PATH = os.path.join(MODEL_DIR, 'disease_predictor.pkl')
SYMPTOMS_PATH = os.path.join(MODEL_DIR, 'symptoms.pkl')

# Global variables for caching
clf = None
feature_columns = None

def load_models():
    global clf, feature_columns
    if clf is None or feature_columns is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(SYMPTOMS_PATH):
            clf = joblib.load(MODEL_PATH)
            feature_columns = joblib.load(SYMPTOMS_PATH)
            print("Successfully loaded ML model and feature columns.")
        else:
            print(f"WARNING: Models not found in {MODEL_DIR}. Run train_model.py first.")

def predict_disease(symptoms: List[str]) -> Optional[str]:
    load_models()
    if clf is None or feature_columns is None or not symptoms:
        return None
    
    # Preprocess incoming symptoms exactly as dataset columns are defined
    # Datasets columns usually have underscores instead of spaces, e.g. "chest_pain"
    processed_symptoms = [sym.lower().strip().replace(' ', '_') for sym in symptoms]
    
    try:
        # Create an empty DataFrame with the exact same columns as the training data
        X_input = pd.DataFrame(np.zeros((1, len(feature_columns))), columns=feature_columns)
        
        # Set the corresponding symptom columns to 1
        for sym in processed_symptoms:
            if sym in X_input.columns:
                X_input.loc[0, sym] = 1
            # Try a direct match if the underscore mapping didn't work
            elif sym.replace('_', ' ') in X_input.columns:
                 X_input.loc[0, sym.replace('_', ' ')] = 1
        
        # Predict the disease
        prediction = clf.predict(X_input)
        
        return str(prediction[0]) if len(prediction) > 0 else None
    except Exception as e:
        print(f"Error predicting disease: {e}")
        return None
