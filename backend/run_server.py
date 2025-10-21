#!/usr/bin/env python3
"""
Startup script for the Sprint Coordinator FastAPI server.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Sprint Coordinator API server...")
    print("Frontend should be available at: http://localhost:5173")
    print("API documentation available at: http://localhost:8001/docs")
    print("Press Ctrl+C to stop the server")
    
    # Run the FastAPI app directly
    uvicorn.run(
        "app.fastapi_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
