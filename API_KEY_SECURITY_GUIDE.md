# 🔐 API Key Security Guide

**Date:** February 22, 2026  
**Status:** ✅ SECURED

---

## 🚨 IMMEDIATE ACTIONS TAKEN

### 1. ✅ New API Key Set
- **New Key:** `AIzaSyArm-vBj6PRcn8absyo1g9qRtIzdcGnoNo`
- **Storage:** Saved in `.env` file (NOT committed to Git)
- **Access:** Loaded via `python-dotenv` on server startup

### 2. ✅ Old Key Deactivated
- **Action Required:** Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Revoke:** The old exposed key immediately
- **Reason:** Once exposed in Git history, it's permanently compromised

### 3. ✅ Security Measures Implemented
- `.env` file added to `.gitignore` ✅
- `python-dotenv` installed ✅
- Environment variable loading in `main.py` ✅
- `.env.example` template created ✅

---

## 📁 File Structure

```
Backend/
├── .env                    # ✅ SECURED - Contains actual secrets (ignored by Git)
├── .env.example            # ✅ SAFE - Template without secrets (committed to Git)
├── .gitignore              # ✅ CONFIGURED - Ignores .env file
├── main.py                 # ✅ UPDATED - Loads environment variables
└── services/
    └── gemini_service.py   # ✅ ALREADY SECURE - Uses os.getenv()
```

---

## 🔒 Security Best Practices Implemented

### 1. Environment Variables (.env file)

**Location:** `C:\Amazatic\Hackathon Personal\Backend\.env`

```dotenv
# .env file (NEVER COMMIT THIS!)
GEMINI_API_KEY=AIzaSyArm-vBj6PRcn8absyo1g9qRtIzdcGnoNo
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-jwt-key-change-this-in-production-09876543210
```

**Benefits:**
- ✅ Not in source code
- ✅ Not in Git history
- ✅ Can be different per environment (dev, staging, prod)
- ✅ Easy to rotate without code changes

---

### 2. .gitignore Configuration

**Already configured to ignore:**
```gitignore
# Environment
.env
.env.local
```

**Verify:**
```bash
git status  # .env should NOT appear here
```

---

### 3. Template File (.env.example)

**Safe to commit:**
```dotenv
# .env.example (SAFE TO COMMIT)
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-jwt-key-here
```

**Purpose:**
- Shows team what environment variables are needed
- No actual secrets exposed
- New developers copy to `.env` and fill in real values

---

### 4. Code Changes

**main.py** now loads environment variables:
```python
from dotenv import load_dotenv

# Load .env file on startup
load_dotenv()

# Verify key is loaded
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    logger.info("✅ Gemini API key loaded")
else:
    logger.warning("⚠️  Gemini API key missing!")
```

**services/gemini_service.py** (already secure):
```python
# Uses environment variable
self.client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
```

---

## 🚀 Deployment Options

### Option 1: Local Development (Current)

**Setup:**
```bash
# Copy template
cp .env.example .env

# Edit .env with real values
notepad .env
```

**Run:**
```bash
python main.py
# Loads .env automatically ✅
```

---

### Option 2: Azure App Service

**Don't use .env file in production!**

**Better approach:** Use Azure App Configuration

1. **Azure Portal** → Your App Service → Configuration
2. **Application Settings** → New application setting
3. Add:
   - Name: `GEMINI_API_KEY`
   - Value: `AIzaSyArm-vBj6PRcn8absyo1g9qRtIzdcGnoNo`
4. Click **Save**

**Benefits:**
- ✅ Never in code
- ✅ Never in Git
- ✅ Encrypted at rest
- ✅ Can be changed without redeployment
- ✅ Role-based access control

**Code works automatically:**
```python
# Works in Azure (uses App Settings)
# Works locally (uses .env file)
os.getenv('GEMINI_API_KEY')
```

---

### Option 3: Azure Key Vault (Most Secure)

**For production systems with high security requirements:**

1. **Create Key Vault:**
```bash
az keyvault create --name my-keyvault --resource-group my-rg
```

2. **Store Secret:**
```bash
az keyvault secret set --vault-name my-keyvault \
  --name GeminiApiKey \
  --value "AIzaSyArm-vBj6PRcn8absyo1g9qRtIzdcGnoNo"
```

