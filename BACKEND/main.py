from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prescription import check_prescription, extract_medications, check_drug_interactions
from typing import Dict, List, Optional

# Import gesture only if available (may fail on server without webcam)
try:
    from gesture import detect_gesture
except Exception as e:
    detect_gesture = None
    print(f"Warning: Gesture detection unavailable: {e}")

app = FastAPI(title="MedFusion Backend")

# Enable CORS for Streamlit Cloud and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (secure in production by listing specific URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Prescription(BaseModel):
    text: str

class PatientProfile(BaseModel):
    age: int
    blood_pressure: str
    temperature: float
    medical_history: List[str]
    allergies: List[str]

class DrugInteractionRequest(BaseModel):
    medications: List[str]
    patient_profile: PatientProfile

@app.get("/")
def root():
    return {"message": "MedFusion Backend Running"}

# Basic prescription verification API
@app.post("/verify_prescription")
def verify_prescription(data: Prescription):
    result = check_prescription(data.text)
    return {"input": data.text, "result": result}

class PrescriptionWithProfile(BaseModel):
    text: str
    patient_profile: PatientProfile

# Enhanced prescription verification with patient profile
@app.post("/verify_prescription_with_profile")
def verify_prescription_with_profile(data: PrescriptionWithProfile):
    profile_dict = {
        "age": data.patient_profile.age,
        "blood_pressure": data.patient_profile.blood_pressure,
        "temperature": data.patient_profile.temperature,
        "medical_history": data.patient_profile.medical_history,
        "allergies": data.patient_profile.allergies
    }
    result = check_prescription(data.text, profile_dict)
    return {"input": data.text, "patient_profile": profile_dict, "result": result}

# Drug interaction checking API
@app.post("/check_drug_interactions")
def check_drug_interactions_endpoint(data: DrugInteractionRequest):
    profile_dict = {
        "age": data.patient_profile.age,
        "blood_pressure": data.patient_profile.blood_pressure,
        "temperature": data.patient_profile.temperature,
        "medical_history": data.patient_profile.medical_history,
        "allergies": data.patient_profile.allergies
    }
    result = check_drug_interactions(data.medications, profile_dict)
    return {"medications": data.medications, "patient_profile": profile_dict, "interaction_analysis": result}

# Medication extraction API
@app.post("/extract_medications")
def extract_medications_endpoint(data: Prescription):
    medications = extract_medications(data.text)
    return {"input": data.text, "medications": medications}

# Gesture detection API
@app.get("/gesture_detect")
def gesture_detect():
    if detect_gesture is None:
        return {"error": "Gesture detection unavailable on this server", "gesture_detected": None}
    gesture = detect_gesture()
    return {"gesture_detected": gesture}
