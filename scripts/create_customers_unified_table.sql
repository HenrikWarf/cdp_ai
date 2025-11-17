-- ============================================================================
-- AetherSegment AI - Customers Unified Table
-- ============================================================================
-- This SQL creates a consolidated customer table with all attributes and 
-- behavioral metrics aggregated across multiple time windows (all-time, 90d, 30d)
-- 
-- Purpose: Power conversational segmentation with single-table queries
-- Refresh: Should be run daily or on-demand via build_customers_unified_table.py
-- ============================================================================

-- Replace these placeholders with actual values when executing
-- {project_id}, {dataset_id}

-- ============================================================================
-- CTE 1a: Transaction Category Rankings (for most purchased/recent)
-- ============================================================================
WITH transaction_category_rankings AS (
  SELECT
    customer_id,
    product_category,
    COUNT(*) as category_purchase_count,
    MAX(timestamp) as last_category_purchase,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) as purchase_rank,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY MAX(timestamp) DESC) as recency_rank
  FROM `{project_id}.{dataset_id}.transactions`
  GROUP BY customer_id, product_category
),

-- ============================================================================
-- CTE 1b: Transaction Metrics Aggregation
-- ============================================================================
transaction_metrics AS (
  SELECT
    t.customer_id,
    
    -- Lifetime transaction metrics
    COUNT(*) as total_purchases,
    SUM(order_value) as total_revenue,
    AVG(order_value) as avg_order_value,
    MIN(timestamp) as first_purchase_date,
    MAX(timestamp) as last_purchase_date,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(timestamp)), DAY) as days_since_last_purchase,
    
    -- Purchase frequency (purchases per month)
    ROUND(COUNT(*) / GREATEST(1, DATE_DIFF(CURRENT_DATE(), DATE(MIN(timestamp)), DAY) / 30.0), 2) as purchase_frequency_per_month,
    
    -- Last 90 days metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)) as purchases_90d,
    SUM(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) THEN order_value ELSE 0 END) as revenue_90d,
    AVG(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) THEN order_value END) as avg_order_value_90d,
    
    -- Last 30 days metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)) as purchases_30d,
    SUM(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) THEN order_value ELSE 0 END) as revenue_30d,
    AVG(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) THEN order_value END) as avg_order_value_30d,
    
    -- Category insights (join with rankings CTE)
    MAX(CASE WHEN tcr.purchase_rank = 1 THEN tcr.product_category END) as most_purchased_category,
    MAX(CASE WHEN tcr.recency_rank = 1 THEN tcr.product_category END) as most_recent_category
    
  FROM `{project_id}.{dataset_id}.transactions` t
  LEFT JOIN transaction_category_rankings tcr ON t.customer_id = tcr.customer_id
  GROUP BY t.customer_id
),

-- ============================================================================
-- CTE 2: Abandoned Cart Metrics Aggregation
-- ============================================================================
cart_metrics AS (
  SELECT
    customer_id,
    
    -- Lifetime cart metrics
    COUNT(*) as total_abandoned_carts,
    SUM(cart_value) as total_abandoned_cart_value,
    AVG(cart_value) as avg_abandoned_cart_value,
    MAX(timestamp) as last_cart_abandonment_date,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(timestamp)), DAY) as days_since_last_cart_abandonment,
    
    -- Last 30 days cart metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)) as abandoned_carts_30d,
    SUM(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) THEN cart_value ELSE 0 END) as abandoned_cart_value_30d,
    
    -- Last 90 days cart metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)) as abandoned_carts_90d
    
  FROM `{project_id}.{dataset_id}.abandoned_carts`
  WHERE status = 'abandoned'
  GROUP BY customer_id
),

-- ============================================================================
-- CTE 3a: Behavioral Event Category Rankings (for most viewed)
-- ============================================================================
behavioral_category_rankings AS (
  SELECT
    customer_id,
    product_category,
    COUNT(*) as view_count,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) as view_rank
  FROM `{project_id}.{dataset_id}.behavioral_events`
  WHERE event_type IN ('page_view', 'product_view')
  GROUP BY customer_id, product_category
),

