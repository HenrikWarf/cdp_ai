
from google.adk.agents import LlmAgent
import bigquery_tools

bigquery_agent = LlmAgent(
    name="bigquery_expert",
    model="gemini-2.5-flash",
    instruction="""You are a BigQuery expert.
    Your role is to help with BigQuery tasks like exploring datasets,
    checking table schemas, and running queries.
    Use the available tools to answer questions and perform tasks related to BigQuery.
    """,
    tools=[
        bigquery_tools.list_datasets,
        bigquery_tools.list_tables,
        bigquery_tools.get_table_schema,
        bigquery_tools.run_query,
    ],
)
