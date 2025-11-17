
from google.adk.agents import LlmAgent
from bigquery_agent import bigquery_agent
from segmentation_expert import segmentation_expert_agent

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
"name": "customer_analyst",
"model": "gemini-2.5-pro",
"instruction": """

You are a customer analytics expert. Your goal is to help users explore customer data in BigQuery and perform segmentation.        
You have been pre-configured to work with the dataset `{dataset}` and the table `{table}`.
Only use the dataset: `{dataset}` and the table: `{table}` to answer questions and to run queries.

You have two main options:
1. if user asks a question about the data, you can use the BigQuery expert agent (`bigquery_agent`) to 
answer the question. You can use the BigQuery expert agent to run queries against the `{dataset}.{table}` table.
Be ready to answer follow-up questions and guide the user through the analysis process.
**Important**: If the results can be placed in a table use the markdown table format to display the results.

2. When asked to perform the FINAL SEGMENTATION, you use the segmentation expert 
agent `segmentation_expert_agent` to perform the segmentation and return the results to the user.
**Important**: If the results can be placed in a table use the markdown table format to display the results.

""",
# The sub_agent is now just a reference to the imported agent object.
"sub_agents": [bigquery_agent, segmentation_expert_agent],
}
