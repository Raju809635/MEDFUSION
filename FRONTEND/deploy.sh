#!/bin/bash

# MedFusion Frontend Deployment Script

echo "🏥 MedFusion Frontend Deployment"
echo "================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Building Docker image..."
    docker build -t medfusion-frontend .
    
    echo "🚀 Running container..."
    docker run -d \
        --name medfusion-frontend \
        -p 8501:8501 \
        --restart unless-stopped \
        medfusion-frontend
    
    echo "✅ Frontend deployed at http://localhost:8501"
}

# Function to deploy with Docker Compose
deploy_compose() {
    echo "🐳 Starting services with Docker Compose..."
    docker-compose up -d --build
    
    echo "✅ Services deployed:"
    echo "   - Frontend: http://localhost:8501"
    echo "   - Backend: http://localhost:8000"
}

# Function to deploy locally
deploy_local() {
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    echo "🚀 Starting Streamlit app..."
    streamlit run app.py --server.port=8501
}

# Main menu
echo "Choose deployment method:"
echo "1) Docker (Frontend only)"
echo "2) Docker Compose (Frontend + Backend)"
echo "3) Local development"
echo "4) Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        deploy_docker
        ;;
    2)
        deploy_compose
        ;;
    3)
        deploy_local
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac