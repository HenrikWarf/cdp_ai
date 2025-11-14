import os
import logging
from google.cloud import bigquery
import pandas as pd
import google.auth

# Configure logging for this module
logger = logging.getLogger(__name__)

def get_bigquery_client():
    """
    Initializes and returns a BigQuery client with explicit credentials.
    """
    try:
        credentials, project = google.auth.default()
        project_id = os.environ.get("BIGQUERY_PROJECT") or project
        logger.info(f"Initializing BigQuery client for project: {project_id}")
        return bigquery.Client(project=project_id, credentials=credentials)
    except Exception as e:
        logger.error("Failed to initialize BigQuery client", exc_info=True)
        raise

def list_datasets() -> str:
    """Lists all datasets in the BigQuery project."""
    logger.info("Attempting to list datasets...")
    try:
        client = get_bigquery_client()
        datasets = list(client.list_datasets())
        dataset_ids = [dataset.dataset_id for dataset in datasets]
        result = f"Available datasets: {', '.join(dataset_ids)}"
        logger.info(f"Successfully listed datasets: {result}")
        return result
    except Exception as e:
        logger.error("Failed to list datasets", exc_info=True)
        return f"An error occurred while listing datasets: {e}"

def list_tables(dataset_id: str) -> str:
    """Lists all tables in a given BigQuery dataset."""
    logger.info(f"Attempting to list tables for dataset: {dataset_id}")
    try:
        client = get_bigquery_client()
        tables = list(client.list_tables(dataset_id))
        table_ids = [table.table_id for table in tables]
        result = f"Tables in dataset '{dataset_id}': {', '.join(table_ids)}"
        logger.info(f"Successfully listed tables: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to list tables in dataset {dataset_id}", exc_info=True)
        return f"An error occurred while listing tables: {e}"

def get_table_schema(dataset_id: str, table_id: str) -> str:
    """Gets the schema of a given BigQuery table."""
    logger.info(f"Attempting to get schema for table: {dataset_id}.{table_id}")
    try:
        client = get_bigquery_client()
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)
        schema_info = [f"{field.name}: {field.field_type}" for field in table.schema]
        result = f"Schema for table '{dataset_id}.{table_id}':\n" + "\n".join(schema_info)
        logger.info(f"Successfully retrieved schema for {dataset_id}.{table_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get schema for table {dataset_id}.{table_id}", exc_info=True)
        return f"An error occurred while getting table schema: {e}"

def run_query(query: str) -> str:
    """
    Runs a SQL query on BigQuery and returns the result as a pandas DataFrame.
    """
    logger.info(f"Attempting to run query:\n---START QUERY---\n{query}\n---END QUERY---")
    try:
        client = get_bigquery_client()
        df = client.query(query).to_dataframe()
        result = df.to_string()
        logger.info(f"Query successful. Result rows: {len(df)}")
        return result
    except Exception as e:
        logger.error("BigQuery query failed", exc_info=True)
        return f"An error occurred while running the query: {e}"