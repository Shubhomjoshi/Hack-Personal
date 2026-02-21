# 🚀 Azure Deployment Guide - Document Intelligence API
## 📋 Prerequisites
- Azure account with active subscription
- Azure CLI installed
- Git installed
- Your application code ready
---
## 🎯 Azure Services Required
1. **Azure App Service** - Host the FastAPI application
2. **Azure Database for PostgreSQL** - Production database
3. **Azure Blob Storage** - Store uploaded documents
4. **Azure Key Vault** (Optional) - Store secrets securely
---
## 📦 Step 1: Prepare Your Application
### 1.1 Files Created for Azure:
✅ `Procfile` - Tells Azure how to start your app
✅ `runtime.txt` - Specifies Python version
✅ `requirements_azure.txt` - Production dependencies
✅ `azure_config.py` - Azure-specific configuration
✅ `services/azure_storage.py` - Azure Blob Storage integration
### 1.2 Update main.py for Production:
The CORS origins should be updated to include your Azure domain:
```python
# In azure_config.py, update ALLOWED_ORIGINS:
ALLOWED_ORIGINS = [
    ""https://your-app-name.azurewebsites.net"",
    ""https://www.yourdomain.com"",
]
```
---
## 🛠️ Step 2: Install Azure CLI
### Windows:
```powershell
# Using winget
winget install Microsoft.AzureCLI
# Or download from:
# https://aka.ms/installazurecliwindows
```
### Verify Installation:
```bash
az --version
az login
```
---
## 📊 Step 3: Create Azure Resources
### 3.1 Create Resource Group
```bash
# Set variables
$RESOURCE_GROUP=""document-intelligence-rg""
$LOCATION=""eastus""
$APP_NAME=""document-intelligence-api""
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```
### 3.2 Create Azure Database for PostgreSQL
```bash
$DB_SERVER_NAME=""doc-intel-db-server""
$DB_ADMIN_USER=""docadmin""
$DB_ADMIN_PASSWORD=""YourSecurePassword123!""
$DB_NAME=""documents_db""
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user $DB_ADMIN_USER \
  --admin-password $DB_ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15 \
  --storage-size 32 \
  --public-access All
# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME
# Get connection string
$DB_CONNECTION_STRING=""postgresql://${DB_ADMIN_USER}@${DB_SERVER_NAME}:${DB_ADMIN_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}?sslmode=require""
```
### 3.3 Create Azure Storage Account
```bash
$STORAGE_ACCOUNT_NAME=""docintelstore""  # Must be globally unique
$CONTAINER_NAME=""documents""
# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
# Get connection string
$STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --output tsv)
# Create container
az storage container create \
  --name $CONTAINER_NAME \
  --connection-string $STORAGE_CONNECTION_STRING \
  --public-access off
```
### 3.4 Create App Service Plan
```bash
$APP_SERVICE_PLAN=""doc-intel-plan""
# Create Linux App Service Plan (B1 Basic tier)
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku B1
```
### 3.5 Create Web App
```bash
# Create web app
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --name $APP_NAME \
  --runtime ""PYTHON:3.10"" \
  --startup-file ""gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 120""
```
---
## 🔐 Step 4: Configure Environment Variables
```bash
# Set all required environment variables
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    ENVIRONMENT=""production"" \
    DATABASE_URL=""$DB_CONNECTION_STRING"" \
    AZURE_STORAGE_CONNECTION_STRING=""$STORAGE_CONNECTION_STRING"" \
    AZURE_STORAGE_CONTAINER_NAME=""$CONTAINER_NAME"" \
    GEMINI_API_KEY=""your-gemini-api-key"" \
    JWT_SECRET_KEY=""your-super-secret-jwt-key-change-this"" \
    WORKERS=""4"" \
    TIMEOUT=""120"" \
    LOG_LEVEL=""INFO"" \
    MAX_UPLOAD_SIZE=""52428800"" \
    UPLOAD_DIR=""/tmp/uploads""
```
---
## 📤 Step 5: Deploy Your Application
### Option A: Deploy from Local Git
```bash
# Configure local git deployment
az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
# Get deployment credentials
az webapp deployment list-publishing-credentials \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
# Add Azure remote
cd ""C:\Amazatic\Hackathon Personal\Backend""
git init
git add .
git commit -m ""Initial commit for Azure deployment""
$DEPLOY_URL=$(az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query url -o tsv)
git remote add azure $DEPLOY_URL
git push azure main
```
### Option B: Deploy from GitHub (Recommended)
```bash
# Push your code to GitHub first, then:
az webapp deployment source config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/your-username/your-repo \
  --branch main \
  --manual-integration
```
### Option C: Deploy from ZIP
```bash
# Create deployment ZIP (exclude .venv, node_modules, etc.)
cd ""C:\Amazatic\Hackathon Personal\Backend""
$timestamp = Get-Date -Format ""yyyyMMddHHmmss""
Compress-Archive -Path * -DestinationPath ""deploy_$timestamp.zip"" -Force
# Deploy ZIP
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --src ""deploy_$timestamp.zip""
```
---
## 🔍 Step 6: Initialize Database
### Run database migrations on Azure:
```bash
# SSH into Azure Web App
az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP
# Once connected, run:
cd /home/site/wwwroot
python -m pip install -r requirements_azure.txt
python init_database.py
exit
```
Or use the Kudu console:
- Go to: `https://$APP_NAME.scm.azurewebsites.net/DebugConsole`
- Navigate to `/home/site/wwwroot`
- Run: `python init_database.py`
---
## ✅ Step 7: Test Your Deployment
### 7.1 Check if app is running:
```bash
# View application logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
# Check app status
az webapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query state
```
### 7.2 Test endpoints:
```bash
# Root endpoint
curl https://$APP_NAME.azurewebsites.net/
# Health check
curl https://$APP_NAME.azurewebsites.net/health
# API docs
# Open in browser: https://$APP_NAME.azurewebsites.net/docs
```
---
## 📝 Step 8: Configure Custom Domain (Optional)
```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname www.yourdomain.com
# Enable HTTPS
az webapp config ssl bind \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --certificate-thumbprint YOUR_CERT_THUMBPRINT \
  --ssl-type SNI
```
---
## 🔧 Step 9: Configure Scaling (Optional)
### Auto-scaling based on CPU:
```bash
# Enable auto-scale
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource $APP_NAME \
  --resource-type Microsoft.Web/serverFarms \
  --name autoscale-$APP_NAME \
  --min-count 1 \
  --max-count 5 \
  --count 2
# Scale out when CPU > 70%
az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name autoscale-$APP_NAME \
  --condition ""Percentage CPU > 70 avg 5m"" \
  --scale out 1
# Scale in when CPU < 30%
az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name autoscale-$APP_NAME \
  --condition ""Percentage CPU < 30 avg 5m"" \
  --scale in 1
```
---
## 🔄 Step 10: Continuous Deployment Setup
### GitHub Actions (Recommended):
Create `.github/workflows/azure-deploy.yml`:
```yaml
name: Deploy to Azure Web App
on:
  push:
    branches: [ main ]
  workflow_dispatch:
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements_azure.txt
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```
Get publish profile:
```bash
az webapp deployment list-publishing-profiles \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --xml
```
Add to GitHub Secrets:
- `AZURE_WEBAPP_NAME`: Your app name
- `AZURE_WEBAPP_PUBLISH_PROFILE`: The XML output from above command
---
## 📊 Step 11: Monitoring & Logging
### Enable Application Insights:
```bash
# Create Application Insights
$APPINSIGHTS_NAME=""doc-intel-insights""
az monitor app-insights component create \
  --app $APPINSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web
# Connect to Web App
$INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app $APPINSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=""$INSTRUMENTATION_KEY""
```
### View Logs:
```bash
# Stream logs in real-time
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
# Download logs
az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP
```
---
## 🛡️ Security Best Practices
### 1. Use Managed Identity:
```bash
az webapp identity assign \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```
### 2. Restrict Database Access:
```bash
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```
### 3. Enable HTTPS Only:
```bash
az webapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --https-only true
```
---
## 💰 Cost Estimation (Monthly)
| Service | Tier | Est. Cost |
|---------|------|-----------|
| App Service | B1 Basic | ~$13 |
| PostgreSQL | Burstable B1ms | ~$12 |
| Blob Storage | Standard LRS | ~$2-5 |
| **Total** | | **~$27-30/month** |
---
## 🔧 Troubleshooting
### Common Issues:
**1. App not starting:**
```bash
# Check logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
# Verify startup command
az webapp config show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query ""appCommandLine""
```
**2. Database connection issues:**
- Verify connection string in app settings
- Check firewall rules
- Ensure SSL mode is enabled
**3. File upload issues:**
- Check Azure Storage connection string
- Verify container exists and has correct permissions
- Check UPLOAD_DIR path (use /tmp/uploads on Azure)
**4. High memory usage:**
- Reduce number of workers
- Upgrade to higher tier (B2 or B3)
---
## 📞 Useful Commands
```bash
# Restart app
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
# View app settings
az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP
# Update app setting
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings KEY=""VALUE""
# Delete resource group (cleanup everything)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
---
## ✅ Deployment Checklist
- [ ] Azure CLI installed and logged in
- [ ] Resource group created
- [ ] PostgreSQL database created and configured
- [ ] Azure Storage account created
- [ ] App Service created
- [ ] Environment variables configured
- [ ] Code deployed
- [ ] Database initialized
- [ ] Health check endpoint responding
- [ ] API documentation accessible (/docs)
- [ ] CORS configured for frontend domain
- [ ] Monitoring enabled (Application Insights)
- [ ] HTTPS enforced
- [ ] Custom domain configured (if needed)
---
## 🚀 Your App is Live!
Access your API at:
- **Main App**: `https://$APP_NAME.azurewebsites.net`
- **API Docs**: `https://$APP_NAME.azurewebsites.net/docs`
- **Health Check**: `https://$APP_NAME.azurewebsites.net/health`
---
## 📚 Additional Resources
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/azure/postgresql/)
- [Azure Blob Storage](https://docs.microsoft.com/azure/storage/blobs/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
---
**Need Help?** Check Azure Portal logs or contact Azure Support.
