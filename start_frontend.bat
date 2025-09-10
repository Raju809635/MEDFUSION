@echo off
echo Starting MedFusion Frontend Application...
echo ==========================================

cd FRONTEND

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting Streamlit app on http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 8501 --server.address 0.0.0.0

pause
