# CDP Analytics - Conversational Analytics Interface

This is a conversational analytics interface for the AetherSegment CDP, built with **CopilotKit**, **Google ADK**, and **Next.js**. It provides an AI-powered chat interface that can query and analyze customer data from BigQuery.

## 🎯 Features

- **Natural Language Queries**: Ask questions about your customer data in plain English
- **Real-time Data Visualization**: Query results are displayed in beautiful, interactive tables
- **Multiple Analysis Types**:
  - Customer queries with flexible filtering
  - Segment analysis and performance metrics
  - Revenue trends over time
- **Shared State**: Agent results are synchronized with the UI in real-time
- **Professional UI**: Clean, modern interface built with Tailwind CSS

## 📋 Prerequisites

- **Node.js** 18+ (for the frontend)
- **Python** 3.12+ (for the agent backend)
- **Google AI API Key** (for Gemini model)
- **Google Cloud Service Account** (for BigQuery access)
- **BigQuery Dataset** with CDP data

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# This will automatically install Python dependencies via postinstall hook
# Or manually install Python dependencies:
cd agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment Variables

Create a `.env` file in the `ai-cdp/agent/` directory using the template:

```bash
cp ENV_TEMPLATE.txt agent/.env
```

Edit `agent/.env` with your actual credentials:

```env
# Google AI API Key (for Gemini model)
GOOGLE_API_KEY=your_google_ai_api_key_here

# Google Cloud Platform Configuration
GCP_PROJECT_ID=ml-developer-project-fe07
GOOGLE_APPLICATION_CREDENTIALS=../../sa/ml-developer-project-fe07-8b97033e35a7.json

# BigQuery Configuration
BIGQUERY_DATASET=aethersegment_cdp

# Server Configuration (optional)
PORT=8000
```

**Note**: The `GOOGLE_APPLICATION_CREDENTIALS` path is relative to the `agent/` directory.

### 3. Start the Development Server

```bash
# Start both UI and agent together
npm run dev
```

This will start:
- **Frontend (Next.js)**: http://localhost:3000
- **Agent Backend (FastAPI)**: http://localhost:8000

## 📚 Available Scripts

```bash
npm run dev          # Start both UI and agent in development mode
npm run dev:ui       # Start only the Next.js UI
npm run dev:agent    # Start only the ADK agent backend
npm run dev:debug    # Start with debug logging enabled
npm run build        # Build the Next.js app for production
npm run start        # Start the production server
npm run lint         # Run ESLint
npm run install:agent # Manually install Python dependencies
```

## 🧪 Testing the Integration

1. Open http://localhost:3000 in your browser
2. The chat sidebar will be open on the right side
3. Try these example queries:

```
"Show me all customers"
"Query customers with revenue over $1000"
"What are our customer segments?"
"Show revenue trends for the last 30 days"
"Show me the top 20 customers by purchase count"
```

The agent will execute the appropriate BigQuery queries and display results in the main content area.

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Frontend (Next.js + CopilotKit)  │
│   - Port 3000                       │
│   - React UI with chat sidebar      │
│   - Real-time state synchronization │
└───────────────┬─────────────────────┘
                │
                │ AG-UI Protocol
                │ (HTTP)
                │
┌───────────────▼─────────────────────┐
│   Agent Backend (FastAPI + ADK)    │
│   - Port 8000                       │
│   - Google ADK LlmAgent             │
│   - AG-UI Protocol endpoint         │
└───────────────┬─────────────────────┘
                │
                │ BigQuery API
                │
