"""
One-time migration script to copy customers_unified to cdp_data.customers

This script:
1. Creates the cdp_data dataset if it doesn't exist
2. Copies aethersegment_cdp.customers_unified to cdp_data.customers
3. Preserves all data, schema, and descriptions

Usage:
    python scripts/migrate_to_cdp_data.py
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
SOURCE_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')
SOURCE_TABLE = 'customers_unified'
TARGET_DATASET = 'cdp_data'
TARGET_TABLE = 'customers'


def migrate_table():
    """
    Copy customers_unified table to new cdp_data.customers location
    """
    print("\n" + "="*70)
    print("  Migration: customers_unified → cdp_data.customers")
    print("="*70 + "\n")
    
    if not GOOGLE_CLOUD_PROJECT:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
    
    # Initialize BigQuery client
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    
    source_table_id = f"{GOOGLE_CLOUD_PROJECT}.{SOURCE_DATASET}.{SOURCE_TABLE}"
    target_dataset_id = f"{GOOGLE_CLOUD_PROJECT}.{TARGET_DATASET}"
    target_table_id = f"{target_dataset_id}.{TARGET_TABLE}"
    
    # ========================================================================
    # Step 1: Check if source table exists
    # ========================================================================
    print(f"📊 Checking source table: {source_table_id}")
    
    try:
        source_table = client.get_table(source_table_id)
        print(f"✓ Source table found ({source_table.num_rows:,} rows)\n")
    except Exception as e:
        print(f"\n❌ Source table not found: {source_table_id}")
        print("   Run 'python scripts/build_customers_unified_table.py' to create the unified table first.")
        return
    
    # ========================================================================
    # Step 2: Create target dataset if it doesn't exist
    # ========================================================================
    print(f"📂 Creating target dataset: {TARGET_DATASET}")
    
    try:
        dataset = bigquery.Dataset(target_dataset_id)
        dataset.location = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
        dataset.description = "Consolidated customer data for conversational segmentation and AI-powered analytics"
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset {TARGET_DATASET} ready\n")
    except Exception as e:
        print(f"❌ Failed to create dataset: {str(e)}")
        return
    
    # ========================================================================
    # Step 3: Copy table (preserves schema, data, and descriptions)
    # ========================================================================
    print(f"🔄 Copying table to: {target_table_id}")
    print("   This may take 30-60 seconds...\n")
    
    try:
        # Use BigQuery's native table copy (preserves everything)
        job = client.copy_table(
            source_table_id,
            target_table_id,
            job_config=bigquery.CopyJobConfig(
                write_disposition='WRITE_TRUNCATE'  # Overwrite if exists
            )
        )
        
        # Wait for completion
        job.result()
        
        # Get the copied table
        target_table = client.get_table(target_table_id)
        
        print(f"✓ Table copied successfully!")
        print(f"  Rows copied: {target_table.num_rows:,}")
        print(f"  Columns: {len(target_table.schema)}")
        
    except Exception as e:
        print(f"❌ Failed to copy table: {str(e)}")
        return
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*70)
    print("  ✓ Migration Complete!")
    print("="*70)
    print(f"\n  Source: {source_table_id}")
    print(f"  Target: {target_table_id}")
    print(f"\n  Next Steps:")
    print(f"  - Use '{target_table_id}' for conversational segmentation")
    print(f"  - Run 'python scripts/refresh_customers_unified.py' for daily updates")
    print(f"  - (Optional) Delete old table: {source_table_id}")
    print(f"\n  View in BigQuery Console:")
    print(f"  https://console.cloud.google.com/bigquery?project={GOOGLE_CLOUD_PROJECT}&ws=!1m5!1m4!4m3!1s{GOOGLE_CLOUD_PROJECT}!2s{TARGET_DATASET}!3s{TARGET_TABLE}")
    print("\n")


def main():
    """Main entry point"""
    try:
        migrate_table()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()

