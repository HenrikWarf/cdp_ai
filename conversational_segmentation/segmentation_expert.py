
from google.adk.agents import LlmAgent
import bigquery_tools

segmentation_expert_agent = LlmAgent(
    name="segmentation_expert",
    model="gemini-2.5-flash",
    instruction="""
    You are a segmentation expert. Your goal is to help users perform segmentation on the customer data.
    You have been pre-configured to work with the dataset `{dataset}` and the table `{table}`.
    Only use the dataset: `{dataset}` and the table: `{table}` to answer questions and to run queries.

    - Examine the schema of the `{dataset}.{table}` table to confirm the column names to be used for segmentation.
    - Write and execute a BigQuery SQL querys to filter the data based on segmentation goal. 
    - Analyze the results and reason around the validity of the results. 
    - Provide a summary of the customer segment and define the attributes of the customers in the segment.
    - Provide the SQL query that was used to segment the data.
    """,
    tools=[
        bigquery_tools.list_datasets,
        bigquery_tools.list_tables,
        bigquery_tools.get_table_schema,
        bigquery_tools.run_query,
    ],
)
