import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login/', { username, password });
    return response.data;
  },

  register: async (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh_token: refreshToken });
    }
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile/');
    return response.data.user;
  },

  updateProfile: async (userData: {
    first_name?: string;
    last_name?: string;
    email?: string;
  }) => {
    const response = await api.put('/auth/profile/update/', userData);
    return response.data;
  },

  changePassword: async (passwordData: {
    old_password: string;
    new_password: string;
  }) => {
    const response = await api.post('/auth/change-password/', passwordData);
    return response.data;
  },
};