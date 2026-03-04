from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import AnalyzeRequest, AnalyzeResponse
from services.nlp_engine import extract_symptoms
from services.risk_scorer import compute_risk
from services.translator import translate_text
from services.ml_predictor import predict_disease

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
    
    # 3. Compute Risk & Classification
    result = compute_risk(detected_symptoms, age=req.user_age)
    
    # 4. Predict likely disease if we have symptoms
    predicted_condition = None
    if result["detected_symptoms"]:
        raw_prediction = predict_disease(result["detected_symptoms"])
        if raw_prediction:
            predicted_condition = raw_prediction

    # 5. Generate Explanations and Recommendation
    explanations = [f"{sym} increases risk." for sym in result["detected_symptoms"]]
    if not explanations:
        explanations = ["No severe symptoms detected."]
        
    if predicted_condition:
        explanations.append(f"AI Model indicates possible traits of: {predicted_condition}")

    # 6. Translate Final Response back if needed
    recommendation = result["recommendation"]
    if lang != "en":
        # Translate explanation & recommendation
        explanations = [translate_text(e, src="en", dest=lang) for e in explanations]
        recommendation = translate_text(recommendation, src="en", dest=lang)
        if predicted_condition:
            predicted_condition = translate_text(predicted_condition, src="en", dest=lang)
            
    return AnalyzeResponse(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        detected_symptoms=result["detected_symptoms"],
        predicted_condition=predicted_condition,
        explanation=explanations,
        recommendation=recommendation
    )

@app.get("/health")
def health():
    return {"status": "ok"}
