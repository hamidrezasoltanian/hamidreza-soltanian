import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
} from '@mui/material';
import {
  Notifications,
  Email,
  Settings,
  Add,
  Edit,
  Delete,
  TestTube,
  Save,
  Refresh,
} from '@mui/icons-material';
import { useNotifications } from '../contexts/NotificationContext';
import NotificationCenter from '../components/NotificationCenter';
import EmailNotifications from '../components/EmailNotifications';

const NotificationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);
  const [showEmailManager, setShowEmailManager] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showTestDialog, setShowTestDialog] = useState(false);

  const { 
    notifications, 
    unreadCount, 
    addNotification, 
    clearAllNotifications,
    getNotificationsByCategory 
  } = useNotifications();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleTestNotification = () => {
    addNotification({
      title: 'تست اعلان',
      message: 'این یک اعلان تستی است',
      type: 'info',
      category: 'system',
      priority: 'medium',
    });
  };

  const handleTestEmail = () => {
    addNotification({
      title: 'تست ایمیل',
      message: 'ایمیل تستی ارسال شد',
      type: 'success',
      category: 'system',
      priority: 'medium',
    });
  };

  const systemNotifications = getNotificationsByCategory('system');
  const userNotifications = getNotificationsByCategory('user');
  const businessNotifications = getNotificationsByCategory('business');
  const securityNotifications = getNotificationsByCategory('security');

  const tabs = [
    { 
      label: 'مرکز اعلان‌ها', 
      value: 0, 
      icon: <Notifications />,
      count: notifications.length,
      description: 'مدیریت تمام اعلان‌های سیستم'
    },
    { 
      label: 'ایمیل‌ها', 
      value: 1, 
      icon: <Email />,
      count: 0,
      description: 'مدیریت ارسال و دریافت ایمیل‌ها'
    },
    { 
      label: 'تنظیمات', 
      value: 2, 
      icon: <Settings />,
      count: 0,
      description: 'تنظیمات اعلان‌ها و ایمیل‌ها'
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          مدیریت اعلان‌ها
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<TestTube />}
            onClick={() => setShowTestDialog(true)}
          >
            تست اعلان
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => window.location.reload()}
          >
            به‌روزرسانی
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    کل اعلان‌ها
                  </Typography>
                  <Typography variant="h4">
                    {notifications.length}
                  </Typography>
                </Box>
                <Notifications color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    خوانده نشده
                  </Typography>
                  <Typography variant="h4" color="error">
                    {unreadCount}
                  </Typography>
                </Box>
                <Notifications color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    سیستم
                  </Typography>
                  <Typography variant="h4">
                    {systemNotifications.length}
                  </Typography>
                </Box>
                <Settings color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    تجاری
                  </Typography>
                  <Typography variant="h4">
                    {businessNotifications.length}
                  </Typography>
                </Box>
                <Email color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            {tabs.map((tab) => (
              <Tab
                key={tab.value}
                label={
                  <Box display="flex" alignItems="center" gap={1}>
                    {tab.icon}
                    {tab.label}
                    {tab.count > 0 && (
                      <Chip label={tab.count} size="small" color="primary" />
                    )}
                  </Box>
                }
              />
            ))}
          </Tabs>
        </Box>

        <CardContent>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                مرکز اعلان‌ها
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                مدیریت و مشاهده تمام اعلان‌های سیستم
              </Typography>
              <Button
                variant="contained"
                startIcon={<Notifications />}
                onClick={() => setShowNotificationCenter(true)}
              >
                باز کردن مرکز اعلان‌ها
              </Button>
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                مدیریت ایمیل‌ها
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                ارسال، مدیریت و پیگیری ایمیل‌ها
              </Typography>
              <Button
                variant="contained"
                startIcon={<Email />}
                onClick={() => setShowEmailManager(true)}
              >
                باز کردن مدیریت ایمیل‌ها
              </Button>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                تنظیمات اعلان‌ها
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                پیکربندی تنظیمات اعلان‌ها و ایمیل‌ها
              </Typography>
              <Button
                variant="contained"
                startIcon={<Settings />}
                onClick={() => setShowSettings(true)}
              >
                باز کردن تنظیمات
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Notification Center Dialog */}
      <NotificationCenter
        open={showNotificationCenter}
        onClose={() => setShowNotificationCenter(false)}
      />

      {/* Email Manager Dialog */}
      <Dialog 
        open={showEmailManager} 
        onClose={() => setShowEmailManager(false)} 
        maxWidth="xl" 
        fullWidth
      >
        <DialogTitle>مدیریت ایمیل‌ها</DialogTitle>
        <DialogContent>
          <EmailNotifications />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEmailManager(false)}>بستن</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="md" fullWidth>
        <DialogTitle>تنظیمات اعلان‌ها</DialogTitle>
        <DialogContent>
          <Box>
            <Typography variant="h6" gutterBottom>اعلان‌های سیستم</Typography>
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="فعال کردن اعلان‌های سیستم"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="فعال کردن اعلان‌های ایمیل"
            />
            <FormControlLabel
              control={<Switch />}
              label="فعال کردن اعلان‌های صوتی"
            />
            <FormControlLabel
              control={<Switch defaultChecked />}
              label="فعال کردن اعلان‌های مرورگر"
            />
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>تنظیمات ایمیل</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="ایمیل فرستنده"
                  defaultValue="noreply@company.com"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="نام فرستنده"
                  defaultValue="سیستم CRM/ERP"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="SMTP Server"
                  defaultValue="smtp.gmail.com"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Port"
                  type="number"
                  defaultValue="587"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>انصراف</Button>
          <Button variant="contained" startIcon={<Save />}>ذخیره</Button>
        </DialogActions>
      </Dialog>

      {/* Test Dialog */}
      <Dialog open={showTestDialog} onClose={() => setShowTestDialog(false)}>
        <DialogTitle>تست اعلان‌ها</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            این دکمه‌ها برای تست سیستم اعلان‌ها استفاده می‌شوند:
          </Typography>
          <Box display="flex" flexDirection="column" gap={2}>
            <Button
              variant="outlined"
              startIcon={<Notifications />}
              onClick={handleTestNotification}
            >
              تست اعلان سیستم
            </Button>
            <Button
              variant="outlined"
              startIcon={<Email />}
              onClick={handleTestEmail}
            >
              تست اعلان ایمیل
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTestDialog(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotificationsPage;