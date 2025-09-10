# MedFusion Frontend (Streamlit)

A modern, interactive web interface for the MedFusion medical assistant system built with Streamlit.

## Features

- 🏠 **Home Dashboard** - System overview and feature highlights
- 🔍 **Prescription Verification** - AI-powered prescription safety analysis
- 👋 **Gesture Detection** - Real-time emergency gesture recognition
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🎨 **Modern UI** - Clean, professional medical interface

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure backend is running:**
   Make sure your FastAPI backend is running on `http://localhost:8000`

## Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   Navigate to `-http://localhost:8501`

## Usage

### Prescription Verification
1. Navigate to the "Prescription" tab
2. Enter prescription text in the text area
3. Click "Verify Prescription" to analyze
4. Review the AI-powered safety assessment

### Gesture Detection
1. Navigate to the "Gesture" tab
2. Use the camera to capture hand gestures
3. Click "Detect Gesture" to analyze
4. System will alert if emergency gestures are detected

## Configuration

The app connects to the FastAPI backend at `http://localhost:8000` by default. To change this, modify the `API_BASE_URL` variable in `app.py`.

## Dependencies

- `streamlit` - Web application framework
- `requests` - HTTP client for API calls
- `opencv-python` - Computer vision processing
- `pillow` - Image processing
- `plotly` - Interactive visualizations
- `streamlit-option-menu` - Enhanced navigation menu
- `streamlit-camera-input-live` - Live camera input

## Troubleshooting

### Backend Connection Issues
- Ensure the FastAPI backend is running on port 8000
- Check that the backend endpoints are accessible
- Verify firewall settings allow local connections

### Camera Issues
- Grant camera permissions in your browser
- Ensure no other applications are using the camera
- Try refreshing the page if camera doesn't load

### Performance Issues
- Close other browser tabs to free up memory
- Ensure stable internet connection for API calls
- Check system resources (CPU, RAM) usage
