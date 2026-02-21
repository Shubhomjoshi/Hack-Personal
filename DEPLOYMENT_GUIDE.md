# 🚀 FastAPI Deployment Guide - Document Intelligence System

This guide covers deploying your FastAPI application to various cloud platforms.

---

## 📋 Table of Contents
1. [Render.com (Recommended - FREE)](#1-rendercom-recommended---free)
2. [Railway.app (Easy & Fast)](#2-railwayapp-easy--fast)
3. [Heroku](#3-heroku)
4. [AWS EC2](#4-aws-ec2)
5. [Google Cloud Run](#5-google-cloud-run)
6. [Azure App Service](#6-azure-app-service)
7. [DigitalOcean App Platform](#7-digitalocean-app-platform)

---

## ✅ Pre-Deployment Checklist

Before deploying to any platform:

- [ ] All dependencies in `requirements.txt`
- [ ] Environment variables documented
- [ ] Database (SQLite → PostgreSQL for production)
- [ ] File uploads handled (use cloud storage in production)
- [ ] CORS configured properly
- [ ] API keys secured
- [ ] Testing completed locally

---

## 1. Render.com (Recommended - FREE)

**Best for**: Quick deployment, free tier available, PostgreSQL included

### Steps:

#### 1. Create `render.yaml` (Infrastructure as Code)
```yaml
services:
  - type: web
    name: document-intelligence-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: document-intelligence-db
          property: connectionString
    healthCheckPath: /health

databases:
  - name: document-intelligence-db
    databaseName: documents_db
    user: documents_user
```

#### 2. Add Render-specific configs to `main.py`:
```python
import os
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
```

#### 3. Deploy:
```bash
# Option A: Connect GitHub repo (Recommended)
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render auto-detects Python and uses render.yaml

# Option B: Manual
1. Push code to GitHub
2. On Render dashboard, click "New Web Service"
3. Connect repo and configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 4. Set Environment Variables:
In Render dashboard → Environment:
```
GEMINI_API_KEY=your_actual_key_here
DATABASE_URL=postgresql://... (auto-generated if using Render PostgreSQL)
```

**Free Tier**: 750 hours/month, auto-sleep after 15 min inactivity

**URL**: `https://document-intelligence-api.onrender.com`

---

## 2. Railway.app (Easy & Fast)

**Best for**: Simplest deployment, automatic HTTPS

### Steps:

#### 1. Install Railway CLI (optional):
```bash
npm i -g @railway/cli
railway login
```

#### 2. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

#### 3. Deploy:
```bash
# Option A: CLI
railway init
railway up

# Option B: GitHub (Recommended)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects FastAPI
```

#### 4. Add Environment Variables:
```bash
railway variables set GEMINI_API_KEY=your_key_here
```

**Free Tier**: $5 credit/month (~500 hours)

**URL**: `https://your-app.up.railway.app`

---

## 3. Heroku

**Best for**: Traditional PaaS, many add-ons

### Steps:

#### 1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

#### 2. Create `runtime.txt`:
```
python-3.10.13
```

#### 3. Update `requirements.txt`:
Add:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For PostgreSQL
```

#### 4. Deploy:
```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create document-intelligence-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key_here

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

**Free Tier**: None (starts at $5/month for Eco Dynos)

**URL**: `https://document-intelligence-api.herokuapp.com`

---

## 4. AWS EC2

**Best for**: Full control, scalability

### Steps:

#### 1. Launch EC2 Instance:
- AMI: Ubuntu 22.04 LTS
- Instance Type: t2.micro (free tier) or t2.small
- Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

#### 2. Connect and Setup:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Clone your repo
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn
```

#### 3. Create systemd service (`/etc/systemd/system/fastapi.service`):
```ini
[Unit]
Description=FastAPI Document Intelligence
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/your-repo
Environment="PATH=/home/ubuntu/your-repo/venv/bin"
Environment="GEMINI_API_KEY=your_key_here"
ExecStart=/home/ubuntu/your-repo/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

#### 4. Configure Nginx (`/etc/nginx/sites-available/fastapi`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    client_max_body_size 50M;  # For file uploads
}
```

#### 5. Start Services:
```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi
sudo systemctl enable fastapi
sudo systemctl restart nginx

# Enable HTTPS with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Cost**: ~$10-50/month depending on instance

**URL**: `https://your-domain.com` or `http://ec2-xx-xx-xx-xx.compute.amazonaws.com`

---

## 5. Google Cloud Run

**Best for**: Serverless, auto-scaling, pay-per-use

### Steps:

#### 1. Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8080

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 2. Create `.dockerignore`:
```
.venv
venv
__pycache__
*.pyc
.git
.env
*.db
uploads/*
!uploads/.gitkeep
```

#### 3. Deploy:
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project your-project-id

# Build and deploy
gcloud run deploy document-intelligence-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here \
  --memory 2Gi \
  --timeout 300 \
  --max-instances 10
```

**Free Tier**: 2 million requests/month

**URL**: `https://document-intelligence-api-xxx-uc.a.run.app`

---

## 6. Azure App Service

**Best for**: Windows-centric organizations, .NET integration

### Steps:

#### 1. Install Azure CLI:
```bash
# Windows
winget install Microsoft.AzureCLI

# Login
az login
```

#### 2. Create App Service:
```bash
# Create resource group
az group create --name DocumentIntelligenceRG --location eastus

# Create App Service plan
az appservice plan create \
  --name DocumentIntelligencePlan \
  --resource-group DocumentIntelligenceRG \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --name document-intelligence-api \
  --resource-group DocumentIntelligenceRG \
  --plan DocumentIntelligencePlan \
  --runtime "PYTHON:3.10"

# Configure startup command
az webapp config set \
  --name document-intelligence-api \
  --resource-group DocumentIntelligenceRG \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app"

# Set environment variables
az webapp config appsettings set \
  --name document-intelligence-api \
  --resource-group DocumentIntelligenceRG \
  --settings GEMINI_API_KEY=your_key_here
```

#### 3. Deploy:
```bash
# Option A: ZIP deployment
zip -r app.zip . -x "*.git*" "*.venv*" "*.db"
az webapp deployment source config-zip \
  --name document-intelligence-api \
  --resource-group DocumentIntelligenceRG \
  --src app.zip

# Option B: GitHub Actions (recommended)
az webapp deployment github-actions add \
  --name document-intelligence-api \
  --resource-group DocumentIntelligenceRG \
  --repo your-username/your-repo \
  --branch main
```

**Cost**: Starts at ~$13/month (B1 tier)

**URL**: `https://document-intelligence-api.azurewebsites.net`

---

## 7. DigitalOcean App Platform

**Best for**: Simple, affordable, great docs

### Steps:

#### 1. Create `app.yaml`:
```yaml
name: document-intelligence-api
services:
- name: api
  github:
    repo: your-username/your-repo
    branch: main
    deploy_on_push: true
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  http_port: 8080
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: GEMINI_API_KEY
    scope: RUN_TIME
    value: ${GEMINI_API_KEY}
databases:
- name: documents-db
  engine: PG
  version: "15"
```

#### 2. Deploy:
```bash
# Install doctl CLI
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create app
doctl apps create --spec app.yaml

# Or use Web UI
# 1. Go to https://cloud.digitalocean.com/apps
# 2. Click "Create App"
# 3. Connect GitHub repo
# 4. DigitalOcean auto-detects configuration
```

**Cost**: Starts at $5/month (Basic plan)

**URL**: `https://document-intelligence-api-xxxxx.ondigitalocean.app`

---

## 🔐 Security Checklist for Production

Before going live:

1. **Environment Variables**: Never commit `.env` files
2. **HTTPS**: Use SSL/TLS certificates (Let's Encrypt is free)
3. **CORS**: Restrict `allow_origins` to specific domains:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```
4. **Rate Limiting**: Add rate limiting middleware
5. **Database**: Use PostgreSQL instead of SQLite
6. **File Storage**: Use S3/GCS/Azure Blob instead of local storage
7. **Monitoring**: Set up logging and error tracking (Sentry)
8. **Backups**: Automate database backups

---

## 📊 Comparison Table

| Platform | Free Tier | Ease | Database | File Storage | Best For |
|----------|-----------|------|----------|--------------|----------|
| **Render** | ✅ 750hrs | ⭐⭐⭐⭐⭐ | PostgreSQL ✅ | Persistent disk | Quick start |
| **Railway** | $5 credit | ⭐⭐⭐⭐⭐ | PostgreSQL ✅ | Volumes | Simplest |
| **Heroku** | ❌ | ⭐⭐⭐⭐ | PostgreSQL ✅ | Ephemeral | Traditional |
| **AWS EC2** | ✅ 1 year | ⭐⭐⭐ | Self-hosted | EBS/S3 | Full control |
| **GCP Run** | ✅ 2M req | ⭐⭐⭐⭐ | Cloud SQL | Cloud Storage | Serverless |
| **Azure** | ❌ | ⭐⭐⭐ | Azure SQL | Blob Storage | Enterprise |
| **DigitalOcean** | ❌ | ⭐⭐⭐⭐ | PostgreSQL ✅ | Spaces | Affordable |

---

## 🎯 Recommended: Render.com for Beginners

**Why?**
- ✅ Free tier with 750 hours/month
- ✅ Zero configuration - just connect GitHub
- ✅ Automatic HTTPS
- ✅ Free PostgreSQL database
- ✅ Persistent disk storage
- ✅ Easy environment variable management
- ✅ Auto-deploy on git push

**Quick Start:**
1. Push your code to GitHub
2. Go to https://render.com → Sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Render detects Python automatically
6. Add environment variables in dashboard
7. Click "Create Web Service"
8. Done! Your API is live in ~5 minutes

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

**Next Steps**: Choose a platform and follow the specific section above! 🚀

