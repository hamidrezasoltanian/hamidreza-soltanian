import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

export interface Widget {
  id: string;
  title: string;
  type: 'chart' | 'stat' | 'table' | 'list';
  size: 'small' | 'medium' | 'large';
  visible: boolean;
  position: { x: number; y: number };
  data?: any;
}

export interface FilterOptions {
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  category: string[];
  status: string[];
  amountRange: [number, number];
  trend: 'all' | 'up' | 'down';
  groupBy: 'none' | 'category' | 'status' | 'date';
  showZeroValues: boolean;
}

export interface DashboardConfig {
  widgets: Widget[];
  layout: 'grid' | 'list';
  theme: 'light' | 'dark';
  refreshInterval: number;
}

const defaultWidgets: Widget[] = [
  {
    id: 'customers-stat',
    title: 'مشتریان',
    type: 'stat',
    size: 'small',
    visible: true,
    position: { x: 0, y: 0 },
    data: { value: 0, trend: 12 }
  },
  {
    id: 'products-stat',
    title: 'محصولات',
    type: 'stat',
    size: 'small',
    visible: true,
    position: { x: 1, y: 0 },
    data: { value: 0, trend: 8 }
  },
  {
    id: 'invoices-stat',
    title: 'فاکتورها',
    type: 'stat',
    size: 'small',
    visible: true,
    position: { x: 2, y: 0 },
    data: { value: 0, trend: 23 }
  },
  {
    id: 'sales-stat',
    title: 'فروش',
    type: 'stat',
    size: 'small',
    visible: true,
    position: { x: 3, y: 0 },
    data: { value: 0, trend: 15 }
  },
  {
    id: 'sales-chart',
    title: 'نمودار فروش ماهانه',
    type: 'chart',
    size: 'large',
    visible: true,
    position: { x: 0, y: 1 },
    data: [
      { name: 'فروردین', value: 4000 },
      { name: 'اردیبهشت', value: 3000 },
      { name: 'خرداد', value: 2000 },
      { name: 'تیر', value: 2780 },
      { name: 'مرداد', value: 1890 },
      { name: 'شهریور', value: 2390 },
    ]
  },
  {
    id: 'recent-activities',
    title: 'فعالیت‌های اخیر',
    type: 'list',
    size: 'medium',
    visible: true,
    position: { x: 2, y: 1 },
    data: [
      { title: 'فاکتور جدید ایجاد شد', subtitle: 'مبلغ: 1,500,000 تومان', time: '2 دقیقه پیش', icon: '📄' },
      { title: 'مشتری جدید اضافه شد', subtitle: 'شرکت: فناوری پارس', time: '15 دقیقه پیش', icon: '👤' },
      { title: 'محصول جدید ثبت شد', subtitle: 'نام: لپ‌تاپ ایسوس', time: '1 ساعت پیش', icon: '💻' },
      { title: 'موجودی انبار به‌روزرسانی شد', subtitle: 'انبار: مرکزی', time: '2 ساعت پیش', icon: '📦' },
    ]
  },
  {
    id: 'top-products',
    title: 'محصولات پرفروش',
    type: 'table',
    size: 'medium',
    visible: true,
    position: { x: 0, y: 2 },
    data: [
      { name: 'لپ‌تاپ ایسوس', value: '45' },
      { name: 'موبایل سامسونگ', value: '32' },
      { name: 'تبلت اپل', value: '28' },
      { name: 'هدفون سونی', value: '21' },
    ]
  },
  {
    id: 'system-status',
    title: 'وضعیت سیستم',
    type: 'table',
    size: 'small',
    visible: true,
    position: { x: 2, y: 2 },
    data: [
      { name: 'سرور', value: 'آنلاین' },
      { name: 'دیتابیس', value: 'متصل' },
      { name: 'API', value: 'فعال' },
    ]
  }
];

export const useDashboard = () => {
  const [config, setConfig] = useState<DashboardConfig>(() => {
    const saved = localStorage.getItem('dashboard-config');
    if (saved) {
      return JSON.parse(saved);
    }
    return {
      widgets: defaultWidgets,
      layout: 'grid',
      theme: 'light',
      refreshInterval: 30000
    };
  });

  const [isConfiguring, setIsConfiguring] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);

  // Save config to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('dashboard-config', JSON.stringify(config));
  }, [config]);

  const toggleWidgetVisibility = (widgetId: string) => {
    setConfig(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId
          ? { ...widget, visible: !widget.visible }
          : widget
      )
    }));
  };

  const updateWidgetPosition = (widgetId: string, position: { x: number; y: number }) => {
    setConfig(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId
          ? { ...widget, position }
          : widget
      )
    }));
  };

  const updateWidgetSize = (widgetId: string, size: 'small' | 'medium' | 'large') => {
    setConfig(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId
          ? { ...widget, size }
          : widget
      )
    }));
  };

  const addWidget = (widget: Omit<Widget, 'id' | 'position'>) => {
    const newWidget: Widget = {
      ...widget,
      id: `widget-${Date.now()}`,
      position: { x: 0, y: 0 }
    };
    setConfig(prev => ({
      ...prev,
      widgets: [...prev.widgets, newWidget]
    }));
  };

  const removeWidget = (widgetId: string) => {
    setConfig(prev => ({
      ...prev,
      widgets: prev.widgets.filter(widget => widget.id !== widgetId)
    }));
  };

  const resetDashboard = () => {
    setConfig({
      widgets: defaultWidgets,
      layout: 'grid',
      theme: 'light',
      refreshInterval: 30000
    });
  };

  const updateConfig = (updates: Partial<DashboardConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const getVisibleWidgets = () => {
    return config.widgets.filter(widget => widget.visible);
  };

  const getWidgetById = (id: string) => {
    return config.widgets.find(widget => widget.id === id);
  };

  return {
    config,
    widgets: config.widgets,
    visibleWidgets: getVisibleWidgets(),
    isConfiguring,
    selectedWidget,
    toggleWidgetVisibility,
    updateWidgetPosition,
    updateWidgetSize,
    addWidget,
    removeWidget,
    resetDashboard,
    updateConfig,
    getWidgetById,
    setIsConfiguring,
    setSelectedWidget,
  };
};