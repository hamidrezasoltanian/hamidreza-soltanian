import { apiClient } from './apiClient';

export interface Warehouse {
  id: number;
  name: string;
  code: string;
  address?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const inventoryService = {
  async getWarehouses(): Promise<Warehouse[]> {
    const response = await apiClient.get('/inventory/warehouses/');
    return response.data.results || response.data;
  },

  async getWarehouse(id: number): Promise<Warehouse> {
    const response = await apiClient.get(`/inventory/warehouses/${id}/`);
    return response.data;
  },

  async createWarehouse(warehouse: Partial<Warehouse>): Promise<Warehouse> {
    const response = await apiClient.post('/inventory/warehouses/', warehouse);
    return response.data;
  },

  async updateWarehouse(id: number, warehouse: Partial<Warehouse>): Promise<Warehouse> {
    const response = await apiClient.put(`/inventory/warehouses/${id}/`, warehouse);
    return response.data;
  },

  async deleteWarehouse(id: number): Promise<void> {
    await apiClient.delete(`/inventory/warehouses/${id}/`);
  },
};