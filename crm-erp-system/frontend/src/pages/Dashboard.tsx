import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  IconButton,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  ShoppingCart,
  Receipt,
  AccountBalance,
  MoreVert,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';

// Sample data for charts
const salesData = [
  { month: 'فروردین', sales: 4000, profit: 2400 },
  { month: 'اردیبهشت', sales: 3000, profit: 1398 },
  { month: 'خرداد', sales: 2000, profit: 9800 },
  { month: 'تیر', sales: 2780, profit: 3908 },
  { month: 'مرداد', sales: 1890, profit: 4800 },
  { month: 'شهریور', sales: 2390, profit: 3800 },
  { month: 'مهر', sales: 3490, profit: 4300 },
];

const categoryData = [
  { name: 'الکترونیک', value: 400, color: '#0088FE' },
  { name: 'لوازم خانگی', value: 300, color: '#00C49F' },
  { name: 'پوشاک', value: 300, color: '#FFBB28' },
  { name: 'مواد غذایی', value: 200, color: '#FF8042' },
];

const recentActivities = [
  { id: 1, type: 'invoice', title: 'فاکتور جدید #1234', time: '5 دقیقه پیش', amount: '12,500,000' },
  { id: 2, type: 'customer', title: 'مشتری جدید: شرکت نوآوران', time: '15 دقیقه پیش' },
  { id: 3, type: 'product', title: 'محصول جدید: لپ تاپ ASUS', time: '1 ساعت پیش' },
  { id: 4, type: 'payment', title: 'دریافت پرداخت #5678', time: '2 ساعت پیش', amount: '8,000,000' },
];

interface StatCardProps {
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon, color }) => {
  const isPositive = change >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography color="textSecondary" gutterBottom variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {value}
              </Typography>
            </Box>
            <Avatar
              sx={{
                bgcolor: `${color}.light`,
                color: `${color}.main`,
                width: 56,
                height: 56,
              }}
            >
              {icon}
            </Avatar>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isPositive ? (
              <ArrowUpward color="success" fontSize="small" />
            ) : (
              <ArrowDownward color="error" fontSize="small" />
            )}
            <Typography
              variant="body2"
              color={isPositive ? 'success.main' : 'error.main'}
              sx={{ fontWeight: 'medium' }}
            >
              {Math.abs(change)}%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              نسبت به ماه قبل
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => setLoading(false), 1000);
  }, []);

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
        داشبورد مدیریت
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="کل فروش"
            value="458.2M"
            change={12.5}
            icon={<TrendingUp />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="مشتریان"
            value="1,234"
            change={8.3}
            icon={<People />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="محصولات"
            value="567"
            change={-2.1}
            icon={<ShoppingCart />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="فاکتورها"
            value="89"
            change={15.7}
            icon={<Receipt />}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Sales Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                نمودار فروش و سود
              </Typography>
              <IconButton size="small">
                <MoreVert />
              </IconButton>
            </Box>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="sales"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                  name="فروش"
                />
                <Area
                  type="monotone"
                  dataKey="profit"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  fillOpacity={0.6}
                  name="سود"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Category Pie Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              فروش بر اساس دسته‌بندی
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activities & Top Products */}
      <Grid container spacing={3}>
        {/* Recent Activities */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              فعالیت‌های اخیر
            </Typography>
            <List>
              {recentActivities.map((activity, index) => (
                <React.Fragment key={activity.id}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        {activity.type === 'invoice' && <Receipt />}
                        {activity.type === 'customer' && <People />}
                        {activity.type === 'product' && <ShoppingCart />}
                        {activity.type === 'payment' && <AccountBalance />}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="caption" color="textSecondary">
                            {activity.time}
                          </Typography>
                          {activity.amount && (
                            <Chip
                              label={`${activity.amount} تومان`}
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < recentActivities.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Top Products */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              محصولات پرفروش
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  { name: 'لپ تاپ ASUS', sales: 45 },
                  { name: 'موبایل Samsung', sales: 38 },
                  { name: 'یخچال LG', sales: 32 },
                  { name: 'تلویزیون Sony', sales: 28 },
                  { name: 'ماشین لباسشویی', sales: 25 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="sales" fill="#8884d8" name="تعداد فروش" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;