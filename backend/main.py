from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import AnalyzeRequest, AnalyzeResponse
from services.nlp_engine import extract_symptoms
from services.translator import translate_text
import json

# Import the new hybrid model
from services.hybrid_triage_model import hybrid_clinical_triage_engine

# Initialize FastAPI app
app = FastAPI(title="AI Healthcare Triage API", version="1.0.0")

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_symptoms(req: AnalyzeRequest):
    original_text = req.text
    lang = req.language
    
    # 1. Translate string input if not English
    if lang != "en":
        english_text = translate_text(original_text, src=lang, dest="en")
    else:
        english_text = original_text
        
    # 2. Extract Symptoms from English Text
    detected_symptoms = extract_symptoms(english_text)
    
    patient_data = {
        "symptoms": detected_symptoms,
        "age": req.user_age or 0,
        "existing_conditions": []
    }
    
    # 4. Compute Risk & Classification via Hybrid Engine
    hybrid_result_str = hybrid_clinical_triage_engine(patient_data)
    result = json.loads(hybrid_result_str)

    possible_conditions = result.get("possible_conditions", [])
    explanations = result.get("explanations", [])
    
    if not explanations:
        explanations = ["No severe symptoms detected."]
        
    if possible_conditions:
        explanations.append(f"AI Model indicates possible traits of: {', '.join(possible_conditions)}")

    # 5. Translate Final Response back if needed
    recommendation = result.get("recommendation", "")
    if lang != "en":
        # Translate explanation & recommendation
        explanations = [translate_text(e, src="en", dest=lang) for e in explanations]
        recommendation = translate_text(recommendation, src="en", dest=lang)
        possible_conditions = [translate_text(c, src="en", dest=lang) for c in possible_conditions]
            
    return AnalyzeResponse(
        risk_score=result.get("risk_score", 0),
        risk_level=result.get("risk_level", "LOW"),
        detected_symptoms=result.get("detected_symptoms", []),
        possible_conditions=possible_conditions,
        explanation=explanations,
        recommendation=recommendation
    )

@app.get("/health")
def health():
    return {"status": "ok"}
