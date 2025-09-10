import os
import requests
from dotenv import load_dotenv
import json
from typing import Dict, List, Tuple

# Load Hugging Face API key
load_dotenv()
API_KEY = os.getenv("HUGGING_FACE_API_KEY", "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")

# Validate API key format
if not API_KEY.startswith("hf_"):
    API_KEY = "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"

# Hugging Face Inference API (you can change model)
API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Drug Interaction Database
DRUG_INTERACTIONS = {
    "paracetamol": {
        "interactions": {
            "warfarin": {"severity": "moderate", "effect": "Increased bleeding risk", "recommendation": "Monitor INR closely"},
            "alcohol": {"severity": "high", "effect": "Liver damage", "recommendation": "Avoid alcohol completely"},
            "aspirin": {"severity": "moderate", "effect": "Increased bleeding risk", "recommendation": "Use with caution"}
        },
        "contraindications": ["liver_disease", "alcoholism"],
        "alternatives": ["ibuprofen", "naproxen"]
    },
    "ibuprofen": {
        "interactions": {
            "aspirin": {"severity": "high", "effect": "Increased bleeding risk", "recommendation": "Avoid combination"},
            "warfarin": {"severity": "high", "effect": "Increased bleeding risk", "recommendation": "Monitor INR closely"},
            "lithium": {"severity": "moderate", "effect": "Increased lithium levels", "recommendation": "Monitor lithium levels"}
        },
        "contraindications": ["heart_disease", "stomach_ulcer", "kidney_disease"],
        "alternatives": ["paracetamol", "naproxen"]
    },
    "aspirin": {
        "interactions": {
            "warfarin": {"severity": "high", "effect": "Severe bleeding risk", "recommendation": "Avoid combination"},
            "ibuprofen": {"severity": "high", "effect": "Increased bleeding risk", "recommendation": "Avoid combination"},
            "methotrexate": {"severity": "moderate", "effect": "Increased methotrexate toxicity", "recommendation": "Monitor closely"}
        },
        "contraindications": ["bleeding_disorder", "stomach_ulcer", "asthma"],
        "alternatives": ["paracetamol", "acetaminophen"]
    },
    "insulin": {
        "interactions": {
            "alcohol": {"severity": "high", "effect": "Hypoglycemia risk", "recommendation": "Monitor blood sugar closely"},
            "beta_blockers": {"severity": "moderate", "effect": "Masked hypoglycemia symptoms", "recommendation": "Monitor blood sugar frequently"}
        },
        "contraindications": ["hypoglycemia", "allergy"],
        "alternatives": ["metformin", "glipizide"]
    },
    "metformin": {
        "interactions": {
            "alcohol": {"severity": "high", "effect": "Lactic acidosis risk", "recommendation": "Avoid alcohol"},
            "contrast_dye": {"severity": "high", "effect": "Kidney damage", "recommendation": "Stop 48 hours before procedure"}
        },
        "contraindications": ["kidney_disease", "liver_disease", "heart_failure"],
        "alternatives": ["insulin", "glipizide"]
    }
}

# Patient Profile Requirements
PATIENT_PROFILE_FIELDS = ["age", "blood_pressure", "temperature", "medical_history", "allergies"]

def extract_medications(text: str) -> List[str]:
    """Extract medication names from text"""
    text_lower = text.lower()
    medications = []
    
    # Common medication patterns
    med_patterns = [
        "paracetamol", "acetaminophen", "ibuprofen", "aspirin", "naproxen",
        "insulin", "metformin", "glipizide", "warfarin", "lithium",
        "methotrexate", "beta_blockers", "alcohol"
    ]
    
    for med in med_patterns:
        if med in text_lower:
            medications.append(med)
    
    return medications

