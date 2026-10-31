import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const STORAGE_BASE_URL = import.meta.env.VITE_STORAGE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor for Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-clear if already on login page
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password, full_name, role) => api.post('/auth/register', { email, password, full_name, role }),
  getMe: () => api.get('/auth/me'),
};

export const mediaAPI = {
  upload: (formData, onProgress) =>
    api.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    }),
  getMedia: (id) => api.get(`/media/${id}`),
  deleteMedia: (id) => api.delete(`/media/${id}`),
};

export const analysisAPI = {
  create: (media_id, model_name) => api.post('/analysis/create', { media_id, model_name }),
  analyzeImageDirect: (formData, onProgress) =>
    api.post('/analysis/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => onProgress && event.total && onProgress(Math.round((event.loaded * 100) / event.total)),
    }),
  analyzeVideoDirect: (formData, onProgress) =>
    api.post('/analysis/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => onProgress && event.total && onProgress(Math.round((event.loaded * 100) / event.total)),
    }),
  analyzeAudioDirect: (formData, onProgress) =>
    api.post('/analysis/audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => onProgress && event.total && onProgress(Math.round((event.loaded * 100) / event.total)),
    }),
  getJob: (id) => api.get(`/analysis/${id}`),
  getStatus: (id) => api.get(`/analysis/${id}/status`),
  getHistory: (params) => api.get('/analysis/history', { params }),
  retry: (id) => api.post(`/analysis/${id}/retry`),
};

export const reviewAPI = {
  getPending: () => api.get('/reviews/pending'),
  updateStatus: (analysisId, status, notes) =>
    api.patch(`/reviews/${analysisId}/status`, { status, notes }),
  updateNotes: (analysisId, notes) =>
    api.post(`/reviews/${analysisId}/notes`, { notes }),
};

export const reportAPI = {
  downloadPdfUrl: (analysisId) => `${API_BASE_URL}/reports/${analysisId}/pdf`,
  downloadCsvUrl: (analysisId) => `${API_BASE_URL}/reports/${analysisId}/csv`,
  downloadPdf: (analysisId) =>
    api.get(`/reports/${analysisId}/pdf`, { responseType: 'blob' }),
  downloadCsv: (analysisId) =>
    api.get(`/reports/${analysisId}/csv`, { responseType: 'blob' }),
};

export const adminAPI = {
  getMetrics: () => api.get('/admin/metrics'),
  getUsers: () => api.get('/admin/users'),
  updateRole: (userId, role) => api.patch(`/admin/users/${userId}/role`, { role }),
  getModels: () => api.get('/admin/models'),
  getAuditLogs: (limit = 100) => api.get('/admin/audit-logs', { params: { limit } }),
};

export default api;
