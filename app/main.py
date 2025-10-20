"""
Main entry point for the Sprint Coordinator application.
Provides an async interface for interacting with the sequential agent system.
"""

import asyncio
import logging
from typing import Optional
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.genai import types
from config import APP_NAME, DEFAULT_USER_ID
from copilot.agent import create_master_agent, create_session_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress ADK internal logging
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

class SprintCoordinatorApp:
    """Main application class for the Sprint Coordinator."""
    
    def __init__(self):
        """Initialize the application with master agent and session service."""
        self.master_agent = create_master_agent()
        self.session_service = create_session_service()
        self.session: Optional[Session] = None
        self.runner: Optional[Runner] = None
        self.user_id = DEFAULT_USER_ID
        self.session_id = "main_session"
    
    async def initialize(self) -> None:
        """Initialize the session and runner."""
        try:
            # Create session
            self.session = await self.session_service.create_session(
                app_name=APP_NAME,
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            # Create runner
            self.runner = Runner(
                agent=self.master_agent,
                app_name=APP_NAME,
                session_service=self.session_service
            )
            
            logger.info("Sprint Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sprint Coordinator: {e}")
            raise
    
    async def run(self) -> None:
        """Main application loop."""
        print("Welcome to the Sprint Coordinator!")
        print("=" * 50)
        print("This system will guide you through your sprint items using a")
        print("Design -> Execute -> Report -> Learn workflow.")
        print("=" * 50)
        
        try:
            # Start the conversation
            await self._start_conversation()
            
            # Main interaction loop
            while True:
                user_input = await self._get_user_input()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using the Sprint Coordinator!")
                    break
                
                if user_input.strip():
                    await self._process_user_input(user_input)
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"An error occurred: {e}")
    
    async def _start_conversation(self) -> None:
        """Start the initial conversation with the agent."""
        initial_message = "Hello! I'm ready to help you work through your sprint items. Let's get started!"
        await self._send_message_to_agent(initial_message)
    
    async def _get_user_input(self) -> str:
        """Get user input from the console."""
        try:
            return input("\nYou: ")
        except EOFError:
            return "quit"
    
    async def _process_user_input(self, user_input: str) -> None:
        """Process user input and get agent response."""
        await self._send_message_to_agent(user_input)
    
    async def _send_message_to_agent(self, message: str) -> None:
        """Send a message to the agent and stream the response."""
        try:
            # Create content object
            content = types.Content(
                role='user',
                parts=[types.Part(text=message)]
            )
            
            # Run the agent and stream responses
            events = self.runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=content
            )
            
            print(f"\nSprint Coordinator: ", end="", flush=True)
            
            async for event in events:
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    print(final_response)
                elif hasattr(event, 'content') and event.content:
                    # Stream partial responses
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                print(part.text, end="", flush=True)
                
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            print(f"Error communicating with agent: {e}")


async def main():
    """Main entry point."""
    app = SprintCoordinatorApp()
    
    try:
        await app.initialize()
        await app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Application error: {e}")


if __name__ == "__main__":
    # Run the application
    asyncio.run(main())
