import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  type: 'welcome' | 'invoice' | 'payment' | 'reminder' | 'alert' | 'custom';
  variables: string[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface EmailNotification {
  id: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  body: string;
  templateId?: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  status: 'pending' | 'sent' | 'failed' | 'delivered' | 'opened' | 'clicked';
  scheduledAt?: string;
  sentAt?: string;
  errorMessage?: string;
  attachments?: Array<{
    name: string;
    url: string;
    size: number;
  }>;
  metadata?: any;
}

export interface EmailSettings {
  smtpHost: string;
  smtpPort: number;
  smtpUsername: string;
  smtpPassword: string;
  smtpUseTls: boolean;
  fromEmail: string;
  fromName: string;
  replyTo?: string;
  maxRetries: number;
  retryDelay: number;
}

class EmailService {
  private baseURL = `${API_BASE_URL}/email`;

  // Email Templates
  async getTemplates(): Promise<EmailTemplate[]> {
    const response = await axios.get(`${this.baseURL}/templates/`);
    return response.data;
  }

  async getTemplate(id: string): Promise<EmailTemplate> {
    const response = await axios.get(`${this.baseURL}/templates/${id}/`);
    return response.data;
  }

  async createTemplate(template: Omit<EmailTemplate, 'id' | 'createdAt' | 'updatedAt'>): Promise<EmailTemplate> {
    const response = await axios.post(`${this.baseURL}/templates/`, template);
    return response.data;
  }

  async updateTemplate(id: string, template: Partial<EmailTemplate>): Promise<EmailTemplate> {
    const response = await axios.patch(`${this.baseURL}/templates/${id}/`, template);
    return response.data;
  }

  async deleteTemplate(id: string): Promise<void> {
    await axios.delete(`${this.baseURL}/templates/${id}/`);
  }

  // Email Notifications
  async getNotifications(params?: {
    status?: string;
    priority?: string;
    page?: number;
    pageSize?: number;
  }): Promise<{ results: EmailNotification[]; count: number }> {
    const response = await axios.get(`${this.baseURL}/notifications/`, { params });
    return response.data;
  }

  async getNotification(id: string): Promise<EmailNotification> {
    const response = await axios.get(`${this.baseURL}/notifications/${id}/`);
    return response.data;
  }

  async sendEmail(notification: Omit<EmailNotification, 'id' | 'status' | 'sentAt'>): Promise<EmailNotification> {
    const response = await axios.post(`${this.baseURL}/notifications/`, notification);
    return response.data;
  }

  async sendBulkEmail(notifications: Omit<EmailNotification, 'id' | 'status' | 'sentAt'>[]): Promise<EmailNotification[]> {
    const response = await axios.post(`${this.baseURL}/notifications/bulk/`, { notifications });
    return response.data;
  }

  async scheduleEmail(notification: Omit<EmailNotification, 'id' | 'status' | 'sentAt'>, scheduledAt: string): Promise<EmailNotification> {
    const response = await axios.post(`${this.baseURL}/notifications/schedule/`, {
      ...notification,
      scheduledAt,
    });
    return response.data;
  }

  async retryEmail(id: string): Promise<EmailNotification> {
    const response = await axios.post(`${this.baseURL}/notifications/${id}/retry/`);
    return response.data;
  }

  async cancelEmail(id: string): Promise<void> {
    await axios.post(`${this.baseURL}/notifications/${id}/cancel/`);
  }

  // Email Settings
  async getSettings(): Promise<EmailSettings> {
    const response = await axios.get(`${this.baseURL}/settings/`);
    return response.data;
  }

  async updateSettings(settings: Partial<EmailSettings>): Promise<EmailSettings> {
    const response = await axios.patch(`${this.baseURL}/settings/`, settings);
    return response.data;
  }

  async testConnection(): Promise<{ success: boolean; message: string }> {
    const response = await axios.post(`${this.baseURL}/settings/test/`);
    return response.data;
  }

  // Email Analytics
  async getAnalytics(params?: {
    startDate?: string;
    endDate?: string;
    groupBy?: 'day' | 'week' | 'month';
  }): Promise<{
    totalSent: number;
    totalDelivered: number;
    totalOpened: number;
    totalClicked: number;
    deliveryRate: number;
    openRate: number;
    clickRate: number;
    timeline: Array<{
      date: string;
      sent: number;
      delivered: number;
      opened: number;
      clicked: number;
    }>;
  }> {
    const response = await axios.get(`${this.baseURL}/analytics/`, { params });
    return response.data;
  }

  // Template Rendering
  async renderTemplate(templateId: string, variables: Record<string, any>): Promise<{ subject: string; body: string }> {
    const response = await axios.post(`${this.baseURL}/templates/${templateId}/render/`, { variables });
    return response.data;
  }

  // Email Validation
  async validateEmail(email: string): Promise<{ valid: boolean; message?: string }> {
    const response = await axios.post(`${this.baseURL}/validate/`, { email });
    return response.data;
  }

  // Bulk Email Validation
  async validateEmails(emails: string[]): Promise<Array<{ email: string; valid: boolean; message?: string }>> {
    const response = await axios.post(`${this.baseURL}/validate/bulk/`, { emails });
    return response.data;
  }

  // Email Queue Status
  async getQueueStatus(): Promise<{
    pending: number;
    processing: number;
    failed: number;
    total: number;
  }> {
    const response = await axios.get(`${this.baseURL}/queue/status/`);
    return response.data;
  }

  // Clear Failed Emails
  async clearFailedEmails(): Promise<{ cleared: number }> {
    const response = await axios.post(`${this.baseURL}/queue/clear-failed/`);
    return response.data;
  }
}

export const emailService = new EmailService();
export default emailService;