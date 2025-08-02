import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send a message and get response
  sendMessage: async (message, sessionId) => {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  // Get chat history
  getHistory: async (sessionId = null, limit = 50) => {
    const params = { limit };
    if (sessionId) params.session_id = sessionId;
    
    const response = await api.get('/chat/history', { params });
    return response.data;
  },

  // Clear chat history
  clearHistory: async (sessionId = null) => {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await api.delete('/chat/history', { params });
    return response.data;
  },

  // Get all sessions
  getSessions: async () => {
    const response = await api.get('/chat/sessions');
    return response.data;
  },
};

export const uploadAPI = {
  // Upload a single file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Upload multiple files
  uploadMultipleFiles: async (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await api.post('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const notionAPI = {
  // Sync Notion database
  syncNotion: async () => {
    const response = await api.post('/notion/sync');
    return response.data;
  },

  // Get Notion status
  getStatus: async () => {
    const response = await api.get('/notion/status');
    return response.data;
  },
};

export default api; 