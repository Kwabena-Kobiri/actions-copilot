import React, { useState, useEffect, useRef } from 'react';
import SprintItemCard from './SprintItemCard';
import { useSprint } from '../context/SprintContext';
import { getApiUrl } from '../config';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const websocketRef = useRef(null);
  const { clearChat, selectedSprintItem } = useSprint();

  // Clear messages when clearChat is triggered
  useEffect(() => {
    if (clearChat) {
      setMessages([]);
      setUploadedFiles([]);
      disconnectWebSocket();
    }
  }, [clearChat]);

  // Initialize chat when sprint item is selected
  useEffect(() => {
    if (selectedSprintItem && !isConnected) {
      initializeChat();
    }
  }, [selectedSprintItem, isConnected]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const initializeChat = async () => {
    if (!selectedSprintItem) return;

    try {
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const userId = `user_${Date.now()}`;
      
      // Connect to WebSocket
      connectWebSocket(userId, sessionId);
      
      // Add initial bot message
      setMessages([{
        id: Date.now(),
        text: "Hello! I'm ready to help you work through your sprint item. Let's start with the Design Phase!",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      setIsConnected(true);
    } catch (error) {
      console.error('Error initializing chat:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: "Sorry, I couldn't connect to the chat service. Please try again.",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  };

  const connectWebSocket = (userId, sessionId) => {
    if (websocketRef.current) {
      websocketRef.current.close();
    }

    const wsUrl = getApiUrl('/ws/chat').replace('http://', 'ws://').replace('https://', 'wss://');
    const websocket = new WebSocket(wsUrl);
    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    websocket.onmessage = (event) => {
      const message = event.data;
      
      if (message === '--streaming ended--') {
        setIsLoading(false);
        return;
      }
      
      // Update the last bot message with streaming content
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'bot') {
          lastMessage.text = (lastMessage.text || '') + message;
        } else {
          newMessages.push({
            id: Date.now(),
            text: message,
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString()
          });
        }
        return newMessages;
      });
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsLoading(false);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    // Store user and session info for sending messages
    websocket.userId = userId;
    websocket.sessionId = sessionId;
  };

  const disconnectWebSocket = () => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setIsConnected(false);
  };

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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() && uploadedFiles.length === 0) return;
    if (!selectedSprintItem) return;
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) return;

    const messageText = inputValue || (uploadedFiles.length > 0 ? `Sent ${uploadedFiles.length} file(s)` : '');

    // Add user message with files if any
    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
      files: uploadedFiles.length > 0 ? [...uploadedFiles] : undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message via WebSocket
      const message = {
        user_id: websocketRef.current.userId,
        session_id: websocketRef.current.sessionId,
        message: messageText,
        sprint_item_id: selectedSprintItem.item_id
      };

      websocketRef.current.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "Sorry, I couldn't send your message. Please try again.",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      }]);
      setIsLoading(false);
    }

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
            <p>Please select a sprint item to start chatting!</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Start a conversation about your sprint item!</p>
            {isLoading && <p className="text-blue-500">Connecting...</p>}
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
                <p className="text-sm">{message.text}</p>
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
            className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full"
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
            placeholder="Type your message"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={!selectedSprintItem || isLoading}
            className={`p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full ${
              !selectedSprintItem || isLoading
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-blue-600 hover:text-blue-700'
            }`}
          >
            {isLoading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
          </form>
        </div>
      </div>
    </div>
  );
}
