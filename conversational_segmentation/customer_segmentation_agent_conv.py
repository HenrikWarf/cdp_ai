
from google.adk.agents import LlmAgent
from bigquery_agent import bigquery_agent

class ConversationalCustomerSegmentationAgent(LlmAgent):
    """
    A conversational agent that can be initialized with BigQuery context.
    """
    def __init__(self, dataset: str, table: str, **kwargs):
        super().__init__(**kwargs)
        # Dynamically format the instruction with the provided context
        self.instruction = self.instruction.format(dataset=dataset, table=table)

# --- Agent Configuration Template ---
# This is now just a dictionary of parameters, NOT an agent instance.
# This prevents the sub-agent from being parented prematurely.
AGENT_CONFIG = {
    "name": "customer_segmentation_analyst",
    "model": "gemini-2.5-flash",
    "instruction": """You are a customer segmentation analyst.
Your goal is to help users explore customer data in BigQuery and perform segmentation.
You have been pre-configured to work with the dataset `{dataset}` and the table `{table}`.

Wait for the user's request.
Use the BigQuery expert agent to answer questions or to run queries against the `{dataset}.{table}` table.
Be ready to answer follow-up questions and guide the user through the analysis process.

When asked to perform the segmentation, you can follow these steps:
1. Examine the schema of the `{dataset}.{table}` table to confirm the column names.
2. Write and execute a BigQuery SQL query to filter the data based on segmentation goal. 
3. Analyze the results and reason around the validity of the results. 
4. Provide a summary of the customer segment and define the attributes of the customers in the segment.
""",
    # The sub_agent is now just a reference to the imported agent object.
    "sub_agents": [bigquery_agent],
}
