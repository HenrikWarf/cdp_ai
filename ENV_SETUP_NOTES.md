# Environment Setup Notes

## Your Existing .env File

Your project already has a `.env` file in the root directory with all necessary GCP and BigQuery credentials.

## What the Chat Agent Uses

The conversational analytics chat agent uses **all variables from your existing `.env` file**:

### Existing Variables (Already Configured)
- ✅ `GOOGLE_APPLICATION_CREDENTIALS` - Service account key for BigQuery/GCP access
- ✅ `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- ✅ `BIGQUERY_DATASET` - Your BigQuery dataset name
- ✅ `GOOGLE_CLOUD_REGION` - GCP region (optional)

### New Variable (Add to Existing .env)
- ➕ `GOOGLE_API_KEY` - Required for Gemini AI (chat agent)

## How It Works

All components load from the **same root `.env` file**:

```
ai_cdp/
├── .env                          ← Your existing file (add GOOGLE_API_KEY here)
├── backend/
│   ├── app.py                    ← Flask API (uses .env)
│   ├── config.py                 ← Config class (loads .env)
│   └── chat_agent/
│       ├── main.py               ← Chat agent (uses .env)
│       └── tools.py              ← BigQuery tools (uses .env)
└── run_chat.py                   ← Startup script (loads .env)
```

## Environment Variable Flow

### 1. Root .env File
Located at: `ai_cdp/.env`

Contains all configuration:
```env
# GCP Authentication (already configured)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_DATASET=aethersegment_cdp

# Gemini API Key (add this)
GOOGLE_API_KEY=your-google-api-key-here
```

### 2. Config Class
`backend/config.py` loads variables using `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads from root .env

class Config:
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET')
    # ... etc
```

### 3. Chat Agent Components
All components explicitly load from root `.env`:

**run_chat.py:**
```python
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
```

**backend/chat_agent/main.py:**
```python
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
# Uses Config.GOOGLE_APPLICATION_CREDENTIALS
# Uses Config.GOOGLE_CLOUD_PROJECT
# Uses Config.BIGQUERY_DATASET
```

**backend/chat_agent/tools.py:**
```python
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
# Passes Config values to BigQueryService
```

## Why Two Keys?

### GOOGLE_APPLICATION_CREDENTIALS (Service Account)
- **Purpose**: Authenticate to GCP services (BigQuery, Vertex AI)
- **Format**: Path to JSON file
- **Used by**: BigQuery client, GCP Python libraries
- **Scope**: Full GCP API access (BigQuery read/write)
- **Already configured** ✅

### GOOGLE_API_KEY (API Key)
- **Purpose**: Authenticate to Google AI services (Gemini)
- **Format**: String API key
- **Used by**: Google ADK, Gemini API
- **Scope**: Gemini model access only
- **Needs to be added** ➕

## Service Account vs API Key

Both are needed for the chat agent:

| Component | Auth Method | Used For |
|-----------|-------------|----------|
| BigQuery queries | Service Account (JSON) | Query customer data |
| Gemini AI | API Key | Natural language understanding |

## Adding GOOGLE_API_KEY

### Step 1: Get API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Step 2: Add to .env
Open your existing `.env` file:
```bash
# Windows
notepad .env

# Mac/Linux
nano .env
```

Add the line:
```env
GOOGLE_API_KEY=your-actual-api-key-here
```

Save and close.

### Step 3: Verify
Run the chat agent to verify:
```bash
python run_chat.py
```

You should see:
```
✓ Loaded environment variables from: C:\...\ai_cdp\.env
✓ Google API Key: Found (AIzaSyBxxx...)
✓ GCP Project: your-project-id
✓ BigQuery Dataset: aethersegment_cdp
✓ Service Account: path/to/service-account.json
```

## Troubleshooting

### "GOOGLE_API_KEY not found"
**Solution**: Make sure you added it to the root `.env` file, not a different location.

### "Service account file not found"
**Problem**: Path in `GOOGLE_APPLICATION_CREDENTIALS` is wrong
**Solution**: 
1. Check the path in your `.env` file
2. Verify the file exists at that location
3. Use absolute path (e.g., `C:\Users\...` on Windows)

### Chat agent can't query BigQuery
**Problem**: Service account doesn't have BigQuery permissions
**Solution**: Your service account should already work (it works for Flask API). The chat agent uses the same credentials.

### Variables not loading
**Problem**: .env file location wrong
**Solution**: Ensure `.env` is in project root (`ai_cdp/.env`), not in subdirectories

## Summary

✅ **One .env file** - Root directory only
✅ **Existing variables** - All reused by chat agent  
✅ **One new variable** - Just add GOOGLE_API_KEY
✅ **No duplication** - All components share same configuration
✅ **Consistent paths** - All references point to root .env

Your existing BigQuery setup works perfectly with the new chat agent!

