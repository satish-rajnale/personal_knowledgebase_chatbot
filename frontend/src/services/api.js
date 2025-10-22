import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
  // Sync Notion pages
  syncNotion: async (pageIds) => {
    const response = await api.post('/notion/sync', { page_ids: pageIds });
    return response.data;
  },

  // Get Notion pages
  getPages: async () => {
    const response = await api.get('/notion/pages');
    return response.data;
  },

  // Get Notion databases
  getDatabases: async () => {
    const response = await api.get('/notion/databases');
    return response.data;
  },

  // Get Notion status
  getStatus: async () => {
    const response = await api.get('/notion/status');
    return response.data;
  },

  // Get Notion embeddings
  getEmbeddings: async () => {
    const response = await api.get('/notion/embeddings');
    return response.data;
  },
};

export const authAPI = {
  // Create anonymous user
  createAnonymousUser: async () => {
    const response = await api.post('/auth/anonymous');
    return response.data;
  },

  // Login with email
  loginWithEmail: async (email) => {
    const response = await api.post('/auth/email', { email });
    return response.data;
  },

  // Get user profile
  getUserProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  // Refresh user profile (same as getUserProfile but more explicit)
  refreshUserProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  // Get usage stats
  getUsageStats: async () => {
    const response = await api.get('/auth/usage');
    return response.data;
  },

  // Authorize Notion
  authorizeNotion: async () => {
    const response = await api.post('/auth/notion/authorize');
    return response.data;
  },

  // Handle Notion OAuth callback
  notionCallback: async (code, state) => {
    const response = await api.post('/auth/notion/callback', { code, state });
    return response;
  },

  // Submit contact form
  submitContactForm: async (formData) => {
    const response = await api.post('/contact', formData);
    return response.data;
  },

  // Logout user
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// API service methods
api.setToken = (token) => {
  localStorage.setItem('token', token);
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

api.clearToken = () => {
  localStorage.removeItem('token');
  delete api.defaults.headers.common['Authorization'];
};

export default api; 