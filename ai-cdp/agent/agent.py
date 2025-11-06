"""CDP Analytics Agent"""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import json
from typing import Dict, List, Any
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# Configure console encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# ADK imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.genai import types

# ============================================================================
# Agent Tools (to be added later)
# ============================================================================

# Tools will be added here by the user

# ============================================================================
# Agent Definition
# ============================================================================

cdp_analytics_agent = LlmAgent(
    name="agent",
    model="gemini-2.5-flash",
    instruction="""You are a CDP (Customer Data Platform) Analytics Assistant.

I can help you with customer data analysis questions. Feel free to ask me anything about customer data, analytics, or insights.

I'm here to have a conversation with you and help answer your questions about customer data platforms.""",
    tools=[]
)

# ============================================================================
# FastAPI App
# ============================================================================

# Create ADK middleware agent instance
# Wrap the ADK agent with AG-UI protocol support
adk_agent = ADKAgent(cdp_analytics_agent)

# Create FastAPI app
app = FastAPI(title="CDP Analytics Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_agent, path="/")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "agent": "agent",
        "model": "gemini-2.5-flash",
        "tools": []
    }

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*70)
    print("CDP Analytics Agent with Google ADK + AG-UI Protocol")
    print("="*70)
    
    # Check required environment variables
    required_vars = {
        "GOOGLE_API_KEY": "Google AI API Key"
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask API keys
            if "KEY" in var or "CREDENTIALS" in var:
                display_value = value[:20] + "..." if len(value) > 20 else value
            else:
                display_value = value
            print(f"[OK] {description}: {display_value}")
        else:
            print(f"[X] {description}: NOT SET")
            all_present = False
    
    print("="*70)
    
    if not all_present:
        print("\nWARNING: Some required environment variables are not set!")
        print("         Please set them in your .env file\n")
    
    port = int(os.getenv("PORT", 8000))
    print(f"\n>>> Starting server on http://localhost:{port}")
    print(f">>> AG-UI Endpoint: http://localhost:{port}/")
    print(f">>> Health Check: http://localhost:{port}/health")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
