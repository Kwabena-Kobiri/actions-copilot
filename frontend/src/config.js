// Configuration for the Sprint Coordinator frontend
export const config = {
  // Backend API base URL
  API_BASE_URL: 'http://localhost:8001',
  
  // API endpoints
  ENDPOINTS: {
    SPRINTS: '/api/sprints',
    SPRINT_ITEM: '/api/sprints',
    BMC: '/api/canvas/bmc',
    VPC: '/api/canvas/vpc',
    SEGMENTS: '/api/canvas/segments',
    CHAT_INIT: '/api/chat/init',
    CHAT_STREAM: '/api/chat/stream',
    WS_CHAT: '/ws/chat'
  },
  
  // SSE configuration
  SSE: {
    RECONNECT_INTERVAL: 3000, // 3 seconds
    MAX_RECONNECT_ATTEMPTS: 5
  }
};

// Helper function to build full API URLs
export const getApiUrl = (endpoint) => {
  return `${config.API_BASE_URL}${endpoint}`;
};
