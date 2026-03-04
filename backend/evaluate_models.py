import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import os
import time

TRAIN_DATA_PATH = os.path.join(os.path.dirname(__file__), '../training_data.csv')
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), '../test_data.csv')

def evaluate_models():
    print(f"Loading data...")
    df_train = pd.read_csv(TRAIN_DATA_PATH)
    df_test = pd.read_csv(TEST_DATA_PATH)
    
    if 'Unnamed: 133' in df_train.columns:
        df_train = df_train.drop('Unnamed: 133', axis=1)
    if 'Unnamed: 133' in df_test.columns:
        df_test = df_test.drop('Unnamed: 133', axis=1)
        
    y_train = df_train['prognosis']
    X_train = df_train.drop('prognosis', axis=1)
    
    y_test = df_test['prognosis']
    X_test = df_test.drop('prognosis', axis=1)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Support Vector Machine (SVC)": SVC(kernel='linear', random_state=42)
    }

    results = []

    for name, model in models.items():
        print(f"Training {name}...")
        start_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        results.append({
            "Model": name,
            "Accuracy": accuracy * 100,
            "Training Time (s)": training_time
        })
        print(f"{name} Accuracy: {accuracy * 100:.2f}%")

    print("\n--- Summary ---")
    results_df = pd.DataFrame(results).sort_values(by="Accuracy", ascending=False)
    print(results_df.to_string(index=False))
    
    best_model = results_df.iloc[0]['Model']
    print(f"\nBest model based on test accuracy is: {best_model}")

if __name__ == "__main__":
    evaluate_models()
