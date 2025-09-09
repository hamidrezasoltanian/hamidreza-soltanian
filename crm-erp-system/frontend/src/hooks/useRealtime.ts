import { useEffect, useRef, useState } from 'react';
import { useAuth } from './useAuth';

interface RealtimeMessage {
  type: string;
  data?: any;
  notification?: any;
  count?: number;
}

export const useRealtime = (endpoint: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<RealtimeMessage | null>(null);
  const { user, token } = useAuth();
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = () => {
    if (!user || !token) return;

    const wsUrl = `ws://localhost:8000/ws/${endpoint}/?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`Connected to ${endpoint} WebSocket`);
      setIsConnected(true);
      setSocket(ws);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message: RealtimeMessage = JSON.parse(event.data);
        setLastMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log(`Disconnected from ${endpoint} WebSocket`);
      setIsConnected(false);
      setSocket(null);
      
      // Attempt to reconnect
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++;
        const delay = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`Attempting to reconnect to ${endpoint} (attempt ${reconnectAttempts.current})`);
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for ${endpoint}:`, error);
    };

    setSocket(ws);
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socket) {
      socket.close();
      setSocket(null);
      setIsConnected(false);
    }
  };

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    if (user && token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user, token, endpoint]);

  return {
    socket,
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
};

export const useNotifications = () => {
  const { lastMessage, sendMessage } = useRealtime('notifications');
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'new_notification':
          setNotifications(prev => [lastMessage.notification, ...prev]);
          break;
        case 'unread_count':
          setUnreadCount(lastMessage.count || 0);
          break;
        case 'notifications_list':
          setNotifications(lastMessage.notifications || []);
          break;
      }
    }
  }, [lastMessage]);

  const markAsRead = (notificationId: string) => {
    sendMessage({
      type: 'mark_as_read',
      notification_id: notificationId
    });
  };

  const markAllAsRead = () => {
    sendMessage({
      type: 'mark_all_as_read'
    });
  };

  const loadNotifications = (page: number = 1) => {
    sendMessage({
      type: 'get_notifications',
      page
    });
  };

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    loadNotifications
  };
};

export const useDashboard = () => {
  const { lastMessage } = useRealtime('dashboard');
  const [updates, setUpdates] = useState<any[]>([]);

  useEffect(() => {
    if (lastMessage) {
      setUpdates(prev => [lastMessage, ...prev.slice(0, 49)]); // Keep last 50 updates
    }
  }, [lastMessage]);

  return {
    updates,
    lastUpdate: lastMessage
  };
};