def check_drug_interactions(medications: List[str], patient_profile: Dict) -> Dict:
    """Check for drug interactions and patient-specific risks with detailed analysis"""
    results = {
        "interactions": [],
        "contraindications": [],
        "alternatives": [],
        "risk_level": "low",
        "recommendations": [],
        "detailed_analysis": {},
        "safety_score": 100,
        "monitoring_required": [],
        "dosage_adjustments": [],
        "timing_considerations": [],
        "side_effects_watch": []
    }
    
    # Detailed medication analysis
    results["detailed_analysis"]["medications_found"] = len(medications)
    results["detailed_analysis"]["medication_list"] = medications
    
    # Check pairwise interactions with detailed analysis
    interaction_count = 0
    for i, med1 in enumerate(medications):
        for med2 in medications[i+1:]:
            if med1 in DRUG_INTERACTIONS and med2 in DRUG_INTERACTIONS[med1]["interactions"]:
                interaction = DRUG_INTERACTIONS[med1]["interactions"][med2]
                interaction_count += 1
                
                # Calculate safety score impact
                if interaction["severity"] == "high":
                    results["safety_score"] -= 40
                elif interaction["severity"] == "moderate":
                    results["safety_score"] -= 20
                else:
                    results["safety_score"] -= 10
                
                detailed_interaction = {
                    "drugs": f"{med1} + {med2}",
                    "severity": interaction["severity"],
                    "effect": interaction["effect"],
                    "recommendation": interaction["recommendation"],
                    "mechanism": get_interaction_mechanism(med1, med2),
                    "onset_time": get_interaction_onset(med1, med2),
                    "monitoring_needed": get_monitoring_requirements(med1, med2),
                    "alternative_timing": get_alternative_timing(med1, med2)
                }
                
                results["interactions"].append(detailed_interaction)
                
                # Add monitoring requirements
                if detailed_interaction["monitoring_needed"]:
                    results["monitoring_required"].extend(detailed_interaction["monitoring_needed"])
                
                # Update risk level
                if interaction["severity"] == "high":
                    results["risk_level"] = "high"
                elif interaction["severity"] == "moderate" and results["risk_level"] != "high":
                    results["risk_level"] = "moderate"
    
    results["detailed_analysis"]["interaction_count"] = interaction_count
    
    # Check contraindications with detailed analysis
    contraindication_count = 0
    for med in medications:
        if med in DRUG_INTERACTIONS:
            contraindications = DRUG_INTERACTIONS[med]["contraindications"]
            for condition in contraindications:
                if condition in patient_profile.get("medical_history", []):
                    contraindication_count += 1
                    results["safety_score"] -= 50  # High penalty for contraindications
                    
                    detailed_contraindication = {
                        "drug": med,
                        "condition": condition,
                        "risk": "high",
                        "explanation": get_contraindication_explanation(med, condition),
                        "alternative_approach": get_alternative_approach(med, condition),
                        "monitoring_required": get_contraindication_monitoring(med, condition)
                    }
                    
                    results["contraindications"].append(detailed_contraindication)
                    results["risk_level"] = "high"
    
    results["detailed_analysis"]["contraindication_count"] = contraindication_count
    
    # Suggest alternatives with detailed information
    for med in medications:
        if med in DRUG_INTERACTIONS:
            alternatives = DRUG_INTERACTIONS[med]["alternatives"]
            for alt in alternatives:
                results["alternatives"].append({
                    "original": med,
                    "alternative": alt,
                    "reason": get_alternative_reason(med, alt),
                    "dosage_equivalent": get_dosage_equivalent(med, alt),
                    "considerations": get_alternative_considerations(med, alt)
                })
    
    # Generate comprehensive recommendations based on patient profile
    age = patient_profile.get("age", 0)
    bp = patient_profile.get("blood_pressure", "normal")
    temp = patient_profile.get("temperature", 98.6)
    medical_history = patient_profile.get("medical_history", [])
    allergies = patient_profile.get("allergies", [])
    
    # Age-based recommendations
    if age > 65:
        results["recommendations"].append({
            "category": "Age",
            "message": "⚠️ Elderly patient - reduce dosages and monitor closely",
            "details": "Patients over 65 may have reduced kidney/liver function, requiring lower doses",
            "action": "Start with 50-75% of normal adult dose, monitor for side effects"
        })
        results["dosage_adjustments"].append("Reduce all dosages by 25-50% for elderly patient")
        results["safety_score"] -= 10
    
    if age < 18:
        results["recommendations"].append({
            "category": "Age",
            "message": "👶 Pediatric patient - use age-appropriate dosing",
            "details": "Children metabolize medications differently than adults",
            "action": "Use pediatric dosing charts and weight-based calculations"
        })
        results["safety_score"] -= 5
    
    # Blood pressure considerations
    if bp == "high":
        results["recommendations"].append({
            "category": "Cardiovascular",
            "message": "⚠️ High blood pressure - avoid NSAIDs, prefer paracetamol",
            "details": "NSAIDs can increase blood pressure and interfere with antihypertensive medications",
            "action": "Use paracetamol instead of ibuprofen/aspirin for pain relief"
        })
        results["safety_score"] -= 15
    
    if bp == "low":
        results["recommendations"].append({
            "category": "Cardiovascular",
            "message": "⚠️ Low blood pressure - monitor for dizziness",
            "details": "Some medications can further lower blood pressure",
            "action": "Monitor blood pressure regularly, avoid sudden position changes"
        })
        results["safety_score"] -= 5
    
    # Temperature considerations
    if temp > 100.4:
        results["recommendations"].append({
            "category": "Fever",
            "message": "🌡️ Fever present - consider antipyretics, monitor temperature",
            "details": "Fever may indicate infection requiring specific treatment",
            "action": "Use antipyretics, monitor temperature every 4 hours, seek medical attention if fever persists"
        })
        results["monitoring_required"].append("Temperature monitoring every 4 hours")
        results["safety_score"] -= 5
    
    # Medical history considerations
    if "diabetes" in medical_history:
        results["recommendations"].append({
            "category": "Diabetes",
            "message": "🍯 Diabetes present - monitor blood sugar levels",
            "details": "Some medications can affect blood sugar control",
            "action": "Monitor blood glucose more frequently, adjust diabetes medications if needed"
        })
        results["monitoring_required"].append("Blood glucose monitoring")
        results["safety_score"] -= 10
    
    if "liver_disease" in medical_history:
        results["recommendations"].append({
            "category": "Liver",
            "message": "⚠️ Liver disease - avoid hepatotoxic medications",
            "details": "Liver function may be impaired, affecting medication metabolism",
            "action": "Avoid paracetamol, use lower doses, monitor liver function"
        })
        results["safety_score"] -= 20
    
    if "kidney_disease" in medical_history:
        results["recommendations"].append({
            "category": "Kidney",
            "message": "⚠️ Kidney disease - adjust dosages for renal function",
            "details": "Reduced kidney function affects medication clearance",
            "action": "Use lower doses, avoid nephrotoxic medications, monitor kidney function"
        })
        results["safety_score"] -= 20
    
    # Allergy considerations
    if allergies:
        results["recommendations"].append({
            "category": "Allergies",
            "message": f"⚠️ Allergies present: {', '.join(allergies)}",
            "details": "Avoid medications that may cause allergic reactions",
            "action": "Check all medications for allergen content, have emergency medications ready"
        })
        results["safety_score"] -= 15
    
    # Timing considerations
    results["timing_considerations"] = get_timing_recommendations(medications)
    
    # Side effects to watch
    results["side_effects_watch"] = get_side_effects_to_watch(medications, patient_profile)
    
    # Nutritional recommendations
    results["nutritional_guidance"] = get_nutritional_recommendations(medications, patient_profile)
    
    # Lifestyle recommendations
    results["lifestyle_guidance"] = get_lifestyle_recommendations(medications, patient_profile)
    
    # Ensure safety score doesn't go below 0
    results["safety_score"] = max(0, results["safety_score"])
    
    return results

