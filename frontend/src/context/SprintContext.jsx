import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { getApiUrl } from '../config';

const SprintContext = createContext();

// Action types
const ACTIONS = {
  SELECT_SPRINT_ITEM: 'SELECT_SPRINT_ITEM',
  TOGGLE_AUTO_MODE: 'TOGGLE_AUTO_MODE',
  SHOW_CONFIRMATION: 'SHOW_CONFIRMATION',
  HIDE_CONFIRMATION: 'HIDE_CONFIRMATION',
  CONFIRM_SWITCH: 'CONFIRM_SWITCH',
  CANCEL_SWITCH: 'CANCEL_SWITCH',
  CLEAR_CHAT: 'CLEAR_CHAT',
  SET_SPRINTS: 'SET_SPRINTS',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR'
};

// Initial state
const initialState = {
  sprints: [],
  selectedSprintItem: null,
  autoMode: false,
  showConfirmation: false,
  pendingSprintItem: null,
  loading: false,
  error: null
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

    case ACTIONS.SET_SPRINTS:
      return {
        ...state,
        sprints: action.payload,
        loading: false,
        error: null
      };

    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
        error: null
      };

    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };

    default:
      return state;
  }
}

// Provider component
export function SprintProvider({ children }) {
  const [state, dispatch] = useReducer(sprintReducer, initialState);

  // Fetch sprints from backend API
  const fetchSprints = async () => {
    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      const response = await fetch(getApiUrl('/api/sprints'));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      dispatch({ type: ACTIONS.SET_SPRINTS, payload: data.sprints });
    } catch (error) {
      console.error('Error fetching sprints:', error);
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
    }
  };

  // Fetch sprints on component mount
  useEffect(() => {
    fetchSprints();
  }, []);

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
    clearChat,
    fetchSprints
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
