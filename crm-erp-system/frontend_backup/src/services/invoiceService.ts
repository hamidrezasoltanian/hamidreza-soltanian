import { apiClient } from './apiClient';

export interface Invoice {
  id: number;
  invoice_number: string;
  customer: number;
  customer_name?: string;
  total_amount: number;
  status: 'draft' | 'pending' | 'approved' | 'paid' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export const invoiceService = {
  async getInvoices(): Promise<Invoice[]> {
    const response = await apiClient.get('/invoices/');
    return response.data.results || response.data;
  },

  async getInvoice(id: number): Promise<Invoice> {
    const response = await apiClient.get(`/invoices/${id}/`);
    return response.data;
  },

  async createInvoice(invoice: Partial<Invoice>): Promise<Invoice> {
    const response = await apiClient.post('/invoices/', invoice);
    return response.data;
  },

  async updateInvoice(id: number, invoice: Partial<Invoice>): Promise<Invoice> {
    const response = await apiClient.put(`/invoices/${id}/`, invoice);
    return response.data;
  },

  async deleteInvoice(id: number): Promise<void> {
    await apiClient.delete(`/invoices/${id}/`);
  },
};