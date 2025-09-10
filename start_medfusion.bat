@echo off
echo ==========================================
echo        MedFusion - AI Medical Assistant
echo ==========================================
echo.

echo This will start both the backend and frontend services.
echo.

echo 1. Backend will run on: http://localhost:8000
echo 2. Frontend will run on: http://localhost:8501
echo.

echo Starting Backend Server...
start "MedFusion Backend" cmd /k "start_backend.bat"

echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak

echo Starting Frontend Application...
start "MedFusion Frontend" cmd /k "start_frontend.bat"

echo.
echo ==========================================
echo   MedFusion services are starting!
echo ==========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:8501
echo.
echo Both services will open in separate windows.
echo Close those windows to stop the services.
echo.

pause
