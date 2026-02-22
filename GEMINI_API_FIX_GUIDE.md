# Gemini API Key Configuration Guide

## Problem: Gemini API Key Not Working

If you're seeing errors like:
- `400 INVALID_ARGUMENT`
- `API Key not found. Please pass a valid API key`
- `API_KEY_INVALID`

Follow these steps:

---

## Solution Steps

### 1. Get a Valid Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key (starts with `AIzaSy...`)

### 2. Update Your `.env` File

Edit the file: `C:\Amazatic\Hackathon Personal\Backend\.env`

Update this line:
```
GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

Example:
```
GEMINI_API_KEY=AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw
```

### 3. Restart the Server

**IMPORTANT:** After changing `.env`, you MUST restart the FastAPI server:

```powershell
# Stop the current server (Ctrl+C if running)
# Then start again:
cd "C:\Amazatic\Hackathon Personal\Backend"
python main.py
```

### 4. Verify the API Key is Loaded

When the server starts, you should see:
```
✅ Gemini API key loaded from environment
```

If you see:
```
⚠️  Gemini API key not found in environment
```

Then the `.env` file was not loaded correctly.

---

## Testing the API Key

Run this test script:

```powershell
cd "C:\Amazatic\Hackathon Personal\Backend"
python test_gemini_api_key.py
```

This will tell you if your API key is valid and working.

---

## Common Issues

### Issue 1: API Key Expired or Invalid

**Solution:** Generate a new API key from Google AI Studio

### Issue 2: Environment Variable Not Loading

**Symptoms:**
- Server starts but Gemini features don't work
- Logs show "API key not found"

**Solution:**
```powershell
# Manually set the environment variable:
$env:GEMINI_API_KEY = "AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw"

# Verify it's set:
echo $env:GEMINI_API_KEY

# Then start server:
python main.py
```

### Issue 3: Wrong Model Name

**Symptoms:** 
- Error: "Model not found" or "Invalid model"

**Solution:**
Use one of these valid models:
- `gemini-2.0-flash-exp` (recommended - fast and free)
- `gemini-1.5-flash`
- `gemini-1.5-pro`

The code has been updated to use `gemini-2.0-flash-exp` by default.

### Issue 4: Rate Limiting or 503 Errors

**Symptoms:**
- `503 UNAVAILABLE`
- "This model is currently experiencing high demand"

**Solution:**
- Wait a few minutes and try again
- The code includes automatic retry logic (3 attempts)
- If persistent, consider using a different model

---

## Security Best Practices

### DO NOT commit API keys to Git!

The `.env` file is in `.gitignore` for safety.

### For Production Deployment (Azure):

1. **Don't use `.env` file in production**
2. **Use Azure App Service Configuration:**

```powershell
# Set environment variable in Azure:
az webapp config appsettings set --resource-group YOUR_RG \
  --name YOUR_APP_NAME \
  --settings GEMINI_API_KEY="YOUR_API_KEY"
```

3. **Or use Azure Key Vault** for extra security

---

## Verification Checklist

- [ ] Got API key from https://aistudio.google.com/app/apikey
- [ ] Updated `.env` file with new key
- [ ] Restarted the FastAPI server
- [ ] Saw "✅ Gemini API key loaded" in logs
- [ ] Ran `test_gemini_api_key.py` successfully
- [ ] Uploaded a document and signature detection worked

---

## Current Configuration

**File:** `C:\Amazatic\Hackathon Personal\Backend\.env`
```dotenv
GEMINI_API_KEY=AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw
```

**Model Used:** `gemini-2.0-flash-exp`

**Services Using Gemini:**
1. `services/gemini_service.py` - Signature detection & OCR
2. `services/document_processing_agent.py` - AI orchestration
3. `services/classification/gemini_classifier.py` - Document classification

---

## Testing After Fix

### Test 1: Check Environment Variable
```powershell
echo $env:GEMINI_API_KEY
```
Should output: `AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw`

### Test 2: Run API Key Test
```powershell
python test_gemini_api_key.py
```
Should output: `✅ TEST PASSED`

### Test 3: Upload a Document
```powershell
# Use the upload API endpoint
POST /api/documents/upload
```
Check logs for:
```
✅ Gemini Document Analyzer ready!
📤 Sending document to Gemini for comprehensive analysis...
```

---

## Need Help?

If issues persist:

1. Check logs in terminal for detailed error messages
2. Verify API key at: https://aistudio.google.com/app/apikey
3. Try generating a fresh API key
4. Make sure you're using a valid Google account with AI Studio access

---

Last Updated: February 22, 2026

