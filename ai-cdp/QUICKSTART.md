# 🚀 Quick Start Guide - CDP Analytics

Get up and running with the Conversational Analytics interface in 5 minutes!

## Step 1: Install Node.js Dependencies

```bash
cd ai-cdp
npm install
```

This will automatically install both Node.js and Python dependencies.

## Step 2: Configure Environment

Create the environment file:

```bash
# Windows PowerShell
Copy-Item ENV_TEMPLATE.txt agent\.env

# Linux/Mac
cp ENV_TEMPLATE.txt agent/.env
```

Edit `agent/.env` with your credentials:

```env
GOOGLE_API_KEY=your_google_api_key_from_makersuite
GCP_PROJECT_ID=ml-developer-project-fe07
GOOGLE_APPLICATION_CREDENTIALS=../../sa/ml-developer-project-fe07-8b97033e35a7.json
BIGQUERY_DATASET=aethersegment_cdp
```

**Important**: 
- Get your `GOOGLE_API_KEY` from: https://makersuite.google.com/app/apikey
- The service account path is relative to the `agent/` directory
- Use the same service account as your main CDP application

## Step 3: Start Everything

```bash
npm run dev
```

This starts:
- **Frontend**: http://localhost:3000
- **Agent**: http://localhost:8000

## Step 4: Try It Out!

Open http://localhost:3000 and try these queries in the chat:

```
"Show me all customers"
"What are our customer segments?"
"Show revenue trends for the last 7 days"
"Query customers with revenue over $1000"
```

## 🎉 That's It!

You should see:
- A chat interface on the right side
- Query results displayed in the main content area
- Real-time updates as the agent executes queries

## Common Issues

### "npx not found"
→ Install Node.js from https://nodejs.org/

### "Module not found: uvicorn"
→ Run `npm run install:agent` to reinstall Python dependencies

### "BigQuery permission denied"
→ Check that your service account has BigQuery Data Viewer and Job User roles

### "GOOGLE_API_KEY not set"
→ Make sure you created `agent/.env` from the template and added your API key

## Need Help?

Check the full README.md for detailed documentation and troubleshooting.

