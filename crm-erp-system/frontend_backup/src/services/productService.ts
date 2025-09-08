import { apiClient } from './apiClient';

export interface Product {
  id: number;
  name: string;
  code: string;
  description?: string;
  price: number;
  cost: number;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const productService = {
  async getProducts(): Promise<Product[]> {
    const response = await apiClient.get('/products/');
    return response.data.results || response.data;
  },

  async getProduct(id: number): Promise<Product> {
    const response = await apiClient.get(`/products/${id}/`);
    return response.data;
  },

  async createProduct(product: Partial<Product>): Promise<Product> {
    const response = await apiClient.post('/products/', product);
    return response.data;
  },

  async updateProduct(id: number, product: Partial<Product>): Promise<Product> {
    const response = await apiClient.put(`/products/${id}/`, product);
    return response.data;
  },

  async deleteProduct(id: number): Promise<void> {
    await apiClient.delete(`/products/${id}/`);
  },
};