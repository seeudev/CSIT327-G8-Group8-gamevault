import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
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

// Refresh token on 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('accessToken', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    axios.post(`${API_URL}/auth/token/`, { username, password }),
  
  register: (userData) =>
    axios.post(`${API_URL}/users/`, userData),
  
  getCurrentUser: () =>
    api.get('/users/me/'),
  
  updateUser: (userData) =>
    api.put('/users/me/', userData),
};

// Games API
export const gamesAPI = {
  getGames: (params) =>
    api.get('/games/', { params }),
  
  getGame: (id) =>
    api.get(`/games/${id}/`),
};

// Orders API
export const ordersAPI = {
  getOrders: () =>
    api.get('/orders/'),
  
  createOrder: (gameIds) =>
    api.post('/orders/', { game_ids: gameIds }),
  
  getOrder: (id) =>
    api.get(`/orders/${id}/`),
  
  getOrderKeys: (id) =>
    api.get(`/orders/${id}/keys/`),
};

export default api;