def get_interaction_mechanism(med1: str, med2: str) -> str:
    """Get detailed mechanism of drug interaction"""
    mechanisms = {
        ("paracetamol", "alcohol"): "Both are metabolized by liver enzymes, causing increased liver toxicity",
        ("aspirin", "ibuprofen"): "Both inhibit COX enzymes, increasing bleeding risk",
        ("warfarin", "aspirin"): "Both affect blood clotting, increasing bleeding risk",
        ("insulin", "alcohol"): "Alcohol can cause hypoglycemia by inhibiting glucose production"
    }
    return mechanisms.get((med1, med2), "Unknown mechanism of interaction")

def get_interaction_onset(med1: str, med2: str) -> str:
    """Get expected onset time of interaction"""
    onsets = {
        ("paracetamol", "alcohol"): "2-4 hours after consumption",
        ("aspirin", "ibuprofen"): "Within 1-2 hours",
        ("warfarin", "aspirin"): "Within 24-48 hours",
        ("insulin", "alcohol"): "Within 30 minutes to 2 hours"
    }
    return onsets.get((med1, med2), "Variable onset time")

def get_monitoring_requirements(med1: str, med2: str) -> List[str]:
    """Get specific monitoring requirements for interaction"""
    monitoring = {
        ("paracetamol", "alcohol"): ["Liver function tests", "Monitor for jaundice"],
        ("aspirin", "ibuprofen"): ["Bleeding time", "Watch for bruising"],
        ("warfarin", "aspirin"): ["INR levels", "Bleeding signs"],
        ("insulin", "alcohol"): ["Blood glucose", "Hypoglycemia symptoms"]
    }
    return monitoring.get((med1, med2), ["General monitoring recommended"])

def get_alternative_timing(med1: str, med2: str) -> str:
    """Get alternative timing to minimize interaction"""
    timing = {
        ("paracetamol", "alcohol"): "Take paracetamol at least 2 hours before alcohol",
        ("aspirin", "ibuprofen"): "Space doses 2-4 hours apart",
        ("warfarin", "aspirin"): "Avoid combination, use alternative pain relief",
        ("insulin", "alcohol"): "Monitor blood sugar closely if alcohol consumed"
    }
    return timing.get((med1, med2), "Consult healthcare provider for timing")

def get_contraindication_explanation(med: str, condition: str) -> str:
    """Get detailed explanation of contraindication"""
    explanations = {
        ("paracetamol", "liver_disease"): "Paracetamol is metabolized by the liver and can cause further damage",
        ("ibuprofen", "heart_disease"): "NSAIDs can increase cardiovascular risk and fluid retention",
        ("aspirin", "bleeding_disorder"): "Aspirin inhibits platelet function and increases bleeding risk"
    }
    return explanations.get((med, condition), "Medication may worsen the condition")

