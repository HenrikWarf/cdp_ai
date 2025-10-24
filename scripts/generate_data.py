"""
Generate synthetic customer data for BigQuery
Creates realistic customer profiles, transactions, behavioral events, and campaign history
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple config loading (avoid importing backend to prevent circular imports)
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')


# Data generation parameters
NUM_CUSTOMERS = 10000
NUM_TRANSACTIONS = 50000
NUM_BEHAVIORAL_EVENTS = 100000
NUM_CAMPAIGNS = 20
NUM_ABANDONED_CARTS = 5000


class DataGenerator:
    """Generate synthetic customer data for the CDP"""
    
    def __init__(self):
        if not GOOGLE_CLOUD_PROJECT:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        
        self.client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
        self.customer_ids = []
        
        # Product catalog
        # Product categories and products - Furniture & Home Furnishing Company (like IKEA)
        self.product_categories = [
            'Living Room', 'Bedroom', 'Kitchen & Dining', 'Office', 'Storage & Organization',
            'Bathroom', 'Outdoor', 'Lighting', 'Textiles', 'Decoration'
        ]
        
        self.products = {
            'Living Room': ['Sofa', 'Armchair', 'Coffee Table', 'TV Stand', 'Bookshelf', 'Side Table', 'Rug', 'Ottoman'],
            'Bedroom': ['Bed Frame', 'Mattress', 'Wardrobe', 'Nightstand', 'Dresser', 'Bedding Set', 'Mirror', 'Bedside Lamp'],
            'Kitchen & Dining': ['Dining Table', 'Dining Chairs', 'Bar Stool', 'Kitchen Cabinet', 'Cookware Set', 'Dinnerware Set', 'Kitchen Cart', 'Cutlery Set'],
            'Office': ['Desk', 'Office Chair', 'Filing Cabinet', 'Desk Lamp', 'Bookcase', 'Monitor Stand', 'Storage Box', 'Whiteboard'],
            'Storage & Organization': ['Shelving Unit', 'Storage Boxes', 'Drawer Unit', 'Closet Organizer', 'Shoe Rack', 'Wall Shelf', 'Storage Basket', 'Cabinet'],
            'Bathroom': ['Bathroom Cabinet', 'Mirror Cabinet', 'Towel Rack', 'Bath Mat', 'Shower Curtain', 'Storage Trolley', 'Vanity Unit', 'Bathroom Shelf'],
            'Outdoor': ['Patio Set', 'Garden Chair', 'Outdoor Table', 'Sun Lounger', 'Parasol', 'Outdoor Storage', 'Planter', 'Garden Bench'],
            'Lighting': ['Floor Lamp', 'Table Lamp', 'Ceiling Light', 'Pendant Light', 'Desk Lamp', 'LED Strip', 'Wall Light', 'Smart Bulb'],
            'Textiles': ['Curtains', 'Cushions', 'Throw Blanket', 'Duvet Cover', 'Pillow', 'Bath Towel', 'Table Runner', 'Rug'],
            'Decoration': ['Wall Art', 'Vase', 'Picture Frame', 'Candle Holder', 'Plant Pot', 'Clock', 'Decorative Bowl', 'Wall Sticker']
        }
        
        # Cities for location data - Multi-country distribution
        self.cities = [
            # United States - 40%
            ('New York', 'United States'), ('Los Angeles', 'United States'), ('Chicago', 'United States'),
            ('Houston', 'United States'), ('Phoenix', 'United States'), ('Seattle', 'United States'),
            
            # United Kingdom - 25%
            ('London', 'United Kingdom'), ('Manchester', 'United Kingdom'), ('Birmingham', 'United Kingdom'),
            ('Glasgow', 'United Kingdom'), ('Edinburgh', 'United Kingdom'),
            
            # Canada - 20%
            ('Toronto', 'Canada'), ('Vancouver', 'Canada'), ('Montreal', 'Canada'),
            ('Calgary', 'Canada'), ('Ottawa', 'Canada'),
            
            # Australia - 15%
            ('Sydney', 'Australia'), ('Melbourne', 'Australia'), ('Brisbane', 'Australia'),
            ('Perth', 'Australia'), ('Adelaide', 'Australia')
        ]
        
        # Acquisition sources
        self.acquisition_sources = [
            'organic_search', 'paid_search', 'social_media', 'email_campaign',
            'referral', 'direct', 'display_ads', 'affiliate'
        ]
        
        # First names for personalization
        self.first_names = [
            'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason',
            'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia',
            'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail', 'Michael',
            'Emily', 'Daniel', 'Elizabeth', 'Matthew', 'Sofia', 'Jackson', 'Avery',
            'Sebastian', 'Ella', 'Jack', 'Scarlett', 'Aiden', 'Grace', 'Owen', 'Chloe'
        ]
    
    def create_dataset_and_tables(self):
        """Create the BigQuery dataset and tables"""
        print("Creating BigQuery dataset and tables...")
        
        # Create dataset
        dataset_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = GOOGLE_CLOUD_REGION
        dataset = self.client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset {BIGQUERY_DATASET} ready")
        
        # Define table schemas
        schemas = {
            'customers': [
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('email_address', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('first_name', 'STRING'),
                bigquery.SchemaField('location_city', 'STRING'),
                bigquery.SchemaField('location_country', 'STRING'),
                bigquery.SchemaField('acquisition_source', 'STRING'),
                bigquery.SchemaField('creation_date', 'TIMESTAMP'),
                bigquery.SchemaField('clv_score', 'FLOAT'),
            ],
            'customer_scores': [
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('discount_sensitivity_score', 'FLOAT'),
                bigquery.SchemaField('free_shipping_sensitivity_score', 'FLOAT'),
                bigquery.SchemaField('exclusivity_seeker_flag', 'BOOLEAN'),
                bigquery.SchemaField('churn_probability_score', 'FLOAT'),
                bigquery.SchemaField('social_proof_affinity', 'FLOAT'),
                bigquery.SchemaField('content_engagement_score', 'FLOAT'),
            ],
            'transactions': [
                bigquery.SchemaField('transaction_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('order_value', 'FLOAT'),
                bigquery.SchemaField('product_category', 'STRING'),
                bigquery.SchemaField('product_name', 'STRING'),
                bigquery.SchemaField('timestamp', 'TIMESTAMP'),
            ],
            'abandoned_carts': [
                bigquery.SchemaField('cart_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('cart_value', 'FLOAT'),
                bigquery.SchemaField('items', 'STRING'),  # JSON string
                bigquery.SchemaField('timestamp', 'TIMESTAMP'),
                bigquery.SchemaField('status', 'STRING'),
            ],
            'behavioral_events': [
                bigquery.SchemaField('event_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('event_type', 'STRING'),
                bigquery.SchemaField('product_category', 'STRING'),
                bigquery.SchemaField('product_name', 'STRING'),
                bigquery.SchemaField('timestamp', 'TIMESTAMP'),
            ],
            'campaign_history': [
                bigquery.SchemaField('campaign_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('customer_id', 'STRING', mode='REQUIRED'),
                bigquery.SchemaField('trigger_type', 'STRING'),
                bigquery.SchemaField('converted', 'BOOLEAN'),
                bigquery.SchemaField('control_group', 'BOOLEAN'),
                bigquery.SchemaField('timestamp', 'TIMESTAMP'),
            ],
        }
        
        # Create tables
        for table_name, schema in schemas.items():
            table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.{table_name}"
            table = bigquery.Table(table_id, schema=schema)
            table = self.client.create_table(table, exists_ok=True)
            print(f"✓ Table {table_name} ready")
    
    def load_dataframe(self, table_name, df):
        """Load a pandas DataFrame into BigQuery"""
        table_id = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )
        
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for the job to complete
        
        print(f"✓ Loaded {len(df):,} rows into {table_name}")
    
    def generate_customers(self):
        """Generate customer profiles"""
        customers = []
        current_date = datetime.now()
        
        for i in range(NUM_CUSTOMERS):
            customer_id = f"cust_{i+1:06d}"
            self.customer_ids.append(customer_id)
            
            # Generate creation date (customers acquired over last 2 years)
            days_ago = random.randint(1, 730)
            creation_date = current_date - timedelta(days=days_ago)
            
            # CLV score (0-1, skewed towards lower values with some high-value customers)
            # CLV score: beta(5, 2) gives mean of ~0.71 (71%) - realistic distribution
            # This creates: some high-value (top 20%), many mid-value (60%), some low-value (20%)
            clv_score = min(1.0, abs(np.random.beta(5, 2)))
            
            city, country = random.choice(self.cities)
            
            customers.append({
                'customer_id': customer_id,
                'email_address': f"{random.choice(self.first_names).lower()}.{customer_id}@example.com",
                'first_name': random.choice(self.first_names),
                'location_city': city,
                'location_country': country,
                'acquisition_source': random.choice(self.acquisition_sources),
                'creation_date': creation_date,
                'clv_score': round(clv_score, 3),
            })
        
        df = pd.DataFrame(customers)
        print(f"✓ Generated {len(df)} customers")
        return df
    
    def generate_customer_scores(self):
        """Generate ML-derived customer scores"""
        scores = []
        
        for customer_id in self.customer_ids:
            scores.append({
                'customer_id': customer_id,
                'discount_sensitivity_score': round(random.uniform(0, 1), 3),
                'free_shipping_sensitivity_score': round(random.uniform(0, 1), 3),
                'exclusivity_seeker_flag': random.choice([True, False]),
                'churn_probability_score': round(random.uniform(0, 1), 3),
                'social_proof_affinity': round(random.uniform(0, 1), 3),
                'content_engagement_score': round(random.uniform(0, 1), 3),
            })
        
        df = pd.DataFrame(scores)
        print(f"✓ Generated scores for {len(df)} customers")
        return df
    
    def generate_transactions(self):
        """Generate transaction history"""
        transactions = []
        current_date = datetime.now()
        
        # Distribute transactions across customers (some customers buy more than others)
        for _ in range(NUM_TRANSACTIONS):
            customer_id = random.choice(self.customer_ids)
            
            # Transaction date (within last year)
            days_ago = random.randint(1, 365)
            transaction_date = current_date - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Select product
            category = random.choice(self.product_categories)
            product = random.choice(self.products[category])
            
            # Order value (furniture prices - varies by category)
            # Furniture tends to be higher value than typical e-commerce
            category_price_ranges = {
                'Living Room': (200, 2500),  # Sofas, large furniture
                'Bedroom': (150, 1800),
                'Kitchen & Dining': (100, 1500),
                'Office': (150, 1200),
                'Storage & Organization': (30, 400),
                'Bathroom': (50, 600),
                'Outdoor': (100, 1200),
                'Lighting': (20, 300),
                'Textiles': (10, 150),
                'Decoration': (15, 200)
            }
            price_range = category_price_ranges.get(category, (50, 500))
            order_value = round(random.uniform(price_range[0], price_range[1]), 2)
            
            transactions.append({
                'transaction_id': f"txn_{len(transactions)+1:08d}",
                'customer_id': customer_id,
                'order_value': order_value,
                'product_category': category,
                'product_name': product,
                'timestamp': transaction_date,
            })
        
        df = pd.DataFrame(transactions)
        print(f"✓ Generated {len(df)} transactions")
        return df
    
    def generate_abandoned_carts(self):
        """Generate abandoned cart data"""
        carts = []
        current_date = datetime.now()
        
        # Select subset of customers who have abandoned carts
        customers_with_carts = random.sample(self.customer_ids, NUM_ABANDONED_CARTS)
        
        for i, customer_id in enumerate(customers_with_carts):
            # Cart abandoned in last 30 days
            # 70% of carts in last 7 days for better testing
            if random.random() < 0.7:
                hours_ago = random.randint(1, 168)  # Last 7 days
            else:
                hours_ago = random.randint(169, 720)  # 7-30 days ago
            cart_date = current_date - timedelta(hours=hours_ago)
            
            # Generate cart items
            num_items = random.randint(1, 5)
            items = []
            total_value = 0
            
            for _ in range(num_items):
                category = random.choice(self.product_categories)
                product = random.choice(self.products[category])
                # Use same furniture pricing as transactions
                category_price_ranges = {
                    'Living Room': (200, 2500),
                    'Bedroom': (150, 1800),
                    'Kitchen & Dining': (100, 1500),
                    'Office': (150, 1200),
                    'Storage & Organization': (30, 400),
                    'Bathroom': (50, 600),
                    'Outdoor': (100, 1200),
                    'Lighting': (20, 300),
                    'Textiles': (10, 150),
                    'Decoration': (15, 200)
                }
                price_range = category_price_ranges.get(category, (50, 500))
                price = round(random.uniform(price_range[0], price_range[1]), 2)
                items.append({'product': product, 'category': category, 'price': price})
                total_value += price
            
            carts.append({
                'cart_id': f"cart_{i+1:06d}",
                'customer_id': customer_id,
                'cart_value': round(total_value, 2),
                'items': json.dumps(items),
                'timestamp': cart_date,
                'status': 'abandoned',
            })
        
        df = pd.DataFrame(carts)
        print(f"✓ Generated {len(df)} abandoned carts")
        return df
    
    def generate_behavioral_events(self):
        """Generate behavioral events (page views, clicks, etc.)"""
        events = []
        current_date = datetime.now()
        
        event_types = ['page_view', 'product_view', 'add_to_cart', 'add_to_wishlist', 
                      'search', 'category_browse', 'review_read']
        
        for i in range(NUM_BEHAVIORAL_EVENTS):
            customer_id = random.choice(self.customer_ids)
            
            # Event timestamp (last 90 days)
            hours_ago = random.randint(1, 2160)
            event_date = current_date - timedelta(hours=hours_ago, minutes=random.randint(0, 59))
            
            category = random.choice(self.product_categories)
            product = random.choice(self.products[category])
            
            events.append({
                'event_id': f"evt_{i+1:08d}",
                'customer_id': customer_id,
                'event_type': random.choice(event_types),
                'product_category': category,
                'product_name': product,
                'timestamp': event_date,
            })
        
        df = pd.DataFrame(events)
        print(f"✓ Generated {len(df)} behavioral events")
        return df
    
    def generate_campaign_history(self):
        """Generate historical campaign data for uplift training"""
        campaigns = []
        current_date = datetime.now()
        
        trigger_types = ['discount', 'free_shipping', 'scarcity', 'exclusivity', 
                        'social_proof', 'content', 'bundling', 'cashback']
        
        # Generate multiple campaigns
        for campaign_num in range(NUM_CAMPAIGNS):
            campaign_id = f"camp_{campaign_num+1:03d}"
            trigger = random.choice(trigger_types)
            
            # Each campaign targets 20-30% of customers
            num_targeted = int(len(self.customer_ids) * random.uniform(0.2, 0.3))
            targeted_customers = random.sample(self.customer_ids, num_targeted)
            
            # Campaign date (within last 2 years)
            days_ago = random.randint(30, 730)
            campaign_date = current_date - timedelta(days=days_ago)
            
            # Split into treatment and control groups
            control_size = int(num_targeted * 0.3)
            control_group = set(random.sample(targeted_customers, control_size))
            
            for customer_id in targeted_customers:
                is_control = customer_id in control_group
                
                # Conversion rates differ by trigger and control/treatment
                if is_control:
                    conversion_prob = 0.10  # Baseline conversion
                else:
                    # Different triggers have different effectiveness
                    trigger_effectiveness = {
                        'discount': 0.25,
                        'free_shipping': 0.22,
                        'scarcity': 0.20,
                        'exclusivity': 0.18,
                        'social_proof': 0.16,
                        'content': 0.14,
                        'bundling': 0.23,
                        'cashback': 0.21,
                    }
                    conversion_prob = trigger_effectiveness.get(trigger, 0.15)
                
                converted = random.random() < conversion_prob
                
                campaigns.append({
                    'campaign_id': campaign_id,
                    'customer_id': customer_id,
                    'trigger_type': trigger,
                    'converted': converted,
                    'control_group': is_control,
                    'timestamp': campaign_date
                })
        
        df = pd.DataFrame(campaigns)
        print(f"✓ Generated {len(df)} campaign history records")
        return df
    
    def load_all_data(self):
        """Generate and load all data into BigQuery"""
        print("\n" + "="*60)
        print("  AetherSegment AI - Data Generation")
        print("="*60 + "\n")
        
        # Create dataset and tables
        self.create_dataset_and_tables()
        
        print("\nGenerating data...")
        
        # Generate all data
        customers_df = self.generate_customers()
        scores_df = self.generate_customer_scores()
        transactions_df = self.generate_transactions()
        carts_df = self.generate_abandoned_carts()
        events_df = self.generate_behavioral_events()
        campaigns_df = self.generate_campaign_history()
        
        print("\nLoading data into BigQuery...")
        
        # Load data into BigQuery
        self.load_dataframe('customers', customers_df)
        self.load_dataframe('customer_scores', scores_df)
        self.load_dataframe('transactions', transactions_df)
        self.load_dataframe('abandoned_carts', carts_df)
        self.load_dataframe('behavioral_events', events_df)
        self.load_dataframe('campaign_history', campaigns_df)
        
        print("\n" + "="*60)
        print("  ✓ Data Generation Complete!")
        print("="*60)
        print(f"  Dataset: {BIGQUERY_DATASET}")
        print(f"  Project: {GOOGLE_CLOUD_PROJECT}")
        print(f"  Customers: {len(customers_df):,}")
        print(f"  Transactions: {len(transactions_df):,}")
        print(f"  Abandoned Carts: {len(carts_df):,}")
        print(f"  Behavioral Events: {len(events_df):,}")
        print(f"  Campaign Records: {len(campaigns_df):,}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    try:
        generator = DataGenerator()
        generator.load_all_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