┌───────────────▼─────────────────────┐
│   Google BigQuery                   │
│   - Dataset: aethersegment_cdp      │
│   - Tables: customers, events       │
└─────────────────────────────────────┘
```

## 🛠️ Agent Tools

The CDP Analytics Agent has the following capabilities:

### `query_customers`
Query customer data with flexible filtering and limits.
- **Parameters**: `limit` (int), `filters` (SQL WHERE clause)
- **Example**: Query customers where `total_revenue > 1000` with `limit=20`

### `get_customer_segments`
Get an overview of all customer segments with aggregate statistics.
- **Returns**: Segment names, customer counts, revenue metrics

### `get_revenue_trends`
Analyze revenue trends over a specified time period.
- **Parameters**: `days` (int)
- **Example**: Get trends for last 30 days

### `clear_results`
Clear the displayed results from the main content area.

## 📁 Project Structure

```
ai-cdp/
├── agent/                      # Python agent backend
│   ├── agent.py               # ADK agent with BigQuery tools
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (create this)
├── src/
│   └── app/
│       ├── api/
│       │   └── copilotkit/
│       │       └── route.ts   # CopilotKit API endpoint (AG-UI bridge)
│       ├── page.tsx           # Main CDP analytics UI
│       ├── layout.tsx         # Next.js layout with CopilotKit provider
│       └── globals.css        # Global styles
├── scripts/                   # Setup and run scripts
│   ├── setup-agent.sh         # Install Python dependencies (Linux/Mac)
│   ├── setup-agent.bat        # Install Python dependencies (Windows)
│   ├── run-agent.sh           # Run agent server (Linux/Mac)
│   └── run-agent.bat          # Run agent server (Windows)
├── package.json               # Node.js dependencies and scripts
├── ENV_TEMPLATE.txt           # Environment variable template
└── README.md                  # This file
```

## 🔧 Customization

### Adding New Agent Tools

Edit `agent/agent.py` and add new tool functions:

```python
def your_new_tool(tool_context: ToolContext, param1: str) -> str:
    """
    Description of what your tool does.
    """
    # Your logic here
    result = {"status": "success", "data": "..."}
    
    # Update shared state if needed
    tool_context.state["your_key"] = your_data
    
    return json.dumps(result)

# Add to the agent's tools list
cdp_analytics_agent = LlmAgent(
    name="cdp_analytics_agent",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[query_customers, get_customer_segments, your_new_tool]
)
```

### Customizing the UI

Edit `src/app/page.tsx` to modify:
- The main content layout
- Data table columns and formatting
- Theme colors and styling
- Empty state messages

## 🐛 Troubleshooting

### Agent Connection Issues
**Problem**: Chat shows "I'm having trouble connecting"

**Solution**:
1. Check that the agent is running on port 8000
2. Verify `GOOGLE_API_KEY` is set correctly
3. Check the agent terminal for error messages

### BigQuery Access Issues
**Problem**: "Error querying customers" or permission denied

**Solution**:
1. Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Ensure the service account has BigQuery Data Viewer and Job User roles
3. Check that the dataset name matches (`BIGQUERY_DATASET=aethersegment_cdp`)

### Python Virtual Environment Issues
**Problem**: Python dependencies not found

**Solution**:
```bash
cd agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Port Already in Use
**Problem**: "Address already in use" error

**Solution**:
```bash
# Kill process on port 8000 (agent)
# Linux/Mac: lsof -ti:8000 | xargs kill -9
# Windows: netstat -ano | findstr :8000, then taskkill /PID <pid> /F

# Kill process on port 3000 (frontend)
# Similar process for port 3000
```

## 📖 Documentation Links

- **CopilotKit Docs**: https://docs.copilotkit.ai
- **Google ADK Docs**: https://google.github.io/adk-docs/
- **AG-UI Protocol**: https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui
- **Next.js Docs**: https://nextjs.org/docs
- **BigQuery API**: https://cloud.google.com/bigquery/docs

## 🤝 Integration with Main CDP

This conversational analytics interface is designed to work alongside the main CDP application:

- **Main CDP Backend**: Flask app on port 5000
- **Main CDP Frontend**: HTML/JS served via Flask
- **Analytics Chat Backend**: FastAPI on port 8000 (this project)
- **Analytics Chat Frontend**: Next.js on port 3000 (this project)

All services can run concurrently and share the same BigQuery dataset.

## 📝 License

MIT License - See parent project's LICENSE file for details.