def get_alternative_approach(med: str, condition: str) -> str:
    """Get alternative approach for contraindicated medication"""
    approaches = {
        ("paracetamol", "liver_disease"): "Use ibuprofen or topical pain relief instead",
        ("ibuprofen", "heart_disease"): "Use paracetamol or topical treatments",
        ("aspirin", "bleeding_disorder"): "Use paracetamol for pain relief"
    }
    return approaches.get((med, condition), "Consult healthcare provider for alternatives")

def get_contraindication_monitoring(med: str, condition: str) -> List[str]:
    """Get monitoring requirements for contraindicated medication"""
    monitoring = {
        ("paracetamol", "liver_disease"): ["Liver function tests", "Monitor for liver damage signs"],
        ("ibuprofen", "heart_disease"): ["Blood pressure", "Heart function monitoring"],
        ("aspirin", "bleeding_disorder"): ["Bleeding time", "Platelet count"]
    }
    return monitoring.get((med, condition), ["Close monitoring required"])

def get_alternative_reason(med: str, alt: str) -> str:
    """Get reason for suggesting alternative medication"""
    reasons = {
        ("paracetamol", "ibuprofen"): "Ibuprofen has anti-inflammatory properties",
        ("ibuprofen", "paracetamol"): "Paracetamol is safer for heart patients",
        ("aspirin", "paracetamol"): "Paracetamol doesn't affect blood clotting"
    }
    return reasons.get((med, alt), "Alternative may be safer for this patient")

def get_dosage_equivalent(med: str, alt: str) -> str:
    """Get dosage equivalent for alternative medication"""
    equivalents = {
        ("paracetamol", "ibuprofen"): "500mg paracetamol ≈ 200mg ibuprofen",
        ("ibuprofen", "paracetamol"): "200mg ibuprofen ≈ 500mg paracetamol",
        ("aspirin", "paracetamol"): "325mg aspirin ≈ 500mg paracetamol"
    }
    return equivalents.get((med, alt), "Consult healthcare provider for dosage")

def get_alternative_considerations(med: str, alt: str) -> str:
    """Get considerations for alternative medication"""
    considerations = {
        ("paracetamol", "ibuprofen"): "Take with food to avoid stomach irritation",
        ("ibuprofen", "paracetamol"): "May not have anti-inflammatory effect",
        ("aspirin", "paracetamol"): "No anti-inflammatory or blood-thinning effect"
    }
    return considerations.get((med, alt), "Monitor for effectiveness and side effects")

def get_timing_recommendations(medications: List[str]) -> List[str]:
    """Get timing recommendations for medications"""
    timing_recs = []
    
    if "insulin" in medications:
        timing_recs.append("Take insulin 30 minutes before meals")
    
    if "metformin" in medications:
        timing_recs.append("Take metformin with meals to reduce stomach upset")
    
    if "paracetamol" in medications:
        timing_recs.append("Take paracetamol every 4-6 hours as needed")
    
    if "ibuprofen" in medications:
        timing_recs.append("Take ibuprofen with food to protect stomach")
    
    return timing_recs

def get_side_effects_to_watch(medications: List[str], patient_profile: Dict) -> List[str]:
    """Get side effects to watch for based on medications and patient profile"""
    side_effects = []
    
    if "paracetamol" in medications:
        side_effects.append("Liver damage signs (jaundice, dark urine)")
    
    if "ibuprofen" in medications:
        side_effects.append("Stomach irritation, heart problems")
    
    if "aspirin" in medications:
        side_effects.append("Bleeding, stomach ulcers")
    
    if "insulin" in medications:
        side_effects.append("Hypoglycemia (low blood sugar)")
    
    if "metformin" in medications:
        side_effects.append("Lactic acidosis, stomach upset")
    
    # Patient-specific side effects
    if patient_profile.get("age", 0) > 65:
        side_effects.append("Increased risk of falls, confusion")
    
    if "liver_disease" in patient_profile.get("medical_history", []):
        side_effects.append("Worsening liver function")
    
    if "kidney_disease" in patient_profile.get("medical_history", []):
        side_effects.append("Worsening kidney function")
    
    return side_effects

