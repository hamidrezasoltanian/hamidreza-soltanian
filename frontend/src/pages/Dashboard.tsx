import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  TextField,
  InputAdornment,
  Paper,
  Divider,
  Stack,
  Badge,
  Tooltip,
  Fab,
} from '@mui/material';
import {
  TrendingUp,
  People,
  AttachMoney,
  ShoppingCart,
  MoreVert,
  Search,
  FilterList,
  Refresh,
  Add,
  ArrowUpward,
  ArrowDownward,
  Dashboard as DashboardIcon,
  Analytics,
  Timeline,
  Speed,
  Notifications,
  Settings,
  LightMode,
  DarkMode,
  AutoMode,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../hooks/useAuth';
import { useDashboard } from '../hooks/useDashboard';
import { FilterOptions } from '../hooks/useDashboard';
import { AnimatedCard, StatCard, FeatureCard } from '../components/ui/AnimatedCard';
import { StaggerContainer, StaggerItem, FadeIn, HoverScale } from '../components/animations/FadeIn';
import { useTheme } from '../contexts/ThemeContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { isDarkMode, toggleTheme, themeMode } = useTheme();
  const [filters, setFilters] = useState<FilterOptions>({
    dateRange: '30d',
    amountRange: [0, 1000000] as [number, number],
    status: 'all',
    search: '',
  });

  const { data: dashboardData, isLoading, refetch } = useDashboard(filters);

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleRefresh = () => {
    refetch();
  };

  const statCards = [
    {
      title: 'کل مشتریان',
      value: dashboardData?.totalCustomers || 0,
      subtitle: 'مشتریان فعال',
      icon: <People />,
      color: 'primary' as const,
      trend: { value: 12, isPositive: true },
    },
    {
      title: 'فروش ماه',
      value: `${(dashboardData?.monthlyRevenue || 0).toLocaleString()} تومان`,
      subtitle: 'درآمد این ماه',
      icon: <AttachMoney />,
      color: 'success' as const,
      trend: { value: 8, isPositive: true },
    },
    {
      title: 'فاکتورها',
      value: dashboardData?.totalInvoices || 0,
      subtitle: 'فاکتورهای صادر شده',
      icon: <ShoppingCart />,
      color: 'secondary' as const,
      trend: { value: 5, isPositive: true },
    },
    {
      title: 'محصولات',
      value: dashboardData?.totalProducts || 0,
      subtitle: 'محصولات موجود',
      icon: <TrendingUp />,
      color: 'warning' as const,
      trend: { value: 3, isPositive: false },
    },
  ];

  const features = [
    {
      title: 'مدیریت مشتریان',
      description: 'مدیریت کامل اطلاعات مشتریان و ارتباطات',
      icon: <People />,
      color: 'primary' as const,
    },
    {
      title: 'سیستم فاکتور',
      description: 'صدور و مدیریت فاکتورها و پیش فاکتورها',
      icon: <ShoppingCart />,
      color: 'success' as const,
    },
    {
      title: 'گزارشات',
      description: 'گزارشات جامع و تحلیل داده‌ها',
      icon: <Analytics />,
      color: 'secondary' as const,
    },
    {
      title: 'انبارداری',
      description: 'مدیریت موجودی و کنترل انبار',
      icon: <Timeline />,
      color: 'warning' as const,
    },
  ];

  const recentActivities = [
    {
      id: 1,
      type: 'customer',
      title: 'مشتری جدید اضافه شد',
      description: 'احمد محمدی - مشتری حقیقی',
      time: '2 ساعت پیش',
      avatar: 'AM',
    },
    {
      id: 2,
      type: 'invoice',
      title: 'فاکتور جدید صادر شد',
      description: 'فاکتور #1234 - مبلغ 2,500,000 تومان',
      time: '4 ساعت پیش',
      avatar: 'IN',
    },
    {
      id: 3,
      type: 'product',
      title: 'محصول جدید اضافه شد',
      description: 'لپ‌تاپ Dell - دسته‌بندی کامپیوتر',
      time: '6 ساعت پیش',
      avatar: 'PR',
    },
  ];

  return (
    <Box sx={{ p: 3, minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Header */}
      <FadeIn>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mb: 3,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                خوش آمدید، {user?.first_name}!
              </Typography>
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                امروز {new Date().toLocaleDateString('fa-IR')} است
              </Typography>
            </Box>
            <Stack direction="row" spacing={2} alignItems="center">
              <Tooltip title="تغییر تم">
                <IconButton onClick={toggleTheme} sx={{ color: 'white' }}>
                  {themeMode === 'light' ? <DarkMode /> : themeMode === 'dark' ? <AutoMode /> : <LightMode />}
                </IconButton>
              </Tooltip>
              <Tooltip title="تنظیمات">
                <IconButton sx={{ color: 'white' }}>
                  <Settings />
                </IconButton>
              </Tooltip>
              <Tooltip title="اعلان‌ها">
                <IconButton sx={{ color: 'white' }}>
                  <Badge badgeContent={4} color="error">
                    <Notifications />
                  </Badge>
                </IconButton>
              </Tooltip>
            </Stack>
          </Box>
        </Paper>
      </FadeIn>

      {/* Stats Cards */}
      <StaggerContainer staggerDelay={0.1}>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {statCards.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <StaggerItem>
                <StatCard
                  title={stat.title}
                  value={stat.value}
                  subtitle={stat.subtitle}
                  icon={stat.icon}
                  color={stat.color}
                  trend={stat.trend}
                  delay={index * 0.1}
                />
              </StaggerItem>
            </Grid>
          ))}
        </Grid>
      </StaggerContainer>

      <Grid container spacing={3}>
        {/* Features Grid */}
        <Grid item xs={12} md={8}>
          <FadeIn delay={0.4}>
            <AnimatedCard sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  ویژگی‌های سیستم
                </Typography>
                <Grid container spacing={2}>
                  {features.map((feature, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <HoverScale>
                        <FeatureCard
                          title={feature.title}
                          description={feature.description}
                          icon={feature.icon}
                          color={feature.color}
                          delay={0.5 + index * 0.1}
                        />
                      </HoverScale>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </AnimatedCard>
          </FadeIn>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12} md={4}>
          <FadeIn delay={0.6}>
            <AnimatedCard>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    فعالیت‌های اخیر
                  </Typography>
                  <IconButton size="small">
                    <MoreVert />
                  </IconButton>
                </Box>
                <List>
                  {recentActivities.map((activity, index) => (
                    <ListItem key={activity.id} sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            bgcolor: activity.type === 'customer' ? 'primary.main' : 
                                    activity.type === 'invoice' ? 'success.main' : 'warning.main',
                            width: 40,
                            height: 40,
                            fontSize: '0.875rem',
                          }}
                        >
                          {activity.avatar}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {activity.title}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              {activity.description}
                            </Typography>
                            <Typography variant="caption" display="block" color="text.secondary">
                              {activity.time}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </AnimatedCard>
          </FadeIn>
        </Grid>
      </Grid>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          boxShadow: '0 8px 32px rgba(33, 150, 243, 0.3)',
          '&:hover': {
            background: 'linear-gradient(45deg, #1976D2 30%, #1CB5E0 90%)',
            transform: 'scale(1.1)',
          },
        }}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default Dashboard;