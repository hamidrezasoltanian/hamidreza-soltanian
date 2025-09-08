import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { toast, ToastContainer, ToastOptions } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  read: boolean;
  category: 'system' | 'user' | 'business' | 'security';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  actionUrl?: string;
  actionText?: string;
  data?: any;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  showToast: (message: string, type?: Notification['type'], options?: ToastOptions) => void;
  getNotificationsByCategory: (category: Notification['category']) => Notification[];
  getNotificationsByPriority: (priority: Notification['priority']) => Notification[];
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>(() => {
    const saved = localStorage.getItem('notifications');
    return saved ? JSON.parse(saved) : [];
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  // Save notifications to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('notifications', JSON.stringify(notifications));
  }, [notifications]);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Show toast notification
    const toastType = notification.type === 'error' ? 'error' : 
                     notification.type === 'warning' ? 'warning' : 
                     notification.type === 'success' ? 'success' : 'info';
    
    toast(notification.message, {
      type: toastType,
      position: 'top-right',
      autoClose: notification.priority === 'urgent' ? 10000 : 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });

    // Play sound for urgent notifications
    if (notification.priority === 'urgent') {
      // You can add sound here
      console.log('🔔 Urgent notification sound');
    }
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const showToast = useCallback((message: string, type: Notification['type'] = 'info', options?: ToastOptions) => {
    const toastType = type === 'error' ? 'error' : 
                     type === 'warning' ? 'warning' : 
                     type === 'success' ? 'success' : 'info';
    
    toast(message, {
      type: toastType,
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }, []);

  const getNotificationsByCategory = useCallback((category: Notification['category']) => {
    return notifications.filter(notification => notification.category === category);
  }, [notifications]);

  const getNotificationsByPriority = useCallback((priority: Notification['priority']) => {
    return notifications.filter(notification => notification.priority === priority);
  }, [notifications]);

  // Auto-cleanup old notifications (older than 7 days)
  useEffect(() => {
    const cleanup = () => {
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      
      setNotifications(prev => 
        prev.filter(notification => notification.timestamp > sevenDaysAgo)
      );
    };

    const interval = setInterval(cleanup, 24 * 60 * 60 * 1000); // Run daily
    return () => clearInterval(interval);
  }, []);

  const value = {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    showToast,
    getNotificationsByCategory,
    getNotificationsByPriority,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={true}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
    </NotificationContext.Provider>
  );
};