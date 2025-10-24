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
- **Backend**: Python (Flask), Pandas, NumPy
- **AI/LLM**: Google Gemini 2.5 Flash via Vertex AI
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

3. **💬 Conversational Analytics** (`conversational-analytics.html`)
   - *Coming Soon* - Natural language data queries
   - Interactive exploration of customer data
   - AI-generated visualizations and insights

### Key Components

1. **Campaign Intent Interpreter** - Gemini-powered natural language processor
2. **Causal Segmentation Engine** - Uplift score simulation for trigger optimization
3. **BigQuery Data Layer** - Synthetic customer dataset with rich behavioral attributes
4. **REST API** - Segment activation, analysis, and overview endpoints
5. **Modular UI** - Shared navigation and component architecture

## 📊 Data Model

### BigQuery Tables

#### `customers` (10,000 records)
- Customer identity and demographics
- Location data (city, country)
- CLV scores
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

Create a `.env` file in the project root:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
BIGQUERY_DATASET=aethersegment_cdp
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# CORS Configuration
ALLOWED_ORIGINS=*
```

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

### 4. Start the Backend

```bash
# Run the Flask application
python run.py
```

Backend will be available at `http://localhost:5000`

### 5. Open the Frontend

Open `frontend/index.html` in your browser, or use a local server:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 8000
```

Then visit `http://localhost:8000`

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

### `GET /api/v1/overview/stats`
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

### `POST /api/v1/campaigns/analyze`
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

### `POST /api/v1/segments/preview-filters`
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

### `POST /api/v1/segments/create`
Create final segment with trigger selection

**Request**:
```json
{
  "campaign_objective": "...",
  "override_trigger": "personalized_discount_offer",
  "additional_filters": {...}
}
```

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
