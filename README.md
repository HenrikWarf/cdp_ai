# AetherSegment AI - Home Furnishing CDP Prototype

An AI-first Customer Data Platform designed for a fictional home furnishing retailer (similar to IKEA). This prototype demonstrates intelligent customer segmentation using LLM-powered campaign analysis and uplift modeling.

## 🏢 Business Context

**Company Type**: Home Furnishing Retailer  
**Product Categories**:
- Living Room (Sofas, Armchairs, Coffee Tables, TV Stands, Bookshelves)
- Bedroom (Bed Frames, Mattresses, Wardrobes, Nightstands, Dressers)
- Kitchen & Dining (Dining Tables, Chairs, Bar Stools, Cookware)
- Office (Desks, Office Chairs, Filing Cabinets, Desk Lamps)
- Storage & Organization (Shelving Units, Storage Boxes, Drawer Units)
- Bathroom (Cabinets, Mirror Cabinets, Towel Racks)
- Outdoor (Patio Sets, Garden Chairs, Outdoor Tables)
- Lighting (Floor Lamps, Table Lamps, Ceiling Lights)
- Textiles (Curtains, Cushions, Throw Blankets, Bedding)
- Decoration (Wall Art, Vases, Picture Frames, Candles)

**Global Presence**:
- 🇺🇸 United States (40% of customers) - 6 cities
- 🇬🇧 United Kingdom (25% of customers) - 5 cities
- 🇨🇦 Canada (20% of customers) - 5 cities
- 🇦🇺 Australia (15% of customers) - 5 cities

## 🏗️ Architecture

### Tech Stack
- **Data Layer**: Google BigQuery (GCP)
- **Backend**: Python (Flask + FastAPI), Pandas, NumPy
- **AI/LLM**: Google Gemini 2.5 Flash via Vertex AI + Google ADK
- **Agent Framework**: Google ADK (Agent Development Kit) for conversational queries
- **Frontend**: Vanilla HTML/CSS/JavaScript (Modular)
- **Deployment**: Local development server

### Application Pages

The platform consists of three main applications:

1. **📊 Overview Dashboard** (`index.html`)
   - Landing page with key metrics and insights
   - Real-time customer statistics from BigQuery
   - Campaign opportunities identification
   - Geographic and value segment distribution
   - Data health monitoring

2. **🎯 Campaign Segmentation** (`campaign-segmentation.html`)
   - AI-powered campaign analysis and segmentation
   - Natural language campaign input
   - Multi-stage segment refinement workflow
   - Trigger optimization and selection
   - Export and activation capabilities

3. **💬 Conversational Analytics** (Next.js App - `ai-cdp/`)
   - **NEW!** Full-featured conversational interface powered by CopilotKit + Google ADK + Gemini 2.5 Flash
   - Modern Next.js frontend with real-time state synchronization via AG-UI Protocol
   - Chat sidebar with professional UI and data tables in main content area
   - Natural language queries for customers, segments, and revenue trends
   - Multi-turn conversations with context awareness
   - Runs on FastAPI backend (port 8000) + Next.js frontend (port 3000)
   - See `ai-cdp/README.md` and `ai-cdp/QUICKSTART.md` for setup

### Key Components

1. **Campaign Intent Interpreter** - Gemini-powered natural language processor
2. **Causal Segmentation Engine** - Uplift score simulation for trigger optimization
3. **Conversational Analytics Agent** - **NEW!** ADK-powered agent with CopilotKit frontend for natural language data queries (see `ai-cdp/`)
4. **BigQuery Data Layer** - Synthetic customer dataset with rich behavioral attributes
5. **REST API** - Flask (port 5000) for campaigns/segments + FastAPI (port 8000) for conversational analytics
6. **Modular UI** - Shared navigation (HTML/CSS/JS) + Next.js app for conversational analytics

## 📊 Data Model

### BigQuery Tables

#### `customers` (10,000 records)
- Customer identity and demographics
- Location data (city, country)
- CLV scores (0-1 scale, with business-friendly interpretation)
- Acquisition source and creation date

#### `transactions` (50,000+ records)
- Purchase history with realistic furniture pricing
- Product categories and names
- Order values ($10-$2,500 depending on category)

#### `behavioral_events` (100,000+ records)
- Website/app interactions
- Product views, cart actions, wishlist additions
- Session duration and engagement metrics
- **New**: Room planner usage, AR views, stock checks

#### `abandoned_carts` (2,000+ records)
- Cart abandonment data (70% within last 7 days)
- Multi-item carts with furniture products
- Cart values and item details

#### `campaign_history` (20+ campaigns)
- Historical campaign performance
- Control/treatment groups for uplift modeling
- Conversion tracking

