"""
Add demographic data (age, gender, income_level) to existing customers in BigQuery
This script updates the customers table with realistic demographic information
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import random
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple config loading
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')


def add_demographic_columns():
    """Add demographic columns to customers table if they don't exist"""
    print("Step 1: Adding demographic columns to customers table...")
    
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers"
    
    # Get existing table schema
    table = client.get_table(table_id)
    existing_fields = [field.name for field in table.schema]
    
    # Check if columns already exist
    new_fields = []
    if 'age' not in existing_fields:
        new_fields.append(bigquery.SchemaField('age', 'INTEGER'))
        print("  ✓ Will add 'age' column")
    else:
        print("  ⚠️  'age' column already exists")
    
    if 'gender' not in existing_fields:
        new_fields.append(bigquery.SchemaField('gender', 'STRING'))
        print("  ✓ Will add 'gender' column")
    else:
        print("  ⚠️  'gender' column already exists")
    
    if 'income_level' not in existing_fields:
        new_fields.append(bigquery.SchemaField('income_level', 'STRING'))
        print("  ✓ Will add 'income_level' column")
    else:
        print("  ⚠️  'income_level' column already exists")
    
    # Add new columns if needed
    if new_fields:
        # Update schema
        new_schema = list(table.schema) + new_fields
        table.schema = new_schema
        table = client.update_table(table, ["schema"])
        print(f"✓ Added {len(new_fields)} new columns to customers table")
    else:
        print("✓ All demographic columns already exist")
    
    return True


def generate_demographics_for_customers():
    """Fetch customers and generate demographic data"""
    print("\nStep 2: Generating demographic data for existing customers...")
    
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    
    # Fetch all customers with their CLV scores
    query = f"""
        SELECT customer_id, clv_score, age, gender, income_level
        FROM `{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers`
    """
    
    print("  Fetching customers from BigQuery...")
    customers_df = client.query(query).to_dataframe()
    print(f"  ✓ Found {len(customers_df)} customers")
    
    # Check if demographics already exist
    has_demographics = (
        customers_df['age'].notna().sum() > 0 or
        customers_df['gender'].notna().sum() > 0 or
        customers_df['income_level'].notna().sum() > 0
    )
    
    if has_demographics:
        print("  ⚠️  Some customers already have demographic data")
        response = input("  Do you want to regenerate demographics for ALL customers? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("  Skipping demographic generation")
            return False
    
    # Generate demographics for each customer
    print("  Generating demographics...")
    demographics_data = []
    
    for idx, row in customers_df.iterrows():
        customer_id = row['customer_id']
        clv_score = row['clv_score']
        
        # Generate age (18-75, weighted toward 25-55)
        age_normalized = np.random.beta(2.5, 2.5)
        age = int(18 + age_normalized * (75 - 18))
        
        # Generate gender with realistic distribution
        gender_rand = random.random()
        if gender_rand < 0.48:
            gender = 'Male'
        elif gender_rand < 0.96:
            gender = 'Female'
        elif gender_rand < 0.98:
            gender = 'Non-Binary'
        else:
            gender = 'Prefer Not to Say'
        
        # Generate income level correlated with CLV
        if clv_score >= 0.85:
            income_level = random.choices(['premium', 'high', 'medium'], weights=[0.6, 0.3, 0.1])[0]
        elif clv_score >= 0.70:
            income_level = random.choices(['premium', 'high', 'medium'], weights=[0.2, 0.5, 0.3])[0]
        elif clv_score >= 0.50:
            income_level = random.choices(['high', 'medium', 'low'], weights=[0.2, 0.6, 0.2])[0]
        else:
            income_level = random.choices(['medium', 'low'], weights=[0.4, 0.6])[0]
        
        demographics_data.append({
            'customer_id': customer_id,
            'age': age,
            'gender': gender,
            'income_level': income_level
        })
    
    demographics_df = pd.DataFrame(demographics_data)
    print(f"  ✓ Generated demographics for {len(demographics_df)} customers")
    
    return demographics_df


def update_customers_table(demographics_df):
    """Update customers table with demographic data"""
    print("\nStep 3: Updating customers table with demographic data...")
    
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    
    # Create a temporary table with the demographics data
    temp_table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.temp_demographics"
    
    print("  Creating temporary table with demographics...")
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        schema=[
            bigquery.SchemaField('customer_id', 'STRING'),
            bigquery.SchemaField('age', 'INTEGER'),
            bigquery.SchemaField('gender', 'STRING'),
            bigquery.SchemaField('income_level', 'STRING'),
        ]
    )
    
    job = client.load_table_from_dataframe(
        demographics_df, temp_table_id, job_config=job_config
    )
    job.result()
    print(f"  ✓ Created temp table with {len(demographics_df)} rows")
    
    # Update customers table using MERGE
    print("  Merging demographics into customers table...")
    merge_query = f"""
        MERGE `{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers` AS target
        USING `{temp_table_id}` AS source
        ON target.customer_id = source.customer_id
        WHEN MATCHED THEN
          UPDATE SET
            age = source.age,
            gender = source.gender,
            income_level = source.income_level
    """
    
    job = client.query(merge_query)
    job.result()
    print("  ✓ Successfully merged demographics into customers table")
    
    # Clean up temp table
    print("  Cleaning up temporary table...")
    client.delete_table(temp_table_id)
    print("  ✓ Removed temporary table")
    
    return True


