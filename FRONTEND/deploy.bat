@echo off
echo 🏥 MedFusion Frontend Deployment
echo =================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo Choose deployment method:
echo 1) Docker (Frontend only)
echo 2) Docker Compose (Frontend + Backend)
echo 3) Local development
echo 4) Exit

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto docker_deploy
if "%choice%"=="2" goto compose_deploy
if "%choice%"=="3" goto local_deploy
if "%choice%"=="4" goto exit
goto invalid_choice

:docker_deploy
echo 🐳 Building Docker image...
docker build -t medfusion-frontend .
if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo 🚀 Running container...
docker run -d --name medfusion-frontend -p 8501:8501 --restart unless-stopped medfusion-frontend
if %errorlevel% neq 0 (
    echo ❌ Container start failed
    pause
    exit /b 1
)

echo ✅ Frontend deployed at http://localhost:8501
goto end

:compose_deploy
echo 🐳 Starting services with Docker Compose...
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo ❌ Docker Compose failed
    pause
    exit /b 1
)

echo ✅ Services deployed:
echo    - Frontend: http://localhost:8501
echo    - Backend: http://localhost:8000
goto end

:local_deploy
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Dependency installation failed
    pause
    exit /b 1
)

echo 🚀 Starting Streamlit app...
streamlit run app.py --server.port=8501
goto end

:invalid_choice
echo ❌ Invalid choice. Please run the script again.
pause
exit /b 1

:exit
echo 👋 Goodbye!
exit /b 0

:end
pause