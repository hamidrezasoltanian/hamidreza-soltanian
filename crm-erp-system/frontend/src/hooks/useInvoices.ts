import { useQuery } from '@tanstack/react-query';
import { invoiceService } from '../services/invoiceService';

export const useInvoices = () => {
  return useQuery({
    queryKey: ['invoices'],
    queryFn: () => invoiceService.getInvoices(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useInvoice = (id: number) => {
  return useQuery({
    queryKey: ['invoice', id],
    queryFn: () => invoiceService.getInvoice(id),
    enabled: !!id,
  });
};