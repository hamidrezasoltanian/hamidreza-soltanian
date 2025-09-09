import { useState, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface OfflineAction {
  id: string;
  type: string;
  url: string;
  method: string;
  headers: Record<string, string>;
  body?: string;
  timestamp: number;
}

export const useOffline = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingActions, setPendingActions] = useState<OfflineAction[]>([]);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      console.log('App is online');
      
      // Sync pending actions when coming back online
      syncPendingActions();
    };

    const handleOffline = () => {
      setIsOnline(false);
      console.log('App is offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load pending actions from localStorage
    loadPendingActions();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadPendingActions = useCallback(() => {
    try {
      const stored = localStorage.getItem('offline_actions');
      if (stored) {
        const actions = JSON.parse(stored);
        setPendingActions(actions);
      }
    } catch (error) {
      console.error('Error loading pending actions:', error);
    }
  }, []);

  const savePendingActions = useCallback((actions: OfflineAction[]) => {
    try {
      localStorage.setItem('offline_actions', JSON.stringify(actions));
      setPendingActions(actions);
    } catch (error) {
      console.error('Error saving pending actions:', error);
    }
  }, []);

  const addPendingAction = useCallback((action: Omit<OfflineAction, 'id' | 'timestamp'>) => {
    const newAction: OfflineAction = {
      ...action,
      id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now()
    };

    const updatedActions = [...pendingActions, newAction];
    savePendingActions(updatedActions);

    return newAction.id;
  }, [pendingActions, savePendingActions]);

  const removePendingAction = useCallback((actionId: string) => {
    const updatedActions = pendingActions.filter(action => action.id !== actionId);
    savePendingActions(updatedActions);
  }, [pendingActions, savePendingActions]);

  const syncPendingActions = useCallback(async () => {
    if (!isOnline || pendingActions.length === 0) {
      return;
    }

    console.log(`Syncing ${pendingActions.length} pending actions...`);

    const syncPromises = pendingActions.map(async (action) => {
      try {
        const response = await fetch(action.url, {
          method: action.method,
          headers: action.headers,
          body: action.body
        });

        if (response.ok) {
          console.log(`Successfully synced action: ${action.id}`);
          removePendingAction(action.id);
          
          // Invalidate relevant queries
          queryClient.invalidateQueries();
          
          return { success: true, actionId: action.id };
        } else {
          console.error(`Failed to sync action ${action.id}:`, response.status);
          return { success: false, actionId: action.id, error: response.status };
        }
      } catch (error) {
        console.error(`Error syncing action ${action.id}:`, error);
        return { success: false, actionId: action.id, error: error.message };
      }
    });

    const results = await Promise.all(syncPromises);
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    console.log(`Sync completed: ${successCount} successful, ${failureCount} failed`);

    return { successCount, failureCount, results };
  }, [isOnline, pendingActions, removePendingAction, queryClient]);

  const clearAllPendingActions = useCallback(() => {
    savePendingActions([]);
  }, [savePendingActions]);

  const retryFailedActions = useCallback(async () => {
    const failedActions = pendingActions.filter(action => {
      const now = Date.now();
      const actionAge = now - action.timestamp;
      // Retry actions older than 5 minutes
      return actionAge > 5 * 60 * 1000;
    });

    if (failedActions.length === 0) {
      return { successCount: 0, failureCount: 0 };
    }

    console.log(`Retrying ${failedActions.length} failed actions...`);
    return await syncPendingActions();
  }, [pendingActions, syncPendingActions]);

  return {
    isOnline,
    pendingActions,
    addPendingAction,
    removePendingAction,
    syncPendingActions,
    clearAllPendingActions,
    retryFailedActions
  };
};

export const useOfflineMutation = () => {
  const { isOnline, addPendingAction } = useOffline();

  const offlineMutation = useCallback(async (
    mutationFn: () => Promise<any>,
    offlineAction: Omit<OfflineAction, 'id' | 'timestamp'>
  ) => {
    if (isOnline) {
      try {
        return await mutationFn();
      } catch (error) {
        // If online but request failed, queue for retry
        console.log('Request failed, queuing for offline retry');
        addPendingAction(offlineAction);
        throw error;
      }
    } else {
      // If offline, queue the action
      console.log('App is offline, queuing action');
      const actionId = addPendingAction(offlineAction);
      return { offline: true, actionId };
    }
  }, [isOnline, addPendingAction]);

  return { offlineMutation };
};

export const useOfflineQuery = () => {
  const { isOnline } = useOffline();
  const queryClient = useQueryClient();

  const offlineQuery = useCallback(async (
    queryKey: string[],
    queryFn: () => Promise<any>,
    options: {
      staleTime?: number;
      cacheTime?: number;
      retry?: boolean;
    } = {}
  ) => {
    const {
      staleTime = 5 * 60 * 1000, // 5 minutes
      cacheTime = 10 * 60 * 1000, // 10 minutes
      retry = true
    } = options;

    if (isOnline) {
      // Online: normal query with caching
      return queryClient.fetchQuery({
        queryKey,
        queryFn,
        staleTime,
        cacheTime,
        retry
      });
    } else {
      // Offline: try to get from cache
      const cachedData = queryClient.getQueryData(queryKey);
      if (cachedData) {
        console.log('Returning cached data for offline query');
        return cachedData;
      } else {
        throw new Error('No cached data available for offline query');
      }
    }
  }, [isOnline, queryClient]);

  return { offlineQuery };
};