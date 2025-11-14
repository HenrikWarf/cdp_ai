import asyncio
import os
import uuid
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
# Import the agent class and the configuration dictionary
from customer_segmentation_agent_conv import ConversationalCustomerSegmentationAgent, AGENT_CONFIG

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Environment Setup ---
from dotenv import load_dotenv
from pathlib import Path

# Load from local .env file in conversational_segmentation folder
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Resolve service account credentials path
sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if sa_path and not os.path.isabs(sa_path):
    resolved_sa_path = (current_dir / sa_path).resolve()
    if resolved_sa_path.is_file():
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(resolved_sa_path)
    else:
        logging.warning(f"Service account file not found: {sa_path} (resolved to {resolved_sa_path})")

BIGQUERY_PROJECT = os.environ.get("BIGQUERY_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.environ.get("BIGQUERY_TABLE")

# Set BIGQUERY_PROJECT env var if using GOOGLE_CLOUD_PROJECT
if BIGQUERY_PROJECT and not os.environ.get("BIGQUERY_PROJECT"):
    os.environ["BIGQUERY_PROJECT"] = BIGQUERY_PROJECT

if not all([BIGQUERY_PROJECT, BIGQUERY_DATASET, BIGQUERY_TABLE]):
    logging.error("One or more environment variables are missing. Please ensure GOOGLE_CLOUD_PROJECT (or BIGQUERY_PROJECT), BIGQUERY_DATASET, and BIGQUERY_TABLE are set in your .env file.")

# --- ADK Setup ---
APP_NAME = "customer_segmentation_app_conv"
USER_ID = "webapp_user"

# --- Initialize the Agent with Context from .env file ---
# Create the single, definitive instance of the agent here.
# We unpack the configuration dictionary and pass the dynamic context.
contextual_agent = ConversationalCustomerSegmentationAgent(
    dataset=BIGQUERY_DATASET,
    table=BIGQUERY_TABLE,
    **AGENT_CONFIG
)

session_service = InMemorySessionService()
runner = Runner(
    agent=contextual_agent, # Use the new, correctly initialized agent instance
    app_name=APP_NAME,
    session_service=session_service,
)

# --- FastAPI App ---
app = FastAPI()

# --- WebSocket Chat Endpoint ---
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    logging.info(f"New client connected, session created: {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"[{session_id}] Received message: {data}")

            user_content = Content(role="user", parts=[Part(text=data)])

            async for event in runner.run_async(
                user_id=USER_ID, session_id=session_id, new_message=user_content
            ):
                logging.info(f"[{session_id}] Agent Event: {type(event).__name__} from {event.author}")
                
                response = {"type": type(event).__name__, "author": event.author, "content": None}
                if event.content and event.content.parts:
                    response["content"] = event.content.parts[0].text
                    logging.info(f"[{session_id}] Event Content: {response['content']}")

                await websocket.send_json(response)

    except WebSocketDisconnect:
        logging.info(f"Client disconnected, session ended: {session_id}")
        await session_service.delete_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    except Exception as e:
        logging.error(f"An error occurred in session {session_id}: {e}", exc_info=True)
        await websocket.send_json({"type": "error", "content": "An internal error occurred."})

# --- Serve Frontend Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')