#### `customer_scores`
- ML-derived propensity scores
- Discount sensitivity, free shipping sensitivity
- Churn probability, content engagement
- Exclusivity seeker flags

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Google Cloud Project with BigQuery enabled
- Service account with BigQuery permissions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (or copy from `env_template_chat.txt`):

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
BIGQUERY_DATASET=aethersegment_cdp
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Google API Key (Required for Conversational Analytics)
# Get from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# CORS Configuration
ALLOWED_ORIGINS=*
```

**Note**: The `GOOGLE_API_KEY` is required for the new Conversational Analytics feature.

### 3. Generate Initial Data

```bash
# Generate all synthetic data (10,000 customers, 50K+ transactions, etc.)
python scripts/generate_data.py
```

This will:
- Create all BigQuery tables
- Generate 10,000 customer profiles across 4 countries
- Create 50,000+ furniture purchase transactions
- Generate 100,000+ behavioral events
- Create 2,000+ abandoned carts
- Populate customer propensity scores

### 4. Start All Services

#### Option A: Automated Startup (Recommended)

Start all services with one command:

**Windows:**
```powershell
.\start_services.ps1
```

**Mac/Linux:**
```bash
chmod +x start_services.sh  # First time only
./start_services.sh
```

This will automatically start:
- Flask API (Port 5000)
- Chat Agent (Port 8000)
- Frontend (Port 5500)
- Open your browser to the application

To stop all services:
```bash
.\stop_services.ps1    # Windows
./stop_services.sh     # Mac/Linux
```

#### Option B: Manual Startup

If you prefer to start services manually, you need **three** terminals:

**Terminal 1: Main Flask API (Port 5000)**
```bash
python run.py
```

**Terminal 2: Frontend (Port 5500)**
```bash
cd frontend
python -m http.server 5500
```

**Optional - Terminal 3: Conversational Analytics (Ports 8000 + 3000)**
```bash
cd ai-cdp
npm run dev
```
This starts both the agent backend (port 8000) and Next.js frontend (port 3000).
See `ai-cdp/QUICKSTART.md` for detailed setup instructions.

See `RUNNING_SERVICES.md` for detailed service management guide.

### 5. Access the Application

If you used the automated startup scripts, your browser should open automatically to:
```
http://localhost:5500/index.html
```

If starting manually, the frontend will be available at the port you specified (5500 in the example above).

**Alternative options for serving frontend:**
- Use VS Code Live Server extension
- Use Python's built-in server: `cd frontend && python -m http.server 8000`

## 🔄 Near Real-Time Event Generation

To simulate ongoing customer activity and demonstrate near real-time capabilities:

```bash
# Add 500 new events (default)
python scripts/add_realtime_events.py

