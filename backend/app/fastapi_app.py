"""
FastAPI application for the Sprint Coordinator.
Provides HTTP endpoints for the React frontend to interact with the AI agent.
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types
from .config import APP_NAME, DEFAULT_USER_ID
from .copilot.agent import create_master_agent, create_session_service, root_agent
from .copilot.tools.sprint_tools import (
    _get_sprint_items,
    _get_sprint_item,
    _update_sprint_item_status
)
from .copilot.tools.canvas_tools import (
    _get_business_model_canvas,
    _update_business_model_canvas,
    _get_value_proposition_canvas,
    _update_value_proposition_canvas,
    _get_customer_segments,
    _update_customer_segments
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress ADK internal logging
# logging.getLogger("google_adk").setLevel(logging.WARNING)
# logging.getLogger("google_genai").setLevel(logging.WARNING)
# logging.getLogger("httpx").setLevel(logging.WARNING)

# Global instances - will be initialized in lifespan
master_agent = None
session_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global master_agent, session_service
    
    # Startup
    logger.info("Initializing Sprint Coordinator API...")
    try:
        # Use the imported root_agent instead of creating a new one
        master_agent = root_agent
        session_service = create_session_service()
        logger.info("Sprint Coordinator API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Sprint Coordinator API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sprint Coordinator API...")

# Create FastAPI app
app = FastAPI(
    title="Sprint Coordinator API",
    description="AI-powered sprint coordination system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    sprint_item_id: str
    message: str
    session_id: str

class ChatResponse(BaseModel):
    message: str
    session_id: str
    sprint_item_id: str

class WebSocketMessage(BaseModel):
    user_id: str
    session_id: str
    message: str
    sprint_item_id: str

# In-memory session storage for active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Sprint Coordinator API is running"}

@app.get("/test")
async def test():
    """Test endpoint to verify server is working."""
    try:
        result = _get_sprint_items()
        return {"status": "success", "data": json.loads(result)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/sprints")
async def get_sprints():
    """Get all sprint items."""
    try:
        result = _get_sprint_items()
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error fetching sprints: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sprints/{item_id}")
async def get_sprint_item_by_id(item_id: str):
    """Get specific sprint item by ID."""
    try:
        result = _get_sprint_item(item_id)
        data = json.loads(result)
        if "error" in data:
            raise HTTPException(status_code=404, detail=data["error"])
        return data
    except Exception as e:
        logger.error(f"Error fetching sprint item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/canvas/bmc")
async def get_bmc():
    """Get Business Model Canvas."""
    try:
        result = _get_business_model_canvas()
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error fetching BMC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/canvas/vpc")
async def get_vpc():
    """Get Value Proposition Canvas."""
    try:
        result = _get_value_proposition_canvas()
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error fetching VPC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/canvas/segments")
async def get_segments():
    """Get Customer Segments."""
    try:
        result = _get_customer_segments()
        return json.loads(result)
    except Exception as e:
        logger.error(f"Error fetching segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def initialize_session(session_id: str, sprint_item_id: str) -> Session:
    """Initialize a new session with the selected sprint item."""
    if session_service is None:
        raise HTTPException(status_code=500, detail="Session service not initialized")
    
    try:
        # Create session
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
            session_id=session_id
        )
        
        # Store sprint item in session state
        session.state["current_sprint_item"] = sprint_item_id
        session.state["current_phase"] = "design"
        session.state["phase_summaries"] = {}
        session.state["user_preferences"] = {}
        session.state["workflow_progress"] = {}
        
        # Store session reference
        active_sessions[session_id] = {
            "session": session,
            "sprint_item_id": sprint_item_id
        }
        
        logger.info(f"Initialized session {session_id} with sprint item {sprint_item_id}")
        return session
        
    except Exception as e:
        logger.error(f"Error initializing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize session: {str(e)}")

async def stream_agent_response_websocket(websocket: WebSocket, user_id: str, session_id: str, message: str, sprint_item_id: str):
    """Stream AI agent response using WebSocket."""
    if master_agent is None or session_service is None:
        await websocket.send_text("Agent not initialized. Please try again.")
        return
    
    try:
        # Create runner
        runner = Runner(
            agent=master_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        # Create content object
        content = types.Content(
            role='user',
            parts=[types.Part(text=message)]
        )
        
        logger.info(f"Processing streaming query for session {session_id}: {message}")
        start_agent_processing = time.time()
        
        # Create RunConfig with streaming enabled
        run_config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            max_llm_calls=200
        )
        
        # Process the query with streaming
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
            run_config=run_config
        ):
            # Only process events from the sprint coordinator agent that contain meaningful text
            if (event.author == 'sprint_coordinator' and 
                event.content and 
                event.content.parts and 
                hasattr(event.content.parts[0], 'text') and 
                event.content.parts[0].text):
                
                text_chunk = event.content.parts[0].text
                
                # Handle streaming tokens
                if hasattr(event, 'partial') and event.partial:
                    # Send individual token/chunk
                    await websocket.send_text(text_chunk)
                    
                elif event.is_final_response():
                    # Send final complete response
                    await websocket.send_text("--streaming ended--")
                    logger.info(f"--streaming ended--")
                    break
                    
        end_agent_processing = time.time()
        logger.info(f"Streaming query completed for session {session_id} in {end_agent_processing - start_agent_processing:.2f}s")
        
    except Exception as e:
        logger.error(f"Error during agent processing: {e}")
        await websocket.send_text("Something went wrong. Please try again.")

@app.post("/api/chat/init")
async def init_chat(request: ChatRequest):
    """Initialize a chat session with a selected sprint item."""
    try:
        # Initialize session
        await initialize_session(request.session_id, request.sprint_item_id)
        
        return {
            "message": "Chat session initialized successfully",
            "session_id": request.session_id,
            "sprint_item_id": request.sprint_item_id,
            "phase": "design"
        }
    except Exception as e:
        logger.error(f"Error initializing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses from the agent.
    
    Expected message format:
    {
        "user_id": "string",
        "session_id": "string", 
        "message": "string",
        "sprint_item_id": "string"
    }
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            try:
                raw_message = await websocket.receive_text()
                request_data = json.loads(raw_message)
                
                # Validate required fields
                if not all(key in request_data for key in ["user_id", "session_id", "message", "sprint_item_id"]):
                    logger.error("Missing required fields: user_id, session_id, message, sprint_item_id")
                    await websocket.send_text("Missing required fields. Please try again.")
                    continue
                    
                user_id = request_data["user_id"]
                session_id = request_data["session_id"]
                message = request_data["message"]
                sprint_item_id = request_data["sprint_item_id"]
            
            except Exception as e:
                logger.error(f"Error parsing message: {str(e)}")
                await websocket.send_text("Error parsing message. Please try again.")
                continue

            # Initialize session if not exists
            if session_id not in active_sessions:
                try:
                    await initialize_session(session_id, sprint_item_id)
                except Exception as e:
                    logger.error(f"Error initializing session: {e}")
                    await websocket.send_text("Error initializing session. Please try again.")
                    continue

            # Stream the agent response
            await stream_agent_response_websocket(
                websocket, user_id, session_id, message, sprint_item_id
            )

    except WebSocketDisconnect as err:
        logger.info(f"WebSocket client disconnected: {err}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text("Connection error. Please try again.")
        except:
            # Connection might be closed
            pass
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")

@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """Legacy SSE endpoint - kept for compatibility."""
    return StreamingResponse(
        stream_agent_response_sse(request.session_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

async def stream_agent_response_sse(session_id: str, message: str):
    """Legacy SSE streaming function."""
    if master_agent is None or session_service is None:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Agent not initialized', 'session_id': session_id})}\n\n"
        return
    
    try:
        # Get or create session
        if session_id not in active_sessions:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found. Please initialize chat first.', 'session_id': session_id})}\n\n"
            return
        
        session_data = active_sessions[session_id]
        session = session_data["session"]
        sprint_item_id = session_data["sprint_item_id"]
        
        # Create runner
        runner = Runner(
            agent=master_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        # Create content object
        content = types.Content(
            role='user',
            parts=[types.Part(text=message)]
        )
        
        # Stream the response
        events = runner.run_async(
            user_id=DEFAULT_USER_ID,
            session_id=session_id,
            new_message=content
        )
        
        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                yield f"data: {json.dumps({'type': 'final', 'message': final_response, 'session_id': session_id})}\n\n"
            elif hasattr(event, 'content') and event.content:
                # Stream partial responses
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield f"data: {json.dumps({'type': 'partial', 'message': part.text, 'session_id': session_id})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
        
    except Exception as e:
        logger.error(f"Error streaming agent response: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'session_id': session_id})}\n\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