def get_nutritional_recommendations(medications: List[str], patient_profile: Dict) -> Dict:
    """Get nutritional recommendations based on medications and patient profile"""
    nutrition = {
        "foods_to_eat": [],
        "foods_to_avoid": [],
        "nutrients_needed": [],
        "supplements": [],
        "meal_timing": [],
        "hydration": [],
        "special_diet": []
    }
    
    # Medication-specific nutritional advice
    if "paracetamol" in medications:
        nutrition["foods_to_eat"].extend([
            "Milk thistle tea (supports liver)",
            "Green leafy vegetables (antioxidants)",
            "Berries (vitamin C)",
            "Whole grains (fiber)"
        ])
        nutrition["foods_to_avoid"].extend([
            "Alcohol (liver damage)",
            "High-fat foods (liver stress)",
            "Processed foods (additives)"
        ])
        nutrition["nutrients_needed"].extend([
            "Vitamin C (antioxidant)",
            "N-acetylcysteine (liver support)",
            "Milk thistle (liver protection)"
        ])
        nutrition["hydration"].append("Drink 8-10 glasses of water daily to support liver function")
    
    if "ibuprofen" in medications:
        nutrition["foods_to_eat"].extend([
            "Bananas (potassium)",
            "Oatmeal (stomach coating)",
            "Ginger tea (anti-inflammatory)",
            "Yogurt (probiotics)"
        ])
        nutrition["foods_to_avoid"].extend([
            "Spicy foods (stomach irritation)",
            "Citrus fruits (acidity)",
            "Caffeine (stomach irritation)"
        ])
        nutrition["nutrients_needed"].extend([
            "Omega-3 fatty acids (anti-inflammatory)",
            "Probiotics (gut health)",
            "Magnesium (muscle relaxation)"
        ])
        nutrition["meal_timing"].append("Take with food to protect stomach lining")
    
    if "aspirin" in medications:
        nutrition["foods_to_eat"].extend([
            "Dark leafy greens (vitamin K)",
            "Lean proteins (iron)",
            "Citrus fruits (vitamin C)",
            "Nuts and seeds (healthy fats)"
        ])
        nutrition["foods_to_avoid"].extend([
            "Alcohol (bleeding risk)",
            "Ginkgo biloba (bleeding risk)",
            "Garlic supplements (bleeding risk)"
        ])
        nutrition["nutrients_needed"].extend([
            "Iron (prevent anemia)",
            "Vitamin K (blood clotting)",
            "Folate (red blood cells)"
        ])
        nutrition["hydration"].append("Stay well-hydrated to prevent blood thickening")
    
    if "insulin" in medications:
        nutrition["foods_to_eat"].extend([
            "Complex carbohydrates (brown rice, quinoa)",
            "Lean proteins (chicken, fish)",
            "Non-starchy vegetables",
            "Healthy fats (avocado, olive oil)"
        ])
        nutrition["foods_to_avoid"].extend([
            "Simple sugars (candy, soda)",
            "Refined carbohydrates (white bread)",
            "High-sugar fruits (grapes, mangoes)"
        ])
        nutrition["nutrients_needed"].extend([
            "Chromium (glucose metabolism)",
            "Magnesium (insulin sensitivity)",
            "Alpha-lipoic acid (nerve protection)"
        ])
        nutrition["meal_timing"].append("Eat consistent meals at regular times")
        nutrition["special_diet"].append("Follow diabetic meal plan with carb counting")
    
    if "metformin" in medications:
        nutrition["foods_to_eat"].extend([
            "High-fiber foods (beans, lentils)",
            "Whole grains (oats, barley)",
            "Leafy greens (folate)",
            "Lean proteins"
        ])
        nutrition["foods_to_avoid"].extend([
            "Alcohol (lactic acidosis risk)",
            "High-sugar foods",
            "Processed foods"
        ])
        nutrition["nutrients_needed"].extend([
            "Vitamin B12 (deficiency risk)",
            "Folate (red blood cells)",
            "Iron (prevent anemia)"
        ])
        nutrition["meal_timing"].append("Take with meals to reduce stomach upset")
    
    # Patient profile-based nutritional advice
    age = patient_profile.get("age", 0)
    medical_history = patient_profile.get("medical_history", [])
    
    # Age-based nutrition
    if age > 65:
        nutrition["nutrients_needed"].extend([
            "Calcium (bone health)",
            "Vitamin D (bone health)",
            "B12 (absorption decreases with age)",
            "Protein (muscle maintenance)"
        ])
        nutrition["foods_to_eat"].extend([
            "Dairy products (calcium)",
            "Fatty fish (vitamin D)",
            "Lean meats (protein)",
            "Nuts (healthy fats)"
        ])
        nutrition["special_diet"].append("Consider senior-specific nutritional needs")
    
    if age < 18:
        nutrition["nutrients_needed"].extend([
            "Calcium (bone growth)",
            "Iron (growth and development)",
            "Zinc (immune system)",
            "Protein (growth)"
        ])
        nutrition["foods_to_eat"].extend([
            "Milk and dairy (calcium)",
            "Lean meats (iron and protein)",
            "Fruits and vegetables (vitamins)",
            "Whole grains (energy)"
        ])
        nutrition["special_diet"].append("Ensure adequate nutrition for growth and development")
    
    # Medical condition-based nutrition
    if "diabetes" in medical_history:
        nutrition["special_diet"].append("Follow diabetic diet with controlled carbohydrates")
        nutrition["foods_to_eat"].extend([
            "Low-glycemic index foods",
            "Fiber-rich foods",
            "Lean proteins",
            "Healthy fats"
        ])
        nutrition["foods_to_avoid"].extend([
            "High-sugar foods",
            "Refined carbohydrates",
            "Sugary beverages"
        ])
    
    if "heart_disease" in medical_history:
        nutrition["special_diet"].append("Follow heart-healthy diet")
        nutrition["foods_to_eat"].extend([
            "Fatty fish (omega-3)",
            "Nuts and seeds (healthy fats)",
            "Fruits and vegetables (antioxidants)",
            "Whole grains (fiber)"
        ])
        nutrition["foods_to_avoid"].extend([
            "Saturated fats",
            "Trans fats",
            "High-sodium foods",
            "Processed meats"
        ])
        nutrition["nutrients_needed"].extend([
            "Omega-3 fatty acids",
            "Potassium (blood pressure)",
            "Magnesium (heart rhythm)"
        ])
    
    if "liver_disease" in medical_history:
        nutrition["special_diet"].append("Follow liver-friendly diet")
        nutrition["foods_to_eat"].extend([
            "Milk thistle tea",
            "Green leafy vegetables",
            "Lean proteins",
            "Whole grains"
        ])
        nutrition["foods_to_avoid"].extend([
            "Alcohol",
            "High-fat foods",
            "Processed foods",
            "Excessive protein"
        ])
        nutrition["nutrients_needed"].extend([
            "Milk thistle",
            "N-acetylcysteine",
            "Vitamin E (antioxidant)"
        ])
    
    if "kidney_disease" in medical_history:
        nutrition["special_diet"].append("Follow kidney-friendly diet")
        nutrition["foods_to_eat"].extend([
            "Low-potassium fruits (apples, berries)",
            "Low-phosphorus foods",
            "Lean proteins (in moderation)",
            "Healthy fats"
        ])
        nutrition["foods_to_avoid"].extend([
            "High-potassium foods (bananas, oranges)",
            "High-phosphorus foods (dairy, nuts)",
            "High-sodium foods",
            "Excessive protein"
        ])
        nutrition["nutrients_needed"].extend([
            "B-complex vitamins",
            "Iron (prevent anemia)",
            "Calcium (bone health)"
        ])
    
    # General health recommendations
    nutrition["hydration"].append("Drink 8-10 glasses of water daily")
    nutrition["meal_timing"].append("Eat regular meals to maintain stable blood sugar")
    nutrition["supplements"].append("Consider multivitamin if diet is inadequate")
    
    return nutrition

