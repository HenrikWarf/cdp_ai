# Conversational Segmentation Engine

## Overview

The Conversational Segmentation Engine enables natural language queries against customer data using the consolidated `cdp_data.customers` table. This eliminates the need for complex SQL JOINs and provides fast, intuitive customer segment creation through conversation.

## cdp_data.customers Table

### Purpose

The `cdp_data.customers` table consolidates all customer data into a single denormalized table with one row per customer. This table lives in the dedicated `cdp_data` dataset for clean separation from raw source tables. Each row contains:

- **Core Profile**: Demographics, location, CLV score
- **ML Scores**: Discount sensitivity, churn probability, product affinities
- **Transaction Metrics**: Purchase history across all-time, 90-day, and 30-day windows
- **Cart Abandonment**: Abandoned cart metrics and dates
- **Behavioral Engagement**: Event tracking and engagement rates
- **Campaign Response**: Historical campaign performance

### Schema (100+ Columns)

#### Core Profile
- `customer_id` - Unique identifier
- `email_address`, `first_name`
- `location_city`, `location_country`
- `age`, `gender`, `income_level`
- `clv_score` - Customer lifetime value (0-1)
- `days_as_customer` - Tenure in days

#### ML Scores
- `discount_sensitivity_score` (0-1)
- `free_shipping_sensitivity_score` (0-1)
- `churn_probability_score` (0-1)
- `exclusivity_seeker_flag`
- `social_proof_affinity` (0-1)
- `content_engagement_score` (0-1)

#### Product Affinities (0-1 each)
- `living_room_affinity`
- `bedroom_affinity`
- `kitchen_dining_affinity`
- `office_affinity`
- `outdoor_affinity`
- `lighting_affinity`
- `storage_affinity`
- `textiles_affinity`
- `bathroom_affinity`
- `decoration_affinity`

#### Transaction Metrics

**Lifetime:**
- `total_purchases`, `total_revenue`, `avg_order_value`
- `first_purchase_date`, `last_purchase_date`, `days_since_last_purchase`
- `purchase_frequency_per_month`

**Last 90 Days:**
- `purchases_90d`, `revenue_90d`, `avg_order_value_90d`

**Last 30 Days:**
- `purchases_30d`, `revenue_30d`, `avg_order_value_30d`

**Category Insights:**
- `most_purchased_category`
- `most_recent_category`

#### Cart Abandonment
- `total_abandoned_carts`, `total_abandoned_cart_value`
- `last_cart_abandonment_date`, `days_since_last_cart_abandonment`
- `abandoned_carts_30d`, `abandoned_cart_value_30d`, `abandoned_carts_90d`

#### Behavioral Engagement
- `total_events_lifetime`, `events_90d`, `events_30d`
- `last_event_date`, `days_since_last_event`
- `most_viewed_category`
- `engagement_rate_per_day`

#### Campaign Response
- `total_campaigns_received`, `total_campaigns_converted`
- `overall_conversion_rate`, `conversion_rate_90d`
- `campaigns_90d`, `conversions_90d`, `campaigns_30d`
- `most_responsive_trigger_type`
- `last_campaign_date`, `days_since_last_campaign`

## Building the Table

### Initial Build

After generating base data, the unified table is automatically built:

```bash
python scripts/generate_data.py
```

### Manual Build

To rebuild the table manually:

```bash
python scripts/build_customers_unified_table.py
```

This script:
1. Executes the SQL query from `create_customers_unified_table.sql`
2. Applies comprehensive column descriptions
3. Updates table-level documentation
4. Displays summary statistics

### Scheduled Refresh

For production, schedule the refresh script to run daily:

```bash
# Run refresh manually
python scripts/refresh_customers_unified.py

# Or schedule with cron (Linux/Mac)
0 2 * * * cd /path/to/ai_cdp && python scripts/refresh_customers_unified.py

# Or use Cloud Scheduler for BigQuery
# https://cloud.google.com/scheduler/docs
```

## Querying Examples

### Simple Queries

