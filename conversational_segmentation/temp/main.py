
import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from customer_segmentation_agent import customer_segmentation_agent

# --- Configuration ---
APP_NAME = "customer_segmentation_app"
USER_ID = "test_user"
SESSION_ID = "test_session"

async def main():
    """
    This function sets up the ADK runner and runs the customer segmentation agent.
    """
    print("--- Customer Segmentation Agent ---")
    print("This agent will segment customers based on their purchasing behavior using BigQuery.")
    print("\nInstructions:")
    print("1. Make sure you have authenticated with Google Cloud CLI: `gcloud auth application-default login`")
    print("2. Create a file named .env in this directory.")
    print("3. Add the following line to the .env file, replacing with your GCP project ID:")
    print("   BIGQUERY_PROJECT=your-gcp-project-id")
    print("4. In your BigQuery project, create a dataset (e.g., 'customer_data').")
    print("5. Open the sample_data.sql file, replace 'your_dataset' with your dataset name, and run the query in your BigQuery console.")
    print("-" * 30)

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("BIGQUERY_PROJECT"):
        print("\nERROR: BIGQUERY_PROJECT environment variable not set.")
        print("Please follow the instructions above.")
        return

    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(
        agent=customer_segmentation_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    initial_prompt = "Please segment the customers in the customer_transactions table."
    print(f"\nInitial Prompt: {initial_prompt}\n")

    user_content = Content(role="user", parts=[Part(text=initial_prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(f"Final Response from {event.author}:")
            print(event.content.parts[0].text)
        elif event.content and event.content.parts:
            print(f"Intermediate Response from {event.author}:")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
