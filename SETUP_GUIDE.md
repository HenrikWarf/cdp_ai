# AetherSegment AI - Quick Setup Guide

This guide will help you set up AetherSegment AI in under 15 minutes.

## Prerequisites Checklist

- [ ] Python 3.9 or higher installed
- [ ] Google Cloud Platform account created
- [ ] Git installed (optional)

## Step-by-Step Setup

### 1. Python Environment (2 minutes)

```bash
# Navigate to project directory
cd ai_cdp

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Checkpoint**: You should see packages installing. This may take 2-3 minutes.

### 2. Google Cloud Platform Setup (5 minutes)

#### A. Create GCP Project
1. Go to https://console.cloud.google.com
2. Click "Select a project" → "New Project"
3. Name it "aethersegment-ai" (or your choice)
4. Click "Create"
5. Note your **Project ID** (you'll need this)

#### B. Enable Required APIs
1. In the GCP Console, search for "BigQuery API"
2. Click "Enable"
3. Search for "Vertex AI API"
4. Click "Enable"
5. Wait for confirmation

#### C. Create Service Account
1. Navigate to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: `aethersegment-service`
4. Click "Create and Continue"
5. Grant roles:
   - "BigQuery Admin"
   - "Vertex AI User"
6. Click "Continue" → "Done"

#### D. Generate Key
1. Find your new service account in the list
2. Click the three dots → "Manage Keys"
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Click "Create"
6. Save the downloaded JSON file to your project folder as `gcp-credentials.json`

**Checkpoint**: You should have a JSON file downloaded.

### 3. Configuration (3 minutes)

#### Create .env file

**Windows (PowerShell):**
```powershell
Copy-Item env_template.txt .env
notepad .env
```

**macOS/Linux:**
```bash
cp env_template.txt .env
nano .env
```

#### Edit the .env file with your values:

```env
# Paste your GCP Project ID here
GOOGLE_CLOUD_PROJECT=aethersegment-ai

# Set your GCP region (us-central1 is recommended)
GOOGLE_CLOUD_REGION=us-central1

# This stays the same
BIGQUERY_DATASET=aethersegment_cdp

# Update this path to where you saved the JSON file
# Windows example:
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourName\Documents\projects\ai_cdp\gcp-credentials.json
# macOS/Linux example:
# GOOGLE_APPLICATION_CREDENTIALS=/Users/yourname/projects/ai_cdp/gcp-credentials.json

# Leave these as-is for development
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:5500
```

**Checkpoint**: Your .env file is saved with all required values.

### 4. Generate Test Data (3 minutes)

```bash
# Make sure virtual environment is activated
python scripts/generate_data.py
```

You should see:
```
Creating BigQuery dataset and tables...
Generating 10,000 customer profiles...
✓ Generated 10,000 customers
...
✓ Data Generation Complete!
```

**Checkpoint**: Data is loaded into BigQuery. You can verify by checking the BigQuery console.

### 5. Start the Application (1 minute)

#### Terminal 1 - Start Backend:
```bash
python backend/app.py
```

You should see:
```
============================================================
  AetherSegment AI - Backend Server
============================================================
  Running on: http://localhost:5000
```

#### Terminal 2 - Start Frontend:

**Option A: VS Code Live Server** (Easiest)
1. Install "Live Server" extension in VS Code
2. Right-click `frontend/index.html`
3. Click "Open with Live Server"

**Option B: Python HTTP Server**
```bash
cd frontend
python -m http.server 8000-
# Then open http://localhost:8000 in browser
```

**Checkpoint**: You can access the application in your browser!

## 🎉 You're Done!

### Test It Out

1. Open the frontend (http://localhost:8000 or http://127.0.0.1:5500)
2. Click one of the example chips (e.g., "Abandoned Cart Recovery")
3. Click "Analyze Campaign"
4. Wait 3-5 seconds for AI analysis
5. Review the recommendations
6. Click "Create Segment & Get Customers"
7. See your personalized customer segment!

## Common Issues & Solutions

### Issue: "GOOGLE_CLOUD_PROJECT is required"
**Solution**: Check your .env file - make sure the GCP project ID is correct

### Issue: "Could not connect to backend"
**Solution**: 
- Make sure backend is running (`python backend/app.py`)
- Check that port 5000 is not in use
- Verify no firewall is blocking localhost

### Issue: "Failed to create dataset" or "Vertex AI initialization error"
**Solution**:
- Verify GCP credentials path in .env is correct
- Check that service account has both "BigQuery Admin" and "Vertex AI User" roles
- Make sure both BigQuery API and Vertex AI API are enabled
- Verify GOOGLE_CLOUD_REGION is set correctly

### Issue: Data generation is slow
**Solution**: This is normal! It takes 2-3 minutes to generate and upload 10,000+ records.

### Issue: Frontend shows CORS error
**Solution**:
- Make sure backend is running
- Update `ALLOWED_ORIGINS` in .env to include your frontend URL
- Restart the backend after changing .env

## Next Steps

1. **Explore the UI**: Try different campaign objectives
2. **Check BigQuery**: View your data in the GCP console
3. **API Testing**: Use the API endpoints directly with curl or Postman
4. **Customize**: Modify trigger types, add more data, adjust models

## Getting Help

- Check the main README.md for detailed documentation
- Review the troubleshooting section
- Examine console logs for error messages
- Verify all environment variables are set correctly

## Cleanup (Optional)

If you want to remove everything:

```bash
# Delete BigQuery dataset
# In GCP Console: BigQuery → aethersegment_cdp → Delete

# Remove virtual environment
deactivate
rm -rf venv  # macOS/Linux
# or
rmdir /s venv  # Windows

# Remove generated files
rm .env
rm gcp-credentials.json
```

---

**Happy segmenting!** 🚀

