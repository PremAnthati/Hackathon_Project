from backend.services.hybrid_triage_model import hybrid_clinical_triage_engine
import json

data = {
    "symptoms": [{"name": "headache", "severity": "moderate", "days": 2}],
    "age": 30,
    "existing_conditions": []
}

res = hybrid_clinical_triage_engine(data)
print(res)
