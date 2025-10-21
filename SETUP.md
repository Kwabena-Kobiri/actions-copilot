# Sprint Coordinator - FastAPI Integration Setup

This guide will help you set up and run the Sprint Coordinator application with the new FastAPI backend integration.

## Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- Google API Key for Gemini

## Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `backend` directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   APP_NAME=sprint_coordinator
   DEFAULT_USER_ID=user1234
   ```

5. **Start the FastAPI server:**
   ```bash
   python run_server.py
   ```
   
   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/`

## Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

## Usage

1. **Start both servers** (backend and frontend)
2. **Open the frontend** in your browser at `http://localhost:5173`
3. **Select a sprint item** from the list
4. **Start chatting** with the AI agent - it will begin with the Design Phase
5. **Follow the workflow** through Design → Execute → Report → Learn phases

## Data Synchronization

Both the frontend and backend now use the shared `global data/` folder:
- `sprints.json` - Sprint items and analysis
- `bmc.json` - Business Model Canvas
- `vpc.json` - Value Proposition Canvas  
- `segments.json` - Customer Segments

When the backend updates any of these files, the frontend will immediately see the changes.

## API Endpoints

- `GET /api/sprints` - Get all sprint items
- `GET /api/sprints/{item_id}` - Get specific sprint item
- `GET /api/canvas/bmc` - Get Business Model Canvas
- `GET /api/canvas/vpc` - Get Value Proposition Canvas
- `GET /api/canvas/segments` - Get Customer Segments
- `POST /api/chat/init` - Initialize chat session
- `POST /api/chat/stream` - Stream AI responses (SSE)

## Troubleshooting

1. **CORS Issues:** Make sure the frontend URL is included in the CORS origins in `fastapi_app.py`
2. **API Key Issues:** Verify your Google API key is correctly set in the `.env` file
3. **Data Loading Issues:** Check that the `global data/` folder exists and contains the JSON files
4. **Connection Issues:** Ensure both servers are running and accessible on their respective ports

## Development Notes

- The backend uses Server-Sent Events (SSE) for real-time streaming of AI responses
- Session management is handled in-memory (suitable for development)
- The AI agent starts directly from the Design Phase when a sprint item is selected
- All data operations are synchronized through the shared `global data/` folder
