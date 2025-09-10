@echo off
echo Starting MedFusion Backend Server...
echo =====================================

cd BACKEND

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
