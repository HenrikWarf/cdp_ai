# AetherSegment AI - API Documentation

Complete REST API reference for AetherSegment AI backend.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, no authentication is required for the prototype. In production, implement API keys or OAuth 2.0.

## Endpoints

### 1. Health Check

Check if the backend service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "AetherSegment AI",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Analyze Campaign

Analyze a natural language campaign objective and get insights.

**Endpoint:** `POST /campaigns/analyze`

**Request Body:**
```json
{
  "objective": "Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers"
}
```

**Response:**
```json
{
  "campaign_objective_object": {
    "campaign_goal": "conversion",
    "target_behavior": "abandoned_cart",
    "target_subgroup": "high_value_shopper",
    "metric_target": {
      "type": "conversion_rate_increase",
      "value": 0.20
    },
    "time_constraint": "48_hours_post_abandonment",
    "proposed_intervention": "personalized_discount_offer",
    "underlying_assumptions": ["price_sensitive", "prior_engagement_with_products"]
  },
  "segment_preview": {
    "segment_id": "SEG_20241027_ABCD1234",
    "estimated_size": 15000,
    "predicted_uplift": 0.18,
    "predicted_roi": "5x",
    "avg_clv_score": 0.82,
    "avg_cart_value": 125.50,
    "common_product_categories": ["Electronics", "Fashion", "Home & Garden"],
    "demographic_breakdown": {
      "top_cities": {
        "New York": 3500,
        "Los Angeles": 2800,
        "Chicago": 2100
      }
    }
  },
  "trigger_suggestions": [
    {
      "trigger_type": "value_driven",
      "trigger_name": "Personalized Discount Offer",
      "confidence_score": 0.82,
      "predicted_uplift": 0.18,
      "description": "Offer a targeted discount based on customer value and cart contents",
      "rationale": "Based on historical campaign data, this trigger is highly effective..."
    }
  ],
  "explainability": {
    "why_this_segment": "This segment was selected based on your campaign goal...",
    "key_factors": [
      {
        "feature": "CLV Score",
        "importance": 0.25,
        "description": "Customer lifetime value prediction"
      }
    ],
    "recommended_trigger": "Personalized Discount Offer",
    "trigger_rationale": "...",
    "sample_size": 1000,
    "confidence_level": "high"
  }
}
```

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Missing or invalid objective
- `500 Internal Server Error` - Analysis failed

---

### 3. Create Segment

Create a complete customer segment for activation.

**Endpoint:** `POST /segments/create`

**Request Body:**
```json
{
  "campaign_objective": "Increase conversion for abandoned carts by 20%...",
  "override_trigger": "free_shipping"  // Optional
}
```

**Response:**
```json
{
  "segment_id": "SEG_20241027_ABCD1234",
  "campaign_objective_ref": "Increase conversion for abandoned carts...",
  "query_timestamp": "2024-10-27T10:45:00Z",
  "estimated_size": 15000,
  "criteria_used": "SELECT customer_id, email_address... WHERE...",
  "customer_profiles": [
    {
      "customer_id": "cust001",
      "email": "alice.cust001@example.com",
      "first_name": "Alice",
      "clv_score": 0.85,
      "location_city": "New York",
      "abandoned_cart_id": "cart_123",
      "cart_value": 125.50,
      "cart_items": ["Product A", "Product B"]
    }
  ],
  "metadata": {
    "segment_id": "SEG_20241027_ABCD1234",
    "estimated_size": 15000,
    "predicted_uplift": 0.18,
    "predicted_roi": "5x",
    "avg_clv_score": 0.82,
    "avg_cart_value": 125.50
  },
  "recommended_trigger": {
    "trigger_type": "value_driven",
    "trigger_name": "Personalized Discount Offer",
    "confidence_score": 0.82,
    "predicted_uplift": 0.18
  }
}
```

**Status Codes:**
- `200 OK` - Segment created
- `400 Bad Request` - Invalid request
- `500 Internal Server Error` - Creation failed

---

### 4. Get Segment Customers

Retrieve the customer list for a specific segment.

**Endpoint:** `GET /segments/{segment_id}/customers`

**Query Parameters:**
- `limit` (optional) - Maximum number of customers to return

**Example:**
```
GET /segments/SEG_20241027_ABCD1234/customers?limit=100
```

