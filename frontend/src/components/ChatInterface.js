import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import { chatAPI } from '../services/api';
import { Send, Plus, Trash2, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import MessageSources from './MessageSources';

function ChatInterface() {
  const { messages, sessionId, isLoading, error, addMessage, setLoading, setError, clearError, newSession } = useChat();
  const { refreshUsage } = useAuth();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInputMessage('');
    setLoading(true);
    clearError();

    try {
      const response = await chatAPI.sendMessage(inputMessage, sessionId);
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        sources: response.sources,
      };

      addMessage(assistantMessage);
      
      // Refresh usage stats after successful query
      try {
        await refreshUsage();
      } catch (usageError) {
        console.warn('Failed to refresh usage stats:', usageError);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message');
    }
  };

  const handleNewSession = () => {
    newSession();
    inputRef.current?.focus();
  };

  const handleClearHistory = async () => {
    try {
      await chatAPI.clearHistory(sessionId);
      newSession();
      
      // Refresh usage stats after clearing history
      try {
        await refreshUsage();
      } catch (usageError) {
        console.warn('Failed to refresh usage stats after clearing history:', usageError);
      }
    } catch (err) {
      setError('Failed to clear chat history');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* Chat Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Chat</h2>
        <div className="flex space-x-2">
          <button
            onClick={handleNewSession}
            className="btn-secondary flex items-center space-x-2"
            title="New Chat"
          >
            <Plus size={16} />
            <span>New Chat</span>
          </button>
          <button
            onClick={handleClearHistory}
            className="btn-secondary flex items-center space-x-2"
            title="Clear History"
          >
            <Trash2 size={16} />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="h-full flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <RefreshCw size={24} />
                  </div>
                  <p className="text-lg font-medium mb-2">Start a conversation</p>
                  <p className="text-sm">Ask questions about your uploaded documents</p>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                    {message.sources && message.sources.length > 0 && (
                      <MessageSources sources={message.sources} />
                    )}
                    <div className="text-xs opacity-70 mt-2">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="message-assistant">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mx-4 mb-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="border-t p-4">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                className="input-field flex-1"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={16} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface; 