# Add custom number of events
python scripts/add_realtime_events.py 1000
```

This incremental script:
- ✅ Fetches the last event timestamp from BigQuery
- ✅ Generates new events distributed between then and now
- ✅ Uses realistic furniture browsing behavior patterns
- ✅ Appends events without regenerating existing data
- ✅ Perfect for demonstrating live CDP capabilities

**Tip**: Run this script periodically (e.g., every 5 minutes with a cron job or Task Scheduler) to continuously populate your CDP with fresh activity.

## 🎯 Example Campaign Objectives

Try these natural language campaign objectives:

### Abandoned Cart Recovery
```
"Recover abandoned furniture carts from high-value customers in the last 48 hours 
with a personalized 15% discount to increase conversion by 25%"
```

### Cross-Sell to Recent Buyers
```
"Recommend complementary furniture items to customers who purchased sofas 
in the last 30 days to drive cross-sell revenue by 20%"
```

### Win-Back Lapsed Customers
```
"Re-engage customers with high churn risk who haven't purchased in 90 days 
using exclusive offers to bring back 15%"
```

### New Customer Onboarding
```
"Welcome new customers acquired in the last 7 days with free shipping 
to encourage first purchase and boost repeat rate by 30%"
```

### Geographic Expansion
```
"Target high CLV customers in London and Manchester with exclusive 
new product launches to drive regional sales growth"
```

## 🎨 UI Workflow

### Overview Dashboard (Landing Page)
- **Key Metrics**: Total customers, abandoned carts (7d), avg CLV, at-risk customers
- **Geographic Distribution**: Customer breakdown by country (interactive charts)
- **Value Segments**: High/Medium/Low value customer distribution
- **Campaign Opportunities**: AI-identified segments ready for targeting
- **Behavioral Insights**: Recent activity patterns and top categories
- **Data Health**: Real-time monitoring of data freshness and coverage

### Campaign Segmentation Workflow

#### Step 1: Campaign Input
- Enter natural language campaign objective
- AI interprets intent and extracts structured data

#### Step 2: Campaign Analysis
- View AI interpretation (Campaign Objective Object)
- See full eligible segment with AI-applied filters
- Review segment size, avg CLV, predicted uplift

#### Step 3: Select Trigger & Preview Impact
- Choose from AI-ranked trigger recommendations
- Preview segment impact (before/after trigger filtering)
- Apply trigger filter to narrow to high-response customers

#### Step 4: Refine Segment (Optional)
- Review AI-applied filters and trigger filter
- Add additional custom filters:
  - Location (country, city)
  - Customer value (CLV threshold)
  - Cart value (for abandoned cart campaigns)
- Preview filter impact before applying

#### Step 5: Activate Segment
- Review final segment metrics
- View explainability (why this segment?)
- Create segment and export customer list
- Integration options: JSON, CSV, or API endpoint

## 📡 API Endpoints

### Main Flask API (Port 5000)

#### `GET /api/v1/overview/stats`
Get overview dashboard statistics

**Response**:
```json
{
  "metrics": {
    "total_customers": 10000,
    "abandoned_carts_7d": 3483,
    "avg_clv_score": 0.71,
    "at_risk_customers": 3940
  },
  "geographic_distribution": {...},
  "value_segments": {...},
  "opportunities": [...],
  "behavioral_insights": [...],
  "data_health": {...}
}
```

#### `POST /api/v1/campaigns/analyze`
Analyze natural language campaign objective

**Request**:
```json
{
  "objective": "Recover abandoned carts..."
}
```

**Response**:
```json
{
  "campaign_objective_object": {...},
  "segment_preview": {...},
  "trigger_suggestions": [...]
}
```

#### `POST /api/v1/segments/preview-filters`
Preview impact of additional filters

**Request**:
```json
{
  "campaign_objective_object": {...},
  "new_filters": {
    "location_country": "United Kingdom",
    "clv_min": 0.8
  }
}
```

#### `POST /api/v1/segments/create`
Create final segment with trigger selection

**Request**:
```json
{
  "campaign_objective": "...",
  "override_trigger": "personalized_discount_offer",
  "additional_filters": {...}
}
```

### Conversational Analytics API (Port 8000)

#### `GET /health`
Health check for chat agent

**Response**:
```json
{
  "status": "healthy",
  "agent": "ready"
}
```

#### `GET /`
Agent information and available tools

**Response**:
```json
{
  "status": "healthy",
  "agent": "cdp_analytics_agent",
  "model": "gemini-2.5-flash",
  "tools": 6,
  "tool_names": [
    "query_customers",
    "get_customer_statistics",
    "query_transactions",
    "query_behavioral_events",
    "query_abandoned_carts",
    "get_clv_analysis"
  ]
}
```

#### `POST /chat`
Send a natural language query to the agent

**Request**:
```json
{
  "message": "How many customers do we have?"
}
```

**Response**:
```json
{
  "status": "success",
  "response": "Based on the data, we have 10,000 total customers...",
  "timestamp": "2024-..."
}
```

**Example Queries**:
- "How many customers do we have?"
- "Show me customers from London"
- "What's the average CLV score?"
- "How many abandoned carts in the last 7 days?"
- "Which countries have the highest CLV?"

## 🧠 AI Features

### 1. Campaign Intent Interpretation (Gemini 2.5 Flash)
- Parses natural language into structured Campaign Objective Object
- Extracts: goal, target behavior, metric targets, time constraints
- Maps to standardized trigger types

### 2. Uplift Score Simulation
- Simulates causal effects of different marketing triggers
- Considers customer sensitivity scores
- Factors in CLV, campaign alignment, and trigger effectiveness
- Generates differentiated recommendations

### 3. Dynamic Query Generation
- Builds BigQuery SQL based on AI interpretation
- Handles complex time constraints
- Filters by behavior, value, and engagement

### 4. Explainability
- Shows which filters were auto-applied by AI
- Provides rationale for trigger recommendations
- Displays feature importance and sample profiles

### 5. CLV Score Interpretation
- Converts raw CLV scores (0-1) into business-friendly language
- Classifies customers into value tiers (Premium, Above Average, Average, Below Average)
- Shows comparison to baseline and percentile rankings
- Provides actionable insights for each segment's value profile

### 6. Conversational Analytics (Google ADK + Gemini 2.5 Flash)
- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Tool Selection**: Agent automatically chooses the right BigQuery query tool
- **Structured Data Display**: Results shown as tables, statistics, and insights
- **Context Awareness**: Agent understands customer data domain
- **Six Query Tools**:
  - `query_customers`: Search and filter customer profiles
  - `get_customer_statistics`: Overview metrics and KPIs
  - `query_transactions`: Transaction history analysis
  - `query_behavioral_events`: Behavioral data exploration
  - `query_abandoned_carts`: Cart abandonment tracking
  - `get_clv_analysis`: CLV breakdown by country

### 7. Product Affinity Intelligence
A comprehensive product recommendation and targeting system with three levels:

**Level 1: Category Affinity Scores**
- Calculates affinity scores (0-1) for each product category based on purchase history
- Weighted by both purchase frequency (60%) and spending (40%)
- Tracks 10 furniture categories: Living Room, Bedroom, Kitchen & Dining, Office, Outdoor, Lighting, Storage, Textiles, Bathroom, Decoration

**Level 2: Purchase Profile Enrichment**
- **Favorite Category**: Primary product interest area
- **Secondary Category**: Secondary interest for cross-sell opportunities
- **Cross-Category Shopper**: Flag for customers who purchase across 3+ categories
- **Price Tier Preference**: Budget (<$300), Mid ($300-800), Premium (>$800) based on AOV

**Level 3: Product Association Rules**
- 20+ predefined cross-sell rules based on purchasing patterns
- Association strength (0-1) indicating likelihood of co-purchase
- Common sequence tracking (1=immediate, 2=next purchase, 3=future)
- Examples:
  - Living Room → Lighting (0.75 strength)
  - Bedroom → Textiles (0.85 strength)
  - Office → Storage (0.82 strength)

**Campaign Integration:**
- Automatically filters segments by product affinity when mentioned in campaign objective
- 5 product-specific campaign templates showcasing cross-sell opportunities
- Displays customer product preferences in segment profiles with visual tags

## 🛠️ Development

### Project Structure
```
ai_cdp/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   │   ├── intent_interpreter.py    # Gemini campaign interpreter
│   │   ├── causal_engine.py         # Uplift modeling
│   │   └── query_builder.py         # Dynamic SQL generation
│   ├── services/
│   │   ├── bigquery_service.py      # BigQuery client
│   │   └── segment_service.py       # Segmentation logic
│   └── api/
│       ├── routes.py                # Campaign & segment endpoints
│       ├── overview_routes.py       # Overview dashboard endpoints
│       └── schemas.py               # Pydantic models
├── frontend/
│   ├── index.html                   # Overview Dashboard (landing)
│   ├── campaign-segmentation.html   # Campaign Segmentation app
│   ├── conversational-analytics.html # Coming Soon page
│   ├── css/
│   │   ├── main.css                 # Global design system
│   │   ├── overview.css             # Overview page styles
│   │   ├── components.css           # Shared components
│   │   ├── dashboard.css            # Dashboard widgets
│   │   └── conversational-analytics.css
│   └── js/
│       ├── app.js                   # Campaign Segmentation logic
│       ├── overview.js              # Overview Dashboard logic
│       ├── components/
│       │   ├── Navigation.js        # Shared navigation
│       │   ├── SegmentDashboard.js  # Segment metrics
│       │   └── Explainability.js    # AI explainability
│       ├── services/
│       │   └── apiClient.js         # API communication
│       └── utils/
│           └── helpers.js           # Utility functions
├── scripts/
│   ├── generate_data.py             # Initial data generation
│   ├── add_realtime_events.py       # Incremental event generation
│   └── check_data_distribution.py   # Data validation utility
├── requirements.txt
├── run.py                           # Backend startup script
└── .env                             # Environment configuration
```

### Key Files
- `backend/models/intent_interpreter.py` - Gemini integration
- `backend/models/causal_engine.py` - Uplift modeling
- `backend/utils/clv_interpreter.py` - CLV score interpretation utility
- `scripts/generate_data.py` - Furniture data generation
- `scripts/add_realtime_events.py` - Real-time event simulator

## 📝 Notes

- **Synthetic Data**: All customer data is fictional and generated for demonstration purposes
- **Uplift Scores**: Simulated based on customer propensity scores (no actual causal model trained)
- **Gemini Integration**: Requires valid GCP credentials and Vertex AI API enabled
- **BigQuery Costs**: Monitor query costs; dataset is ~100MB with sample data
- **Real-Time Events**: Run `add_realtime_events.py` periodically to simulate live activity

## 🎓 Learning Outcomes

This prototype demonstrates:
1. ✅ LLM-powered campaign interpretation
2. ✅ Dynamic customer segmentation
3. ✅ Uplift modeling for trigger optimization
4. ✅ Multi-stage segment refinement workflow
5. ✅ Real-time data integration patterns
6. ✅ Explainable AI for marketing use cases
7. ✅ Modern CDP architecture with BigQuery

## 📄 License

This is a prototype application for demonstration purposes.

## 🙋 Questions?

This prototype was built to showcase AI-first CDP capabilities for a fictional home furnishing retailer.
