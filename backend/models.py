from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalyzeRequest(BaseModel):
    text: str
    language: str = "en"  # "en" or "te" (Telugu)
    user_age: Optional[int] = None
    patient_data: Optional[Dict[str, Any]] = None

class SymptomInfo(BaseModel):
    symptom_name: str
    is_present: bool

class AnalyzeResponse(BaseModel):
    risk_score: int
    risk_level: str
    detected_symptoms: List[str]
    possible_conditions: Optional[List[str]] = None
    explanation: List[str]
    recommendation: str
