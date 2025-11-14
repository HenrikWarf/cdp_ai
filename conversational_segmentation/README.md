# Conversational Customer Segmentation Agent

This project implements an AI-powered conversational agent using the Google Agent Development Kit (ADK) that enables natural language exploration and analysis of customer segments. Ask questions in plain English to discover insights about your customers, identify behavioral patterns, and create meaningful segments from your BigQuery data.

## Overview

The Conversational Segmentation Agent allows you to explore and analyze customer data through natural conversation. Instead of writing complex SQL queries or learning data analysis tools, simply ask questions like:

- "Who are my high-value customers?"
- "Show me customers at risk of churning"
- "What segments exist based on purchase behavior?"
- "Find customers in California who spent over $1000 last month"

The agent understands your intent, queries your BigQuery data, and provides actionable insights through a conversational interface.

## Key Features

### 🗣️ Natural Language Queries
Ask questions about your customers in plain English. The agent translates your questions into precise BigQuery queries automatically.

### 🎯 Intelligent Segmentation
Discover customer segments through conversation. The agent can perform multiple types of analysis including:
- **RFM Analysis** (Recency, Frequency, Monetary) for behavioral segmentation
- **Geographic segmentation** by location and demographics
- **Product affinity** based on purchase patterns
- **Lifetime value** analysis
- **Custom segmentation** based on any data attribute

### 💬 Interactive Conversations
Build on previous questions to dive deeper. The agent maintains context throughout your conversation, allowing you to refine your analysis iteratively.

### 📊 BigQuery Integration
Directly connects to your Google BigQuery data warehouse. Query millions of customer records in seconds with no data movement required.

### 🤖 Multi-Agent Architecture
Uses a sophisticated multi-agent system:
- **Customer Segmentation Analyst**: Understands your business questions and orchestrates the analysis
- **BigQuery Expert**: Handles all database interactions, schema exploration, and query execution

## Architecture

The system leverages Google's Agent Development Kit (ADK) with a hierarchical agent structure:

1. **Main Agent** (`customer_segmentation_analyst`): 
   - Interprets natural language queries about customer segmentation
   - Plans analysis approaches
   - Generates insights and recommendations
   - Maintains conversation context

2. **Sub-Agent** (`bigquery_expert`):
   - Explores BigQuery datasets and schemas
   - Executes SQL queries
   - Returns structured data to the main agent

## Prerequisites

- Python 3.10+
- Google Cloud Platform account
- BigQuery API enabled
- Service account with BigQuery access

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd conversational_segmentation
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Cloud authentication:**
   ```bash
   gcloud auth application-default login
   ```

5. **Set up environment variables:**
   Create a `.env` file with your BigQuery configuration:
   ```env
   BIGQUERY_PROJECT=your-gcp-project-id
   BIGQUERY_DATASET=customer_data_retail
   BIGQUERY_TABLE=customer
   ```

## Data Setup

Your BigQuery table should contain customer data with fields like:
- Customer identifiers (customer_id, user_id, etc.)
- Transaction information (dates, amounts, products)
- Customer attributes (location, demographics, etc.)

Example schema for a customer transactions table:
```sql
customer_id: STRING
transaction_date: DATE
amount: FLOAT64
product_category: STRING
location: STRING
```

See `sample_data.sql` for a sample data structure.

## Usage

### Web Interface (Recommended)

Run the FastAPI server with the conversational UI:

```bash
python api.py
```

Then open your browser to `http://localhost:8001` to access the chat interface.

### Command Line Interface

For direct command-line interaction:

```bash
# Interactive conversation mode
python main_conv.py

# Single analysis execution
python main.py
```

### Example Conversations

**Discovering High-Value Customers:**
```
You: Who are my most valuable customers?
Agent: I'll analyze customer lifetime value and purchase frequency...
      [Shows top customers with spending patterns]
```

**Identifying At-Risk Segments:**
```
You: Which customers haven't purchased recently?
Agent: Let me check recency data...
      [Identifies customers by last purchase date]
```

**Geographic Analysis:**
```
You: Show me customer distribution by region
Agent: I'll segment customers by location...
      [Provides geographic breakdown]
```

## Use Cases

- **Campaign Planning**: Identify target segments for marketing campaigns
- **Churn Prevention**: Find at-risk customers before they leave
- **Product Recommendations**: Understand purchase patterns for personalization
- **Customer Lifetime Value**: Discover and nurture high-value customers
- **Market Analysis**: Explore customer demographics and behaviors
- **Business Intelligence**: Answer ad-hoc questions about your customer base

## Integration

This agent integrates with the AetherSegment AI CDP platform, providing a conversational interface for customer segmentation alongside campaign management and analytics tools.

Access through the CDP:
1. Navigate to **Conversational Segmentation** in the main menu
2. Click **Start Conversational Segmentation**
3. Begin asking questions about your customers

## Files

- `api.py`: FastAPI server with WebSocket support for the web interface
- `customer_segmentation_agent_conv.py`: Conversational agent with context awareness
- `customer_segmentation_agent.py`: Single-execution segmentation agent
- `bigquery_agent.py`: Sub-agent for BigQuery interactions
- `bigquery_tools.py`: BigQuery tool implementations
- `main_conv.py`: Interactive CLI conversation mode
- `main.py`: Single analysis execution mode
- `static/`: Web UI files (React-based chat interface)
- `sample_data.sql`: Sample data structure for testing

## Technical Details

- Built with **Google Agent Development Kit (ADK)**
- Uses **Gemini 2.5 Pro** for natural language understanding
- **FastAPI** + **WebSocket** for real-time conversations
- **React** frontend for rich chat UI
- **BigQuery** as the data warehouse

## Notes

While RFM (Recency, Frequency, Monetary) analysis is one of the segmentation methods available, this agent is designed to handle a wide variety of customer analysis questions through natural conversation. The agent adapts its analysis approach based on your specific questions and data structure.