```sql
-- High-value customers in New York
SELECT customer_id, email_address, clv_score, total_revenue
FROM `project.cdp_data.customers`
WHERE location_city = 'New York' AND clv_score > 0.8;

-- Recent cart abandoners with high cart value
SELECT customer_id, email_address, abandoned_carts_30d, abandoned_cart_value_30d
FROM `project.cdp_data.customers`
WHERE abandoned_carts_30d > 0 
  AND abandoned_cart_value_30d > 500
  AND days_since_last_cart_abandonment <= 7;

-- Active customers at risk of churn
SELECT customer_id, email_address, churn_probability_score, purchases_30d
FROM `project.cdp_data.customers`
WHERE churn_probability_score > 0.7
  AND purchases_90d > 0;
```

### Complex Segmentation

```sql
-- Discount-sensitive customers who abandoned high-value carts
SELECT 
    customer_id, 
    email_address,
    discount_sensitivity_score,
    abandoned_cart_value_30d,
    last_cart_abandonment_date
FROM `project.cdp_data.customers`
WHERE discount_sensitivity_score > 0.7
  AND abandoned_carts_30d > 0
  AND abandoned_cart_value_30d > 300
  AND days_since_last_cart_abandonment <= 3
ORDER BY abandoned_cart_value_30d DESC;

-- Cross-sell opportunity: Living room buyers without bedroom purchases
SELECT 
    customer_id,
    email_address,
    living_room_affinity,
    bedroom_affinity,
    most_recent_category,
    days_since_last_purchase
FROM `project.cdp_data.customers`
WHERE living_room_affinity > 0.5
  AND bedroom_affinity = 0
  AND days_since_last_purchase <= 90
ORDER BY living_room_affinity DESC;
```

### Time-Window Analysis

```sql
-- Customers active in last 30 days but not last 7 days
SELECT customer_id, email_address, purchases_30d, days_since_last_purchase
FROM `project.cdp_data.customers`
WHERE purchases_30d > 0
  AND days_since_last_purchase > 7;

-- Campaign fatigue analysis
SELECT 
    customer_id,
    campaigns_90d,
    conversions_90d,
    conversion_rate_90d,
    days_since_last_campaign
FROM `project.cdp_data.customers`
WHERE campaigns_90d >= 5
  AND conversion_rate_90d < 0.1;
```

## Conversational AI Integration

The unified table is designed for natural language querying. Example conversational queries:

**User**: "Show me high-income women aged 30-45 in London who abandoned carts in the last 7 days"

**Translated SQL**:
```sql
SELECT *
FROM `project.cdp_data.customers`
WHERE gender = 'Female'
  AND age BETWEEN 30 AND 45
  AND income_level IN ('high', 'premium')
  AND location_city = 'London'
  AND abandoned_carts_30d > 0
  AND days_since_last_cart_abandonment <= 7;
```

**User**: "Find customers who bought living room furniture recently but haven't purchased in the last 30 days"

**Translated SQL**:
```sql
SELECT *
FROM `project.cdp_data.customers`
WHERE most_recent_category = 'Living Room'
  AND purchases_90d > 0
  AND purchases_30d = 0;
```

## Performance Considerations

### Benefits
- **Single table queries**: No JOINs needed
- **Pre-aggregated metrics**: No runtime calculations
- **Fast response times**: Typical queries < 1 second
- **Cost-effective**: One-time aggregation vs. repeated JOINs

### Maintenance
- **Refresh frequency**: Daily (recommended)
- **Table size**: ~10K rows × 100 columns = ~1MB
- **Query cost**: Minimal (single table scan)
- **Build time**: 30-60 seconds

### Future Optimizations
- Incremental refresh (only update changed rows)
- Partitioning by `creation_date` for large datasets (100K+ customers)
- Materialized views for common query patterns
- Real-time updates via streaming inserts

## Troubleshooting

### Build Errors

**Error: "Table not found"**
- Ensure base tables exist: Run `python scripts/generate_data.py` first

**Error: "Column descriptions not applied"**
- Check BigQuery permissions: Need `bigquery.tables.update` permission

**Error: "Query timeout"**
- Increase timeout in script or use async query execution

### Data Quality

**High NULL rates in metrics**
- Expected for customers without transactions/events
- `COALESCE` used to default to 0 where appropriate

**Stale data**
- Run refresh script: `python scripts/refresh_customers_unified.py`

## Resources

- BigQuery Console: View table schema and preview data
- `create_customers_unified_table.sql`: Full SQL logic
- `build_customers_unified_table.py`: Build script with column descriptions
- Main project README: Overview of the entire CDP system
