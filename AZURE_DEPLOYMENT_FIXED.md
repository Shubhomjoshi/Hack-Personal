# 🚀 Azure Deployment Guide - SQLite + GitHub Actions (NO DOCKER)
**Your App:** https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net
---
## ❌ Problem: 409 Conflict Error
The error you encountered:
```
Conflict (CODE: 409)
Failed to deploy web package using OneDeploy
```
**Root Causes:**
1. ✗ Deployment lock - Another deployment was in progress
2. ✗ App not stopped before deployment
3. ✗ Incorrect startup command
4. ✗ Missing worker configuration
**✅ Solution:** We've fixed all of these issues!
---
## 📋 Prerequisites
- ✅ Azure account
- ✅ GitHub repository for your code
- ✅ Azure CLI (optional, for manual commands)
---
## 🎯 Architecture
```
Your Setup:
├── Database: SQLite (local file, NO PostgreSQL)
├── Storage: Local file system (NO Azure Blob Storage)
├── Deployment: GitHub Actions
├── Server: Gunicorn + Uvicorn workers
└── Platform: Azure App Service (Linux, Python 3.10)
```
---
## 📦 STEP 1: Verify Your Files
### Files That MUST Exist:
#### 1. `requirements.txt` ✅
Should contain:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
sqlalchemy==2.0.25
pydantic==2.5.3
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib==4.7.1
bcrypt==4.0.1
python-dotenv==1.0.0
numpy==1.26.3
Pillow==10.2.0
opencv-python-headless==4.9.0.80
pdfplumber==0.11.0
PyMuPDF==1.23.8
pdf2image==1.16.3
easyocr==1.7.0
pytesseract==0.3.10
google-genai>=0.2.0
scikit-learn==1.4.0
scikit-image==0.25.2
sentence-transformers==2.2.2
```
#### 2. `runtime.txt` ✅
```
python-3.10.13
```
#### 3. `.github/workflows/azure-deploy.yml` ✅
GitHub Actions workflow (already created for you)
#### 4. `startup.txt` ✅
Startup command reference:
```
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300 --access-logfile '-' --error-logfile '-'
```
---
## 🔧 STEP 2: Configure Azure App Service
### Option A: Using Azure Portal (Recommended)
1. **Go to Azure Portal:** https://portal.azure.com
2. **Navigate to your App Service:**
   - Search for: `hackathon-billing-d0gtggfzeacfgefm`
   - Click on it
3. **Configuration → General Settings:**
   ```
   Stack: Python
   Python version: 3.10
   ```
4. **Configuration → Startup Command:**
   ```
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300 --access-logfile '-' --error-logfile '-'
   ```
5. **Configuration → Application Settings → New application setting:**
   Add these environment variables:
   | Name | Value |
   |------|-------|
   | `ENVIRONMENT` | `production` |
   | `GEMINI_API_KEY` | `AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw` |
   | `JWT_SECRET_KEY` | `your-super-secret-key-change-this-in-production` |
   | `WEBSITE_HTTPLOGGING_RETENTION_DAYS` | `3` |
   | `WEBSITES_PORT` | `8000` |
   | `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
6. **Save** and wait for restart
---
### Option B: Using Azure CLI
```powershell
# Set variables
$APP_NAME = ""hackathon-billing-d0gtggfzeacfgefm""
$RESOURCE_GROUP = ""your-resource-group-name""  # Get from Azure Portal
# Configure startup command
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file ""gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300 --access-logfile '-' --error-logfile '-'""
# Set environment variables
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    ENVIRONMENT=""production"" \
    GEMINI_API_KEY=""AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw"" \
    JWT_SECRET_KEY=""your-super-secret-key"" \
    WEBSITES_PORT=""8000"" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=""true""
```
---
## 🔐 STEP 3: Setup GitHub Secrets
1. **Go to your GitHub repository**
2. **Settings → Secrets and variables → Actions → New repository secret**
3. **Add these secrets:**
   ### Secret 1: `AZURE_WEBAPP_PUBLISH_PROFILE`
   **How to get it:**
   - Azure Portal → Your App Service
   - Click ""Download publish profile""
   - Open the downloaded `.PublishSettings` file
   - Copy entire XML content
   - Paste as secret value
   **OR use Azure CLI:**
   ```bash
   az webapp deployment list-publishing-profiles \
     --name hackathon-billing-d0gtggfzeacfgefm \
     --resource-group YOUR_RESOURCE_GROUP \
     --xml
   ```
   Copy the output and paste as secret.
   ### Secret 2: `AZURE_RESOURCE_GROUP`
   Value: Your resource group name (e.g., `hackathon-rg`)
   **Find it in Azure Portal:**
   - Go to your App Service
   - Look at the top: `Resource group: your-rg-name`
---
## 🚀 STEP 4: Deploy via GitHub Actions
### Method 1: Push to Main Branch (Automatic)
```bash
# Commit your changes
git add .
git commit -m ""Deploy to Azure with fixed configuration""
git push origin main
```
**What happens:**
1. GitHub Actions workflow triggers automatically
2. Builds your Python app
3. Stops Azure Web App (releases lock)
4. Deploys code
5. Starts Azure Web App
6. Runs health check
**Monitor progress:**
- GitHub → Your repo → Actions tab
- Watch the deployment logs
---
### Method 2: Manual Trigger
1. Go to GitHub → Your repo → Actions
2. Click ""Deploy to Azure Web App""
3. Click ""Run workflow""
4. Select branch: `main`
5. Click ""Run workflow""
---
## 🔧 STEP 5: Fix the 409 Conflict (If It Happens Again)
### Quick Fix via Azure Portal:
1. **Stop the App:**
   - Azure Portal → Your App Service
   - Click ""Stop"" button
   - Wait 30 seconds
