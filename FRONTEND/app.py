import streamlit as st
import requests
import json
from streamlit_option_menu import option_menu
import numpy as np
from PIL import Image
import io
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
BACKEND_TIMEOUT = 5

# Page configuration
st.set_page_config(
    page_title="MedFusion - AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_connection():
    """Check if backend is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=BACKEND_TIMEOUT)
        return response.status_code == 200
    except:
        return False

def verify_prescription_api(prescription_text, patient_profile=None):
    """Call backend prescription verification API"""
    try:
        if patient_profile:
            # Enhanced verification with patient profile
            payload = {
                "text": prescription_text,
                "patient_profile": patient_profile
            }
            response = requests.post(
                f"{API_BASE_URL}/verify_prescription_with_profile",
                json=payload,
                timeout=BACKEND_TIMEOUT
            )
        else:
            # Basic verification
            payload = {"text": prescription_text}
            response = requests.post(
                f"{API_BASE_URL}/verify_prescription",
                json=payload,
                timeout=BACKEND_TIMEOUT
            )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Backend error: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Backend timeout - please check if the backend is running"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to backend - please start the FastAPI server"
    except Exception as e:
        return False, f"Error: {str(e)}"

def extract_medications_api(prescription_text):
    """Call backend medication extraction API"""
    try:
        payload = {"text": prescription_text}
        response = requests.post(
            f"{API_BASE_URL}/extract_medications",
            json=payload,
            timeout=BACKEND_TIMEOUT
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Backend error: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_drug_interactions_api(medications, patient_profile):
    """Call backend drug interaction checking API"""
    try:
        payload = {
            "medications": medications,
            "patient_profile": patient_profile
        }
        response = requests.post(
            f"{API_BASE_URL}/check_drug_interactions",
            json=payload,
            timeout=BACKEND_TIMEOUT
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Backend error: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def gesture_detection_api():
    """Call backend gesture detection API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/gesture_detect",
            timeout=BACKEND_TIMEOUT
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Backend error: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def home_page():
    """Home page with system overview"""
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1>🏥 MedFusion</h1>
        <h2>AI-Powered Medical Assistant</h2>
        <p>Advanced prescription verification, drug interaction analysis, and emergency detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status
    st.subheader("🔧 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    backend_status = check_backend_connection()
    
    with col1:
        if backend_status:
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")
    
    with col2:
        st.info("🟢 Frontend Active")
    
    with col3:
        st.info("🟢 Database Ready")
    
    with col4:
        st.info("🟢 AI Models Loaded")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Verify Prescription", use_container_width=True):
            st.session_state.page = "prescription"
            st.rerun()
    
    with col2:
        if st.button("💊 Drug Interactions", use_container_width=True):
            st.session_state.page = "interactions"
            st.rerun()
    
    with col3:
        if st.button("👋 Gesture Detection", use_container_width=True):
            st.session_state.page = "gesture"
            st.rerun()
    
    # Features Overview
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔍 Prescription Verification**
        - AI-powered prescription analysis
        - Safety scoring and recommendations
        - Patient profile integration
        - Real-time verification
        """)
        
        st.markdown("""
        **💊 Drug Interaction Analysis**
        - Comprehensive interaction database
        - Contraindication checking
        - Alternative medication suggestions
        - Patient-specific risk assessment
        """)
    
    with col2:
        st.markdown("""
        **👋 Emergency Gesture Detection**
        - Real-time hand gesture recognition
        - Silent emergency alerts
        - Camera-based detection
        - Immediate response system
        """)
        
        st.markdown("""
        **🤖 AI-Powered Analysis**
        - Natural language processing
        - Medical knowledge base
        - Intelligent recommendations
        - Continuous learning
        """)

def prescription_page():
    """Prescription verification page"""
    st.title("🔍 Prescription Verification")
    st.markdown("Enter prescription details for AI-powered safety analysis")
    
    # Check backend status
    if not check_backend_connection():
        st.error("🔴 Backend is not available. Please start the FastAPI server on port 8000.")
        st.info("Run: `cd BACKEND && python -m uvicorn main:app --reload` to start the backend.")
        return
    
    # Input Section
    st.subheader("📝 Prescription Input")
    prescription_text = st.text_area(
        "Enter prescription text:",
        placeholder="Example: Take 2 tablets of paracetamol 500mg every 6 hours with meals",
        height=120
    )
    
    # Patient Profile (Optional)
    with st.expander("👤 Patient Profile (Optional for Enhanced Analysis)"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            blood_pressure = st.selectbox("Blood Pressure", ["normal", "high", "low"])
        
        with col2:
            temperature = st.number_input("Temperature (°F)", min_value=95.0, max_value=110.0, value=98.6)
        
        medical_history = st.multiselect(
            "Medical History",
            ["diabetes", "hypertension", "heart_disease", "liver_disease", 
             "kidney_disease", "stomach_ulcer", "asthma", "bleeding_disorder"]
        )
        
        allergies = st.multiselect(
            "Allergies",
            ["penicillin", "aspirin", "ibuprofen", "paracetamol", "sulfa"]
        )
        
        use_profile = len(medical_history) > 0 or len(allergies) > 0 or age != 30
    
    # Analysis Section
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_button = st.button("🔍 Analyze Prescription", type="primary", use_container_width=True)
        extract_meds_button = st.button("💊 Extract Medications", use_container_width=True)
    
    if analyze_button and prescription_text.strip():
        with st.spinner("Analyzing prescription..."):
            if use_profile:
                # Enhanced analysis with patient profile
                patient_profile = {
                    "age": age,
                    "blood_pressure": blood_pressure,
                    "temperature": temperature,
                    "medical_history": medical_history,
                    "allergies": allergies
                }
                success, result = verify_prescription_api(prescription_text, patient_profile)
            else:
                # Basic analysis
                success, result = verify_prescription_api(prescription_text)
            
            if success:
                st.success("✅ Analysis Complete!")
                st.subheader("📋 Results")
                
                # Display input
                st.markdown(f"**Input Text**: {result.get('input', prescription_text)}")
                
                # Display patient profile if used
                if 'patient_profile' in result:
                    st.markdown("**Patient Profile**: Included in analysis")
                
                # Display analysis result
                if 'result' in result:
                    st.markdown("**Analysis**:")
                    st.info(result['result'])
                
            else:
                st.error(f"❌ {result}")
    
    elif extract_meds_button and prescription_text.strip():
        with st.spinner("Extracting medications..."):
            success, result = extract_medications_api(prescription_text)
            
            if success:
                st.success("✅ Medications Extracted!")
                medications = result.get('medications', [])
                
                if medications:
                    st.subheader("💊 Found Medications")
                    for med in medications:
                        st.markdown(f"- **{med}**")
                else:
                    st.info("No medications found in the text")
            else:
                st.error(f"❌ {result}")
    
    elif (analyze_button or extract_meds_button) and not prescription_text.strip():
        st.warning("⚠️ Please enter prescription text")

def interactions_page():
    """Drug interactions analysis page"""
    st.title("💊 Drug Interaction Analysis")
    st.markdown("Check for interactions between multiple medications")
    
    # Check backend status
    if not check_backend_connection():
        st.error("🔴 Backend is not available. Please start the FastAPI server on port 8000.")
        return
    
    # Medications Input
    st.subheader("💊 Medications")
    medications_text = st.text_area(
        "Enter medications (one per line or comma-separated):",
        placeholder="paracetamol\nibuprofen\naspirin",
        height=100
    )
    
    # Parse medications
    if medications_text.strip():
        medications = [med.strip() for med in medications_text.replace(',', '\n').split('\n') if med.strip()]
        
        if medications:
            st.markdown(f"**Found {len(medications)} medications:**")
            for med in medications:
                st.markdown(f"- {med}")
    
    # Patient Profile
    st.subheader("👤 Patient Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        blood_pressure = st.selectbox("Blood Pressure", ["normal", "high", "low"])
    
    with col2:
        temperature = st.number_input("Temperature (°F)", min_value=95.0, max_value=110.0, value=98.6)
    
    medical_history = st.multiselect(
        "Medical History",
        ["diabetes", "hypertension", "heart_disease", "liver_disease", 
         "kidney_disease", "stomach_ulcer", "asthma", "bleeding_disorder"]
    )
    
    allergies = st.multiselect(
        "Allergies",
        ["penicillin", "aspirin", "ibuprofen", "paracetamol", "sulfa"]
    )
    
    # Analysis
    if st.button("🔍 Check Drug Interactions", type="primary"):
        if not medications_text.strip():
            st.warning("⚠️ Please enter medications")
            return
        
        medications = [med.strip() for med in medications_text.replace(',', '\n').split('\n') if med.strip()]
        
        if len(medications) < 2:
            st.warning("⚠️ Please enter at least 2 medications to check for interactions")
            return
        
        with st.spinner("Analyzing drug interactions..."):
            patient_profile = {
                "age": age,
                "blood_pressure": blood_pressure,
                "temperature": temperature,
                "medical_history": medical_history,
                "allergies": allergies
            }
            
            success, result = check_drug_interactions_api(medications, patient_profile)
            
            if success:
                st.success("✅ Interaction Analysis Complete!")
                
                # Display results
                interaction_data = result.get('interaction_analysis', {})
                
                if interaction_data:
                    # Safety Score
                    safety_score = interaction_data.get('safety_score', 100)
                    risk_level = interaction_data.get('risk_level', 'low')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Safety Score", f"{safety_score}/100")
                    with col2:
                        st.metric("Risk Level", risk_level.upper())
                    with col3:
                        interactions = interaction_data.get('interactions', [])
                        st.metric("Interactions Found", len(interactions))
                    
                    # Interactions
                    if interactions:
                        st.subheader("⚠️ Drug Interactions Found")
                        for interaction in interactions:
                            severity = interaction.get('severity', 'unknown')
                            drugs = interaction.get('drugs', 'Unknown')
                            effect = interaction.get('effect', 'Unknown effect')
                            recommendation = interaction.get('recommendation', 'Consult doctor')
                            
                            severity_color = {
                                'high': '🔴',
                                'moderate': '🟡', 
                                'low': '🟢'
                            }.get(severity, '⚪')
                            
                            st.warning(f"""
                            **{severity_color} {drugs}** ({severity.upper()} severity)
                            - **Effect**: {effect}
                            - **Recommendation**: {recommendation}
                            """)
                    
                    # Contraindications
                    contraindications = interaction_data.get('contraindications', [])
                    if contraindications:
                        st.subheader("🚫 Contraindications")
                        for contra in contraindications:
                            drug = contra.get('drug', 'Unknown')
                            condition = contra.get('condition', 'Unknown')
                            st.error(f"**{drug}** is contraindicated with **{condition}**")
                    
                    # Alternatives
                    alternatives = interaction_data.get('alternatives', [])
                    if alternatives:
                        st.subheader("💡 Alternative Medications")
                        for alt in alternatives:
                            original = alt.get('original', 'Unknown')
                            alternative = alt.get('alternative', 'Unknown')
                            st.info(f"Instead of **{original}**, consider **{alternative}**")
                
                else:
                    st.info("No detailed interaction data available")
            else:
                st.error(f"❌ {result}")

def gesture_page():
    """Gesture detection page"""
    st.title("👋 Emergency Gesture Detection")
    st.markdown("Real-time hand gesture detection for emergency situations")
    
    # Check backend status
    if not check_backend_connection():
        st.error("🔴 Backend is not available. Please start the FastAPI server on port 8000.")
        return
    
    st.info("📹 This feature uses your camera to detect hand gestures for emergency situations")
    
    if st.button("🔍 Start Gesture Detection", type="primary"):
        with st.spinner("Starting gesture detection..."):
            success, result = gesture_detection_api()
            
            if success:
                gesture = result.get('gesture_detected', 'None')
                
                if gesture and gesture != 'None':
                    st.success(f"✅ Gesture Detected: **{gesture}**")
                    
                    if 'Emergency' in gesture:
                        st.error("🚨 **EMERGENCY GESTURE DETECTED!**")
                        st.markdown("**Action Required**: Immediate assistance needed")
                else:
                    st.info("No gesture detected")
            else:
                st.error(f"❌ {result}")
    
    st.markdown("---")
    st.markdown("""
    **Supported Gestures:**
    - 🆘 Emergency Signal (Raised Hand)
    - ✋ Help Needed
    - 👍 All OK
    
    **Note**: Make sure your camera is connected and permissions are granted.
    """)

def main():
    """Main application"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/667eea/white?text=MedFusion", use_column_width=True)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Prescription", "Drug Interactions", "Gesture Detection"],
            icons=["house", "file-medical", "pills", "camera"],
            menu_icon="hospital",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        
        st.markdown("---")
        st.markdown("### 🔧 Backend Status")
        if check_backend_connection():
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
            st.info("Start backend:\n`cd BACKEND`\n`uvicorn main:app --reload`")
    
    # Main Content
    if selected == "Home":
        home_page()
    elif selected == "Prescription":
        prescription_page()
    elif selected == "Drug Interactions":
        interactions_page()
    elif selected == "Gesture Detection":
        gesture_page()

if __name__ == "__main__":
    main()
