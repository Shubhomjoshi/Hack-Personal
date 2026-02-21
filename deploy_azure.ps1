# Quick Azure Deployment Script
# Run this after setting up Azure resources
param(
    [string]$AppName = ""document-intelligence-api"",
    [string]$ResourceGroup = ""document-intelligence-rg"",
    [switch]$Deploy
)
Write-Host ""========================================="" -ForegroundColor Cyan
Write-Host ""🚀 Azure Deployment Helper"" -ForegroundColor Cyan
Write-Host ""========================================="" -ForegroundColor Cyan
Write-Host """"
# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host ""✅ Azure CLI found"" -ForegroundColor Green
} catch {
    Write-Host ""❌ Azure CLI not installed"" -ForegroundColor Red
    Write-Host ""Install from: https://aka.ms/installazurecliwindows"" -ForegroundColor Yellow
    exit 1
}
# Check if logged in
$account = az account show 2>$null
if (-not $account) {
    Write-Host ""❌ Not logged into Azure"" -ForegroundColor Red
    Write-Host ""Run: az login"" -ForegroundColor Yellow
    exit 1
}
Write-Host ""✅ Logged into Azure"" -ForegroundColor Green
Write-Host """"
# Check if app exists
Write-Host ""Checking if app exists..."" -ForegroundColor Yellow
$appExists = az webapp show --name $AppName --resource-group $ResourceGroup 2>$null
if (-not $appExists) {
    Write-Host ""❌ App '$AppName' not found in resource group '$ResourceGroup'"" -ForegroundColor Red
    Write-Host ""Create the app first using the deployment guide"" -ForegroundColor Yellow
    exit 1
}
Write-Host ""✅ App found: $AppName"" -ForegroundColor Green
Write-Host """"
if ($Deploy) {
    Write-Host ""📦 Preparing deployment..."" -ForegroundColor Cyan
    # Create deployment ZIP
    $timestamp = Get-Date -Format ""yyyyMMddHHmmss""
    $zipFile = ""deploy_$timestamp.zip""
    Write-Host ""Creating ZIP file: $zipFile"" -ForegroundColor Yellow
    # Exclude files
    $excludeList = @(
        "".venv"",
        ""__pycache__"",
        ""*.pyc"",
        "".git"",
        ""*.db"",
        ""uploads/*"",
        ""*.log"",
        "".env"",
        ""deploy_*.zip""
    )
    # Get all files except excluded
    $files = Get-ChildItem -Path . -Recurse | Where-Object {
        $file = $_
        $shouldInclude = $true
        foreach ($exclude in $excludeList) {
            if ($file.FullName -like ""*$exclude*"") {
                $shouldInclude = $false
                break
            }
        }
        $shouldInclude
    }
    # Create ZIP
    Compress-Archive -Path * -DestinationPath $zipFile -Force
    Write-Host ""✅ ZIP created: $zipFile"" -ForegroundColor Green
    Write-Host """"
    # Deploy to Azure
    Write-Host ""🚀 Deploying to Azure..."" -ForegroundColor Cyan
    Write-Host ""This may take a few minutes..."" -ForegroundColor Yellow
    Write-Host """"
    az webapp deployment source config-zip 
        --resource-group $ResourceGroup 
        --name $AppName 
        --src $zipFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host """"
        Write-Host ""========================================="" -ForegroundColor Green
        Write-Host ""✅ Deployment Successful!"" -ForegroundColor Green
        Write-Host ""========================================="" -ForegroundColor Green
        Write-Host """"
        Write-Host ""Your app is available at:"" -ForegroundColor Cyan
        Write-Host ""https://$AppName.azurewebsites.net"" -ForegroundColor Yellow
        Write-Host """"
        Write-Host ""API Documentation:"" -ForegroundColor Cyan
        Write-Host ""https://$AppName.azurewebsites.net/docs"" -ForegroundColor Yellow
        Write-Host """"
        Write-Host ""View logs with:"" -ForegroundColor Cyan
        Write-Host ""az webapp log tail --name $AppName --resource-group $ResourceGroup"" -ForegroundColor Yellow
        Write-Host """"
    } else {
        Write-Host """"
        Write-Host ""❌ Deployment failed!"" -ForegroundColor Red
        Write-Host ""Check logs for details"" -ForegroundColor Yellow
    }
} else {
    Write-Host ""📋 App Information:"" -ForegroundColor Cyan
    Write-Host """"
    # Get app details
    $appInfo = az webapp show --name $AppName --resource-group $ResourceGroup | ConvertFrom-Json
    Write-Host ""Name: $($appInfo.name)"" -ForegroundColor White
    Write-Host ""State: $($appInfo.state)"" -ForegroundColor White
    Write-Host ""URL: https://$($appInfo.defaultHostName)"" -ForegroundColor White
    Write-Host """"
    Write-Host ""To deploy, run:"" -ForegroundColor Cyan
    Write-Host "".\deploy_azure.ps1 -Deploy"" -ForegroundColor Yellow
    Write-Host """"
}
