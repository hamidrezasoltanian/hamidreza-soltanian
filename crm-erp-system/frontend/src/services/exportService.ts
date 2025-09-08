import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface ExportOptions {
  format: 'excel' | 'csv' | 'pdf' | 'json';
  fields: string[];
  filters?: Record<string, any>;
  dateRange?: {
    start: string;
    end: string;
  };
  groupBy?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface ImportOptions {
  format: 'excel' | 'csv' | 'json';
  mapping: Record<string, string>;
  skipErrors?: boolean;
  updateExisting?: boolean;
  validateData?: boolean;
}

export interface ExportJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  downloadUrl?: string;
  errorMessage?: string;
  createdAt: string;
  completedAt?: string;
}

export interface ImportJob {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  totalRecords: number;
  processedRecords: number;
  errorRecords: number;
  errorMessage?: string;
  createdAt: string;
  completedAt?: string;
}

class ExportService {
  private baseURL = `${API_BASE_URL}/export`;

  // Export functions
  async exportCustomers(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/customers/`, options);
    return response.data;
  }

  async exportProducts(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/products/`, options);
    return response.data;
  }

  async exportInvoices(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/invoices/`, options);
    return response.data;
  }

  async exportInventory(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/inventory/`, options);
    return response.data;
  }

  async exportPersonnel(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/personnel/`, options);
    return response.data;
  }

  async exportAccounting(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/accounting/`, options);
    return response.data;
  }

  async exportTax(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/tax/`, options);
    return response.data;
  }

  async exportReports(options: ExportOptions): Promise<ExportJob> {
    const response = await axios.post(`${this.baseURL}/reports/`, options);
    return response.data;
  }

  // Import functions
  async importCustomers(file: File, options: ImportOptions): Promise<ImportJob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(`${this.baseURL}/customers/import/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async importProducts(file: File, options: ImportOptions): Promise<ImportJob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(`${this.baseURL}/products/import/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async importInvoices(file: File, options: ImportOptions): Promise<ImportJob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(`${this.baseURL}/invoices/import/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async importInventory(file: File, options: ImportOptions): Promise<ImportJob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('options', JSON.stringify(options));

    const response = await axios.post(`${this.baseURL}/inventory/import/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Job management
  async getExportJob(jobId: string): Promise<ExportJob> {
    const response = await axios.get(`${this.baseURL}/jobs/${jobId}/`);
    return response.data;
  }

  async getImportJob(jobId: string): Promise<ImportJob> {
    const response = await axios.get(`${this.baseURL}/jobs/import/${jobId}/`);
    return response.data;
  }

  async getExportJobs(): Promise<ExportJob[]> {
    const response = await axios.get(`${this.baseURL}/jobs/`);
    return response.data;
  }

  async getImportJobs(): Promise<ImportJob[]> {
    const response = await axios.get(`${this.baseURL}/jobs/import/`);
    return response.data;
  }

  async cancelExportJob(jobId: string): Promise<void> {
    await axios.post(`${this.baseURL}/jobs/${jobId}/cancel/`);
  }

  async cancelImportJob(jobId: string): Promise<void> {
    await axios.post(`${this.baseURL}/jobs/import/${jobId}/cancel/`);
  }

  async deleteExportJob(jobId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/jobs/${jobId}/`);
  }

  async deleteImportJob(jobId: string): Promise<void> {
    await axios.delete(`${this.baseURL}/jobs/import/${jobId}/`);
  }

  // Download functions
  async downloadFile(url: string, filename: string): Promise<void> {
    const response = await axios.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  // Template functions
  async getExportTemplate(entity: string): Promise<Blob> {
    const response = await axios.get(`${this.baseURL}/templates/${entity}/`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async downloadExportTemplate(entity: string, format: string): Promise<void> {
    const blob = await this.getExportTemplate(entity);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${entity}_template.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  // Validation functions
  async validateImportFile(file: File, entity: string): Promise<{
    valid: boolean;
    errors: string[];
    warnings: string[];
    recordCount: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity', entity);

    const response = await axios.post(`${this.baseURL}/validate/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Field mapping
  async getFieldMapping(entity: string): Promise<Record<string, string[]>> {
    const response = await axios.get(`${this.baseURL}/mapping/${entity}/`);
    return response.data;
  }

  // Statistics
  async getExportStatistics(): Promise<{
    totalExports: number;
    successfulExports: number;
    failedExports: number;
    totalImports: number;
    successfulImports: number;
    failedImports: number;
    lastExportDate?: string;
    lastImportDate?: string;
  }> {
    const response = await axios.get(`${this.baseURL}/statistics/`);
    return response.data;
  }
}

export const exportService = new ExportService();
export default exportService;