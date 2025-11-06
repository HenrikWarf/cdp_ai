# 🎉 Getting Started with CDP Conversational Analytics

You now have a fully functional conversational analytics interface! Here's everything you need to know to get it running.

## 📋 What You Need

### Already Installed in Your Project
- ✅ Python 3.13 with virtual environment
- ✅ Google Cloud service account JSON file in `sa/`
- ✅ BigQuery dataset `aethersegment_cdp` with customer data

### Need to Install/Configure
- [ ] **Node.js** (version 18+) - [Download here](https://nodejs.org/)
- [ ] **Google AI API Key** - [Get free key here](https://makersuite.google.com/app/apikey)

## 🚀 Step-by-Step Setup (5 minutes)

### Step 1: Install Node.js Dependencies

Open a terminal in the `ai-cdp/` folder:

```bash
cd ai-cdp
npm install
```

This will:
- Install all Node.js packages for the frontend
- Automatically setup a Python virtual environment in `agent/.venv/`
- Install all Python dependencies for the backend

### Step 2: Create Environment File

```bash
# Windows
Copy-Item ENV_TEMPLATE.txt agent\.env

# Mac/Linux
cp ENV_TEMPLATE.txt agent/.env
```

### Step 3: Add Your API Key

Edit `agent/.env` and add your Google AI API key:

```env
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=AIzaSy...your_actual_key_here

# These should already be correct from your main CDP:
GCP_PROJECT_ID=ml-developer-project-fe07
GOOGLE_APPLICATION_CREDENTIALS=../../sa/ml-developer-project-fe07-8b97033e35a7.json
BIGQUERY_DATASET=aethersegment_cdp
```

**Note**: The paths are relative to the `agent/` directory, so `../../sa/` points to your service account file.

### Step 4: Start Everything

```bash
npm run dev
```

This single command starts:
- **Agent Backend** on http://localhost:8000
- **Frontend UI** on http://localhost:3000

You should see output like:

```
[agent] CDP Analytics Agent with Google ADK + AG-UI Protocol
[agent] ✓ Google API Key: AIzaSy...
[agent] ✓ GCP Project: ml-developer-project-fe07
[agent] ✓ BigQuery Dataset: aethersegment_cdp
[agent] 🚀 Starting server on http://localhost:8000
[ui]    ▲ Next.js 15.3.2
[ui]    - Local:        http://localhost:3000
```

### Step 5: Open and Test

1. Open http://localhost:3000 in your browser
2. You'll see:
   - A chat sidebar on the right
   - An empty main content area with welcome message
3. Try your first query in the chat:
   ```
   Show me all customers
   ```
4. Watch as the agent:
   - Processes your request
   - Queries BigQuery
   - Displays results in a beautiful table in the main area

## 🎯 Try These Queries

Once it's running, try these example queries:

### Customer Queries
```
"Show me all customers"
"Query customers with revenue over $1000"
"Show me customers who made more than 5 purchases"
"Find customers in the high_value segment"
```

### Analytics Queries
```
"What are our customer segments?"
"Show me segment performance"
"Which segment has the highest average revenue?"
```

### Trend Analysis
```
"Show revenue trends for the last 7 days"
"What's our revenue pattern for the past 30 days?"
"Show me daily purchase trends for the last 2 weeks"
```

### Conversational Follow-ups
```
After seeing results, you can ask:
"What's the average revenue in this group?"
"How many of these are in the high_value segment?"
"Clear the results"
```

## 📂 Project Structure

Here's what was created in the `ai-cdp/` folder:

```
ai-cdp/
├── agent/
│   ├── agent.py              ← 🤖 The AI agent with BigQuery tools
│   ├── requirements.txt      ← Python dependencies
│   └── .env                  ← ⚙️  YOUR CONFIG (create this!)
│
├── src/app/
│   ├── page.tsx              ← 🎨 Main UI with chat and data tables
│   ├── layout.tsx            ← CopilotKit provider setup
│   └── api/copilotkit/
│       └── route.ts          ← API bridge between UI and agent
│
├── package.json              ← Node.js dependencies
├── README.md                 ← Full documentation
├── QUICKSTART.md             ← Quick reference guide
├── GETTING_STARTED.md        ← This file!
└── IMPLEMENTATION_SUMMARY.md ← Technical details
```

## 🛠️ Useful Commands

```bash
# Start everything (recommended)
npm run dev

# Start only the frontend
npm run dev:ui

# Start only the agent
npm run dev:agent

# Reinstall Python dependencies
npm run install:agent

# Build for production
npm run build

# Run production build
npm run start
```

## 🔍 How It Works

1. **You type a question** in the chat sidebar
2. **The agent (Gemini 2.5 Flash)** understands your intent
3. **It selects the right tool** (e.g., `query_customers`)
4. **Queries BigQuery** with the appropriate SQL
5. **Results appear** in the main content area as formatted tables
6. **Agent responds** with insights and suggestions

All of this happens in real-time with seamless state synchronization!

## 🐛 Common Issues

### "npx: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### "Cannot connect to agent"
**Solution**: 
1. Check that `npm run dev` is running in the `ai-cdp/` folder
2. Verify your `GOOGLE_API_KEY` is set in `agent/.env`
3. Look for errors in the terminal where you ran `npm run dev`

### "BigQuery access denied"
**Solution**:
1. Your service account JSON file should be at: `sa/ml-developer-project-fe07-8b97033e35a7.json`
2. The path in `.env` is relative to `agent/`: `../../sa/filename.json`
3. Make sure the service account has BigQuery permissions

### "Port 8000 already in use"
**Solution**: 
Something else is using port 8000. Either:
- Stop the other service
- Or change the port in `agent/.env`: `PORT=8001`

### Fresh Start
If things get messy, clean restart:
```bash
# Stop everything (Ctrl+C)
# Then:
cd ai-cdp
rm -rf node_modules agent/.venv
npm install
npm run dev
```

## 💡 Tips for Best Experience

1. **Be conversational**: The agent understands natural language!
   - Good: "Show me our top customers"
   - Also good: "Who are our best customers?"
   - Also good: "List high-value customers"

2. **Ask follow-ups**: The agent maintains context
   - "Now show me only the ones from the high_value segment"
   - "What's the average purchase count?"

3. **Use the main area**: Query results appear in the main content, not in chat
   - The agent will tell you what it found
   - But the detailed data is in the tables to the left

4. **Clear when needed**: 
   - Say "clear results" or "start fresh" to clean the display

## 🎓 Next Steps

Once you're comfortable:

1. **Explore the code**: 
   - `agent/agent.py` - Add new BigQuery tools
   - `src/app/page.tsx` - Customize the UI

2. **Read the docs**:
   - `README.md` - Full documentation
   - `IMPLEMENTATION_SUMMARY.md` - Technical deep dive

3. **Extend it**:
   - Add new agent tools for different analyses
   - Create custom table visualizations
   - Add charts and graphs

4. **Integrate**:
   - Link to your main CDP workflows
   - Create segments from chat queries
   - Export data for campaigns

## 🎉 You're All Set!

You now have a powerful AI-powered analytics interface that can:
- ✅ Query your BigQuery data in natural language
- ✅ Display results in beautiful, formatted tables
- ✅ Provide insights and suggestions
- ✅ Handle follow-up questions with context
- ✅ Work alongside your existing CDP application

**Enjoy exploring your data! 🚀**

---

Need more help? Check:
- `README.md` for comprehensive documentation
- `IMPLEMENTATION_SUMMARY.md` for architecture details
- Or ask in the chat - the agent might surprise you! 😉

