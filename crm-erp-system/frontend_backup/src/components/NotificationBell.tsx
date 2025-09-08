import React, { useState } from 'react';
import {
  IconButton,
  Badge,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Notifications,
  NotificationsActive,
  CheckCircle,
  Error,
  Warning,
  Info,
  Settings,
  MarkEmailRead,
} from '@mui/icons-material';
import { useNotifications, Notification } from '../contexts/NotificationContext';
import NotificationCenter from './NotificationCenter';

const NotificationBell: React.FC = () => {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showNotificationCenter, setShowNotificationCenter] = useState(false);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    handleClose();
  };

  const handleViewAll = () => {
    setShowNotificationCenter(true);
    handleClose();
  };

  const handleMarkAllAsRead = () => {
    markAllAsRead();
    handleClose();
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return <CheckCircle color="success" fontSize="small" />;
      case 'error': return <Error color="error" fontSize="small" />;
      case 'warning': return <Warning color="warning" fontSize="small" />;
      case 'info': return <Info color="info" fontSize="small" />;
      default: return <Info fontSize="small" />;
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

  const recentNotifications = notifications.slice(0, 5);

  return (
    <>
      <Tooltip title="اعلان‌ها">
        <IconButton
          color="inherit"
          onClick={handleClick}
          sx={{ position: 'relative' }}
        >
          <Badge badgeContent={unreadCount} color="error">
            {unreadCount > 0 ? <NotificationsActive /> : <Notifications />}
          </Badge>
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 350,
            maxHeight: 400,
            '& .MuiMenuItem-root': {
              px: 2,
              py: 1,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* Header */}
        <Box sx={{ p: 2, pb: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">اعلان‌ها</Typography>
            {unreadCount > 0 && (
              <Chip 
                label={`${unreadCount} خوانده نشده`} 
                color="primary" 
                size="small" 
              />
            )}
          </Box>
        </Box>

        <Divider />

        {/* Recent Notifications */}
        {recentNotifications.length === 0 ? (
          <MenuItem disabled>
            <ListItemText
              primary="اعلانی وجود ندارد"
              secondary="هیچ اعلان جدیدی دریافت نکرده‌اید"
            />
          </MenuItem>
        ) : (
          recentNotifications.map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              sx={{
                backgroundColor: notification.read ? 'transparent' : 'action.hover',
                flexDirection: 'column',
                alignItems: 'flex-start',
              }}
            >
              <Box display="flex" alignItems="center" width="100%" mb={0.5}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  {getNotificationIcon(notification.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography 
                        variant="subtitle2" 
                        fontWeight={notification.read ? 400 : 600}
                        sx={{ flex: 1 }}
                      >
                        {notification.title}
                      </Typography>
                      <Chip
                        label={notification.priority}
                        size="small"
                        color={getPriorityColor(notification.priority) as any}
                      />
                    </Box>
                  }
                />
              </Box>
              <Typography 
                variant="body2" 
                color="textSecondary" 
                sx={{ 
                  ml: 4, 
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}
              >
                {notification.message}
              </Typography>
            </MenuItem>
          ))
        )}

        <Divider />

        {/* Actions */}
        <MenuItem onClick={handleViewAll}>
          <ListItemIcon>
            <Notifications />
          </ListItemIcon>
          <ListItemText primary="مشاهده همه اعلان‌ها" />
        </MenuItem>

        {unreadCount > 0 && (
          <MenuItem onClick={handleMarkAllAsRead}>
            <ListItemIcon>
              <MarkEmailRead />
            </ListItemIcon>
            <ListItemText primary="علامت‌گذاری همه به عنوان خوانده شده" />
          </MenuItem>
        )}

        <MenuItem onClick={() => setShowNotificationCenter(true)}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText primary="تنظیمات اعلان‌ها" />
        </MenuItem>
      </Menu>

      {/* Notification Center */}
      <NotificationCenter
        open={showNotificationCenter}
        onClose={() => setShowNotificationCenter(false)}
      />
    </>
  );
};

export default NotificationBell;