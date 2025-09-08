import { useQuery } from '@tanstack/react-query';
import { inventoryService } from '../services/inventoryService';

export const useInventory = () => {
  return useQuery({
    queryKey: ['inventory'],
    queryFn: () => inventoryService.getWarehouses(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useWarehouse = (id: number) => {
  return useQuery({
    queryKey: ['warehouse', id],
    queryFn: () => inventoryService.getWarehouse(id),
    enabled: !!id,
  });
};