2. **Deploy Again:**
   - GitHub → Actions → Re-run workflow
3. **Start the App:**
   - Azure Portal → Your App Service
   - Click ""Start"" button
---
### Quick Fix via Azure CLI:
```powershell
# Stop app
az webapp stop --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
# Wait a bit
Start-Sleep -Seconds 30
# Deploy (trigger GitHub Actions manually or push code)
# Start app
az webapp start --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
```
---
## 📁 STEP 6: Handle SQLite Database
Since you're using SQLite (not PostgreSQL), the database will be in your app's file system.
### Important Notes:
⚠️ **Azure App Service is ephemeral** - Files can be lost on restart!
**Solution: Use Persistent Storage**
1. **Enable persistent storage:**
   ```bash
   az webapp config appsettings set \
     --name hackathon-billing-d0gtggfzeacfgefm \
     --resource-group YOUR_RESOURCE_GROUP \
     --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
   ```
2. **Store database in persistent path:**
   Update your `database.py`:
   ```python
   import os
   # Use persistent path on Azure
   if os.getenv(""ENVIRONMENT"") == ""production"":
       DB_PATH = ""/home/data/app.db""
       os.makedirs(""/home/data"", exist_ok=True)
   else:
       DB_PATH = ""app.db""
   SQLALCHEMY_DATABASE_URL = f""sqlite:///{DB_PATH}""
   ```
3. **Initialize database on first deploy:**
   After deployment, run this ONCE via SSH:
   ```bash
   # SSH into your app
   az webapp ssh --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
   # Run database initialization
   cd /home/site/wwwroot
   python init_database.py
   exit
   ```
---
## 📂 STEP 7: Handle File Uploads
Since you're not using Azure Blob Storage, files will be stored locally.
### Configure persistent upload directory:
Update your `routers/documents.py`:
```python
import os
# Use persistent path on Azure
if os.getenv(""ENVIRONMENT"") == ""production"":
    UPLOAD_DIR = ""/home/data/uploads""
else:
    UPLOAD_DIR = ""uploads""
os.makedirs(UPLOAD_DIR, exist_ok=True)
```
---
## ✅ STEP 8: Verify Deployment
### 1. Check if app is running:
```bash
curl https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/
```
### 2. Check health endpoint:
```bash
curl https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/health
```
### 3. Check API docs:
Open in browser:
```
https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/docs
```
### 4. View logs:
```powershell
# Stream live logs
az webapp log tail --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
# Or in Azure Portal:
# App Service → Monitoring → Log stream
```
---
## 🐛 Troubleshooting Common Issues
### Issue 1: 409 Conflict Error
**Solution:** Stop app before deploying (GitHub Actions now does this automatically)
### Issue 2: App won't start
**Check logs:**
```bash
az webapp log tail --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
```
**Common fixes:**
- Verify `requirements.txt` has all dependencies
- Check startup command is correct
- Ensure `main.py` exists and has `app` variable
### Issue 3: Database not found
**Solution:**
```bash
# SSH and initialize
az webapp ssh --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
cd /home/site/wwwroot
python init_database.py
```
### Issue 4: Uploads not persisting
**Solution:** Use `/home/data/uploads` path (persistent storage)
### Issue 5: High memory usage / Crashes
**Solution:** Reduce workers in startup command
```
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app ...
```
---
## 📊 Deployment Checklist
Before deploying, verify:
- [ ] `requirements.txt` is complete
- [ ] `runtime.txt` specifies Python 3.10
- [ ] Startup command configured in Azure
- [ ] Environment variables set in Azure
- [ ] GitHub secrets added (publish profile, resource group)
- [ ] GitHub Actions workflow file exists
- [ ] Code pushed to `main` branch
- [ ] Database paths use `/home/data` for production
- [ ] Upload paths use `/home/data` for production
---
## 🎯 Quick Commands Reference
```powershell
# Stop app
az webapp stop --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RG
# Start app
az webapp start --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RG
# Restart app
az webapp restart --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RG
# View logs
az webapp log tail --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RG
# SSH into app
az webapp ssh --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RG
# Get publish profile
az webapp deployment list-publishing-profiles \
  --name hackathon-billing-d0gtggfzeacfgefm \
  --resource-group YOUR_RG \
  --xml
```
---
## 🚀 Next Steps After Successful Deployment
1. ✅ Test all API endpoints
2. ✅ Create first user via `/api/auth/register`
3. ✅ Upload test document
4. ✅ Verify OCR processing works
5. ✅ Check logs for any errors
6. ✅ Monitor performance
7. ✅ Set up custom domain (optional)
8. ✅ Configure Application Insights for monitoring
---
## 📞 Your App URLs
- **Main App:** https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net
- **API Docs:** https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/docs
- **Health Check:** https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/health
---
## 💡 Pro Tips
1. **Always stop app before manual deployments** to avoid 409 errors
2. **Use GitHub Actions** for automated deployments
3. **Monitor logs** during first deployment
4. **Test locally first** before pushing to Azure
5. **Keep secrets in GitHub Secrets**, not in code
6. **Use persistent paths** (`/home/data`) for SQLite and uploads
7. **Enable Application Insights** for production monitoring
---
**Status:** ✅ All files configured and ready for deployment!
**Ready to deploy?** Just push to GitHub and watch GitHub Actions deploy automatically!
