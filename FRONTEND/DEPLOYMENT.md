# MedFusion Frontend Deployment Guide

## Quick Start

### Windows
```bash
deploy.bat
```

### Linux/Mac
```bash
chmod +x deploy.sh
./deploy.sh
```

## Deployment Options

### 1. Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```
Access at: http://localhost:8501

### 2. Docker (Frontend Only)
```bash
docker build -t medfusion-frontend .
docker run -d -p 8501:8501 --name medfusion-frontend medfusion-frontend
```

### 3. Docker Compose (Full Stack)
```bash
docker-compose up -d --build
```
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

### 4. Cloud Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy from repository

#### Heroku
```bash
# Install Heroku CLI
heroku create medfusion-frontend
git push heroku main
```

#### AWS EC2
```bash
# On EC2 instance
sudo apt update
sudo apt install docker.io docker-compose
git clone <your-repo>
cd MEDFUSION/FRONTEND
docker-compose up -d
```

## Environment Variables

Create `.env` file:
```
API_BASE_URL=http://localhost:8000
DOCTOR_PHONE=6304679550
SMS_API_KEY=your_sms_key
```

## Production Configuration

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### SSL with Let's Encrypt
```bash
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Health Check
```bash
curl http://localhost:8501/_stcore/health
```

### Logs
```bash
# Docker logs
docker logs medfusion-frontend

# Docker Compose logs
docker-compose logs -f
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 8501
   lsof -ti:8501 | xargs kill -9
   ```

2. **Backend connection failed**
   - Ensure backend is running on port 8000
   - Check firewall settings
   - Verify API_BASE_URL in config

3. **Camera not working**
   - Grant browser permissions
   - Install OpenCV: `pip install opencv-python`
   - Check camera access in other apps

4. **SMS not sending**
   - Verify phone number format
   - Check SMS service API key
   - Test with different SMS providers

### Performance Optimization

1. **Memory Usage**
   ```bash
   # Limit Docker memory
   docker run -m 512m medfusion-frontend
   ```

2. **CPU Usage**
   ```bash
   # Limit CPU cores
   docker run --cpus="1.0" medfusion-frontend
   ```

## Security

### Production Checklist
- [ ] Change default passwords
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Regular backups
- [ ] Update dependencies

### Environment Security
```bash
# Set secure permissions
chmod 600 .env
chmod 700 deploy.sh
```

## Scaling

### Load Balancing
```yaml
# docker-compose.yml
services:
  frontend:
    deploy:
      replicas: 3
  nginx:
    image: nginx
    ports:
      - "80:80"
```

### Database
- Use external database for user data
- Implement session management
- Add caching layer

## Backup & Recovery

### Data Backup
```bash
# Backup user data
docker exec medfusion-frontend tar -czf /backup/data.tar.gz /app/data

# Backup configuration
cp .env .streamlit/secrets.toml /backup/
```

### Recovery
```bash
# Restore from backup
docker cp /backup/data.tar.gz medfusion-frontend:/app/
docker exec medfusion-frontend tar -xzf /app/data.tar.gz
```