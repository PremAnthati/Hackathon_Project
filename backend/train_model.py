import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import os

# Define path for dataset and output model
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Define path for dataset and output model
TRAIN_DATA_PATH = os.path.join(os.path.dirname(__file__), '../training_data.csv')
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), '../test_data.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'disease_predictor.pkl')
SYMPTOMS_PATH = os.path.join(MODEL_DIR, 'symptoms.pkl')

def train_model():
    print(f"Loading training data from {TRAIN_DATA_PATH}...")
    df_train = pd.read_csv(TRAIN_DATA_PATH)
    
    print(f"Loading test data from {TEST_DATA_PATH}...")
    df_test = pd.read_csv(TEST_DATA_PATH)
    
    # Drop empty trailing column if it exists
    if 'Unnamed: 133' in df_train.columns:
        df_train = df_train.drop('Unnamed: 133', axis=1)
    if 'Unnamed: 133' in df_test.columns:
        df_test = df_test.drop('Unnamed: 133', axis=1)
        
    y_train = df_train['prognosis']
    X_train = df_train.drop('prognosis', axis=1)
    
    y_test = df_test['prognosis']
    X_test = df_test.drop('prognosis', axis=1)
    
    print(f"Features: {len(X_train.columns)}")
    print(f"Number of training samples: {len(X_train)}")
    print(f"Number of test samples: {len(X_test)}")

    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate the model
    score = clf.score(X_test, y_test)
    print(f"Test Accuracy: {score * 100:.2f}%")

    # Ensure model directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Saving model to {MODEL_DIR}...")
    joblib.dump(clf, MODEL_PATH)
    # Save the feature columns so the predictor knows the exact input shape and order
    joblib.dump(list(X_train.columns), SYMPTOMS_PATH)
    
    # Remove old mlb.pkl if it exists to avoid confusion
    old_mlb_path = os.path.join(MODEL_DIR, 'mlb.pkl')
    if os.path.exists(old_mlb_path):
        os.remove(old_mlb_path)
    
    print("Training complete!")

if __name__ == "__main__":
    train_model()