def verify_update():
    """Verify the demographic data was added correctly"""
    print("\nStep 4: Verifying demographic data...")
    
    client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
    
    # Check demographics distribution
    query = f"""
        SELECT
            COUNT(*) as total_customers,
            COUNT(age) as customers_with_age,
            COUNT(gender) as customers_with_gender,
            COUNT(income_level) as customers_with_income,
            ROUND(AVG(age), 1) as avg_age,
            MIN(age) as min_age,
            MAX(age) as max_age
        FROM `{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers`
    """
    
    result = client.query(query).to_dataframe().iloc[0]
    
    print(f"  Total customers: {result['total_customers']}")
    print(f"  Customers with age: {result['customers_with_age']} ({result['customers_with_age']/result['total_customers']*100:.1f}%)")
    print(f"  Customers with gender: {result['customers_with_gender']} ({result['customers_with_gender']/result['total_customers']*100:.1f}%)")
    print(f"  Customers with income: {result['customers_with_income']} ({result['customers_with_income']/result['total_customers']*100:.1f}%)")
    print(f"  Age range: {result['min_age']} - {result['max_age']} (avg: {result['avg_age']})")
    
    # Gender distribution
    print("\n  Gender distribution:")
    gender_query = f"""
        SELECT gender, COUNT(*) as count
        FROM `{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers`
        WHERE gender IS NOT NULL
        GROUP BY gender
        ORDER BY count DESC
    """
    gender_dist = client.query(gender_query).to_dataframe()
    for _, row in gender_dist.iterrows():
        print(f"    {row['gender']}: {row['count']}")
    
    # Income distribution
    print("\n  Income level distribution:")
    income_query = f"""
        SELECT income_level, COUNT(*) as count
        FROM `{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.customers`
        WHERE income_level IS NOT NULL
        GROUP BY income_level
        ORDER BY count DESC
    """
    income_dist = client.query(income_query).to_dataframe()
    for _, row in income_dist.iterrows():
        print(f"    {row['income_level']}: {row['count']}")
    
    print("\n✓ Verification complete!")


def main():
    """Main execution"""
    print("="*60)
    print("Add Demographics to Existing Customer Data")
    print("="*60)
    print()
    
    if not GOOGLE_CLOUD_PROJECT:
        print("❌ Error: GOOGLE_CLOUD_PROJECT environment variable is required")
        return
    
    try:
        # Step 1: Add columns
        add_demographic_columns()
        
        # Step 2: Generate demographics
        demographics_df = generate_demographics_for_customers()
        if demographics_df is False:
            print("\n✓ Script completed (no updates made)")
            return
        
        # Step 3: Update table
        update_customers_table(demographics_df)
        
        # Step 4: Verify
        verify_update()
        
        print("\n" + "="*60)
        print("✓ Demographics successfully added to all customers!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

