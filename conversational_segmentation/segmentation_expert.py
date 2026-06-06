
from google.adk.agents import LlmAgent
import bigquery_tools
import os
import logging
# --- Environment Setup ---
from dotenv import load_dotenv
from pathlib import Path

# Load from local .env file in conversational_segmentation folder
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)
dataset = os.environ.get("BIGQUERY_DATASET")
table = os.environ.get("BIGQUERY_TABLE")


if not all([dataset, table]):
    logging.error("One or more environment variables are missing. Please ensure GOOGLE_CLOUD_PROJECT (or BIGQUERY_PROJECT), BIGQUERY_DATASET, and BIGQUERY_TABLE are set in your .env file.")


segmentation_expert_agent = LlmAgent(
    name="segmentation_expert",
    model="gemini-2.5-flash",
    instruction="""
    You are a segmentation expert. Your goal is to help users perform segmentation on the customer data.
    - Examine the schema of the table to confirm the column names to be used for segmentation.
    - Write and execute a BigQuery SQL querys to filter the data based on segmentation goal. 
    - Analyze the results and reason around the validity of the results. 
    - Provide a summary of the customer segment and define the attributes of the customers in the segment.
    """,
    tools=[
        bigquery_tools.list_datasets,
        bigquery_tools.list_tables,
        bigquery_tools.get_table_schema,
        bigquery_tools.run_query,
    ],
)
