import React, { useState } from 'react';
import {
  Box,
  Drawer,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Chip,
  Button,
  Tabs,
  Tab,
  Badge,
  Divider,
  Tooltip,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Close,
  Notifications,
  NotificationsActive,
  CheckCircle,
  Error,
  Warning,
  Info,
  Delete,
  MarkEmailRead,
  FilterList,
  Search,
  Settings,
  MoreVert,
  Refresh,
} from '@mui/icons-material';
import { useNotifications, Notification } from '../contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';
import { faIR } from 'date-fns/locale';

interface NotificationCenterProps {
  open: boolean;
  onClose: () => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ open, onClose }) => {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    getNotificationsByCategory,
    getNotificationsByPriority,
  } = useNotifications();

  const [activeTab, setActiveTab] = useState(0);
  const [filterCategory, setFilterCategory] = useState<Notification['category'] | 'all'>('all');
  const [filterPriority, setFilterPriority] = useState<Notification['priority'] | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showSettings, setShowSettings] = useState(false);

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return <CheckCircle color="success" />;
      case 'error': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <Info color="info" />;
      default: return <Info />;
    }
  };

  const getPriorityColor = (priority: Notification['priority']) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const getCategoryColor = (category: Notification['category']) => {
    switch (category) {
      case 'system': return 'primary';
      case 'user': return 'secondary';
      case 'business': return 'success';
      case 'security': return 'error';
      default: return 'default';
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    const matchesCategory = filterCategory === 'all' || notification.category === filterCategory;
    const matchesPriority = filterPriority === 'all' || notification.priority === filterPriority;
    const matchesSearch = searchTerm === '' || 
      notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      notification.message.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesCategory && matchesPriority && matchesSearch;
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    if (notification.actionUrl) {
      // Navigate to action URL
      console.log('Navigate to:', notification.actionUrl);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAllAsRead = () => {
    markAllAsRead();
    handleMenuClose();
  };

  const handleClearAll = () => {
    clearAllNotifications();
    handleMenuClose();
  };

  const handleRefresh = () => {
    // Refresh notifications logic here
    handleMenuClose();
  };

  const tabs = [
    { label: 'همه', value: 0, count: notifications.length },
    { label: 'خوانده نشده', value: 1, count: unreadCount },
    { label: 'سیستم', value: 2, count: getNotificationsByCategory('system').length },
    { label: 'کاربر', value: 3, count: getNotificationsByCategory('user').length },
    { label: 'تجاری', value: 4, count: getNotificationsByCategory('business').length },
    { label: 'امنیت', value: 5, count: getNotificationsByCategory('security').length },
  ];

  const getFilteredNotificationsForTab = () => {
    switch (activeTab) {
      case 0: return filteredNotifications;
      case 1: return filteredNotifications.filter(n => !n.read);
      case 2: return filteredNotifications.filter(n => n.category === 'system');
      case 3: return filteredNotifications.filter(n => n.category === 'user');
      case 4: return filteredNotifications.filter(n => n.category === 'business');
      case 5: return filteredNotifications.filter(n => n.category === 'security');
      default: return filteredNotifications;
    }
  };

  return (
    <>
      <Drawer
        anchor="right"
        open={open}
        onClose={onClose}
        sx={{
          '& .MuiDrawer-paper': {
            width: 400,
            maxWidth: '90vw',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              مرکز اعلان‌ها
              {unreadCount > 0 && (
                <Chip 
                  label={unreadCount} 
                  color="primary" 
                  size="small" 
                  sx={{ ml: 1 }} 
                />
              )}
            </Typography>
            <Box>
              <Tooltip title="تنظیمات">
                <IconButton onClick={() => setShowSettings(true)} size="small">
                  <Settings />
                </IconButton>
              </Tooltip>
              <IconButton onClick={handleMenuClick} size="small">
                <MoreVert />
              </IconButton>
              <IconButton onClick={onClose} size="small">
                <Close />
              </IconButton>
            </Box>
          </Box>

          {/* Search and Filters */}
          <Box mb={2}>
            <TextField
              fullWidth
              size="small"
              placeholder="جستجو در اعلان‌ها..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Box>

          <Box display="flex" gap={1} mb={2}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>دسته</InputLabel>
              <Select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value as any)}
                label="دسته"
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="system">سیستم</MenuItem>
                <MenuItem value="user">کاربر</MenuItem>
                <MenuItem value="business">تجاری</MenuItem>
                <MenuItem value="security">امنیت</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>اولویت</InputLabel>
              <Select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value as any)}
                label="اولویت"
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="urgent">فوری</MenuItem>
                <MenuItem value="high">بالا</MenuItem>
                <MenuItem value="medium">متوسط</MenuItem>
                <MenuItem value="low">پایین</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ mb: 2 }}
          >
            {tabs.map((tab) => (
              <Tab
                key={tab.value}
                label={
                  <Box display="flex" alignItems="center" gap={1}>
                    {tab.label}
                    {tab.count > 0 && (
                      <Chip label={tab.count} size="small" color="primary" />
                    )}
                  </Box>
                }
              />
            ))}
          </Tabs>

          <Divider sx={{ mb: 2 }} />

          {/* Notifications List */}
          <List sx={{ maxHeight: '60vh', overflow: 'auto' }}>
            {getFilteredNotificationsForTab().length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="اعلانی یافت نشد"
                  secondary="هیچ اعلانی با فیلترهای انتخابی یافت نشد"
                />
              </ListItem>
            ) : (
              getFilteredNotificationsForTab().map((notification) => (
                <ListItem
                  key={notification.id}
                  button
                  onClick={() => handleNotificationClick(notification)}
                  sx={{
                    backgroundColor: notification.read ? 'transparent' : 'action.hover',
                    borderRadius: 1,
                    mb: 1,
                  }}
                >
                  <ListItemIcon>
                    {getNotificationIcon(notification.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle2" fontWeight={notification.read ? 400 : 600}>
                          {notification.title}
                        </Typography>
                        <Chip
                          label={notification.priority}
                          size="small"
                          color={getPriorityColor(notification.priority) as any}
                        />
                        <Chip
                          label={notification.category}
                          size="small"
                          color={getCategoryColor(notification.category) as any}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {formatDistanceToNow(notification.timestamp, { 
                            addSuffix: true, 
                            locale: faIR 
                          })}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeNotification(notification.id);
                      }}
                      size="small"
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>

          {/* Actions */}
          <Box display="flex" justifyContent="space-between" mt={2}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleMarkAllAsRead}
              disabled={unreadCount === 0}
            >
              علامت‌گذاری همه به عنوان خوانده شده
            </Button>
            <Button
              variant="outlined"
              color="error"
              size="small"
              onClick={handleClearAll}
              disabled={notifications.length === 0}
            >
              پاک کردن همه
            </Button>
          </Box>
        </Box>
      </Drawer>

      {/* Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMarkAllAsRead}>
          <ListItemIcon><MarkEmailRead /></ListItemIcon>
          علامت‌گذاری همه به عنوان خوانده شده
        </MenuItem>
        <MenuItem onClick={handleRefresh}>
          <ListItemIcon><Refresh /></ListItemIcon>
          به‌روزرسانی
        </MenuItem>
        <MenuItem onClick={handleClearAll}>
          <ListItemIcon><Delete /></ListItemIcon>
          پاک کردن همه
        </MenuItem>
      </Menu>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)}>
        <DialogTitle>تنظیمات اعلان‌ها</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary">
            تنظیمات اعلان‌ها در اینجا قرار می‌گیرد
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default NotificationCenter;