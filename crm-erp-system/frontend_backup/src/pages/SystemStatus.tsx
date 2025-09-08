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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
  ExpandMore,
  Storage,
  Api,
  Security,
  Speed,
  Memory,
  NetworkCheck,
} from '@mui/icons-material';

const SystemStatus: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [systemStatus, setSystemStatus] = useState({
    backend: { status: 'online', responseTime: 45, uptime: '99.9%' },
    frontend: { status: 'online', responseTime: 23, uptime: '99.8%' },
    database: { status: 'online', responseTime: 12, uptime: '99.9%' },
    api: { status: 'online', responseTime: 34, uptime: '99.7%' },
  });

  const [moduleStatus, setModuleStatus] = useState([
    { name: 'مشتریان', status: 'active', records: 0, lastUpdate: '2 دقیقه پیش' },
    { name: 'محصولات', status: 'active', records: 0, lastUpdate: '5 دقیقه پیش' },
    { name: 'فاکتورها', status: 'active', records: 0, lastUpdate: '1 دقیقه پیش' },
    { name: 'انبار', status: 'active', records: 0, lastUpdate: '3 دقیقه پیش' },
    { name: 'CRM', status: 'active', records: 0, lastUpdate: '4 دقیقه پیش' },
    { name: 'حسابداری', status: 'active', records: 0, lastUpdate: '6 دقیقه پیش' },
    { name: 'مالیات', status: 'active', records: 0, lastUpdate: '8 دقیقه پیش' },
    { name: 'گزارش‌گیری', status: 'active', records: 0, lastUpdate: '10 دقیقه پیش' },
  ]);

  const [recentLogs, setRecentLogs] = useState([
    { time: '14:30:25', level: 'INFO', message: 'سیستم با موفقیت راه‌اندازی شد', module: 'System' },
    { time: '14:29:18', level: 'INFO', message: 'اتصال به دیتابیس برقرار شد', module: 'Database' },
    { time: '14:28:45', level: 'WARN', message: 'فضای ذخیره‌سازی 75% پر شده است', module: 'Storage' },
    { time: '14:27:32', level: 'INFO', message: 'API endpoint جدید اضافه شد', module: 'API' },
    { time: '14:26:15', level: 'ERROR', message: 'خطا در اتصال به سرویس خارجی', module: 'External' },
    { time: '14:25:08', level: 'INFO', message: 'پشتیبان‌گیری خودکار انجام شد', module: 'Backup' },
  ]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    // Simulate refresh
    setTimeout(() => {
      setSystemStatus(prev => ({
        ...prev,
        backend: { ...prev.backend, responseTime: Math.floor(Math.random() * 50) + 20 },
        frontend: { ...prev.frontend, responseTime: Math.floor(Math.random() * 30) + 10 },
        database: { ...prev.database, responseTime: Math.floor(Math.random() * 20) + 5 },
        api: { ...prev.api, responseTime: Math.floor(Math.random() * 40) + 15 },
      }));
    }, 1000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'active':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
      case 'offline':
        return 'error';
      default:
        return 'default';
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'ERROR':
        return <Error color="error" />;
      case 'WARN':
        return <Warning color="warning" />;
      case 'INFO':
        return <Info color="info" />;
      default:
        return <Info />;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'error';
      case 'WARN':
        return 'warning';
      case 'INFO':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          وضعیت سیستم
        </Typography>
        <Tooltip title="به‌روزرسانی">
          <IconButton onClick={handleRefresh} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* System Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              نمای کلی سیستم
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(systemStatus).map(([key, value]) => (
                <Grid item xs={12} sm={6} md={3} key={key}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {key === 'backend' && 'بک‌اند'}
                            {key === 'frontend' && 'فرانت‌اند'}
                            {key === 'database' && 'دیتابیس'}
                            {key === 'api' && 'API'}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            زمان پاسخ: {value.responseTime}ms
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            آپتایم: {value.uptime}
                          </Typography>
                        </Box>
                        <Chip
                          label={value.status === 'online' ? 'آنلاین' : 'آفلاین'}
                          color={getStatusColor(value.status) as any}
                          icon={<CheckCircle />}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Module Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              وضعیت ماژول‌ها
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ماژول</TableCell>
                    <TableCell>وضعیت</TableCell>
                    <TableCell>رکوردها</TableCell>
                    <TableCell>آخرین به‌روزرسانی</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {moduleStatus.map((module, index) => (
                    <TableRow key={index}>
                      <TableCell>{module.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={module.status === 'active' ? 'فعال' : 'غیرفعال'}
                          color={getStatusColor(module.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{module.records.toLocaleString('fa-IR')}</TableCell>
                      <TableCell>{module.lastUpdate}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* System Resources */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              منابع سیستم
            </Typography>
            <Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">CPU</Typography>
                  <Typography variant="body2">45%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={45} />
              </Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">RAM</Typography>
                  <Typography variant="body2">68%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={68} />
              </Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">فضای ذخیره</Typography>
                  <Typography variant="body2">75%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={75} color="warning" />
              </Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">شبکه</Typography>
                  <Typography variant="body2">23%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={23} />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Logs */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              لاگ‌های اخیر
            </Typography>
            <Box>
              {recentLogs.map((log, index) => (
                <Box key={index} display="flex" alignItems="center" mb={1} p={1} sx={{ 
                  backgroundColor: log.level === 'ERROR' ? 'error.light' : 
                                 log.level === 'WARN' ? 'warning.light' : 'info.light',
                  borderRadius: 1 
                }}>
                  <Box mr={2}>
                    {getLogIcon(log.level)}
                  </Box>
                  <Box flex={1}>
                    <Typography variant="body2" fontWeight="bold">
                      [{log.time}] {log.module}
                    </Typography>
                    <Typography variant="body2">
                      {log.message}
                    </Typography>
                  </Box>
                  <Chip
                    label={log.level}
                    color={getLogColor(log.level) as any}
                    size="small"
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">اطلاعات سیستم</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    اطلاعات سرور
                  </Typography>
                  <Typography variant="body2">سیستم عامل: Ubuntu 22.04 LTS</Typography>
                  <Typography variant="body2">پایتون: 3.13.0</Typography>
                  <Typography variant="body2">Node.js: 18.17.0</Typography>
                  <Typography variant="body2">Django: 5.2.6</Typography>
                  <Typography variant="body2">React: 18.2.0</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    اطلاعات دیتابیس
                  </Typography>
                  <Typography variant="body2">PostgreSQL: 14.9</Typography>
                  <Typography variant="body2">حجم دیتابیس: 245 MB</Typography>
                  <Typography variant="body2">تعداد جداول: 47</Typography>
                  <Typography variant="body2">آخرین بک‌آپ: 2 ساعت پیش</Typography>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemStatus;