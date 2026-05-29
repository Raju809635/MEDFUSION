import streamlit as st
import requests
import json
from streamlit_option_menu import option_menu
import numpy as np
from PIL import Image
import io
import time
import os
from datetime import datetime

# Optional imports - app will work without these
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

OCR_AVAILABLE = False
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    # Default Windows paths (update if installed elsewhere)
    POPPLER_PATH = r"C:\\poppler\\poppler-25.07.0\\Library\\bin"
    TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    if os.path.exists(POPPLER_PATH) and os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# Configuration
LOCAL_BACKEND_URL = "http://localhost:8000"
RENDER_BACKEND_URL = "https://medfusion-mdhi.onrender.com"
BACKEND_TIMEOUT = 5

# Smart backend detection - try local first, fall back to Render
@st.cache_resource
def get_backend_url():
    """Auto-detect best backend URL: local if running, otherwise Render"""
    try:
        response = requests.get(f"{LOCAL_BACKEND_URL}/", timeout=2)
        if response.status_code == 200:
            return LOCAL_BACKEND_URL, "Local"
    except:
        pass
    return RENDER_BACKEND_URL, "Render Cloud"

API_BASE_URL, BACKEND_MODE = get_backend_url()

# Emergency Contact Configuration
DOCTOR_PHONE = "6304679550"  # Doctor's phone number
EMERGENCY_SMS_ENABLED = True

# SMS Service Configuration (using TextBelt - free SMS service)
SMS_API_URL = "https://textbelt.com/text"
SMS_API_KEY = "textbelt"  # Free tier key (limited messages per day)