**Response:**
```json
{
  "segment_id": "SEG_20241027_ABCD1234",
  "count": 100,
  "customers": [
    {
      "customer_id": "cust001",
      "email": "alice.cust001@example.com",
      "first_name": "Alice",
      "clv_score": 0.85,
      "location_city": "New York",
      "abandoned_cart_id": "cart_123",
      "cart_value": 125.50,
      "cart_items": ["Product A", "Product B"]
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Customers retrieved
- `404 Not Found` - Segment not found
- `500 Internal Server Error` - Retrieval failed

---

### 5. Get Segment Metadata

Retrieve metadata for a specific segment.

**Endpoint:** `GET /segments/{segment_id}/metadata`

**Example:**
```
GET /segments/SEG_20241027_ABCD1234/metadata
```

**Response:**
```json
{
  "segment_id": "SEG_20241027_ABCD1234",
  "estimated_size": 15000,
  "predicted_uplift": 0.18,
  "predicted_roi": "5x",
  "avg_clv_score": 0.82,
  "avg_cart_value": 125.50,
  "common_product_categories": ["Electronics", "Fashion"],
  "demographic_breakdown": {
    "top_cities": {
      "New York": 3500,
      "Los Angeles": 2800
    }
  }
}
```

**Status Codes:**
- `200 OK` - Metadata retrieved
- `404 Not Found` - Segment not found
- `500 Internal Server Error` - Retrieval failed

---

### 6. Get Trigger Suggestions

Get ranked trigger recommendations for a campaign objective.

**Endpoint:** `POST /triggers/suggestions`

**Request Body:**
```json
{
  "objective": "Win back churned customers from the past 90 days"
}
```

**Response:**
```json
{
  "triggers": [
    {
      "trigger_type": "value_driven",
      "trigger_name": "Personalized Discount Offer",
      "confidence_score": 0.82,
      "predicted_uplift": 0.18,
      "description": "Offer a targeted discount based on customer value",
      "rationale": "Highly effective for this segment..."
    },
    {
      "trigger_type": "value_driven",
      "trigger_name": "Free Shipping",
      "confidence_score": 0.75,
      "predicted_uplift": 0.15,
      "description": "Eliminate shipping costs to reduce cart abandonment",
      "rationale": "Moderately effective..."
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Suggestions retrieved
- `400 Bad Request` - Invalid objective
- `500 Internal Server Error` - Failed to generate suggestions

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error description"
}
```

**Common Error Types:**
- `Bad Request` - Invalid input parameters
- `Not Found` - Resource doesn't exist
- `Internal Server Error` - Server-side error

---

## Rate Limiting

Currently no rate limiting in prototype. For production:
- Implement rate limiting per API key
- Recommended: 100 requests per minute per key
- Return `429 Too Many Requests` when exceeded

---

## CORS

The API supports CORS for the origins specified in `ALLOWED_ORIGINS` environment variable.

Default allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:5500`

---

## Example Usage

### Using cURL

```bash
# Analyze campaign
curl -X POST http://localhost:5000/api/v1/campaigns/analyze \
  -H "Content-Type: application/json" \
  -d '{"objective": "Increase conversion for abandoned carts by 20%"}'

# Create segment
curl -X POST http://localhost:5000/api/v1/segments/create \
  -H "Content-Type: application/json" \
  -d '{"campaign_objective": "Increase conversion for abandoned carts by 20%"}'

# Get customers
curl http://localhost:5000/api/v1/segments/SEG_20241027_ABCD1234/customers?limit=10
```

### Using Python

```python
import requests

# Analyze campaign
response = requests.post(
    'http://localhost:5000/api/v1/campaigns/analyze',
    json={'objective': 'Increase conversion for abandoned carts by 20%'}
)
analysis = response.json()

# Create segment
response = requests.post(
    'http://localhost:5000/api/v1/segments/create',
    json={'campaign_objective': 'Increase conversion for abandoned carts by 20%'}
)
segment = response.json()
segment_id = segment['segment_id']

# Get customers
response = requests.get(
    f'http://localhost:5000/api/v1/segments/{segment_id}/customers',
    params={'limit': 100}
)
customers = response.json()
```

### Using JavaScript (Frontend)

```javascript
// Analyze campaign
const analysis = await fetch('http://localhost:5000/api/v1/campaigns/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    objective: 'Increase conversion for abandoned carts by 20%'
  })
}).then(res => res.json());

// Create segment
const segment = await fetch('http://localhost:5000/api/v1/segments/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    campaign_objective: 'Increase conversion for abandoned carts by 20%'
  })
}).then(res => res.json());

// Get customers
const customers = await fetch(
  `http://localhost:5000/api/v1/segments/${segment.segment_id}/customers?limit=100`
).then(res => res.json());
```

---

## Versioning

Current API version: `v1`

Version is included in the URL path: `/api/v1/...`

Future versions will be released as `/api/v2/`, etc., maintaining backward compatibility.

---

**For questions or issues, refer to the main README.md or troubleshooting guide.**

