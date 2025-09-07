import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  People,
  Inventory,
  ShoppingCart,
  Assessment,
  TrendingUp,
  TrendingDown,
  Refresh,
  Warning,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useCustomers } from '../hooks/useCustomers';
import { useProducts } from '../hooks/useProducts';
import { useInvoices } from '../hooks/useInvoices';
import { useInventory } from '../hooks/useInventory';

const Dashboard: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const { data: customers, isLoading: customersLoading } = useCustomers();
  const { data: products, isLoading: productsLoading } = useProducts();
  const { data: invoices, isLoading: invoicesLoading } = useInvoices();
  const { data: warehouses, isLoading: warehousesLoading } = useInventory();

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  // Sample data for charts
  const salesData = [
    { name: 'فروردین', amount: 4000, orders: 24 },
    { name: 'اردیبهشت', amount: 3000, orders: 13 },
    { name: 'خرداد', amount: 2000, orders: 98 },
    { name: 'تیر', amount: 2780, orders: 39 },
    { name: 'مرداد', amount: 1890, orders: 48 },
    { name: 'شهریور', amount: 2390, orders: 38 },
  ];

  const categoryData = [
    { name: 'الکترونیک', value: 400, color: '#0088FE' },
    { name: 'پوشاک', value: 300, color: '#00C49F' },
    { name: 'کتاب', value: 300, color: '#FFBB28' },
    { name: 'ورزشی', value: 200, color: '#FF8042' },
  ];

  const recentActivities = [
    { id: 1, action: 'فاکتور جدید ایجاد شد', time: '2 دقیقه پیش', type: 'success' },
    { id: 2, action: 'مشتری جدید اضافه شد', time: '15 دقیقه پیش', type: 'info' },
    { id: 3, action: 'محصول جدید ثبت شد', time: '1 ساعت پیش', type: 'info' },
    { id: 4, action: 'موجودی انبار به‌روزرسانی شد', time: '2 ساعت پیش', type: 'warning' },
    { id: 5, action: 'پرداخت تایید شد', time: '3 ساعت پیش', type: 'success' },
  ];

  const stats = [
    {
      title: 'مشتریان',
      value: customers?.length || 0,
      icon: <People sx={{ fontSize: 40 }} />,
      color: '#1976d2',
      trend: '+12%',
      trendUp: true,
      loading: customersLoading,
    },
    {
      title: 'محصولات',
      value: products?.length || 0,
      icon: <Inventory sx={{ fontSize: 40 }} />,
      color: '#388e3c',
      trend: '+8%',
      trendUp: true,
      loading: productsLoading,
    },
    {
      title: 'فاکتورها',
      value: invoices?.length || 0,
      icon: <ShoppingCart sx={{ fontSize: 40 }} />,
      color: '#f57c00',
      trend: '+23%',
      trendUp: true,
      loading: invoicesLoading,
    },
    {
      title: 'انبارها',
      value: warehouses?.length || 0,
      icon: <Assessment sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
      trend: '+5%',
      trendUp: true,
      loading: warehousesLoading,
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <Schedule color="info" />;
      default: return <CheckCircle />;
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          داشبورد
        </Typography>
        <Tooltip title="به‌روزرسانی">
          <IconButton onClick={handleRefresh} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>
      
      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ position: 'relative', overflow: 'visible' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {stat.loading ? (
                        <LinearProgress sx={{ width: 100 }} />
                      ) : (
                        stat.value.toLocaleString('fa-IR')
                      )}
                    </Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      {stat.trendUp ? (
                        <TrendingUp color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                      ) : (
                        <TrendingDown color="error" sx={{ fontSize: 16, mr: 0.5 }} />
                      )}
                      <Typography variant="body2" color={stat.trendUp ? 'success.main' : 'error.main'}>
                        {stat.trend}
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ color: stat.color }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              نمودار فروش ماهانه
            </Typography>
            <Box height={300}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={salesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="amount" stroke="#8884d8" strokeWidth={2} />
                  <Line type="monotone" dataKey="orders" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              فعالیت‌های اخیر
            </Typography>
            <Box>
              {recentActivities.map((activity) => (
                <Box key={activity.id} display="flex" alignItems="center" mb={2}>
                  <Box mr={1}>
                    {getActivityIcon(activity.type)}
                  </Box>
                  <Box flex={1}>
                    <Typography variant="body2">
                      {activity.action}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {activity.time}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              فروش بر اساس دسته‌بندی
            </Typography>
            <Box height={250}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              وضعیت سیستم
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="body2">سرور</Typography>
                <Chip label="آنلاین" color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="body2">دیتابیس</Typography>
                <Chip label="متصل" color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="body2">API</Typography>
                <Chip label="فعال" color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="body2">فضای ذخیره</Typography>
                <Chip label="75%" color="warning" size="small" />
              </Box>
            </Box>
            <Alert severity="info" sx={{ mt: 2 }}>
              همه سرویس‌ها به درستی کار می‌کنند
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;