# ✅ Azure Deployment Checklist - Fix 409 Error
**Your App:** hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net
---
## 🔥 CRITICAL FIXES APPLIED
✅ **Procfile** - Updated with correct startup command
✅ **GitHub Actions** - Stops app before deploy (fixes 409 error)
✅ **database.py** - Uses persistent storage (/home/data/app.db)
✅ **documents.py** - Uses persistent uploads (/home/data/uploads)
---
## 📋 PRE-DEPLOYMENT CHECKLIST
### Step 1: Azure Portal Configuration
Go to: https://portal.azure.com → hackathon-billing-d0gtggfzeacfgefm
#### Configuration → General Settings:
- [ ] Stack: **Python**
- [ ] Python version: **3.10**
#### Configuration → Startup Command:
```
gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind=0.0.0.0:8000 --timeout 300 --access-logfile '-' --error-logfile '-'
```
#### Configuration → Application Settings (Add these):
- [ ] `ENVIRONMENT` = `production`
- [ ] `GEMINI_API_KEY` = `AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw`
- [ ] `JWT_SECRET_KEY` = `your-super-secret-key-change-this`
- [ ] `WEBSITES_PORT` = `8000`
- [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT` = `true`
- [ ] `WEBSITES_ENABLE_APP_SERVICE_STORAGE` = `true`
**IMPORTANT:** Click **Save** after adding all settings!
---
### Step 2: GitHub Secrets
Go to: Your GitHub Repo → Settings → Secrets and variables → Actions
Add these 2 secrets:
#### Secret 1: `AZURE_WEBAPP_PUBLISH_PROFILE`
Get it from Azure Portal:
1. Go to your App Service
2. Click **Download publish profile**
3. Open the .PublishSettings file
4. Copy entire XML content
5. Paste as secret value in GitHub
#### Secret 2: `AZURE_RESOURCE_GROUP`
Get it from Azure Portal:
1. Go to your App Service
2. Look at the top breadcrumb
3. Copy the resource group name
4. Paste as secret value in GitHub
---
### Step 3: Verify Files
Check these files exist:
- [ ] `requirements.txt` (contains all dependencies)
- [ ] `runtime.txt` (contains `python-3.10.13`)
- [ ] `.github/workflows/azure-deploy.yml` (GitHub Actions workflow)
- [ ] `main.py` (your FastAPI app)
- [ ] `database.py` (updated with persistent storage)
- [ ] `routers/documents.py` (updated with persistent uploads)
---
## 🚀 DEPLOYMENT
### Option A: Automatic (Recommended)
```bash
git add .
git commit -m ""Deploy to Azure with fixes""
git push origin main
```
GitHub Actions will automatically:
1. ✅ Stop the app
2. ✅ Deploy code
3. ✅ Start the app
4. ✅ Run health check
**Monitor:** GitHub → Your repo → Actions tab
---
### Option B: Manual Trigger
1. Go to GitHub → Your repo → Actions
2. Select **Deploy to Azure Web App**
3. Click **Run workflow**
4. Select branch: **main**
5. Click **Run workflow**
---
## 🔧 IF 409 ERROR STILL OCCURS
### Quick Fix:
```powershell
# 1. Stop app
az webapp stop --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
# 2. Wait
Start-Sleep -Seconds 30
# 3. Trigger deployment again (push to GitHub or manual trigger)
# 4. Start app
az webapp start --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
```
---
## ✅ POST-DEPLOYMENT
### 1. Verify App is Running
```bash
curl https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/
```
### 2. Check API Docs
Open: https://hackathon-billing-d0gtggfzeacfgefm.centralindia-01.azurewebsites.net/docs
### 3. Initialize Database (FIRST TIME ONLY)
```bash
# SSH into your app
az webapp ssh --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
# Initialize database
cd /home/site/wwwroot
python init_database.py
exit
```
### 4. View Logs
```bash
az webapp log tail --name hackathon-billing-d0gtggfzeacfgefm --resource-group YOUR_RESOURCE_GROUP
```
Or in Azure Portal:
- App Service → Monitoring → Log stream
---
## 🐛 TROUBLESHOOTING
### App won't start?
1. Check logs in Azure Portal
2. Verify startup command is correct
3. Check Python version is 3.10
4. Verify all environment variables are set
### Database not found?
1. SSH into app
2. Run `python init_database.py`
3. Check if `/home/data/app.db` exists
### Uploads not working?
1. Check if `WEBSITES_ENABLE_APP_SERVICE_STORAGE` is `true`
2. Verify `/home/data/uploads` directory exists
3. Check file permissions
---
## 📞 QUICK COMMANDS
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
```
---
## 📚 FULL DOCUMENTATION
See **AZURE_DEPLOYMENT_FIXED.md** for complete step-by-step guide.
---
## ✅ SUCCESS CRITERIA
Your deployment is successful when:
- [ ] App responds at base URL
- [ ] `/health` endpoint returns 200 OK
- [ ] `/docs` shows API documentation
- [ ] Can register a new user
- [ ] Can upload a document
- [ ] Logs show no errors
---
**Status:** ✅ All fixes applied - Ready to deploy!
**Questions?** Check AZURE_DEPLOYMENT_FIXED.md for detailed instructions.
