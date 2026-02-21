# 🚀 Azure Deployment - Quick Reference
## Files Created for Azure
| File | Purpose |
|------|---------|
| `Procfile` | Tells Azure how to start your app |
| `runtime.txt` | Specifies Python 3.10.13 |
| `requirements_azure.txt` | Production dependencies |
| `azure_config.py` | Azure configuration |
| `services/azure_storage.py` | Azure Blob Storage integration |
| `AZURE_DEPLOYMENT_GUIDE.md` | Complete step-by-step guide |
| `deploy_azure.ps1` | Quick deployment script |
| `.dockerignore` | Exclude files from deployment |
---
## Azure Resources Needed
1. **Resource Group** - Container for all resources
2. **App Service Plan** - Compute resources (B1 Basic recommended)
3. **Web App** - Your FastAPI application
4. **PostgreSQL Database** - Production database
5. **Storage Account** - File uploads (Blob Storage)
**Estimated Cost:** ~$27-30/month
---
## Quick Deployment Steps
### 1. Install Azure CLI
```powershell
winget install Microsoft.AzureCLI
```
### 2. Login to Azure
```powershell
az login
```
### 3. Create Resources
```powershell
# Set variables
$RESOURCE_GROUP = ""document-intelligence-rg""
$LOCATION = ""eastus""
$APP_NAME = ""document-intelligence-api""
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```
### 4. Deploy
```powershell
.\deploy_azure.ps1 -Deploy
```
---
## Environment Variables to Set
Set these in Azure Portal → App Service → Configuration:
```
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@server.postgres.database.azure.com:5432/db?sslmode=require
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=documents
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET_KEY=your-super-secret-key
WORKERS=4
TIMEOUT=120
LOG_LEVEL=INFO
```
---
## Useful Azure CLI Commands
```bash
# View logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
# Restart app
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
# View settings
az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP
# SSH into app
az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP
# Delete everything
az group delete --name $RESOURCE_GROUP --yes
```
---
## Your App URLs
Once deployed:
- **Main App:** `https://your-app-name.azurewebsites.net`
- **API Docs:** `https://your-app-name.azurewebsites.net/docs`
- **Health Check:** `https://your-app-name.azurewebsites.net/health`
---
## Troubleshooting
**App won't start?**
- Check logs: `az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP`
- Verify environment variables are set
- Check Python version in runtime.txt
**Database connection failed?**
- Verify DATABASE_URL is correct
- Check PostgreSQL firewall rules
- Ensure SSL mode is required
**File upload issues?**
- Verify AZURE_STORAGE_CONNECTION_STRING is set
- Check if container exists
- Ensure permissions are correct
---
## Next Steps
1. ✅ Read **AZURE_DEPLOYMENT_GUIDE.md** (complete guide)
2. ✅ Follow steps to create Azure resources
3. ✅ Set environment variables
4. ✅ Deploy using `.\deploy_azure.ps1 -Deploy`
5. ✅ Test your API
6. ✅ Configure custom domain (optional)
7. ✅ Set up monitoring
---
**Need detailed instructions?** See **AZURE_DEPLOYMENT_GUIDE.md**