def get_lifestyle_recommendations(medications: List[str], patient_profile: Dict) -> Dict:
    """Get lifestyle recommendations based on medications and patient profile"""
    lifestyle = {
        "exercise": [],
        "sleep": [],
        "stress_management": [],
        "avoidances": [],
        "monitoring": [],
        "emergency_preparedness": []
    }
    
    # Medication-specific lifestyle advice
    if "insulin" in medications:
        lifestyle["exercise"].append("Regular exercise helps with blood sugar control")
        lifestyle["exercise"].append("Monitor blood sugar before and after exercise")
        lifestyle["monitoring"].append("Check blood glucose levels regularly")
        lifestyle["emergency_preparedness"].append("Always carry glucose tablets or candy")
        lifestyle["avoidances"].append("Avoid alcohol (hypoglycemia risk)")
    
    if "metformin" in medications:
        lifestyle["exercise"].append("Regular exercise improves insulin sensitivity")
        lifestyle["avoidances"].append("Avoid alcohol (lactic acidosis risk)")
        lifestyle["monitoring"].append("Watch for signs of lactic acidosis")
    
    if "aspirin" in medications:
        lifestyle["avoidances"].append("Avoid contact sports (bleeding risk)")
        lifestyle["avoidances"].append("Avoid alcohol (bleeding risk)")
        lifestyle["monitoring"].append("Watch for unusual bleeding or bruising")
        lifestyle["emergency_preparedness"].append("Inform healthcare providers about aspirin use")
    
    if "ibuprofen" in medications:
        lifestyle["exercise"].append("Gentle exercise may help with pain management")
        lifestyle["avoidances"].append("Avoid alcohol (stomach irritation)")
        lifestyle["monitoring"].append("Watch for stomach pain or bleeding")
    
    # Patient profile-based lifestyle advice
    age = patient_profile.get("age", 0)
    medical_history = patient_profile.get("medical_history", [])
    
    if age > 65:
        lifestyle["exercise"].append("Low-impact exercises (walking, swimming)")
        lifestyle["exercise"].append("Balance and strength training")
        lifestyle["sleep"].append("7-9 hours of quality sleep")
        lifestyle["monitoring"].append("Regular health check-ups")
        lifestyle["avoidances"].append("Avoid high-risk activities")
    
    if "diabetes" in medical_history:
        lifestyle["exercise"].append("Regular aerobic exercise (150 minutes/week)")
        lifestyle["exercise"].append("Resistance training 2-3 times/week")
        lifestyle["sleep"].append("Consistent sleep schedule")
        lifestyle["stress_management"].append("Practice stress reduction techniques")
        lifestyle["monitoring"].append("Regular blood glucose monitoring")
    
    if "heart_disease" in medical_history:
        lifestyle["exercise"].append("Cardiac rehabilitation program")
        lifestyle["exercise"].append("Moderate-intensity exercise")
        lifestyle["avoidances"].append("Avoid smoking and secondhand smoke")
        lifestyle["stress_management"].append("Manage stress to protect heart health")
        lifestyle["monitoring"].append("Regular blood pressure monitoring")
    
    # General recommendations
    lifestyle["sleep"].append("7-9 hours of quality sleep per night")
    lifestyle["stress_management"].append("Practice relaxation techniques")
    lifestyle["stress_management"].append("Maintain social connections")
    lifestyle["monitoring"].append("Regular health check-ups")
    
    return lifestyle

