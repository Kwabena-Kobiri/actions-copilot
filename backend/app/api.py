"""
FastAPI application for the Sprint Coordinator.
Provides WebSocket endpoints for streaming chat responses.
"""

import json
import logging
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types
from config import APP_NAME
from copilot.agent import create_master_agent, create_session_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress ADK internal logging
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Initialize FastAPI app
app = FastAPI(title="Sprint Coordinator API")

# Initialize services
master_agent = create_master_agent()
session_service = create_session_service()
runner = Runner(
    agent=master_agent,
    app_name=APP_NAME,
    session_service=session_service
)

# Store app name for session validation
app_name = APP_NAME


@app.websocket("/ws/chat/")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses from the agent.
    
    Expected message format:
    {
        "user_id": "string",
        "session_id": "string", 
        "message": "string"
    }
    
    Response:
    "text"
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            try:
                raw_message = await websocket.receive_text()
                request_data = json.loads(raw_message)
                
                # Validate required fields
                if not all(key in request_data for key in ["user_id", "session_id", "message"]):
                    logger.error("Missing required fields: user_id, session_id, message")
                    await websocket.send_text("Something went wrong. Please contact Customer Support")
                    continue
                    
                user_id = request_data["user_id"]
                session_id = request_data["session_id"]
                message = request_data["message"]
            
            except Exception as e:
                logger.error(f"Error parsing message: {str(e)}")
                await websocket.send_text("Something went wrong. Please contact Customer Support")
                continue

            # Validate or create session
            try:
                current_session = await session_service.get_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # If session doesn't exist, create it
                if not current_session:
                    logger.info(f"Session not found, creating new session: {session_id} for user: {user_id}")
                    current_session = await session_service.create_session(
                        app_name=app_name,
                        user_id=user_id,
                        session_id=session_id
                    )
                    logger.info(f"Session created successfully: {session_id}")
                
            except Exception as e:
                logger.error(f"Session validation/creation error: {str(e)}")
                await websocket.send_text("Something went wrong. Please contact Customer Support")
                continue

            # Create message content
            content = types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )

            logger.info(f"Processing streaming query for session {session_id}: {message}")
            start_agent_processing = time.time()
            
            try:
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
                    if (event.content and 
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
                await websocket.send_text("Something went wrong. Please contact Customer Support")

    except WebSocketDisconnect as err:
        logger.info(f"WebSocket client disconnected: {err}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text("Something went wrong. Please contact Customer Support")
        except:
            # Connection might be closed
            pass
    finally:
        try:
            await websocket.close()
            logger.info("WebSocket connection closed")
        except:
            # Connection already closed
            pass


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Sprint Coordinator API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
