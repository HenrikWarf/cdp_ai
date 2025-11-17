"""
Build Customers Unified Table in BigQuery

This script creates a consolidated customer table by executing the SQL query 
and applying comprehensive column descriptions for documentation and discoverability.

Usage:
    python scripts/build_customers_unified_table.py
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')  # Source dataset
BIGQUERY_TARGET_DATASET = 'cdp_data'  # Target dataset for unified customer table
BIGQUERY_TARGET_TABLE = 'customers'  # Target table name
SQL_FILE_PATH = Path(__file__).parent / 'create_customers_unified_table.sql'


def get_schema_with_descriptions():
    """
    Define complete schema with descriptions for all ~100 columns
    
    Column descriptions are critical for:
    - Documentation and knowledge transfer
    - BigQuery UI exploration
    - Conversational AI understanding
    - Data catalog integration
    """
    
    return [
        # ====================================================================
        # CORE PROFILE (from customers table)
        # ====================================================================
        bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED', 
            description='Unique customer identifier'),
        bigquery.SchemaField('email_address', 'STRING', mode='REQUIRED',
            description='Customer email address'),
        bigquery.SchemaField('first_name', 'STRING',
            description='Customer first name'),
        bigquery.SchemaField('location_city', 'STRING',
            description='Customer city location'),
        bigquery.SchemaField('location_country', 'STRING',
            description='Customer country location'),
        bigquery.SchemaField('acquisition_source', 'STRING',
            description='Channel through which customer was acquired (e.g., organic_search, paid_search, social_media)'),
        bigquery.SchemaField('creation_date', 'DATETIME',
            description='Date when customer account was created'),
        bigquery.SchemaField('days_as_customer', 'INTEGER',
            description='Number of days since customer account creation'),
        bigquery.SchemaField('age', 'INTEGER',
            description='Customer age in years'),
        bigquery.SchemaField('gender', 'STRING',
            description='Customer gender (Male, Female, Non-Binary, Prefer Not to Say)'),
        bigquery.SchemaField('income_level', 'STRING',
            description='Customer income level (low, medium, high, premium)'),
        bigquery.SchemaField('clv_score', 'FLOAT',
            description='Customer Lifetime Value score (0-1, higher = more valuable)'),
        
        # ====================================================================
        # ML SCORES & SENSITIVITIES (from customer_scores table)
        # ====================================================================
        bigquery.SchemaField('discount_sensitivity_score', 'FLOAT',
            description='Likelihood of responding to discount offers (0-1)'),
        bigquery.SchemaField('free_shipping_sensitivity_score', 'FLOAT',
            description='Likelihood of responding to free shipping offers (0-1)'),
        bigquery.SchemaField('exclusivity_seeker_flag', 'BOOLEAN',
            description='Whether customer prefers exclusive/premium products'),
        bigquery.SchemaField('churn_probability_score', 'FLOAT',
            description='Predicted probability of customer churning (0-1, higher = more likely to churn)'),
        bigquery.SchemaField('social_proof_affinity', 'FLOAT',
            description='Responsiveness to social proof messaging (reviews, testimonials) (0-1)'),
        bigquery.SchemaField('content_engagement_score', 'FLOAT',
            description='Engagement level with content marketing (blogs, guides) (0-1)'),
        
        # ====================================================================
        # PRODUCT CATEGORY AFFINITIES (from customer_scores table)
        # ====================================================================
        bigquery.SchemaField('living_room_affinity', 'FLOAT',
            description='Affinity for Living Room products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('bedroom_affinity', 'FLOAT',
            description='Affinity for Bedroom products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('kitchen_dining_affinity', 'FLOAT',
            description='Affinity for Kitchen & Dining products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('office_affinity', 'FLOAT',
            description='Affinity for Office products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('outdoor_affinity', 'FLOAT',
            description='Affinity for Outdoor products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('lighting_affinity', 'FLOAT',
            description='Affinity for Lighting products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('storage_affinity', 'FLOAT',
            description='Affinity for Storage & Organization products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('textiles_affinity', 'FLOAT',
            description='Affinity for Textiles products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('bathroom_affinity', 'FLOAT',
            description='Affinity for Bathroom products based on purchase/browse history (0-1)'),
        bigquery.SchemaField('decoration_affinity', 'FLOAT',
            description='Affinity for Decoration products based on purchase/browse history (0-1)'),
        
        # ====================================================================
        # PURCHASE PROFILE (from customer_scores table)
        # ====================================================================
        bigquery.SchemaField('favorite_category', 'STRING',
            description='Product category with most purchases'),
        bigquery.SchemaField('secondary_category', 'STRING',
            description='Product category with second-most purchases'),
        bigquery.SchemaField('cross_category_shopper', 'BOOLEAN',
            description='Whether customer shops across 3+ product categories'),
        bigquery.SchemaField('price_tier_preference', 'STRING',
            description='Preferred price tier based on average order value (budget, mid, premium)'),
        
        # ====================================================================
        # TRANSACTION METRICS - LIFETIME
        # ====================================================================
        bigquery.SchemaField('total_purchases', 'INTEGER',
            description='Total number of purchases (all-time)'),
        bigquery.SchemaField('total_revenue', 'FLOAT',
            description='Total revenue generated by customer (all-time)'),
        bigquery.SchemaField('avg_order_value', 'FLOAT',
            description='Average order value across all purchases'),
        bigquery.SchemaField('first_purchase_date', 'TIMESTAMP',
            description='Date of customer first purchase'),
        bigquery.SchemaField('last_purchase_date', 'TIMESTAMP',
            description='Date of customer most recent purchase'),
        bigquery.SchemaField('days_since_last_purchase', 'INTEGER',
            description='Days elapsed since last purchase (999999 if never purchased)'),
        bigquery.SchemaField('purchase_frequency_per_month', 'FLOAT',
            description='Average number of purchases per month since first purchase'),
        
        # ====================================================================
        # TRANSACTION METRICS - LAST 90 DAYS
        # ====================================================================
        bigquery.SchemaField('purchases_90d', 'INTEGER',
            description='Number of purchases in last 90 days'),
        bigquery.SchemaField('revenue_90d', 'FLOAT',
            description='Total revenue generated in last 90 days'),
        bigquery.SchemaField('avg_order_value_90d', 'FLOAT',
            description='Average order value in last 90 days'),
        
        # ====================================================================
        # TRANSACTION METRICS - LAST 30 DAYS
        # ====================================================================
        bigquery.SchemaField('purchases_30d', 'INTEGER',
            description='Number of purchases in last 30 days'),
        bigquery.SchemaField('revenue_30d', 'FLOAT',
            description='Total revenue generated in last 30 days'),
        bigquery.SchemaField('avg_order_value_30d', 'FLOAT',
            description='Average order value in last 30 days'),
        
        # ====================================================================
        # TRANSACTION CATEGORY INSIGHTS
        # ====================================================================
        bigquery.SchemaField('most_purchased_category', 'STRING',
            description='Product category with highest purchase count'),
        bigquery.SchemaField('most_recent_category', 'STRING',
            description='Product category of most recent purchase'),
        
        # ====================================================================
        # ABANDONED CART METRICS - LIFETIME
        # ====================================================================
        bigquery.SchemaField('total_abandoned_carts', 'INTEGER',
            description='Total number of abandoned carts (all-time)'),
        bigquery.SchemaField('total_abandoned_cart_value', 'FLOAT',
            description='Total value of all abandoned carts (all-time)'),
        bigquery.SchemaField('avg_abandoned_cart_value', 'FLOAT',
            description='Average value of abandoned carts'),
        bigquery.SchemaField('last_cart_abandonment_date', 'TIMESTAMP',
            description='Date of most recent cart abandonment'),
        bigquery.SchemaField('days_since_last_cart_abandonment', 'INTEGER',
            description='Days elapsed since last cart abandonment (999999 if never abandoned)'),
        
        # ====================================================================
        # ABANDONED CART METRICS - TIME WINDOWS
        # ====================================================================
        bigquery.SchemaField('abandoned_carts_30d', 'INTEGER',
            description='Number of abandoned carts in last 30 days'),
        bigquery.SchemaField('abandoned_cart_value_30d', 'FLOAT',
            description='Total value of abandoned carts in last 30 days'),
        bigquery.SchemaField('abandoned_carts_90d', 'INTEGER',
            description='Number of abandoned carts in last 90 days'),
        
        # ====================================================================
        # BEHAVIORAL ENGAGEMENT METRICS
        # ====================================================================
        bigquery.SchemaField('total_events_lifetime', 'INTEGER',
            description='Total number of behavioral events (page views, clicks, etc.) all-time'),
        bigquery.SchemaField('last_event_date', 'TIMESTAMP',
            description='Date of most recent behavioral event'),
        bigquery.SchemaField('days_since_last_event', 'INTEGER',
            description='Days elapsed since last event (999999 if no events)'),
        bigquery.SchemaField('events_90d', 'INTEGER',
            description='Number of behavioral events in last 90 days'),
        bigquery.SchemaField('events_30d', 'INTEGER',
            description='Number of behavioral events in last 30 days'),
        bigquery.SchemaField('most_viewed_category', 'STRING',
            description='Product category with most page views'),
        bigquery.SchemaField('engagement_rate_per_day', 'FLOAT',
            description='Average number of events per day since first event'),
        
        # ====================================================================
        # CAMPAIGN RESPONSE METRICS - LIFETIME
        # ====================================================================
        bigquery.SchemaField('total_campaigns_received', 'INTEGER',
            description='Total number of campaigns customer has been targeted with (all-time)'),
        bigquery.SchemaField('total_campaigns_converted', 'INTEGER',
            description='Total number of campaigns that resulted in conversion (all-time)'),
        bigquery.SchemaField('overall_conversion_rate', 'FLOAT',
            description='Overall campaign conversion rate (conversions / campaigns received)'),
        
        # ====================================================================
        # CAMPAIGN RESPONSE METRICS - LAST 90 DAYS
        # ====================================================================
        bigquery.SchemaField('campaigns_90d', 'INTEGER',
            description='Number of campaigns received in last 90 days'),
        bigquery.SchemaField('conversions_90d', 'INTEGER',
            description='Number of campaign conversions in last 90 days'),
        bigquery.SchemaField('conversion_rate_90d', 'FLOAT',
            description='Campaign conversion rate in last 90 days'),
        
        # ====================================================================
        # CAMPAIGN RESPONSE METRICS - LAST 30 DAYS
        # ====================================================================
        bigquery.SchemaField('campaigns_30d', 'INTEGER',
            description='Number of campaigns received in last 30 days'),
        
        # ====================================================================
        # CAMPAIGN INSIGHTS
        # ====================================================================
        bigquery.SchemaField('most_responsive_trigger_type', 'STRING',
            description='Campaign trigger type with highest conversion rate (e.g., discount, free_shipping)'),
        bigquery.SchemaField('last_campaign_date', 'TIMESTAMP',
            description='Date of most recent campaign received'),
        bigquery.SchemaField('days_since_last_campaign', 'INTEGER',
            description='Days elapsed since last campaign (999999 if never received campaign)'),
        
        # ====================================================================
        # METADATA
        # ====================================================================
        bigquery.SchemaField('last_updated_at', 'TIMESTAMP',
            description='Timestamp when this row was last updated (refresh timestamp)'),
    ]


def build_customers_unified_table():
    """
    Execute the SQL query to build customers unified table and apply schema with descriptions
    Creates table in cdp_data.customers for use by conversational segmentation agent
    """
    print("\n" + "="*70)
    print("  Building Customers Unified Table")
    print("="*70 + "\n")
    
    if not GOOGLE_CLOUD_PROJECT:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
    
    # Initialize BigQuery client
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    
    # Source dataset (where raw tables live)
    source_dataset_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}"
    
    # Target dataset and table (where unified table will be created)
    target_dataset_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_TARGET_DATASET}"
    table_id = f"{target_dataset_id}.{BIGQUERY_TARGET_TABLE}"
    
    # ========================================================================
    # Step 0: Create target dataset if it doesn't exist
    # ========================================================================
    print(f"📂 Ensuring target dataset exists: {BIGQUERY_TARGET_DATASET}")
    
    try:
        dataset = bigquery.Dataset(target_dataset_id)
        dataset.location = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
        dataset.description = "Consolidated customer data for conversational segmentation and AI-powered analytics"
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset {BIGQUERY_TARGET_DATASET} ready\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not create dataset: {str(e)}\n")
    
    print(f"📊 Target table: {table_id}\n")
    print(f"📊 Source dataset: {BIGQUERY_DATASET}\n")
    
    # ========================================================================
    # Step 1: Load SQL query from file
    # ========================================================================
    print("📄 Loading SQL query from file...")
    
    if not SQL_FILE_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE_PATH}")
    
    with open(SQL_FILE_PATH, 'r') as f:
        sql_query = f.read()
    
    # Replace placeholders
    sql_query = sql_query.replace('{project_id}', GOOGLE_CLOUD_PROJECT)
    sql_query = sql_query.replace('{dataset_id}', BIGQUERY_DATASET)
    
    print("✓ SQL query loaded\n")
    
    # ========================================================================
    # Step 2: Execute query to create/replace table
    # ========================================================================
    print("🔄 Executing query to build table...")
    print("   This may take 30-60 seconds depending on data size...\n")
    
    start_time = time.time()
    
    job_config = bigquery.QueryJobConfig(
        destination=table_id,
        write_disposition='WRITE_TRUNCATE',  # Replace existing table
    )
    
    query_job = client.query(sql_query, job_config=job_config)
    query_job.result()  # Wait for completion
    
    execution_time = time.time() - start_time
    
    print(f"✓ Query executed successfully in {execution_time:.1f} seconds\n")
    
    # ========================================================================
    # Step 3: Apply schema with descriptions
    # ========================================================================
    print("📝 Applying column descriptions...")
    
    # Get the actual table schema (with correct data types from query)
    table = client.get_table(table_id)
    existing_schema = table.schema
    
    # Create description mapping from our defined schema
    schema_with_descriptions = get_schema_with_descriptions()
    description_map = {field.name: field.description for field in schema_with_descriptions}
    
    # Update existing schema fields with descriptions (preserve actual data types)
    updated_schema = []
    for field in existing_schema:
        description = description_map.get(field.name, '')
        updated_field = bigquery.SchemaField(
            field.name,
            field.field_type,  # Use actual type from table
            mode=field.mode,
            description=description
        )
        updated_schema.append(updated_field)
    
    # Update table with descriptions
    table.schema = updated_schema
    table.description = (
        "Consolidated customer table with all attributes and behavioral metrics "
        "aggregated across multiple time windows (all-time, 90d, 30d). "
        "This table powers conversational segmentation by providing single-table "
        "access to comprehensive customer data without complex JOINs. "
        f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    
    table = client.update_table(table, ['schema', 'description'])
    
    print(f"✓ Applied descriptions for {len(updated_schema)} columns\n")
    
    # ========================================================================
    # Step 4: Display summary statistics
    # ========================================================================
    print("="*70)
    print("  Summary Statistics")
    print("="*70 + "\n")
    
    # Get row count
    query = f"SELECT COUNT(*) as row_count FROM `{table_id}`"
    result = client.query(query).result()
    row_count = list(result)[0].row_count
    
    print(f"  Total Customers: {row_count:,}")
    print(f"  Total Columns: {len(updated_schema)}")
    print(f"  Table Size: ~{row_count * len(updated_schema):,} data points")
    print(f"  Execution Time: {execution_time:.1f} seconds")
    print(f"  Table ID: {table_id}")
    
    # Sample some key metrics
    print(f"\n  Key Metrics (Sample):")
    sample_query = f"""
    SELECT
        COUNT(*) as total_customers,
        AVG(total_purchases) as avg_purchases,
        AVG(total_revenue) as avg_revenue,
        AVG(clv_score) as avg_clv,
        SUM(CASE WHEN purchases_30d > 0 THEN 1 ELSE 0 END) as active_30d,
        SUM(CASE WHEN total_abandoned_carts > 0 THEN 1 ELSE 0 END) as customers_with_abandoned_carts
    FROM `{table_id}`
    """
    result = client.query(sample_query).result()
    stats = list(result)[0]
    
    print(f"    - Avg Purchases/Customer: {stats.avg_purchases:.1f}")
    print(f"    - Avg Revenue/Customer: ${stats.avg_revenue:,.2f}")
    print(f"    - Avg CLV Score: {stats.avg_clv:.2%}")
    print(f"    - Active Last 30d: {stats.active_30d:,} ({stats.active_30d/row_count*100:.1f}%)")
    print(f"    - With Abandoned Carts: {stats.customers_with_abandoned_carts:,} ({stats.customers_with_abandoned_carts/row_count*100:.1f}%)")
    
    print("\n" + "="*70)
    print("  ✓ Build Complete!")
    print("="*70)
    print(f"\n  View in BigQuery Console:")
    print(f"  https://console.cloud.google.com/bigquery?project={GOOGLE_CLOUD_PROJECT}&ws=!1m5!1m4!4m3!1s{GOOGLE_CLOUD_PROJECT}!2s{BIGQUERY_TARGET_DATASET}!3s{BIGQUERY_TARGET_TABLE}")
    print(f"\n  Table Path: {table_id}")
    print("\n")


def main():
    """Main entry point"""
    try:
        build_customers_unified_table()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()