def query_huggingface(text: str):
    """
    Enhanced medical text analysis using local processing
    """
    try:
        # Enhanced local medical analysis
        text_lower = text.lower()
        analysis_parts = []
        
        # Medical entity detection
        medical_terms = {
            "medications": ["tablet", "pill", "capsule", "injection", "inject", "dose", "dosage", "mg", "ml", "units"],
            "conditions": ["diabetes", "hypertension", "fever", "pain", "infection", "inflammation"],
            "instructions": ["take", "apply", "before", "after", "twice", "daily", "weekly", "monthly"],
            "warnings": ["allergy", "side effect", "contraindication", "pregnancy", "liver", "kidney"]
        }
        
        detected_entities = {}
        for category, terms in medical_terms.items():
            found_terms = [term for term in terms if term in text_lower]
            if found_terms:
                detected_entities[category] = found_terms
        
        if detected_entities:
            analysis_parts.append("🔍 **Medical Entities Detected:**")
            for category, terms in detected_entities.items():
                analysis_parts.append(f"  • {category.title()}: {', '.join(terms)}")
        
        # Dosage analysis
        import re
        dosage_patterns = [
            r'(\d+)\s*(mg|ml|units?|tablets?|pills?)',
            r'(\d+)\s*(times?|x)\s*(daily|weekly|monthly)',
            r'(\d+)\s*(before|after)\s*(meals?|food)'
        ]
        
        dosages_found = []
        for pattern in dosage_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                dosages_found.extend([f"{match[0]} {match[1]}" for match in matches])
        
        if dosages_found:
            analysis_parts.append(f"💊 **Dosage Information:** {', '.join(dosages_found)}")
        
        # Risk assessment
        risk_indicators = ["overdose", "excessive", "high dose", "maximum", "caution", "warning"]
        if any(risk in text_lower for risk in risk_indicators):
            analysis_parts.append("⚠️ **Risk Indicators:** Potential high-risk medication detected")
        
        # Safety recommendations
        if "inject" in text_lower or "injection" in text_lower:
            analysis_parts.append("💉 **Injection Safety:** Verify dosage, injection site, and sterile technique")
        elif "tablet" in text_lower or "pill" in text_lower:
            analysis_parts.append("💊 **Oral Medication:** Take with water, follow timing instructions")
        
        if analysis_parts:
            return "\n".join(analysis_parts)
        else:
            return "📋 Medical text analyzed - No specific patterns detected"
            
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}

