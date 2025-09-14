import { apiService, tokenManager } from './api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  is_staff: boolean;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user?: User;
}

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiService.post<AuthResponse>('/auth/token/', credentials);
      const { access, refresh } = response.data;
      
      tokenManager.setTokens(access, refresh);
      
      // Get user info
      const userResponse = await apiService.get<User>('/auth/user/');
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      
      return { ...response.data, user: userResponse.data };
    } catch (error) {
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      const refresh = tokenManager.getRefreshToken();
      if (refresh) {
        await apiService.post('/auth/logout/', { refresh });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      tokenManager.clearTokens();
      window.location.href = '/login';
    }
  }

  async refreshToken(): Promise<string> {
    const refresh = tokenManager.getRefreshToken();
    if (!refresh) {
      throw new Error('No refresh token available');
    }

    const response = await apiService.post<{ access: string }>('/auth/token/refresh/', {
      refresh,
    });

    const { access } = response.data;
    tokenManager.setTokens(access, refresh);
    return access;
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  isAuthenticated(): boolean {
    return !!tokenManager.getAccessToken();
  }

  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    
    // Superusers have all permissions
    if (user.is_superuser) return true;
    
    // Add more permission logic here
    return false;
  }
}

export default new AuthService();