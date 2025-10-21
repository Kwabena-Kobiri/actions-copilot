import React from 'react';
import { SprintProvider } from './context/SprintContext';
import SprintList from './components/SprintList';
import ChatInterface from './components/ChatInterface';
import ConfirmationModal from './components/ConfirmationModal';

function App() {
  return (
    <SprintProvider>
      <div 
        className="h-screen flex bg-gray-100"
        style={{
          height: '100vh',
          display: 'flex',
          backgroundColor: '#f3f4f6'
        }}
      >
        {/* Left Pane - Sprint List */}
        <div 
          className="w-1/3 min-w-80"
          style={{
            width: '33.333333%',
            minWidth: '20rem',
            backgroundColor: 'white',
            borderRight: '1px solid #e5e7eb'
          }}
        >
          <SprintList />
        </div>

        {/* Right Pane - Chat Interface */}
        <div 
          className="flex-1"
          style={{
            flex: '1',
            backgroundColor: '#f9fafb'
          }}
        >
          <ChatInterface />
        </div>

        {/* Confirmation Modal */}
        <ConfirmationModal />
      </div>
    </SprintProvider>
  );
}

export default App;
