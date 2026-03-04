from fastapi.testclient import TestClient
from main import app
from services.nlp_engine import extract_symptoms
from services.risk_scorer import compute_risk

client = TestClient(app)

def test_nlp_extraction():
    symptoms = extract_symptoms("I have a severe headache and I'm feeling dizzy")
    assert "severe_headache" in symptoms
    assert "dizziness" in symptoms

def test_risk_scorer():
    # Fever (20) + Chest Pain (35) = 55 (HIGH risk)
    result = compute_risk(["fever", "chest_pain"])
    assert result["risk_score"] == 55
    assert result["risk_level"] == "HIGH"

def test_analyze_endpoint():
    response = client.post("/analyze", json={
        "text": "I can't breathe and my chest hurts",
        "language": "en"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["HIGH", "CRITICAL"] # 40 + 35 = 75 (HIGH/CRITICAL borderline)
    assert len(data["detected_symptoms"]) > 0

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
