import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ChatContext = createContext();

const initialState = {
  messages: [],
  sessionId: uuidv4(),
  isLoading: false,
  error: null,
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        isLoading: false,
        error: null,
      };
    
    case 'SET_MESSAGES':
      return {
        ...state,
        messages: action.payload,
        isLoading: false,
        error: null,
      };
    
    case 'NEW_SESSION':
      return {
        ...state,
        messages: [],
        sessionId: uuidv4(),
        error: null,
      };
    
    case 'SET_SESSION':
      return {
        ...state,
        sessionId: action.payload,
        error: null,
      };
    
    default:
      return state;
  }
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Load session ID from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chatSessionId');
    if (savedSessionId) {
      dispatch({ type: 'SET_SESSION', payload: savedSessionId });
    }
  }, []);

  // Save session ID to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('chatSessionId', state.sessionId);
  }, [state.sessionId]);

  const value = {
    ...state,
    dispatch,
    addMessage: (message) => dispatch({ type: 'ADD_MESSAGE', payload: message }),
    setLoading: (loading) => dispatch({ type: 'SET_LOADING', payload: loading }),
    setError: (error) => dispatch({ type: 'SET_ERROR', payload: error }),
    clearError: () => dispatch({ type: 'CLEAR_ERROR' }),
    newSession: () => dispatch({ type: 'NEW_SESSION' }),
    setSession: (sessionId) => dispatch({ type: 'SET_SESSION', payload: sessionId }),
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
} 