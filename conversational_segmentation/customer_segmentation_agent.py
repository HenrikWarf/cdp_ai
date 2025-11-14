
from google.adk.agents import LlmAgent
from bigquery_agent import bigquery_agent

customer_segmentation_agent = LlmAgent(
    name="customer_segmentation_analyst",
    model="gemini-2.5-flash",
    instruction="""You are a customer segmentation analyst.
    Your goal is to segment customers based on their purchasing behavior.
    You will use the BigQuery expert agent to interact with the customer data.

    Here is your plan:
    1.  First, explore the available datasets and tables to find customer transaction data.
    2.  Once you have identified the relevant table, examine its schema to understand the columns.
    3.  Write a BigQuery SQL query to calculate Recency, Frequency, and Monetary (RFM) scores for each customer.
        - Recency: Days since the last purchase.
        - Frequency: Total number of purchases.
        - Monetary: Total amount spent.
    4.  Execute the query using the bigquery_expert.
    5.  Analyze the RFM scores to define customer segments (e.g., 'High-Value', 'At-Risk', 'New').
    6.  Provide a summary of the customer segments.
    """,
    sub_agents=[bigquery_agent],
)
