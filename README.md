# MedFusion - AI Medical Assistant

A comprehensive AI-powered medical assistant system that provides prescription verification, drug interaction analysis, and emergency gesture detection.

![MedFusion](https://via.placeholder.com/800x200/667eea/white?text=MedFusion%20-%20AI%20Medical%20Assistant)

## 🏥 Features

### 🔍 Prescription Verification
- AI-powered prescription analysis
- Safety scoring and recommendations
- Patient profile integration
- Real-time verification

### 💊 Drug Interaction Analysis
- Comprehensive interaction database
- Contraindication checking
- Alternative medication suggestions
- Patient-specific risk assessment

### 👋 Emergency Gesture Detection
- Real-time hand gesture recognition
- Silent emergency alerts
- Camera-based detection
- MediaPipe integration

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)
1. Double-click `start_medfusion.bat`
2. Wait for both services to start
3. Open http://localhost:8501 in your browser

### Option 2: Manual Startup
1. **Start Backend:**
   - Double-click `start_backend.bat`
   - Wait for "Application startup complete" message

2. **Start Frontend:**
   - Double-click `start_frontend.bat`
   - Browser should open automatically

## 📋 System Requirements

- **Python 3.7+** (Python 3.10+ recommended)
- **Windows 10/11** (scripts provided for Windows)
- **Webcam** (for gesture detection)
- **Internet connection** (for AI model access)

## 🔧 Manual Installation

### Backend Setup
```bash
cd BACKEND
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend Setup
```bash
cd FRONTEND
pip install -r requirements.txt
streamlit run app.py
```

## 🔗 API Endpoints

The backend provides the following REST API endpoints:

- **GET /** - Health check
- **POST /verify_prescription** - Basic prescription verification
- **POST /verify_prescription_with_profile** - Enhanced verification with patient data
- **POST /extract_medications** - Extract medications from text
- **POST /check_drug_interactions** - Comprehensive drug interaction analysis
- **GET /gesture_detect** - Emergency gesture detection

## 💊 Supported Medications

The system currently supports analysis for:
- **Pain Relief**: Paracetamol, Ibuprofen, Aspirin, Naproxen
- **Diabetes**: Insulin, Metformin, Glipizide
- **Blood Thinners**: Warfarin
- **Mental Health**: Lithium
- **Cancer**: Methotrexate
- **Heart**: Beta Blockers

*Database is continuously expanding*

## 🎯 Usage Examples

### Prescription Verification
```
Input: "Take 2 tablets of paracetamol 500mg every 6 hours with meals"
Output: Safety analysis, dosage verification, timing recommendations
```

### Drug Interaction Check
```
Input: ["paracetamol", "warfarin"]
Output: Bleeding risk warning, monitoring recommendations
```

### Patient Profile Analysis
```
Input: Patient with diabetes + prescription text
Output: Personalized recommendations considering medical history
```

## 🛡️ Safety Features

- **Real-time Analysis**: Immediate prescription verification
- **Contraindication Detection**: Checks against patient medical history
- **Severity Scoring**: High/Medium/Low risk classifications
- **Alternative Suggestions**: Safer medication alternatives
- **Age-based Adjustments**: Dosage recommendations for elderly patients

## 🔍 Troubleshooting

### Backend Won't Start
- Check if Python is installed: `python --version`
- Install dependencies: `pip install -r BACKEND/requirements.txt`
- Check port 8000 availability

### Frontend Won't Connect
- Ensure backend is running on port 8000
- Check firewall settings
- Verify network connectivity

### Gesture Detection Issues
- Grant camera permissions
- Close other camera applications
- Ensure OpenCV is installed

### Performance Issues
- Close unnecessary applications
- Check system resources
- Restart both services

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌──────────────────┐
│   Streamlit     │ ◄──────────────► │   FastAPI        │
│   Frontend      │    requests     │   Backend        │
│   (Port 8501)   │                 │   (Port 8000)    │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │  AI Models &     │
                                    │  Drug Database   │
                                    └──────────────────┘
```

## 📊 Technology Stack

### Backend
- **FastAPI** - High-performance API framework
- **Pydantic** - Data validation
- **MediaPipe** - Gesture detection
- **OpenCV** - Computer vision
- **Hugging Face** - AI models

### Frontend
- **Streamlit** - Web application framework
- **Streamlit-option-menu** - Navigation
- **Requests** - HTTP client
- **Pillow** - Image processing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**IMPORTANT**: This system is for educational and research purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals before making medical decisions.

## 🆘 Support

Having issues? Try these steps:

1. **Check Prerequisites**: Python 3.7+, webcam, internet
2. **Restart Services**: Close all windows and run `start_medfusion.bat`
3. **Update Dependencies**: Run scripts - they auto-install requirements
4. **Check Logs**: Look at console output for error messages
5. **Port Conflicts**: Ensure ports 8000 and 8501 are available

## 🚀 Advanced Usage

### Environment Variables
Create `.env` file in BACKEND folder:
```
HUGGING_FACE_API_KEY=your_key_here
```

### Custom Configuration
Edit configuration in:
- `BACKEND/main.py` - API settings
- `FRONTEND/app.py` - UI settings
- `.env` files - API keys and secrets

### Docker Support (Coming Soon)
```bash
docker-compose up
```

---

**Made with ❤️ for better healthcare** - MedFusion Team
