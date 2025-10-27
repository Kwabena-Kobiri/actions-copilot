"""
Test script for the WebSocket chat endpoint.
Run this script to test the streaming chat functionality.
"""

import asyncio
import json
import websockets
from config import DEFAULT_USER_ID

# WebSocket server URL
WS_URL = "ws://localhost:8000/ws/chat/"

# Test session ID
TEST_SESSION_ID = "test_session_123"

# Test user ID
TEST_USER_ID = DEFAULT_USER_ID


async def test_websocket_chat():
    """Test the WebSocket chat endpoint."""
    print("=" * 60)
    print("Testing WebSocket Chat Endpoint")
    print("=" * 60)
    
    try:
        # Connect to WebSocket
        print(f"\nConnecting to {WS_URL}...")
        async with websockets.connect(WS_URL) as websocket:
            print("Connected successfully!")
            
            # Test messages
            test_messages = [
                "Hello! Can you help me with sprint planning?",
                "What sprint items do I have?",
                "Tell me about my current progress"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n{'='*60}")
                print(f"Test Message {i}/{len(test_messages)}")
                print(f"{'='*60}")
                print(f"User: {message}")
                
                # Prepare request
                request = {
                    "user_id": TEST_USER_ID,
                    "session_id": TEST_SESSION_ID,
                    "message": message
                }
                
                # Send message
                print(f"\nSending: {json.dumps(request, indent=2)}")
                await websocket.send(json.dumps(request))
                
                # Receive and print response
                print("\nAgent Response (streaming):")
                print("-" * 60)
                
                full_response = ""
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                        
                        if response == "--streaming ended--":
                            print("\n" + "-" * 60)
                            print("Streaming completed.")
                            break
                        else:
                            print(response, end="", flush=True)
                            full_response += response
                    
                    except asyncio.TimeoutError:
                        print("\nTimeout waiting for response")
                        break
                
                print(f"\n\nFull Response Length: {len(full_response)} characters")
                print("=" * 60)
                
                # Wait a bit before next message
                await asyncio.sleep(2)
            
            print("\n" + "=" * 60)
            print("All tests completed successfully!")
            print("=" * 60)
    
    except websockets.exceptions.ConnectionRefused:
        print(f"\n❌ Connection refused. Is the server running on {WS_URL}?")
        print("   Start the server with: uvicorn api:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_invalid_message():
    """Test with invalid message format."""
    print("\n" + "=" * 60)
    print("Testing Invalid Message Format")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send invalid message (missing required fields)
            invalid_request = {
                "message": "Hello"
                # Missing user_id and session_id
            }
            
            print(f"Sending invalid request: {json.dumps(invalid_request)}")
            await websocket.send(json.dumps(invalid_request))
            
            response = await websocket.recv()
            print(f"\nResponse: {response}")
            
    except Exception as e:
        print(f"Error: {e}")


async def interactive_chat():
    """Interactive chat mode."""
    print("=" * 60)
    print("Interactive WebSocket Chat")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected! Start typing your messages...\n")
            
            while True:
                # Get user input
                message = input("\nYou: ").strip()
                
                if message.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye!")
                    break
                
                if not message:
                    continue
                
                # Prepare request
                request = {
                    "user_id": TEST_USER_ID,
                    "session_id": TEST_SESSION_ID,
                    "message": message
                }
                
                # Send message
                await websocket.send(json.dumps(request))
                
                # Receive and print response
                print("\nAgent: ", end="", flush=True)
                
                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                        
                        if response == "--streaming ended--":
                            print()
                            break
                        else:
                            print(response, end="", flush=True)
                    
                    except asyncio.TimeoutError:
                        print("\nTimeout waiting for response")
                        break
        
    except websockets.exceptions.ConnectionRefused:
        print(f"\n❌ Connection refused. Is the server running on {WS_URL}?")
        print("   Start the server with: uvicorn api:app --reload")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "test":
            await test_websocket_chat()
        elif mode == "invalid":
            await test_invalid_message()
        elif mode == "interactive" or mode == "i":
            await interactive_chat()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python api_tests.py [test|invalid|interactive]")
    else:
        # Default: run all tests
        await test_websocket_chat()
        print("\n" + "=" * 60)
        print("Run with 'interactive' argument for interactive mode:")
        print("  python api_tests.py interactive")
        print("=" * 60)


if __name__ == "__main__":
    print("\nWebSocket Chat API Test Script")
    print("-" * 60)
    print("Make sure the server is running before testing!")
    print("Start server with: uvicorn api:app --reload")
    print("-" * 60)
    
    asyncio.run(main())
