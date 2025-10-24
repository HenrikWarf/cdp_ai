"""
BigQuery service for data operations
"""
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from typing import List, Dict, Any, Optional
import pandas as pd
from backend.config import Config


class BigQueryService:
    """Service for interacting with BigQuery"""
    
    def __init__(self, project_id: str = None, dataset_id: str = None):
        """
        Initialize BigQuery service
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id or Config.GOOGLE_CLOUD_PROJECT
        self.dataset_id = dataset_id or Config.BIGQUERY_DATASET
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_ref = f"{self.project_id}.{self.dataset_id}"
    
    def query(self, sql: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            sql: SQL query string
            params: Optional query parameters
        
        Returns:
            DataFrame with query results
        """
        try:
            query_job = self.client.query(sql)
            df = query_job.to_dataframe()
            return df
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {str(e)}")
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dictionaries
        
        Args:
            sql: SQL query string
        
        Returns:
            List of row dictionaries
        """
        df = self.query(sql)
        return df.to_dict('records')
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists
        
        Args:
            table_name: Name of the table
        
        Returns:
            True if table exists, False otherwise
        """
        table_ref = f"{self.dataset_ref}.{table_name}"
        try:
            self.client.get_table(table_ref)
            return True
        except NotFound:
            return False
    
    def create_dataset(self):
        """Create the dataset if it doesn't exist"""
        dataset = bigquery.Dataset(self.dataset_ref)
        dataset.location = "US"
        
        try:
            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"Created dataset {self.dataset_ref}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Dataset {self.dataset_ref} already exists")
            else:
                raise
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]):
        """
        Insert rows into a table
        
        Args:
            table_name: Name of the table
            rows: List of row dictionaries
        """
        table_ref = f"{self.dataset_ref}.{table_name}"
        errors = self.client.insert_rows_json(table_ref, rows)
        
        if errors:
            raise RuntimeError(f"Failed to insert rows: {errors}")
    
    def load_dataframe(self, table_name: str, df: pd.DataFrame, write_disposition: str = "WRITE_APPEND"):
        """
        Load a DataFrame into a BigQuery table
        
        Args:
            table_name: Name of the table
            df: DataFrame to load
            write_disposition: Write disposition (WRITE_APPEND, WRITE_TRUNCATE, WRITE_EMPTY)
        """
        table_ref = f"{self.dataset_ref}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
        )
        
        job = self.client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()  # Wait for the job to complete
        
        print(f"Loaded {len(df)} rows into {table_ref}")
    
    def get_table_schema(self, table_name: str) -> List[bigquery.SchemaField]:
        """
        Get the schema of a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of SchemaField objects
        """
        table_ref = f"{self.dataset_ref}.{table_name}"
        table = self.client.get_table(table_ref)
        return table.schema
    
    def get_table_row_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            Number of rows
        """
        sql = f"SELECT COUNT(*) as count FROM `{self.dataset_ref}.{table_name}`"
        result = self.execute_query(sql)
        return result[0]['count'] if result else 0
    
    def create_table_from_schema(self, table_name: str, schema: List[bigquery.SchemaField]):
        """
        Create a table with the given schema
        
        Args:
            table_name: Name of the table to create
            schema: List of SchemaField objects defining the table structure
        """
        table_ref = f"{self.dataset_ref}.{table_name}"
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table_ref}")
        except Exception as e:
            if "Already Exists" in str(e):
                print(f"Table {table_ref} already exists")
            else:
                raise

