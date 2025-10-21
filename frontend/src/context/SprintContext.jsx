import React, { createContext, useContext, useReducer } from 'react';
import { mockSprints } from '../data/mockSprints';

const SprintContext = createContext();

// Action types
const ACTIONS = {
  SELECT_SPRINT_ITEM: 'SELECT_SPRINT_ITEM',
  TOGGLE_AUTO_MODE: 'TOGGLE_AUTO_MODE',
  SHOW_CONFIRMATION: 'SHOW_CONFIRMATION',
  HIDE_CONFIRMATION: 'HIDE_CONFIRMATION',
  CONFIRM_SWITCH: 'CONFIRM_SWITCH',
  CANCEL_SWITCH: 'CANCEL_SWITCH',
  CLEAR_CHAT: 'CLEAR_CHAT'
};

// Initial state
const initialState = {
  sprints: mockSprints.sprints,
  selectedSprintItem: null,
  autoMode: false,
  showConfirmation: false,
  pendingSprintItem: null
};

// Reducer function
function sprintReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SELECT_SPRINT_ITEM:
      // If there's already a selected item, show confirmation
      if (state.selectedSprintItem && state.selectedSprintItem.item_id !== action.payload.item_id) {
        return {
          ...state,
          showConfirmation: true,
          pendingSprintItem: action.payload
        };
      }
      // Otherwise, select the item directly
      return {
        ...state,
        selectedSprintItem: action.payload,
        showConfirmation: false,
        pendingSprintItem: null
      };

    case ACTIONS.TOGGLE_AUTO_MODE:
      return {
        ...state,
        autoMode: !state.autoMode
      };

    case ACTIONS.SHOW_CONFIRMATION:
      return {
        ...state,
        showConfirmation: true,
        pendingSprintItem: action.payload
      };

    case ACTIONS.HIDE_CONFIRMATION:
      return {
        ...state,
        showConfirmation: false,
        pendingSprintItem: null
      };

    case ACTIONS.CONFIRM_SWITCH:
      return {
        ...state,
        selectedSprintItem: state.pendingSprintItem,
        showConfirmation: false,
        pendingSprintItem: null
      };

    case ACTIONS.CANCEL_SWITCH:
      return {
        ...state,
        showConfirmation: false,
        pendingSprintItem: null
      };

    case ACTIONS.CLEAR_CHAT:
      return {
        ...state,
        // This will be handled by the ChatInterface component
      };

    default:
      return state;
  }
}

// Provider component
export function SprintProvider({ children }) {
  const [state, dispatch] = useReducer(sprintReducer, initialState);

  const selectSprintItem = (sprintItem, sprint) => {
    const itemWithSprint = {
      ...sprintItem,
      sprint_title: sprint.title,
      sprint_id: sprint.sprint_id
    };
    dispatch({ type: ACTIONS.SELECT_SPRINT_ITEM, payload: itemWithSprint });
  };

  const toggleAutoMode = () => {
    dispatch({ type: ACTIONS.TOGGLE_AUTO_MODE });
  };

  const confirmSwitch = () => {
    dispatch({ type: ACTIONS.CONFIRM_SWITCH });
  };

  const cancelSwitch = () => {
    dispatch({ type: ACTIONS.CANCEL_SWITCH });
  };

  const clearChat = () => {
    dispatch({ type: ACTIONS.CLEAR_CHAT });
  };

  const value = {
    ...state,
    selectSprintItem,
    toggleAutoMode,
    confirmSwitch,
    cancelSwitch,
    clearChat
  };

  return (
    <SprintContext.Provider value={value}>
      {children}
    </SprintContext.Provider>
  );
}

// Custom hook to use the context
export function useSprint() {
  const context = useContext(SprintContext);
  if (!context) {
    throw new Error('useSprint must be used within a SprintProvider');
  }
  return context;
}