-- ============================================================================
-- CTE 3b: Behavioral Event Metrics Aggregation
-- ============================================================================
behavioral_metrics AS (
  SELECT
    be.customer_id,
    
    -- Lifetime event metrics
    COUNT(*) as total_events_lifetime,
    MAX(timestamp) as last_event_date,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(timestamp)), DAY) as days_since_last_event,
    
    -- Last 90 days event metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)) as events_90d,
    
    -- Last 30 days event metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)) as events_30d,
    
    -- Most viewed category (join with rankings CTE)
    MAX(CASE WHEN bcr.view_rank = 1 THEN bcr.product_category END) as most_viewed_category,
    
    -- Engagement rate (events per day since first event)
    ROUND(COUNT(*) / GREATEST(1, DATE_DIFF(CURRENT_DATE(), DATE(MIN(timestamp)), DAY)), 2) as engagement_rate_per_day
    
  FROM `{project_id}.{dataset_id}.behavioral_events` be
  LEFT JOIN behavioral_category_rankings bcr ON be.customer_id = bcr.customer_id
  GROUP BY be.customer_id
),

-- ============================================================================
-- CTE 4a: Campaign Trigger Rankings (for most responsive trigger)
-- ============================================================================
campaign_trigger_rankings AS (
  SELECT
    customer_id,
    trigger_type,
    COUNT(*) as conversion_count,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) as trigger_rank
  FROM `{project_id}.{dataset_id}.campaign_history`
  WHERE converted = TRUE
  GROUP BY customer_id, trigger_type
),

-- ============================================================================
-- CTE 4b: Campaign Response Metrics Aggregation
-- ============================================================================
campaign_metrics AS (
  SELECT
    ch.customer_id,
    
    -- Lifetime campaign metrics
    COUNT(*) as total_campaigns_received,
    SUM(CASE WHEN converted = TRUE THEN 1 ELSE 0 END) as total_campaigns_converted,
    ROUND(AVG(CASE WHEN converted = TRUE THEN 1.0 ELSE 0.0 END), 3) as overall_conversion_rate,
    
    -- Last 90 days campaign metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)) as campaigns_90d,
    SUM(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) AND converted = TRUE THEN 1 ELSE 0 END) as conversions_90d,
    ROUND(AVG(CASE WHEN CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) THEN CASE WHEN converted = TRUE THEN 1.0 ELSE 0.0 END END), 3) as conversion_rate_90d,
    
    -- Last 30 days campaign metrics
    COUNTIF(CAST(timestamp AS TIMESTAMP) >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)) as campaigns_30d,
    
    -- Most responsive trigger type (join with rankings CTE)
    MAX(CASE WHEN ctr.trigger_rank = 1 THEN ctr.trigger_type END) as most_responsive_trigger_type,
    
    -- Last campaign date
    MAX(timestamp) as last_campaign_date,
    DATE_DIFF(CURRENT_DATE(), DATE(MAX(timestamp)), DAY) as days_since_last_campaign
    
  FROM `{project_id}.{dataset_id}.campaign_history` ch
  LEFT JOIN campaign_trigger_rankings ctr ON ch.customer_id = ctr.customer_id
  GROUP BY ch.customer_id
)

