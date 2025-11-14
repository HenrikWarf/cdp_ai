
import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
# Import the new conversational agent
from customer_segmentation_agent_conv import customer_segmentation_agent_conv

# --- Configuration ---
APP_NAME = "customer_segmentation_app_conv"
USER_ID = "test_user_conv"
SESSION_ID = "test_session_conv"

async def main():
    """
    This function sets up the ADK runner and runs the customer segmentation
    agent in an interactive conversational loop.
    """
    print("--- Conversational Customer Segmentation Agent ---")
    print("This agent can help you analyze customer data from BigQuery.")
    print("Type 'exit' to end the conversation.")
    print("\nInstructions:")
    print("1. Make sure you have authenticated with Google Cloud CLI: `gcloud auth application-default login`")
    print("2. Ensure your .env file is created with your BIGQUERY_PROJECT.")
    print("3. Ensure you have run the sample_data.sql in your BigQuery project.")
    print("-" * 30)

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("BIGQUERY_PROJECT"):
        print("\nERROR: BIGQUERY_PROJECT environment variable not set.")
        return

    # --- Setup the Runner and Session Service ONCE ---
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(
        agent=customer_segmentation_agent_conv, # Use the conversational agent
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("Agent is ready. You can start the conversation.")
    print("Try asking: 'Can you list the datasets?' or 'Please segment the customers.'")

    # --- Interactive Loop ---
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Ending conversation.")
                break

            user_content = Content(role="user", parts=[Part(text=user_input)])

            print("\nAgent:", end="", flush=True)
            final_response_text = ""
            async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                    print(final_response_text) # Print the final response

        except (KeyboardInterrupt, EOFError):
            print("\nEnding conversation.")
            break

if __name__ == "__main__":
    asyncio.run(main())
