/**
 * API Service
 * Handles all HTTP requests to the Django backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: async (userData) => {
    const response = await apiClient.post('/auth/register/', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login/', credentials);
    if (response.data.token) {
      localStorage.setItem('authToken', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  
  logout: async () => {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me/');
    return response.data;
  },
};

// Dataset API
export const datasetAPI = {
  uploadCSV: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/datasets/upload_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },
  
  getDatasets: async () => {
    const response = await apiClient.get('/datasets/');
    return response.data;
  },
  
  getDataset: async (id) => {
    const response = await apiClient.get(`/datasets/${id}/`);
    return response.data;
  },
  
  getHistory: async () => {
    const response = await apiClient.get('/datasets/history/');
    return response.data;
  },
  
  getSummary: async (id) => {
    const response = await apiClient.get(`/datasets/${id}/summary/`);
    return response.data;
  },
  
  generatePDF: async (id) => {
    const response = await apiClient.get(`/datasets/${id}/generate_pdf/`, {
      responseType: 'blob',
    });
    return response.data;
  },
  
  deleteDataset: async (id) => {
    const response = await apiClient.delete(`/datasets/${id}/`);
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get('/health/');
  return response.data;
};

export default apiClient;
