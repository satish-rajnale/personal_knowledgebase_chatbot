import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [usage, setUsage] = useState(null);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      if (token) {
        try {
          // Set token in API service
          api.setToken(token);
          
          // Get user profile
          const profile = await authAPI.getUserProfile();
          setUser(profile);
          
          // Get usage stats
          const usageStats = await authAPI.getUsageStats();
          setUsage(usageStats);
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          // Clear invalid token
          logout();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, [token]);

  const loginAnonymous = async () => {
    try {
      const response = await authAPI.createAnonymousUser();
      const { token: newToken, user_id, is_anonymous } = response;
      
      setToken(newToken);
      setUser({ user_id, is_anonymous, email: null });
      localStorage.setItem('token', newToken);
      api.setToken(newToken);
      
      // Get usage stats
      const usageStats = await authAPI.getUsageStats();
      setUsage(usageStats);
      
      return { success: true };
    } catch (error) {
      console.error('Anonymous login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const loginWithEmail = async (email) => {
    try {
      const response = await authAPI.loginWithEmail(email);
      const { token: newToken, user_id, is_anonymous, email: userEmail } = response;
      
      setToken(newToken);
      setUser({ user_id, is_anonymous, email: userEmail });
      localStorage.setItem('token', newToken);
      api.setToken(newToken);
      
      // Get usage stats
      const usageStats = await authAPI.getUsageStats();
      setUsage(usageStats);
      
      return { success: true };
    } catch (error) {
      console.error('Email login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint (optional, for logging purposes)
      await authAPI.logout();
    } catch (error) {
      console.warn('Backend logout failed, continuing with client-side logout:', error);
    }
    
    // Clear client-side state
    setUser(null);
    setToken(null);
    setUsage(null);
    localStorage.removeItem('token');
    api.clearToken();
  };

  const refreshUsage = async () => {
    if (token) {
      try {
        // Dispatch refresh start event
        window.dispatchEvent(new CustomEvent('usage-refresh-start'));
        
        const usageStats = await authAPI.getUsageStats();
        setUsage(usageStats);
        
        // Dispatch refresh end event
        window.dispatchEvent(new CustomEvent('usage-refresh-end'));
      } catch (error) {
        console.error('Failed to refresh usage:', error);
        // Dispatch refresh end event even on error
        window.dispatchEvent(new CustomEvent('usage-refresh-end'));
      }
    }
  };

  const refreshUserProfile = async () => {
    if (token) {
      try {
        const profile = await authAPI.getUserProfile();
        setUser(profile);
        console.log('✅ User profile refreshed:', profile);
        return profile;
      } catch (error) {
        console.error('Failed to refresh user profile:', error);
        throw error;
      }
    }
  };

  const connectNotion = async () => {
    try {
      const response = await authAPI.authorizeNotion();
      return { success: true, authUrl: response.auth_url };
    } catch (error) {
      console.error('Notion authorization failed:', error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    token,
    loading,
    usage,
    loginAnonymous,
    loginWithEmail,
    logout,
    refreshUsage,
    refreshUserProfile,
    connectNotion,
    isAuthenticated: !!token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 