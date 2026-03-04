export const API_URL = "http://localhost:8000";

export interface AnalyzeResponse {
    risk_score: number;
    risk_level: string;
    detected_symptoms: string[];
    predicted_condition?: string;
    explanation: string[];
    recommendation: string;
}

export const analyzeSymptoms = async (text: string, language: string = "en", age?: number): Promise<AnalyzeResponse> => {
    const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text, language, user_age: age }),
    });
    if (!response.ok) {
        throw new Error("Failed to analyze symptoms");
    }
    return response.json();
};