def check_prescription(text: str, patient_profile: Dict = None) -> str:
    """
    Enhanced prescription analysis with drug interaction checking
    """
    if patient_profile is None:
        patient_profile = {
            "age": 30,
            "blood_pressure": "normal",
            "temperature": 98.6,
            "medical_history": [],
            "allergies": []
        }
    
    # Extract medications from text
    medications = extract_medications(text)
    
    # Check drug interactions
    interaction_results = check_drug_interactions(medications, patient_profile)
    
    # Build analysis result
    analysis_parts = []
    
    # Basic prescription analysis
    text_lower = text.lower()
    
    # Overdose detection
    if any(phrase in text_lower for phrase in ["2 tablets", "double dose", "excessive", "overdose"]):
        analysis_parts.append("⚠️ **Overdose Risk Detected** - Please consult with doctor")
    
    # Drug interaction analysis
    if interaction_results["interactions"]:
        analysis_parts.append("🔍 **Drug Interaction Analysis:**")
        for interaction in interaction_results["interactions"]:
            severity_emoji = "🔴" if interaction["severity"] == "high" else "🟡" if interaction["severity"] == "moderate" else "🟢"
            analysis_parts.append(f"  {severity_emoji} **{interaction['drugs']}**: {interaction['effect']}")
            analysis_parts.append(f"     💡 **Recommendation**: {interaction['recommendation']}")
    
    # Contraindications
    if interaction_results["contraindications"]:
        analysis_parts.append("⚠️ **Contraindications Detected:**")
        for contra in interaction_results["contraindications"]:
            analysis_parts.append(f"  🔴 **{contra['drug']}** - Not suitable for {contra['condition']}")
    
    # Risk level assessment
    risk_emoji = "🔴" if interaction_results["risk_level"] == "high" else "🟡" if interaction_results["risk_level"] == "moderate" else "🟢"
    analysis_parts.append(f"{risk_emoji} **Overall Risk Level**: {interaction_results['risk_level'].upper()}")
    
    # Alternative suggestions
    if interaction_results["alternatives"]:
        unique_alternatives = list(set(interaction_results["alternatives"]))
        analysis_parts.append(f"💊 **Alternative Medications**: {', '.join(unique_alternatives)}")
    
    # Patient-specific recommendations
    if interaction_results["recommendations"]:
        analysis_parts.append("👤 **Patient-Specific Recommendations:**")
        for rec in interaction_results["recommendations"]:
            if isinstance(rec, dict):
                analysis_parts.append(f"  • **{rec['category']}**: {rec['message']}")
                analysis_parts.append(f"    📝 **Details**: {rec['details']}")
                analysis_parts.append(f"    🎯 **Action**: {rec['action']}")
            else:
                analysis_parts.append(f"  • {rec}")
    
    # Nutritional Guidance
    if interaction_results.get("nutritional_guidance"):
        nutrition = interaction_results["nutritional_guidance"]
        analysis_parts.append("🍎 **Nutritional Guidance:**")
        
        if nutrition.get("foods_to_eat"):
            analysis_parts.append("  ✅ **Foods to Eat:**")
            for food in nutrition["foods_to_eat"][:5]:  # Limit to 5 items
                analysis_parts.append(f"    • {food}")
        
        if nutrition.get("foods_to_avoid"):
            analysis_parts.append("  ❌ **Foods to Avoid:**")
            for food in nutrition["foods_to_avoid"][:5]:  # Limit to 5 items
                analysis_parts.append(f"    • {food}")
        
        if nutrition.get("nutrients_needed"):
            analysis_parts.append("  💊 **Nutrients Needed:**")
            for nutrient in nutrition["nutrients_needed"][:5]:  # Limit to 5 items
                analysis_parts.append(f"    • {nutrient}")
        
        if nutrition.get("special_diet"):
            analysis_parts.append("  🥗 **Special Diet:**")
            for diet in nutrition["special_diet"]:
                analysis_parts.append(f"    • {diet}")
    
    # Lifestyle Guidance
    if interaction_results.get("lifestyle_guidance"):
        lifestyle = interaction_results["lifestyle_guidance"]
        analysis_parts.append("🏃 **Lifestyle Recommendations:**")
        
        if lifestyle.get("exercise"):
            analysis_parts.append("  🏃 **Exercise:**")
            for exercise in lifestyle["exercise"][:3]:  # Limit to 3 items
                analysis_parts.append(f"    • {exercise}")
        
        if lifestyle.get("avoidances"):
            analysis_parts.append("  ⚠️ **Avoid:**")
            for avoid in lifestyle["avoidances"][:3]:  # Limit to 3 items
                analysis_parts.append(f"    • {avoid}")
        
        if lifestyle.get("monitoring"):
            analysis_parts.append("  📊 **Monitor:**")
            for monitor in lifestyle["monitoring"][:3]:  # Limit to 3 items
                analysis_parts.append(f"    • {monitor}")
    
    # Safety Score
    safety_score = interaction_results.get("safety_score", 100)
    if safety_score >= 80:
        score_emoji = "🟢"
    elif safety_score >= 60:
        score_emoji = "🟡"
    else:
        score_emoji = "🔴"
    
    analysis_parts.append(f"{score_emoji} **Safety Score**: {safety_score}/100")
    
    # Basic medication patterns
    if any(med in text_lower for med in ["paracetamol", "acetaminophen"]):
        if "1 tablet" in text_lower or "one tablet" in text_lower:
            analysis_parts.append("✅ **Paracetamol**: Normal dose detected")
        else:
            analysis_parts.append("⚠️ **Paracetamol**: Check dosage limits")
    
    if any(abx in text_lower for abx in ["amoxicillin", "penicillin", "antibiotic"]):
        analysis_parts.append("✅ **Antibiotic**: Complete full course as directed")
    
    if "inject" in text_lower or "injection" in text_lower:
        analysis_parts.append("💉 **Injection**: Verify dosage and injection site")
    
    # Return comprehensive analysis
    if analysis_parts:
        return "\n".join(analysis_parts)
    else:
        return f"📋 Prescription analyzed: {len(text)} characters. No specific patterns detected."

    