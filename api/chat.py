import sys
import os
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

from agent.graph import get_agent

app = FastAPI(title="SocioLead Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    lead_captured: bool = False
    session_id: str

agent = None

# Manual state storage (in-memory)
session_states = {}

def get_agent_instance():
    global agent
    if agent is None:
        agent = get_agent()
    return agent


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "SocioLead Agent API is running",
        "version": "1.0.0"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent_app = get_agent_instance()
        
        # Get existing state for this session
        existing_state = session_states.get(request.session_id, {
            "messages": [],
            "intent": None,
            "user_name": None,
            "user_email": None,
            "user_platform": None,
            "lead_captured": False,
            "context": None
        })
        
        print(f"DEBUG - Retrieved state: name={existing_state.get('user_name')}, email={existing_state.get('user_email')}")
        
        # Prepare input - append new message to existing messages
        input_state = {
            "messages": existing_state.get("messages", []) + [HumanMessage(content=request.message)],
            "intent": existing_state.get("intent"),
            "user_name": existing_state.get("user_name"),
            "user_email": existing_state.get("user_email"),
            "user_platform": existing_state.get("user_platform"),
            "lead_captured": existing_state.get("lead_captured", False),
            "context": existing_state.get("context")
        }
        
        print(f"DEBUG - Input state: name={input_state.get('user_name')}, email={input_state.get('user_email')}")
        
        # Invoke agent WITHOUT config (no checkpointer)
        result = agent_app.invoke(input_state)
        
        # Save the updated state
        session_states[request.session_id] = result
        
        print(f"DEBUG - Result state: name={result.get('user_name')}, email={result.get('user_email')}")
        
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "I'm sorry, I couldn't process that. Could you try again?"
        
        return ChatResponse(
            response=response_text,
            intent=result.get("intent"),
            lead_captured=result.get("lead_captured", False),
            session_id=request.session_id
        )
    
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    }


from mangum import Mangum
handler = Mangum(app)
