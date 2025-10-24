import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from dotenv import load_dotenv
from backend.config import Config
from datetime import datetime, timedelta

load_dotenv()

client = bigquery.Client(project=Config.GOOGLE_CLOUD_PROJECT)
dataset = Config.BIGQUERY_DATASET

print("="*60)
print("  Data Distribution Check")
print("="*60)

# 1. Total customers
query = f"SELECT COUNT(*) as total FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.customers`"
result = client.query(query).to_dataframe()
print(f"\n📊 Total Customers: {result['total'].iloc[0]:,}")

# 2. Behavioral events date range
query = f"""
SELECT 
  MIN(timestamp) as earliest,
  MAX(timestamp) as latest,
  COUNT(*) as total_events
FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.behavioral_events`
"""
result = client.query(query).to_dataframe()
print(f"\n📅 Behavioral Events:")
print(f"   Earliest: {result['earliest'].iloc[0]}")
print(f"   Latest: {result['latest'].iloc[0]}")
print(f"   Total: {result['total_events'].iloc[0]:,}")

# 3. Customers by last activity
query = f"""
WITH last_activity AS (
  SELECT 
    customer_id,
    MAX(timestamp) as last_event
  FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.behavioral_events`
  GROUP BY customer_id
)
SELECT
  CASE
    WHEN CAST(last_event AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY) THEN '0-7 days'
    WHEN CAST(last_event AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) THEN '8-30 days'
    WHEN CAST(last_event AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY) THEN '31-90 days'
    ELSE '90+ days (dormant)'
  END as activity_recency,
  COUNT(*) as customer_count
FROM last_activity
GROUP BY activity_recency
ORDER BY 
  CASE activity_recency
    WHEN '0-7 days' THEN 1
    WHEN '8-30 days' THEN 2
    WHEN '31-90 days' THEN 3
    ELSE 4
  END
"""
result = client.query(query).to_dataframe()
print(f"\n👥 Customers by Last Activity:")
for _, row in result.iterrows():
    print(f"   {row['activity_recency']:20s}: {row['customer_count']:,}")

# 4. Customers with NO events (never active)
query = f"""
SELECT COUNT(*) as never_active
FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.customers` c
WHERE NOT EXISTS (
  SELECT 1 FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.behavioral_events` be
  WHERE be.customer_id = c.customer_id
)
"""
result = client.query(query).to_dataframe()
print(f"\n😴 Customers with NO events (never active): {result['never_active'].iloc[0]:,}")

# 5. Abandoned cart date range
query = f"""
SELECT 
  MIN(timestamp) as earliest,
  MAX(timestamp) as latest,
  COUNT(*) as total_carts,
  COUNT(CASE WHEN status = 'abandoned' THEN 1 END) as abandoned_count
FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.abandoned_carts`
"""
result = client.query(query).to_dataframe()
print(f"\n🛒 Abandoned Carts:")
print(f"   Earliest: {result['earliest'].iloc[0]}")
print(f"   Latest: {result['latest'].iloc[0]}")
print(f"   Total: {result['total_carts'].iloc[0]:,}")
print(f"   Abandoned: {result['abandoned_count'].iloc[0]:,}")

# 6. Recent abandoned carts (last 7 days)
query = f"""
SELECT COUNT(*) as recent_abandoned
FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.abandoned_carts`
WHERE status = 'abandoned'
  AND CAST(timestamp AS TIMESTAMP) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
"""
result = client.query(query).to_dataframe()
print(f"   Recent (last 7 days): {result['recent_abandoned'].iloc[0]:,}")

# 7. Lapsed customers (high churn probability)
query = f"""
SELECT COUNT(*) as lapsed_customers
FROM `{Config.GOOGLE_CLOUD_PROJECT}.{dataset}.customer_scores`
WHERE churn_probability_score > 0.6
"""
result = client.query(query).to_dataframe()
print(f"\n👋 Lapsed Customers (churn_probability > 0.6): {result['lapsed_customers'].iloc[0]:,}")

print("\n" + "="*60)
print("✅ Check complete!")