-- ============================================================================
-- Final SELECT: Join all metrics to customer base
-- ============================================================================
SELECT
  -- Core Profile (from customers table)
  c.customer_id,
  c.email_address,
  c.first_name,
  c.location_city,
  c.location_country,
  c.acquisition_source,
  c.creation_date,
  DATE_DIFF(CURRENT_DATE(), DATE(c.creation_date), DAY) as days_as_customer,
  c.age,
  c.gender,
  c.income_level,
  c.clv_score,
  
  -- ML Scores & Affinities (from customer_scores table)
  COALESCE(cs.discount_sensitivity_score, 0.0) as discount_sensitivity_score,
  COALESCE(cs.free_shipping_sensitivity_score, 0.0) as free_shipping_sensitivity_score,
  COALESCE(cs.exclusivity_seeker_flag, FALSE) as exclusivity_seeker_flag,
  COALESCE(cs.churn_probability_score, 0.0) as churn_probability_score,
  COALESCE(cs.social_proof_affinity, 0.0) as social_proof_affinity,
  COALESCE(cs.content_engagement_score, 0.0) as content_engagement_score,
  
  -- Product category affinities
  COALESCE(cs.living_room_affinity, 0.0) as living_room_affinity,
  COALESCE(cs.bedroom_affinity, 0.0) as bedroom_affinity,
  COALESCE(cs.kitchen_dining_affinity, 0.0) as kitchen_dining_affinity,
  COALESCE(cs.office_affinity, 0.0) as office_affinity,
  COALESCE(cs.outdoor_affinity, 0.0) as outdoor_affinity,
  COALESCE(cs.lighting_affinity, 0.0) as lighting_affinity,
  COALESCE(cs.storage_affinity, 0.0) as storage_affinity,
  COALESCE(cs.textiles_affinity, 0.0) as textiles_affinity,
  COALESCE(cs.bathroom_affinity, 0.0) as bathroom_affinity,
  COALESCE(cs.decoration_affinity, 0.0) as decoration_affinity,
  
  -- Purchase profile
  cs.favorite_category,
  cs.secondary_category,
  COALESCE(cs.cross_category_shopper, FALSE) as cross_category_shopper,
  cs.price_tier_preference,
  
  -- Transaction Metrics (from transaction_metrics CTE)
  COALESCE(tm.total_purchases, 0) as total_purchases,
  COALESCE(tm.total_revenue, 0.0) as total_revenue,
  COALESCE(tm.avg_order_value, 0.0) as avg_order_value,
  tm.first_purchase_date,
  tm.last_purchase_date,
  COALESCE(tm.days_since_last_purchase, 999999) as days_since_last_purchase,
  COALESCE(tm.purchase_frequency_per_month, 0.0) as purchase_frequency_per_month,
  
  COALESCE(tm.purchases_90d, 0) as purchases_90d,
  COALESCE(tm.revenue_90d, 0.0) as revenue_90d,
  COALESCE(tm.avg_order_value_90d, 0.0) as avg_order_value_90d,
  
  COALESCE(tm.purchases_30d, 0) as purchases_30d,
  COALESCE(tm.revenue_30d, 0.0) as revenue_30d,
  COALESCE(tm.avg_order_value_30d, 0.0) as avg_order_value_30d,
  
  tm.most_purchased_category,
  tm.most_recent_category,
  
  -- Cart Abandonment Metrics (from cart_metrics CTE)
  COALESCE(cm.total_abandoned_carts, 0) as total_abandoned_carts,
  COALESCE(cm.total_abandoned_cart_value, 0.0) as total_abandoned_cart_value,
  COALESCE(cm.avg_abandoned_cart_value, 0.0) as avg_abandoned_cart_value,
  cm.last_cart_abandonment_date,
  COALESCE(cm.days_since_last_cart_abandonment, 999999) as days_since_last_cart_abandonment,
  COALESCE(cm.abandoned_carts_30d, 0) as abandoned_carts_30d,
  COALESCE(cm.abandoned_cart_value_30d, 0.0) as abandoned_cart_value_30d,
  COALESCE(cm.abandoned_carts_90d, 0) as abandoned_carts_90d,
  
  -- Behavioral Engagement Metrics (from behavioral_metrics CTE)
  COALESCE(bm.total_events_lifetime, 0) as total_events_lifetime,
  bm.last_event_date,
  COALESCE(bm.days_since_last_event, 999999) as days_since_last_event,
  COALESCE(bm.events_90d, 0) as events_90d,
  COALESCE(bm.events_30d, 0) as events_30d,
  bm.most_viewed_category,
  COALESCE(bm.engagement_rate_per_day, 0.0) as engagement_rate_per_day,
  
  -- Campaign Response Metrics (from campaign_metrics CTE)
  COALESCE(cpm.total_campaigns_received, 0) as total_campaigns_received,
  COALESCE(cpm.total_campaigns_converted, 0) as total_campaigns_converted,
  COALESCE(cpm.overall_conversion_rate, 0.0) as overall_conversion_rate,
  COALESCE(cpm.campaigns_90d, 0) as campaigns_90d,
  COALESCE(cpm.conversions_90d, 0) as conversions_90d,
  COALESCE(cpm.conversion_rate_90d, 0.0) as conversion_rate_90d,
  COALESCE(cpm.campaigns_30d, 0) as campaigns_30d,
  cpm.most_responsive_trigger_type,
  cpm.last_campaign_date,
  COALESCE(cpm.days_since_last_campaign, 999999) as days_since_last_campaign,
  
  -- Metadata
  CURRENT_TIMESTAMP() as last_updated_at

FROM `{project_id}.{dataset_id}.customers` c

-- Join customer scores (1:1)
LEFT JOIN `{project_id}.{dataset_id}.customer_scores` cs
  ON c.customer_id = cs.customer_id

-- Join aggregated metrics
LEFT JOIN transaction_metrics tm
  ON c.customer_id = tm.customer_id

LEFT JOIN cart_metrics cm
  ON c.customer_id = cm.customer_id

LEFT JOIN behavioral_metrics bm
  ON c.customer_id = bm.customer_id

LEFT JOIN campaign_metrics cpm
  ON c.customer_id = cpm.customer_id

ORDER BY c.customer_id

