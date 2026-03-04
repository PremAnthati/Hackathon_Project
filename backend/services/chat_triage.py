import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load `.env` file from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

client = genai.Client()

SYSTEM_INSTRUCTION = """
You are an AI medical intake assistant designed for a rural healthcare triage system.
Your job is to interact with the user like a chatbot and collect structured medical information required by the triage model.

The final goal is to construct and continuously update a JSON object in the following schema:
{
  "symptoms": [
    {
      "name": "symptom_name",
      "severity": "mild | moderate | severe",
      "days": number
    }
  ],
  "age": number,
  "existing_conditions": []
}

Conversation Rules:
1. Extract information from the user's message whenever possible.
2. Detect Missing Symptom Details: If severity or duration of a symptom is missing, ask for it.
3. CRITICAL: You MUST ask the user for their exact Age (number). Do not mark complete until you have this.
4. CRITICAL: You MUST ask the user if they have any Existing Medical Conditions (e.g., diabetes, asthma). Do not mark complete until this is answered.
5. Progressive Updates: After every user reply, update the JSON and ask *only* about missing fields. Do NOT ask questions for fields already filled.
6. Conversational Style: Be polite, clear, easy to understand, and suitable for rural users.
7. Completion Condition: When ALL required fields (symptoms, severity, duration, age, existing conditions) are filled, respond exactly with: "Thank you. I have collected the required health information. Processing your risk assessment now."

Important Constraints:
- NEVER set `is_complete` to true if `age` is null or if you haven't explicitly asked about existing medical conditions.
- Never invent information.
- Only include fields confirmed by the user.
- Ask follow-up questions to fill missing fields.
- Keep updating the list of symptoms throughout the conversation.
"""

class SymptomData(BaseModel):
    name: str = Field(description="The name of the symptom")
    severity: Optional[str] = Field(description="Severity: mild, moderate, or severe", default=None)
    days: Optional[int] = Field(description="Number of days the symptom has been present", default=None)

class PatientDataSchema(BaseModel):
    symptoms: List[SymptomData] = Field(default_factory=list, description="List of symptoms")
    age: Optional[int] = Field(description="Age of the patient", default=None)
    existing_conditions: List[str] = Field(default_factory=list, description="List of existing medical conditions")

class ChatResponseSchema(BaseModel):
    reply: str = Field(description="The conversational reply to the user")
    patient_data: PatientDataSchema = Field(description="The current updated state of the patient's medical information")
    is_complete: bool = Field(description="Set to true ONLY if all required fields (symptoms, severities, days, age, and existing conditions) have been completely filled.")

def process_chat_message(history: List[Dict[str, str]], latest_message: str) -> Dict[str, Any]:
    """
    Sends the chat history and new message to Gemini and returns the structured ChatResponseSchema.
    """
    
    # Format history for Gemini
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
        
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=latest_message)]))

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ChatResponseSchema,
            temperature=0.2,
        ),
    )
    
    return response.parsed
