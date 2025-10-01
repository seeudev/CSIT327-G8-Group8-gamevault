import axios from 'axios';

/**
 * API Configuration and Service
 * Handles all HTTP requests to the Django backend with JWT authentication.
 */

// Base API URL - should be configured based on environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Create axios instance with default configuration
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add JWT token to requests
 * Automatically adds the access token to the Authorization header
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle token refresh on 401 errors
 * Automatically refreshes the access token when it expires
 */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          // No refresh token available, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Try to refresh the access token
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        
        // Save new access token
        localStorage.setItem('accessToken', access);

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Authentication API endpoints
 */
export const authAPI = {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise} API response
   */
  register: (userData) => api.post('/auth/register/', userData),

  /**
   * Login user
   * @param {Object} credentials - Username/email and password
   * @returns {Promise} API response
   */
  login: (credentials) => api.post('/auth/login/', credentials),

  /**
   * Logout user
   * @param {string} refreshToken - Refresh token to blacklist
   * @returns {Promise} API response
   */
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),

  /**
   * Get current user profile
   * @returns {Promise} API response
   */
  getProfile: () => api.get('/auth/profile/'),

  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   * @returns {Promise} API response
   */
  updateProfile: (profileData) => api.patch('/auth/profile/', profileData),

  /**
   * Change user password
   * @param {Object} passwordData - Old and new password
   * @returns {Promise} API response
   */
  changePassword: (passwordData) => api.post('/auth/change-password/', passwordData),

  /**
   * Verify JWT token
   * @returns {Promise} API response
   */
  verifyToken: () => api.post('/auth/verify-token/'),

  /**
   * Get user permissions
   * @returns {Promise} API response
   */
  getPermissions: () => api.get('/auth/permissions/'),

  /**
   * Get list of roles
   * @returns {Promise} API response
   */
  getRoles: () => api.get('/auth/roles/'),
};

export default api;
