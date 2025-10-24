"""
Incremental Event Generator for AetherSegment AI
Adds new behavioral events since last run to simulate near real-time customer activity
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

# Import config directly
from backend.config import Config

# Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'aethersegment_cdp')
EVENTS_PER_RUN = 500  # Number of new events to generate each run


class RealtimeEventGenerator:
    """Generate incremental events to simulate near real-time customer activity"""
    
    def __init__(self):
        self.project_id = GOOGLE_CLOUD_PROJECT
        self.dataset_id = BIGQUERY_DATASET
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")
        
        self.client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
        
        # Product categories and products - Furniture & Home Furnishing Company
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
        
        # Event types with realistic furniture browsing behavior
        self.event_types = [
            'page_view', 'product_view', 'add_to_cart', 'remove_from_cart',
            'add_to_wishlist', 'search', 'filter_applied', 'room_planner_used',
            'ar_view', 'stock_check', 'store_locator'
        ]
        
        # Weight for event types (some more common than others)
        self.event_weights = [25, 30, 10, 3, 8, 15, 5, 2, 1, 1, 1]
    
    def get_active_customers(self, limit=1000):
        """Get a sample of customer IDs from the database"""
        query = f"""
        SELECT customer_id
        FROM `{self.project_id}.{self.dataset_id}.customers`
        LIMIT {limit}
        """
        
        result = self.client.query(query).to_dataframe()
        return result['customer_id'].tolist()
    
    def get_last_event_timestamp(self):
        """Get the timestamp of the most recent event"""
        query = f"""
        SELECT MAX(timestamp) as last_timestamp
        FROM `{self.project_id}.{self.dataset_id}.behavioral_events`
        """
        
        try:
            result = self.client.query(query).to_dataframe()
            last_timestamp = result['last_timestamp'].iloc[0]
            
            if pd.isna(last_timestamp):
                # No events yet, return 1 hour ago
                return datetime.now() - timedelta(hours=1)
            
            # Convert to datetime if it's a timestamp
            if isinstance(last_timestamp, pd.Timestamp):
                return last_timestamp.to_pydatetime()
            return last_timestamp
        except Exception as e:
            print(f"⚠️  Could not get last event timestamp: {e}")
            # Default to 1 hour ago
            return datetime.now() - timedelta(hours=1)
    
    def generate_new_events(self, num_events=EVENTS_PER_RUN):
        """Generate new behavioral events since last run"""
        print(f"\n📊 Generating {num_events} new events...")
        
        # Get active customers
        print("   Fetching active customers...")
        customer_ids = self.get_active_customers(limit=1000)
        
        # Get last event timestamp
        last_timestamp = self.get_last_event_timestamp()
        print(f"   Last event was at: {last_timestamp}")
        
        current_time = datetime.now()
        time_diff = (current_time - last_timestamp).total_seconds()
        
        events = []
        
        for i in range(num_events):
            # Random customer from active pool
            customer_id = random.choice(customer_ids)
            
            # Event timestamp: distributed between last event and now
            # Most events are recent (exponential distribution)
            time_offset_seconds = random.expovariate(1 / (time_diff / 3))
            time_offset_seconds = min(time_offset_seconds, time_diff)
            event_timestamp = current_time - timedelta(seconds=time_offset_seconds)
            
            # Event type (weighted random)
            event_type = random.choices(self.event_types, weights=self.event_weights)[0]
            
            # Product details
            category = random.choice(self.product_categories)
            product = random.choice(self.products[category])
            
            events.append({
                'event_id': f"evt_{datetime.now().timestamp()}_{i:06d}",
                'customer_id': customer_id,
                'event_type': event_type,
                'product_category': category,
                'product_name': product,  # Match existing schema
                'timestamp': event_timestamp,
            })
        
        df = pd.DataFrame(events)
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        print(f"   ✓ Generated {len(df)} new events")
        print(f"   Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Event types: {df['event_type'].value_counts().to_dict()}")
        
        return df
    
    def upload_events(self, df):
        """Upload new events to BigQuery"""
        table_id = f"{self.project_id}.{self.dataset_id}.behavioral_events"
        
        print(f"\n📤 Uploading {len(df)} events to BigQuery...")
        
        try:
            # Configure load job
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",  # Append to existing table
                schema=[
                    bigquery.SchemaField("event_id", "STRING"),
                    bigquery.SchemaField("customer_id", "STRING"),
                    bigquery.SchemaField("event_type", "STRING"),
                    bigquery.SchemaField("product_category", "STRING"),
                    bigquery.SchemaField("product_name", "STRING"),  # Match existing schema
                    bigquery.SchemaField("timestamp", "DATETIME"),  # Match existing table schema
                ]
            )
            
            # Upload
            job = self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            )
            job.result()  # Wait for completion
            
            print(f"   ✅ Successfully uploaded {len(df)} events")
            
            # Verify upload
            query = f"""
            SELECT COUNT(*) as total_events
            FROM `{table_id}`
            """
            result = self.client.query(query).to_dataframe()
            total = result['total_events'].iloc[0]
            print(f"   📊 Total events in table: {total:,}")
            
        except Exception as e:
            print(f"   ❌ Error uploading events: {str(e)}")
            raise
    
    def run(self, num_events=EVENTS_PER_RUN):
        """Main execution flow"""
        print("\n" + "="*60)
        print("  AetherSegment AI - Real-Time Event Generator")
        print("="*60)
        print(f"  Project: {self.project_id}")
        print(f"  Dataset: {self.dataset_id}")
        print(f"  Events to generate: {num_events}")
        print("="*60)
        
        try:
            # Generate events
            events_df = self.generate_new_events(num_events)
            
            # Upload to BigQuery
            self.upload_events(events_df)
            
            print("\n✅ Real-time event generation complete!")
            print(f"   {num_events} new events added to behavioral_events table")
            print(f"   Run this script periodically to simulate ongoing customer activity")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            exit(1)


def main():
    """Main entry point"""
    # Allow custom event count via command line
    num_events = EVENTS_PER_RUN
    if len(sys.argv) > 1:
        try:
            num_events = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid event count, using default: {EVENTS_PER_RUN}")
    
    generator = RealtimeEventGenerator()
    generator.run(num_events)


if __name__ == '__main__':
    main()

