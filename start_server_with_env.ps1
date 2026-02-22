#!/usr/bin/env pwsh
# Quick Start Script - Sets environment and starts server
# This ensures Gemini API key is loaded before starting

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Document Intelligence API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location "C:\Amazatic\Hackathon Personal\Backend"

# Load .env file manually (backup if python-dotenv fails)
if (Test-Path ".env") {
    Write-Host "📄 Loading .env file..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and !$key.StartsWith('#')) {
                [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
                if ($key -eq "GEMINI_API_KEY") {
                    Write-Host "   ✅ $key loaded (${value.Substring(0,10)}...)" -ForegroundColor Green
                } else {
                    Write-Host "   ✅ $key loaded" -ForegroundColor Green
                }
            }
        }
    }
} else {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 Starting server..." -ForegroundColor Cyan
Write-Host ""

# Start the server
python main.py