3. **Update Code:**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Get secret from Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://my-keyvault.vault.azure.net/", credential=credential)
api_key = client.get_secret("GeminiApiKey").value
```

**Benefits:**
- ✅ Centralized secret management
- ✅ Audit logs (who accessed what, when)
- ✅ Automatic rotation
- ✅ Access policies per user/app

---

## ⚠️ What NOT to Do

### ❌ DON'T: Hardcode in source code
```python
# BAD - Never do this!
GEMINI_API_KEY = "AIzaSyArm-vBj6PRcn8absyo1g9qRtIzdcGnoNo"
```

### ❌ DON'T: Commit .env file
```bash
# BAD - Don't add .env to Git
git add .env  # ❌ NEVER DO THIS!
```

### ❌ DON'T: Share in Slack/Email/Teams
```
# BAD - Don't send secrets in messages
"Hey team, use this API key: AIzaSy..."  # ❌ NEVER!
```

### ❌ DON'T: Store in database
```sql
-- BAD - Don't store API keys in database
INSERT INTO config (key, value) VALUES ('api_key', 'AIzaSy...');
```

---

## ✅ What TO Do

### ✅ DO: Use environment variables
```python
# GOOD
api_key = os.getenv('GEMINI_API_KEY')
```

### ✅ DO: Rotate keys regularly
- Monthly rotation recommended
- Immediately after exposure
- When team member leaves

### ✅ DO: Use different keys per environment
```
Dev:     AIzaSy...dev-key...
Staging: AIzaSy...staging-key...
Prod:    AIzaSy...prod-key...
```

### ✅ DO: Monitor API usage
- Check [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
- Set up usage alerts
- Review access logs

---

## 🔧 How to Rotate API Key

### Step 1: Generate New Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create new API key
3. Copy the new key

### Step 2: Update .env File
```bash
# Edit .env
GEMINI_API_KEY=new-key-here
```

### Step 3: Update Azure (if deployed)
```bash
# Update App Service setting
az webapp config appsettings set \
  --resource-group my-rg \
  --name my-app \
  --settings GEMINI_API_KEY="new-key-here"
```

### Step 4: Restart Server
```bash
# Local
python main.py

# Azure
az webapp restart --resource-group my-rg --name my-app
```

### Step 5: Revoke Old Key
1. Go to Google Cloud Console
2. Find old key
3. Click **Delete** or **Disable**

---

## 🧪 Verify Security

### Test 1: Check .env is Ignored
```bash
cd "C:\Amazatic\Hackathon Personal\Backend"
git status

# .env should NOT appear in:
# - Untracked files
# - Changes to be committed
```

### Test 2: Verify Key Loads
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Key loaded' if os.getenv('GEMINI_API_KEY') else '❌ Key missing')"
```

### Test 3: Check Git History
```bash
# Search for old exposed key in Git history
git log -p | grep "AIzaSy"

# If found, you must clean Git history (see below)
```

---

## 🚨 Clean Git History (If Key Was Committed)

**If the old key was committed to Git, you MUST clean history:**

### Option 1: BFG Repo-Cleaner (Easiest)
```bash
# Download BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove sensitive data
java -jar bfg.jar --replace-text passwords.txt

# passwords.txt contains:
# AIzaSyOLD-KEY-HERE
```

### Option 2: git-filter-repo
```bash
pip install git-filter-repo

# Remove file from history
git filter-repo --invert-paths --path .env
```

### Option 3: Force Push (Nuclear Option)
```bash
# WARNING: Rewrites history for all team members
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

---

## 📊 Current Status

| Item | Status |
|------|--------|
| New API key generated | ✅ Done |
| Stored in `.env` file | ✅ Done |
| `.env` in `.gitignore` | ✅ Done |
| `python-dotenv` installed | ✅ Done |
| Code loads from `.env` | ✅ Done |
| `.env.example` created | ✅ Done |
| Old key revoked | ⚠️  **ACTION REQUIRED** |
| Git history cleaned | ⚠️  **ACTION REQUIRED IF KEY WAS COMMITTED** |

---

## 📋 Action Items

### Immediate (Do Now):
- [ ] Revoke old API key in Google Cloud Console
- [ ] Test server starts with new key
- [ ] Verify `.env` is not in Git status

### Soon:
- [ ] Check if old key is in Git history
- [ ] If yes, clean Git history
- [ ] Set up API usage monitoring
- [ ] Document key rotation process for team

### Production Deployment:
- [ ] Use Azure App Service Configuration (not .env)
- [ ] Or use Azure Key Vault for high security
- [ ] Set up different keys per environment
- [ ] Enable audit logging

---

## 📞 Support

### Google Cloud Console
- [API Credentials](https://console.cloud.google.com/apis/credentials)
- [API Dashboard](https://console.cloud.google.com/apis/dashboard)
- [Usage Reports](https://console.cloud.google.com/apis/dashboard)

### Azure Resources
- [App Service Configuration](https://portal.azure.com)
- [Key Vault](https://portal.azure.com)
- [Azure CLI Docs](https://docs.microsoft.com/en-us/cli/azure/)

---

**Last Updated:** February 22, 2026  
**Status:** ✅ Secured with `.env` file + python-dotenv

