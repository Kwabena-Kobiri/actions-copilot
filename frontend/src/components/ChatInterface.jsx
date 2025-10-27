import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SprintItemCard from './SprintItemCard';
import { useSprint } from '../context/SprintContext';
import { mockChatResponses } from '../data/mockSprints';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const { clearChat, selectedSprintItem, fetchSprints } = useSprint();

  // Ref to keep track of the item_id for which the current WebSocket is active
  const activeSprintItemIdRef = useRef(null);

  // Clear messages when clearChat is triggered
  useEffect(() => {
    if (clearChat) {
      setMessages([]);
      setUploadedFiles([]);
    }
  }, [clearChat]);

  // Fetch sprints on initial load
  useEffect(() => {
    fetchSprints();
  }, [fetchSprints]);

  // Initialize WebSocket connection and send initial message when sprint item is selected
  useEffect(() => {
    // If no sprint item is selected, close any active WebSocket and reset state
    if (!selectedSprintItem) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      setWs(null);
      setIsConnected(false);
      activeSprintItemIdRef.current = null;
      return;
    }

    const currentItemId = selectedSprintItem.item_id;

    // If the selected item ID is the same as the one for which we have an active WS,
    // and the WS is still open, do nothing. This prevents re-initialization on re-renders
    // caused by `fetchSprints` updating context state.
    if (currentItemId === activeSprintItemIdRef.current && ws && ws.readyState === WebSocket.OPEN) {
      console.log(`WebSocket already active for sprint item ID: ${currentItemId}. Skipping re-initialization.`);
      return;
    }

    // If we reach here, either the item ID has changed, or the WS is not active/closed.
    console.log(`Re-initializing WebSocket for sprint item ID: ${currentItemId}`);

    // Close any existing WebSocket connection before opening a new one
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    setWs(null); // Clear previous WebSocket instance from state
    setIsConnected(false);

    // Reset messages for the new sprint item (or if connection was lost for the same item)
    setMessages([]);

    // Create new session ID for this sprint item
    const newSessionId = `session_${currentItemId}_${Date.now()}`;
    setSessionId(newSessionId);

    // Create WebSocket connection
    const newWebsocket = new WebSocket('ws://localhost:8000/ws/chat/');
    setWs(newWebsocket); // Store the new WebSocket instance in state

    newWebsocket.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
      // Send initial message
      const initialMessage = {
        user_id: 'user1234', // You can get this from user context
        session_id: newSessionId,
        message: `Help me to work on sprint item "${currentItemId}"`
      };
      newWebsocket.send(JSON.stringify(initialMessage));
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: initialMessage.message,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    newWebsocket.onmessage = async (event) => {
      const text = event.data;
      
      if (text === '--streaming ended--') {
        // Streaming completed - fetch updated sprints
        await fetchSprints(); // This should now only update the sprint data, not clear chat
        return;
      }

      // Add or update bot message with streaming text
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage && lastMessage.sender === 'bot' && lastMessage.isStreaming) {
          // Update existing streaming message
          return [
            ...prev.slice(0, -1),
            {
              ...lastMessage,
              text: lastMessage.text + text,
              timestamp: new Date().toLocaleTimeString(),
              isStreaming: true // Keep streaming flag true until final message
            }
          ];
        } else {
          // Create new bot message
          return [
            ...prev,
            {
              id: Date.now(),
              text: text,
              sender: 'bot',
              timestamp: new Date().toLocaleTimeString(),
              isStreaming: true // Mark as streaming
            }
          ];
        }
      });
    };

    newWebsocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setWs(null); // Clear ws state on close
      activeSprintItemIdRef.current = null; // Reset ref on close
    };

    newWebsocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setWs(null); // Clear ws state on error
      activeSprintItemIdRef.current = null; // Reset ref on error
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Error connecting to sprint coordinator. Please try again.",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    // Update the ref with the current item_id that this WebSocket is for
    activeSprintItemIdRef.current = currentItemId;

    // Cleanup function for this specific WebSocket
    return () => {
      console.log('Cleaning up WebSocket for item:', currentItemId);
      if (newWebsocket.readyState === WebSocket.OPEN) {
        newWebsocket.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSprintItem?.item_id, fetchSprints]);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (indexToRemove) => {
    setUploadedFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputValue.trim() && uploadedFiles.length === 0) return;
    if (!ws || !isConnected) return;

    // Add user message with files if any
    const userMessage = {
      id: Date.now(),
      text: inputValue || (uploadedFiles.length > 0 ? `Sent ${uploadedFiles.length} file(s)` : ''),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined
    };

    setMessages(prev => [...prev, userMessage]);

    // Send message via WebSocket
    const message = {
      user_id: 'user1234', // You can get this from user context
      session_id: sessionId,
      message: inputValue.trim()
    };

    ws.send(JSON.stringify(message));

    setInputValue('');
    setUploadedFiles([]);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Sprint Item Card */}
      <div className="p-4 bg-white border-b border-gray-200">
        <SprintItemCard />
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!selectedSprintItem ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Select a sprint item from the left to start a conversation!</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Connecting to your sprint coordinator...</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-900 border border-gray-200'
                }`}
              >
                {message.sender === 'bot' ? (
                  <div className="text-sm prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.text}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm">{message.text}</p>
                )}
                {message.files && message.files.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.files.map((file, index) => (
                      <div key={index} className="text-xs opacity-90 bg-blue-500 bg-opacity-20 px-2 py-1 rounded flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                        {file.name} ({(file.size / 1024).toFixed(1)} KB)
                      </div>
                    ))}
                  </div>
                )}
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200">
        {/* File Chips */}
        {uploadedFiles.length > 0 && (
          <div className="p-3 border-b border-gray-200 bg-gray-50">
            <div className="flex flex-wrap gap-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center bg-gray-700 text-white px-3 py-2 rounded-lg text-sm"
                >
                  <svg className="w-4 h-4 mr-2 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                  <span className="mr-2">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-gray-300 hover:text-white focus:outline-none"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="p-4">
          <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.csv,.xlsx,.pptx"
          />
          
          {/* Attachment Button */}
          <button
            type="button"
            onClick={handleFileButtonClick}
            disabled={!selectedSprintItem || !isConnected}
            className={`p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full ${
              !selectedSprintItem || !isConnected
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title="Upload files"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </button>

          {/* Input Field */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={!selectedSprintItem ? "Select a sprint item to start chatting" : "Type your message"}
            disabled={!selectedSprintItem || !isConnected}
            className={`flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:border-transparent ${
              !selectedSprintItem || !isConnected
                ? 'border-gray-200 bg-gray-100 cursor-not-allowed'
                : 'border-gray-300 focus:ring-blue-500'
            }`}
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={!selectedSprintItem || !isConnected}
            className={`p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full ${
              !selectedSprintItem || !isConnected
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-blue-600 hover:text-blue-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
          </form>
        </div>
      </div>
    </div>
  );
}
