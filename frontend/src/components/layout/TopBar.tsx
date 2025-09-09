import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  TextField,
  InputAdornment,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Stack,
  Tooltip,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search,
  Notifications,
  Settings,
  AccountCircle,
  Logout,
  LightMode,
  DarkMode,
  AutoMode,
  Fullscreen,
  FullscreenExit,
  Help,
  Feedback,
  Keyboard,
  Refresh,
  CloudSync,
  Security,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { useTheme as useCustomTheme } from '../../contexts/ThemeContext';
import { FadeIn, HoverScale } from '../animations/FadeIn';

interface TopBarProps {
  onMenuToggle: () => void;
  title?: string;
}

const TopBar: React.FC<TopBarProps> = ({ onMenuToggle, title = 'داشبورد' }) => {
  const theme = useTheme();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme, themeMode } = useCustomTheme();
  
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);
  const [notificationsMenuAnchor, setNotificationsMenuAnchor] = useState<null | HTMLElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleNotificationsMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsMenuAnchor(event.currentTarget);
  };

  const handleNotificationsMenuClose = () => {
    setNotificationsMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
  };

  const handleFullscreenToggle = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const notifications = [
    {
      id: 1,
      title: 'فاکتور جدید',
      message: 'فاکتور #1234 برای مشتری احمد محمدی صادر شد',
      time: '5 دقیقه پیش',
      type: 'success',
      unread: true,
    },
    {
      id: 2,
      title: 'موجودی کم',
      message: 'محصول لپ‌تاپ Dell موجودی کمی دارد',
      time: '1 ساعت پیش',
      type: 'warning',
      unread: true,
    },
    {
      id: 3,
      title: 'پشتیبان‌گیری',
      message: 'پشتیبان‌گیری روزانه با موفقیت انجام شد',
      time: '2 ساعت پیش',
      type: 'info',
      unread: false,
    },
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'primary';
    }
  };

  return (
    <FadeIn>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          background: isDarkMode 
            ? 'linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(90deg, #ffffff 0%, #f8f9fa 100%)',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backdropFilter: 'blur(10px)',
        }}
      >
        <Toolbar sx={{ px: { xs: 2, sm: 3 } }}>
          {/* Menu Button */}
          <HoverScale>
            <IconButton
              edge="start"
              color="inherit"
              onClick={onMenuToggle}
              sx={{
                mr: 2,
                color: theme.palette.text.primary,
                '&:hover': {
                  backgroundColor: alpha(theme.palette.action.hover, 0.1),
                },
              }}
            >
              <MenuIcon />
            </IconButton>
          </HoverScale>

          {/* Title */}
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 0,
              fontWeight: 700,
              color: theme.palette.text.primary,
              mr: 3,
            }}
          >
            {title}
          </Typography>

          {/* Search */}
          <Box sx={{ flexGrow: 1, maxWidth: 400, mx: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="جستجو در سیستم..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: theme.palette.text.secondary }} />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() => setSearchQuery('')}
                    >
                      ×
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: alpha(theme.palette.action.hover, 0.05),
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.action.hover, 0.1),
                  },
                  '&.Mui-focused': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.05),
                  },
                },
              }}
            />
          </Box>

          {/* Actions */}
          <Stack direction="row" spacing={1} alignItems="center">
            {/* Theme Toggle */}
            <Tooltip title="تغییر تم">
              <HoverScale>
                <IconButton
                  onClick={toggleTheme}
                  sx={{
                    color: theme.palette.text.primary,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.action.hover, 0.1),
                    },
                  }}
                >
                  {themeMode === 'light' ? <DarkMode /> : themeMode === 'dark' ? <AutoMode /> : <LightMode />}
                </IconButton>
              </HoverScale>
            </Tooltip>

            {/* Fullscreen */}
            <Tooltip title={isFullscreen ? 'خروج از تمام صفحه' : 'تمام صفحه'}>
              <HoverScale>
                <IconButton
                  onClick={handleFullscreenToggle}
                  sx={{
                    color: theme.palette.text.primary,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.action.hover, 0.1),
                    },
                  }}
                >
                  {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                </IconButton>
              </HoverScale>
            </Tooltip>

            {/* Sync Status */}
            <Tooltip title="همگام‌سازی">
              <HoverScale>
                <IconButton
                  sx={{
                    color: theme.palette.success.main,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.success.main, 0.1),
                    },
                  }}
                >
                  <CloudSync />
                </IconButton>
              </HoverScale>
            </Tooltip>

            {/* Notifications */}
            <Tooltip title="اعلان‌ها">
              <HoverScale>
                <IconButton
                  onClick={handleNotificationsMenuOpen}
                  sx={{
                    color: theme.palette.text.primary,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.action.hover, 0.1),
                    },
                  }}
                >
                  <Badge 
                    badgeContent={notifications.filter(n => n.unread).length} 
                    color="error"
                    max={9}
                  >
                    <Notifications />
                  </Badge>
                </IconButton>
              </HoverScale>
            </Tooltip>

            {/* Profile */}
            <Tooltip title="پروفایل">
              <HoverScale>
                <IconButton
                  onClick={handleProfileMenuOpen}
                  sx={{
                    p: 0.5,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.action.hover, 0.1),
                    },
                  }}
                >
                  <Avatar
                    sx={{
                      width: 36,
                      height: 36,
                      background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                      color: 'white',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                    }}
                  >
                    {user?.first_name?.[0]}{user?.last_name?.[0]}
                  </Avatar>
                </IconButton>
              </HoverScale>
            </Tooltip>
          </Stack>
        </Toolbar>

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationsMenuAnchor}
          open={Boolean(notificationsMenuAnchor)}
          onClose={handleNotificationsMenuClose}
          PaperProps={{
            sx: {
              width: 360,
              maxHeight: 400,
              mt: 1,
              borderRadius: 2,
              boxShadow: theme.shadows[8],
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              اعلان‌ها
            </Typography>
          </Box>
          {notifications.map((notification) => (
            <MenuItem
              key={notification.id}
              sx={{
                py: 2,
                px: 2,
                borderBottom: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
                '&:hover': {
                  backgroundColor: alpha(theme.palette.action.hover, 0.05),
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, width: '100%' }}>
                <Box sx={{ fontSize: '1.2rem', mt: 0.5 }}>
                  {getNotificationIcon(notification.type)}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {notification.title}
                    </Typography>
                    {notification.unread && (
                      <Chip
                        label="جدید"
                        size="small"
                        color={getNotificationColor(notification.type) as any}
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                    {notification.time}
                  </Typography>
                </Box>
              </Box>
            </MenuItem>
          ))}
        </Menu>

        {/* Profile Menu */}
        <Menu
          anchorEl={profileMenuAnchor}
          open={Boolean(profileMenuAnchor)}
          onClose={handleProfileMenuClose}
          PaperProps={{
            sx: {
              width: 280,
              mt: 1,
              borderRadius: 2,
              boxShadow: theme.shadows[8],
            },
          }}
        >
          <Box sx={{ p: 2, borderBottom: `1px solid ${theme.palette.divider}` }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  color: 'white',
                  fontWeight: 600,
                }}
              >
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </Avatar>
              <Box>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {user?.first_name} {user?.last_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {user?.email}
                </Typography>
              </Box>
            </Box>
          </Box>
          
          <MenuItem onClick={handleProfileMenuClose}>
            <ListItemIcon>
              <AccountCircle />
            </ListItemIcon>
            <ListItemText>پروفایل</ListItemText>
          </MenuItem>
          
          <MenuItem onClick={handleProfileMenuClose}>
            <ListItemIcon>
              <Settings />
            </ListItemIcon>
            <ListItemText>تنظیمات</ListItemText>
          </MenuItem>
          
          <MenuItem onClick={handleProfileMenuClose}>
            <ListItemIcon>
              <Security />
            </ListItemIcon>
            <ListItemText>امنیت</ListItemText>
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={handleProfileMenuClose}>
            <ListItemIcon>
              <Help />
            </ListItemIcon>
            <ListItemText>راهنما</ListItemText>
          </MenuItem>
          
          <MenuItem onClick={handleProfileMenuClose}>
            <ListItemIcon>
              <Feedback />
            </ListItemIcon>
            <ListItemText>ارسال بازخورد</ListItemText>
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <Logout />
            </ListItemIcon>
            <ListItemText>خروج</ListItemText>
          </MenuItem>
        </Menu>
      </AppBar>
    </FadeIn>
  );
};

export default TopBar;