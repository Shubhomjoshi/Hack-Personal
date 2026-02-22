# Set Gemini API Key for Current Session
# Run this if .env file is not loading

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GEMINI API KEY SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set the API key
$env:GEMINI_API_KEY = "AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw"

# Verify it was set
if ($env:GEMINI_API_KEY) {
    Write-Host "✅ GEMINI_API_KEY has been set for this PowerShell session" -ForegroundColor Green
    Write-Host ""
    Write-Host "   API Key: $($env:GEMINI_API_KEY.Substring(0,10))..." -ForegroundColor Yellow
    Write-Host "   Length: $($env:GEMINI_API_KEY.Length) characters" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Note: This only sets the variable for THIS PowerShell window" -ForegroundColor Cyan
    Write-Host "   To make it permanent, update your .env file" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Run: python test_gemini_api_key.py" -ForegroundColor White
    Write-Host "   2. Start server: python main.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Failed to set GEMINI_API_KEY" -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