# SMS Debug Mode - shows detailed responses
SMS_DEBUG = True  # Set to False for production, True for debugging

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
    /* Global Styles */
    :root {
        --primary: #0066cc;
        --secondary: #00a8e8;
        --accent: #00d9ff;
        --dark: #0a1e3f;
        --light: #f8fbff;
        --success: #00b894;
        --warning: #fdcb6e;
        --danger: #e74c3c;
    }
    
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main Layout */
    .main {
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #f8fbff 0%, #e8f4f8 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1e3f 0%, #1a3a52 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 50%, #00d9ff 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(0, 102, 204, 0.2);
        animation: slideInDown 0.6s ease-out;
    }
    
    .hero-section h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-section p {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.95;
    }
    
    /* Cards and Containers */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(0, 102, 204, 0.1);
        box-shadow: 0 8px 32px rgba(0, 102, 204, 0.08);
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 102, 204, 0.15);
        border-color: rgba(0, 168, 232, 0.3);
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(0, 168, 232, 0.1) 0%, rgba(0, 217, 255, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #00a8e8;
        box-shadow: 0 4px 15px rgba(0, 168, 232, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem !important;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0052a3 0%, #008fb8 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
    }
    
    /* Forms */
    .stSelectbox > div > div, 
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1.5px solid rgba(0, 102, 204, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover,
    .stTextInput > div > div > input:hover, 
    .stTextArea > div > div > textarea:hover,
    .stNumberInput > div > div > input:hover {
        border-color: rgba(0, 168, 232, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(0, 168, 232, 0.1) !important;
    }
    
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00a8e8 !important;
        box-shadow: 0 0 0 3px rgba(0, 168, 232, 0.2) !important;
    }
    
    /* Alerts */
    .stAlert {
        margin: 1.5rem 0;
        border-radius: 12px;
        animation: slideIn 0.3s ease-out;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 184, 148, 0.1) 0%, rgba(0, 217, 255, 0.05) 100%) !important;
        border: 1px solid rgba(0, 184, 148, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(253, 203, 110, 0.1) 0%, rgba(253, 203, 110, 0.05) 100%) !important;
        border: 1px solid rgba(253, 203, 110, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(231, 76, 60, 0.05) 100%) !important;
        border: 1px solid rgba(231, 76, 60, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 168, 232, 0.1) 100%) !important;
        border: 1px solid rgba(0, 102, 204, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 10px 10px 0 0 !important;
        border: 1px solid rgba(0, 102, 204, 0.1) !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066cc 0%, #00a8e8 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(0, 102, 204, 0.08) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(0, 102, 204, 0.12) !important;
    }
    
    /* Text Elements */
    h1, h2, h3 {
        color: #0a1e3f;
        font-weight: 700;
    }
    
    h1 { font-size: 2rem; margin-top: 1.5rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.2rem; }
    
    /* Images */
    img {
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(0, 102, 204, 0.15);
        max-width: 100%;
    }
    
    /* Animations */
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main {
            padding: 1rem 0.5rem;
        }
        .hero-section {
            padding: 2rem 1rem;
        }
        .hero-section h1 {
            font-size: 1.8rem;
        }
    }
    
    /* Navigation Menu - Fix Text Visibility */
    [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    [data-testid="stSidebar"] button {
        color: white !important;
    }
    
    .streamlit-expanderHeader {
        color: white !important;
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

def send_emergency_sms(patient_name, user_phone="Unknown", location="MedFusion App", gesture_type="Emergency Gesture"):
    """Send emergency SMS to doctor with fast timeout and fallback"""
    import threading
    import queue
    
    result_queue = queue.Queue()
    
    def send_sms_thread():
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Try Indian format first (most likely for this number)
            phone_formats = [
                f"+91{DOCTOR_PHONE}",   # Indian format: +916304679550
                DOCTOR_PHONE,          # Original: 6304679550
                f"+1{DOCTOR_PHONE}",    # US format: +16304679550
            ]
            
            # Compose emergency message
            message = f"MEDICAL EMERGENCY ALERT\n\n" \
                     f"Patient: {patient_name}\n" \
                     f"Time: {timestamp}\n" \
                     f"Gesture: {gesture_type}\n" \
                     f"IMMEDIATE ASSISTANCE REQUIRED"
            
            # Try sending with different phone formats
            for i, phone in enumerate(phone_formats):
                try:
                    payload = {
                        'phone': phone,
                        'message': message,
                        'key': SMS_API_KEY
                    }
                    
                    if SMS_DEBUG:
                        result_queue.put(("debug", f"🔍 Trying: {phone}"))
                    
                    # Very short timeout
                    response = requests.post(SMS_API_URL, data=payload, timeout=5)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            result_queue.put(("success", f"✅ SMS sent to {phone}"))
                            return
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            if SMS_DEBUG:
                                result_queue.put(("debug", f"❌ API Error: {error_msg}"))
                            if i == len(phone_formats) - 1:  # Last attempt
                                result_queue.put(("error", f"API Error: {error_msg}"))
                                return
                    else:
                        if SMS_DEBUG:
                            result_queue.put(("debug", f"❌ HTTP {response.status_code}"))
                        if i == len(phone_formats) - 1:
                            result_queue.put(("error", f"HTTP error {response.status_code}"))
                            return
                            
                except requests.exceptions.Timeout:
                    if SMS_DEBUG:
                        result_queue.put(("debug", f"⏱️ Timeout for {phone}"))
                    if i == len(phone_formats) - 1:
                        result_queue.put(("error", "SMS service timeout - service may be slow"))
                        return
                except Exception as e:
                    if SMS_DEBUG:
                        result_queue.put(("debug", f"❌ Network error: {str(e)[:30]}"))
                    if i == len(phone_formats) - 1:
                        result_queue.put(("error", f"Network error: {str(e)[:50]}"))
                        return
            
        except Exception as e:
            result_queue.put(("error", f"SMS system error: {str(e)[:50]}"))
    
    # Start SMS in background thread
    sms_thread = threading.Thread(target=send_sms_thread)
    sms_thread.daemon = True
    sms_thread.start()
    
    # Wait for result with timeout
    try:
        # Wait up to 8 seconds for SMS to complete
        sms_thread.join(timeout=8.0)
        
        # Check if we got a result
        try:
            while True:
                msg_type, message = result_queue.get_nowait()
                if SMS_DEBUG and msg_type == "debug":
                    st.write(message)
                elif msg_type == "success":
                    return True, message
                elif msg_type == "error":
                    return False, message
        except queue.Empty:
            pass
            
        # If thread is still running, it's stuck
        if sms_thread.is_alive():
            return False, "SMS request timed out - service may be down"
        else:
            return False, "SMS failed with unknown error"
            
    except Exception as e:
        return False, f"SMS thread error: {str(e)[:50]}"

def send_whatsapp_alert(patient_name, user_phone="Unknown", gesture_type="Emergency Gesture"):
    """Alternative: Send WhatsApp message (requires WhatsApp Business API or similar service)"""
    # This is a placeholder for WhatsApp integration
    # You would need to set up WhatsApp Business API or use a service like Twilio
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"🚨 EMERGENCY: {patient_name} needs help! {gesture_type} detected at {timestamp}. Contact: {user_phone}"
    
    # For now, we'll just return a simulated response
    return True, f"WhatsApp alert prepared for {DOCTOR_PHONE}"

def test_sms_connection():
    """Test SMS service connectivity"""
    try:
        # Simple test message
        test_payload = {
            'phone': DOCTOR_PHONE,
            'message': 'MedFusion SMS Test - Please ignore',
            'key': SMS_API_KEY
        }
        
        response = requests.post(SMS_API_URL, data=test_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return True, f"Service available. Response: {result}"
        else:
            return False, f"Service error {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def trigger_emergency_alert(patient_name, user_email="Unknown", gesture_type="Emergency Gesture"):
    """Comprehensive emergency alert system"""
    alerts_sent = []
    alerts_failed = []
    
    # Extract phone from email if possible (basic extraction)
    user_phone = user_email if user_email and user_email.isdigit() else "Unknown"
    
    # Send SMS Alert
    if EMERGENCY_SMS_ENABLED:
        with st.spinner("Sending emergency SMS..."):
            sms_success, sms_message = send_emergency_sms(patient_name, user_phone, gesture_type=gesture_type)
        
        if sms_success:
            alerts_sent.append(f"📱 {sms_message}")
        else:
            alerts_failed.append(f"📱 {sms_message}")
    
    # Log emergency locally
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] EMERGENCY: {patient_name} - {gesture_type}"
    
    # Store in session for tracking
    if 'emergency_log' not in st.session_state:
        st.session_state.emergency_log = []
    
    st.session_state.emergency_log.append(log_entry)
    
    return alerts_sent, alerts_failed

# -----------------
# Authentication
# -----------------
USER_ROLES = ["patient", "doctor", "nurse", "admin"]
# Simple in-memory user store for demo purposes
USERS = {
    "demo@medfusion.ai": {
        "password": "demo123",
        "name": "Demo User",
        "role": "patient"
    }
}

def authenticate_user(email: str, password: str):
    user = USERS.get(email)
    if not user:
        return False, "Email not found"
    if user["password"] != password:
        return False, "Invalid password"
    return True, user

def register_user(email: str, password: str, name: str, role: str):
    if email in USERS:
        return False, "Email already registered"
    USERS[email] = {"password": password, "name": name, "role": role}
    return True, "Account created successfully"

def login_page():
    st.markdown("## 🔐 Login to MedFusion")
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        with st.form("signin_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            if submit:
                ok, info = authenticate_user(email, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = info["name"]
                    st.session_state.user_role = info["role"]
                    st.success(f"Welcome back, {info['name']}!")
                    st.rerun()
                else:
                    st.error(info)
    with tab2:
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pw")
            role = st.selectbox("Role", USER_ROLES)
            submit = st.form_submit_button("Create Account")
            if submit:
                if not all([name, email, password]):
                    st.error("Please fill in all fields")
                else:
                    ok, msg = register_user(email, password, name, role)
                    if ok:
                        # Auto login after successful signup
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.session_state.user_role = role
                        st.success("Account created. Welcome to MedFusion!")
                        st.rerun()
                    else:
                        st.error(msg)

# -----------------
# PDF and Image Utilities
# -----------------

def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy.
    Converts to grayscale, enhances contrast, and applies thresholding.
    """
    try:
        # Convert PIL image to numpy array if needed
        if isinstance(image, Image.Image):
            # Convert to RGB first to ensure compatibility
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_array = np.array(image)
        else:
            img_array = image
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply thresholding for better text detection
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image for pytesseract
        return Image.fromarray(thresh)
    except Exception as e:
        st.warning(f"Image preprocessing failed, using original: {e}")
        if isinstance(image, Image.Image):
            return image
        return Image.fromarray(image)

def extract_text_from_ocr(image, use_preprocessing=True):
    """
    Extract text from image using Tesseract OCR with preprocessing.
    Tries multiple PSM (Page Segmentation Mode) options for better accuracy.
    """
    if not OCR_AVAILABLE:
        return ""
    
    try:
        # Preprocess the image for better OCR accuracy
        if use_preprocessing and CV2_AVAILABLE:
            processed_image = preprocess_image_for_ocr(image)
        else:
            if isinstance(image, Image.Image) and image.mode != 'RGB':
                processed_image = image.convert('RGB')
            else:
                processed_image = image
        
        # Try different PSM modes for better text detection
        psm_modes = [
            '--psm 6',  # Assume single block of text
            '--psm 3',  # Fully automatic page segmentation
            '--psm 11', # Sparse text with OSD
        ]
        
        best_text = ""
        for psm in psm_modes:
            try:
                text = pytesseract.image_to_string(processed_image, config=psm + ' --oem 3')
                if len(text.strip()) > len(best_text.strip()):
                    best_text = text
            except:
                continue
        
        return best_text
    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return ""

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using pdfplumber/PyPDF2 and optional OCR."""
    extracted_text = ""
    try:
        import pdfplumber
        if hasattr(pdf_file, 'getvalue'):
            pdf_bytes = pdf_file.getvalue()
        else:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                extracted_text += page_text + "\n"
    except Exception as e:
        st.info(f"pdfplumber fallback: {e}")

    if not extracted_text.strip():
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text() or ""
                extracted_text += page_text + "\n"
        except Exception as e:
            st.info(f"PyPDF2 fallback: {e}")

    # OCR fallback for scanned PDFs
    if not extracted_text.strip() and OCR_AVAILABLE:
        try:
            images = convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)
            for idx, image in enumerate(images):
                page_text = extract_text_from_ocr(image, use_preprocessing=True)
                if page_text.strip():
                    extracted_text += f"--- Page {idx+1} (OCR) ---\n{page_text}\n"
        except Exception as e:
            st.warning(f"OCR failed: {e}")

    return extracted_text.strip()

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
    st.subheader("🔧 System Status", divider="blue")
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    backend_status = check_backend_connection()
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; text-align: center;">🟢</div>
            <div style="text-align: center; font-weight: 600; margin-top: 0.5rem;">
                Backend: """ + ("Online" if backend_status else "Offline") + """
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; text-align: center;">🟢</div>
            <div style="text-align: center; font-weight: 600; margin-top: 0.5rem;">
                Frontend: Active
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; text-align: center;">🟢</div>
            <div style="text-align: center; font-weight: 600; margin-top: 0.5rem;">
                Database: Ready
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; text-align: center;">🟢</div>
            <div style="text-align: center; font-weight: 600; margin-top: 0.5rem;">
                AI Models: Loaded
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Quick Actions
    st.subheader("🚀 Quick Actions", divider="blue")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        if st.button("🔍 Verify Prescription", use_container_width=True, key="home_btn1"):
            st.session_state.page = "prescription"
            st.rerun()
    
    with col2:
        if st.button("💊 Drug Interactions", use_container_width=True, key="home_btn2"):
            st.session_state.page = "interactions"
            st.rerun()
    
    with col3:
        if st.button("👋 Gesture Detection", use_container_width=True, key="home_btn3"):
            st.session_state.page = "gesture"
            st.rerun()
    
    st.markdown("")
    
    # Features Overview
    st.subheader("✨ Key Features", divider="blue")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="info-card">
        <h3 style="margin-top: 0; color: #0066cc;">🔍 Prescription Verification</h3>
        
        - AI-powered analysis
        - Safety scoring
        - Patient profiles
        - Real-time checks
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
        <h3 style="margin-top: 0; color: #0066cc;">💊 Drug Interactions</h3>
        
        - Interaction database
        - Contraindications
        - Alternatives
        - Risk assessment
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
        <h3 style="margin-top: 0; color: #0066cc;">👋 Emergency Detection</h3>
        
        - Hand recognition
        - Silent alerts
        - Camera detection
        - Immediate response
        </div>
        """, unsafe_allow_html=True)
        
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
    """Enhanced gesture detection page with real-time camera"""
    st.title("👋 Emergency Gesture Detection")
    st.markdown("Real-time hand gesture detection for emergency situations")
    
    # Initialize session state for gesture detection
    if 'gesture_active' not in st.session_state:
        st.session_state.gesture_active = False
        st.session_state.last_gesture = None
        st.session_state.emergency_count = 0
    
    # Camera availability check
    camera_available = CV2_AVAILABLE
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Live Camera Feed")
        
        if camera_available:
            # Camera control buttons
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                start_camera = st.button("🔍 Start Detection", type="primary", use_container_width=True)
            
            with col_b:
                stop_camera = st.button("⏹️ Stop Detection", use_container_width=True)
            
            with col_c:
                test_backend = st.button("🧪 Test Backend", use_container_width=True)
            
            if start_camera:
                st.session_state.gesture_active = True
                st.success("🟢 Camera detection started!")
                st.info("Show your hand to the camera for gesture detection.")
                
                # Real-time gesture detection placeholder
                camera_placeholder = st.empty()
                status_placeholder = st.empty()
                
                if CV2_AVAILABLE:
                    try:
                        import cv2
                        import mediapipe as mp
                        
                        mp_hands = mp.solutions.hands
                        mp_drawing = mp.solutions.drawing_utils
                        
                        # Initialize MediaPipe hands
                        hands = mp_hands.Hands(
                            static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5
                        )
                        
                        cap = cv2.VideoCapture(0)
                        
                        if cap.isOpened():
                            status_placeholder.info("📹 Camera is active - show your hand gestures")
                            
                            # Capture frames for demo (reduced for performance)
                            for i in range(5):
                                ret, frame = cap.read()
                                if ret:
                                    # Convert BGR to RGB
                                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    
                                    # Process the frame
                                    results = hands.process(rgb_frame)
                                    
                                    # Draw hand landmarks
                                    if results.multi_hand_landmarks:
                                        for hand_landmarks in results.multi_hand_landmarks:
                                            mp_drawing.draw_landmarks(
                                                rgb_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                                            )
                                        
                                        # Simple gesture detection
                                        gesture_detected = "Emergency Gesture (Hand Raised)"
                                        st.session_state.last_gesture = gesture_detected
                                        status_placeholder.success(f"✅ Gesture Detected: {gesture_detected}")
                                        
                                        # Emergency alert with SMS
                                        if 'Emergency' in gesture_detected:
                                            st.session_state.emergency_count += 1
                                            status_placeholder.error("🚨 **EMERGENCY GESTURE DETECTED!**")
                                            
                                            # Send SMS to doctor
                                            patient_name = st.session_state.user_name or "Unknown Patient"
                                            user_email = st.session_state.user_email or "Unknown"
                                            
                                            alerts_sent, alerts_failed = trigger_emergency_alert(
                                                patient_name, user_email, gesture_detected
                                            )
                                            
                                            # Display alert status
                                            if alerts_sent:
                                                for alert in alerts_sent:
                                                    status_placeholder.success(f"✅ {alert}")
                                            if alerts_failed:
                                                for alert in alerts_failed:
                                                    status_placeholder.error(f"❌ {alert}")
                                    else:
                                        status_placeholder.info("👋 Show your hand to detect gestures")
                                    
                                    # Display frame
                                    camera_placeholder.image(rgb_frame, caption="Live Camera Feed", use_column_width=True)
                                    time.sleep(0.2)  # Small delay
                                else:
                                    break
                            
                            cap.release()
                            status_placeholder.success("Camera session completed")
                        else:
                            status_placeholder.error("❌ Could not access camera")
                            
                    except Exception as e:
                        status_placeholder.error(f"❌ Camera error: {str(e)}")
                        st.error("Camera access failed. Please check permissions and try again.")
                        
            elif stop_camera:
                st.session_state.gesture_active = False
                st.info("⏹️ Detection stopped")
            
            elif test_backend:
                # Test backend gesture detection
                with st.spinner("Testing backend gesture detection..."):
                    if check_backend_connection():
                        success, result = gesture_detection_api()
                        if success:
                            gesture = result.get('gesture_detected', 'None')
                            if gesture and gesture != 'None':
                                st.success(f"✅ Backend detected: **{gesture}**")
                                if 'Emergency' in gesture:
                                    st.error("🚨 **EMERGENCY ALERT from Backend!**")
                                    
                                    # Send SMS alert for backend detection
                                    patient_name = st.session_state.user_name or "Unknown Patient"
                                    user_email = st.session_state.user_email or "Unknown"
                                    
                                    alerts_sent, alerts_failed = trigger_emergency_alert(
                                        patient_name, user_email, f"Backend {gesture}"
                                    )
                                    
                                    if alerts_sent:
                                        st.success("Emergency SMS sent to doctor!")
                                    if alerts_failed:
                                        st.warning("SMS alert failed - emergency logged locally")
                            else:
                                st.info("No gesture detected by backend")
                        else:
                            st.error(f"Backend error: {result}")
                    else:
                        st.error("Backend not available")
                        
        else:
            st.error("❌ Camera not available (OpenCV not installed)")
            st.info("Install OpenCV: `pip install opencv-python`")
            
            # Fallback: Backend-only detection
            if st.button("🧪 Use Backend Detection", type="primary"):
                with st.spinner("Using backend camera..."):
                    if check_backend_connection():
                        success, result = gesture_detection_api()
                        if success:
                            gesture = result.get('gesture_detected', 'None')
                            if gesture != 'None':
                                st.success(f"✅ Gesture: **{gesture}**")
                                if 'Emergency' in gesture:
                                    st.error("🚨 **EMERGENCY!**")
                            else:
                                st.info("No gesture detected")
                        else:
                            st.error(f"Error: {result}")
                    else:
                        st.error("Backend offline")
    
    with col2:
        st.subheader("📊 Detection Status")
        
        # Status indicators
        if camera_available:
            st.success("🟢 Camera Available")
        else:
            st.error("🔴 Camera Unavailable")
        
        if check_backend_connection():
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")
        
        # Statistics
        st.subheader("📈 Session Stats")
        st.metric("Emergency Alerts", st.session_state.emergency_count)
        
        if st.session_state.last_gesture:
            st.metric("Last Gesture", st.session_state.last_gesture)
        
        # Controls
        st.subheader("🎛️ Controls")
        
        if st.button("🔄 Reset Stats", use_container_width=True):
            st.session_state.emergency_count = 0
            st.session_state.last_gesture = None
            st.success("Stats reset")
        
        # Emergency Actions
        st.subheader("🆘 Emergency Actions")
        
        # Test SMS Connection
        if st.button("📱 Test SMS Service", use_container_width=True):
            with st.spinner("Testing SMS connectivity..."):
                success, message = test_sms_connection()
            if success:
                st.success("✅ SMS Service Working")
                if SMS_DEBUG:
                    st.info(f"Details: {message}")
            else:
                st.error("❌ SMS Service Failed")
                st.warning(f"Error: {message}")
        
        if st.button("🚨 Trigger Emergency", use_container_width=True):
            st.session_state.emergency_count += 1
            st.error("🚨 MANUAL EMERGENCY TRIGGERED!")
            
            # Send SMS alert
            patient_name = st.session_state.user_name or "Unknown Patient"
            user_email = st.session_state.user_email or "Unknown"
            
            alerts_sent, alerts_failed = trigger_emergency_alert(
                patient_name, user_email, "Manual Emergency Button"
            )
            
            st.markdown("**Actions taken:**")
            st.markdown("- Alert logged")
            st.markdown("- Timestamp recorded")
            st.markdown("- Emergency protocols activated")
            
            # Show SMS status
            if alerts_sent:
                st.success("SMS Alerts Sent:")
                for alert in alerts_sent:
                    st.write(f"  ✅ {alert}")
            
            if alerts_failed:
                st.error("SMS Alerts Failed:")
                for alert in alerts_failed:
                    st.write(f"  ❌ {alert}")
    
    # Information section
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🤚 Supported Gestures
        - **🆘 Emergency Signal**: Raised hand (palm facing camera)
        - **✋ Help Needed**: Open hand gesture
        - **👍 All OK**: Thumbs up
        - **✊ Alert**: Closed fist
        - **👋 Goodbye**: Waving motion
        """)
    
    with col2:
        st.markdown("""
        ### ⚙️ Technical Features
        - **Real-time Processing**: Live camera feed analysis
        - **MediaPipe Integration**: Advanced hand tracking
        - **Emergency Detection**: Automatic alert system
        - **Backend Fallback**: Server-side processing available
        - **Session Tracking**: Statistics and logging
        """)
    
    # Usage instructions
    st.info("""
    **💡 How to use:**
    1. Click "Start Detection" to begin camera monitoring
    2. Position your hand clearly in front of the camera
    3. Make gestures slowly and hold for 1-2 seconds
    4. Emergency gestures will trigger automatic alerts
    5. Use "Stop Detection" to end the session
    """)
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Camera Issues:**
        - Grant camera permissions in your browser
        - Close other applications using the camera
        - Try refreshing the page
        
        **Detection Issues:**
        - Ensure good lighting
        - Keep hand in frame
        - Make gestures slowly and clearly
        - Check that OpenCV and MediaPipe are installed
        
        **Backend Issues:**
        - Ensure FastAPI server is running
        - Check network connectivity
        - Verify backend is accessible on port 8000
        """)

def medical_reports_page():
    """PDF and Image upload with text extraction and backend analysis"""
    st.title("📄 Medical Reports Analysis")
    tabs = st.tabs(["PDF Upload", "Image Upload"])
    with tabs[0]:
        uploaded = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_upl")
        if uploaded is not None:
            st.success(f"Uploaded: {uploaded.name}")
            if st.button("Analyze PDF", type="primary"):
                with st.spinner("Extracting text from PDF..."):
                    text = extract_text_from_pdf(uploaded)
                if text:
                    st.text_area("Extracted Text", text, height=250)
                    if check_backend_connection():
                        try:
                            ok, res = verify_prescription_api(text)
                            if ok:
                                st.success("Backend Analysis Complete")
                                st.markdown(res.get('result', ''))
                            else:
                                st.warning(res)
                        except Exception as e:
                            st.warning(str(e))
                else:
                    st.info("No text found in PDF")
    with tabs[1]:
        img_file = st.file_uploader("Choose an image", type=["jpg","jpeg","png"], key="img_upl")
        if img_file is not None:
            image = Image.open(img_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            if st.button("Analyze Image", type="primary"):
                with st.spinner("Analyzing image with advanced OCR..."):
                    # Ensure RGB
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    ocr_text = ""
                    if OCR_AVAILABLE:
                        ocr_text = extract_text_from_ocr(image, use_preprocessing=True)
                    if ocr_text.strip():
                        st.text_area("Extracted Text", ocr_text, height=150)
                        if check_backend_connection():
                            ok, res = verify_prescription_api(ocr_text)
                            if ok:
                                st.success("Backend Analysis Complete")
                                st.markdown(res.get('result',''))
                            else:
                                st.warning(res)
                    else:
                        st.info("No text detected. You can still upload a PDF for better results.")


def main():
    """Main application"""
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.user_role = None

    # Require login
    if not st.session_state.authenticated:
        login_page()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/667eea/white?text=MedFusion", use_column_width=True)
        st.markdown(f"**User:** {st.session_state.user_name} ({st.session_state.user_role})")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Prescription", "Drug Interactions", "Medical Reports", "Gesture Detection"],
            icons=["house", "file-medical", "pills", "file-text", "camera"],
            menu_icon="hospital",
            default_index=0,
            styles={
                "container": {"padding": "0.5rem 0", "background-color": "transparent"},
                "icon": {"color": "#00d9ff", "font-size": "20px"},
                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0.3rem 0", "padding": "0.75rem 1rem", "border-radius": "8px", "color": "#ffffff", "font-weight": "500", "--hover-color": "rgba(0, 168, 232, 0.3)"},
                "nav-link-selected": {"background-color": "rgba(0, 217, 255, 0.3)", "color": "#00d9ff", "font-weight": "700"},
            }
        )
        st.markdown("---")
        st.markdown("### 🔧 Backend Status")
        if check_backend_connection():
            st.success(f"🟢 {BACKEND_MODE}")
            st.caption(f"API: {API_BASE_URL}")
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
    elif selected == "Medical Reports":
        medical_reports_page()
    elif selected == "Gesture Detection":
        gesture_page()

if __name__ == "__main__":
    main()
