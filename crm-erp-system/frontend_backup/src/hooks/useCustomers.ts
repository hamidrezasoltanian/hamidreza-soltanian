import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerService } from '../services/customerService';
import { toast } from 'react-toastify';

export const useCustomers = (params?: any) => {
  return useQuery({
    queryKey: ['customers', params],
    queryFn: () => customerService.getCustomers(params),
  });
};

export const useCustomer = (id: number) => {
  return useQuery({
    queryKey: ['customer', id],
    queryFn: () => customerService.getCustomer(id),
    enabled: !!id,
  });
};

export const useCustomerStats = () => {
  return useQuery({
    queryKey: ['customer-stats'],
    queryFn: () => customerService.getCustomerStats(),
  });
};

export const useCreateCustomer = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: customerService.createCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
      toast.success('مشتری با موفقیت ایجاد شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در ایجاد مشتری');
    },
  });
};

export const useUpdateCustomer = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      customerService.updateCustomer(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer', id] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
      toast.success('مشتری با موفقیت بروزرسانی شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در بروزرسانی مشتری');
    },
  });
};

export const useDeleteCustomer = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: customerService.deleteCustomer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] });
      toast.success('مشتری با موفقیت حذف شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در حذف مشتری');
    },
  });
};

export const useCustomerCategories = () => {
  return useQuery({
    queryKey: ['customer-categories'],
    queryFn: () => customerService.getCategories(),
  });
};

export const useCreateCustomerCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: customerService.createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-categories'] });
      toast.success('دسته‌بندی با موفقیت ایجاد شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در ایجاد دسته‌بندی');
    },
  });
};

export const useUpdateCustomerCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      customerService.updateCategory(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-categories'] });
      toast.success('دسته‌بندی با موفقیت بروزرسانی شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در بروزرسانی دسته‌بندی');
    },
  });
};

export const useDeleteCustomerCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: customerService.deleteCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-categories'] });
      toast.success('دسته‌بندی با موفقیت حذف شد');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'خطا در حذف دسته‌بندی');
    },
  });
};