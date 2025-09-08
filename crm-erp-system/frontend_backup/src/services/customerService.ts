import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: `${API_BASE_URL}/customers`,
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

export const customerService = {
  // Customer Categories
  getCategories: async () => {
    const response = await api.get('/customer-categories/');
    return response.data;
  },

  createCategory: async (data: any) => {
    const response = await api.post('/customer-categories/', data);
    return response.data;
  },

  updateCategory: async (id: number, data: any) => {
    const response = await api.put(`/customer-categories/${id}/`, data);
    return response.data;
  },

  deleteCategory: async (id: number) => {
    const response = await api.delete(`/customer-categories/${id}/`);
    return response.data;
  },

  // Customers
  getCustomers: async (params?: any) => {
    const response = await api.get('/customers/', { params });
    return response.data;
  },

  getCustomer: async (id: number) => {
    const response = await api.get(`/customers/${id}/`);
    return response.data;
  },

  createCustomer: async (data: any) => {
    const response = await api.post('/customers/', data);
    return response.data;
  },

  updateCustomer: async (id: number, data: any) => {
    const response = await api.put(`/customers/${id}/`, data);
    return response.data;
  },

  deleteCustomer: async (id: number) => {
    const response = await api.delete(`/customers/${id}/`);
    return response.data;
  },

  getCustomerStats: async () => {
    const response = await api.get('/customers/stats/');
    return response.data;
  },
};