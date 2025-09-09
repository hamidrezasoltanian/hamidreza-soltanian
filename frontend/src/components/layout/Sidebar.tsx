import React, { useState } from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Box,
  Typography,
  Divider,
  Avatar,
  Chip,
  Tooltip,
  IconButton,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Dashboard,
  People,
  ShoppingCart,
  Inventory,
  Assessment,
  Settings,
  Notifications,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
  Business,
  Receipt,
  Category,
  AccountBalance,
  Gavel,
  Print,
  CloudUpload,
  CloudDownload,
  Speed,
  Security,
  Backup,
  Analytics,
  Timeline,
  AutoAwesome,
  SmartToy,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { FadeIn, HoverScale } from '../animations/FadeIn';

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  variant?: 'permanent' | 'persistent' | 'temporary';
}

interface MenuItem {
  id: string;
  title: string;
  icon: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  badge?: number;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    title: 'داشبورد',
    icon: <Dashboard />,
    path: '/dashboard',
  },
  {
    id: 'customers',
    title: 'مشتریان',
    icon: <People />,
    path: '/customers',
    badge: 12,
    color: 'primary',
  },
  {
    id: 'products',
    title: 'محصولات',
    icon: <Category />,
    path: '/products',
  },
  {
    id: 'inventory',
    title: 'انبارداری',
    icon: <Inventory />,
    path: '/inventory',
  },
  {
    id: 'invoices',
    title: 'فاکتورها',
    icon: <Receipt />,
    path: '/invoices',
    badge: 5,
    color: 'success',
  },
  {
    id: 'crm',
    title: 'CRM',
    icon: <Business />,
    children: [
      {
        id: 'kanban',
        title: 'کانبان',
        icon: <Timeline />,
        path: '/crm',
      },
      {
        id: 'personnel',
        title: 'پرسنل',
        icon: <People />,
        path: '/personnel',
      },
    ],
  },
  {
    id: 'accounting',
    title: 'حسابداری',
    icon: <AccountBalance />,
    path: '/accounting',
  },
  {
    id: 'tax',
    title: 'مالیات',
    icon: <Gavel />,
    path: '/tax',
  },
  {
    id: 'reports',
    title: 'گزارشات',
    icon: <Assessment />,
    path: '/reports',
  },
  {
    id: 'print',
    title: 'چاپ',
    icon: <Print />,
    path: '/print',
  },
  {
    id: 'ai',
    title: 'هوش مصنوعی',
    icon: <SmartToy />,
    children: [
      {
        id: 'analytics',
        title: 'تحلیل‌ها',
        icon: <Analytics />,
        path: '/analytics',
      },
      {
        id: 'automation',
        title: 'اتوماسیون',
        icon: <AutoAwesome />,
        path: '/automation',
      },
    ],
  },
  {
    id: 'system',
    title: 'سیستم',
    icon: <Settings />,
    children: [
      {
        id: 'notifications',
        title: 'اعلان‌ها',
        icon: <Notifications />,
        path: '/notifications',
        badge: 3,
        color: 'warning',
      },
      {
        id: 'export-import',
        title: 'صادرات/واردات',
        icon: <CloudUpload />,
        path: '/export-import',
      },
      {
        id: 'performance',
        title: 'عملکرد',
        icon: <Speed />,
        path: '/performance',
      },
      {
        id: 'security',
        title: 'امنیت',
        icon: <Security />,
        path: '/security',
      },
      {
        id: 'backup',
        title: 'پشتیبان‌گیری',
        icon: <Backup />,
        path: '/backup',
      },
    ],
  },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onToggle, variant = 'persistent' }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const isDark = theme.palette.mode === 'dark';
  const drawerWidth = 280;

  const handleItemClick = (item: MenuItem) => {
    if (item.children) {
      setExpandedItems(prev => 
        prev.includes(item.id) 
          ? prev.filter(id => id !== item.id)
          : [...prev, item.id]
      );
    } else if (item.path) {
      navigate(item.path);
    }
  };

  const isItemActive = (item: MenuItem): boolean => {
    if (item.path) {
      return location.pathname === item.path;
    }
    if (item.children) {
      return item.children.some(child => child.path === location.pathname);
    }
    return false;
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const isActive = isItemActive(item);
    const isExpanded = expandedItems.includes(item.id);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <React.Fragment key={item.id}>
        <FadeIn delay={level * 0.05}>
          <HoverScale>
            <ListItem disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleItemClick(item)}
                sx={{
                  mx: 1,
                  borderRadius: 2,
                  minHeight: 48,
                  pl: 2 + level * 2,
                  backgroundColor: isActive 
                    ? alpha(theme.palette.primary.main, 0.1)
                    : 'transparent',
                  border: isActive 
                    ? `1px solid ${alpha(theme.palette.primary.main, 0.3)}`
                    : '1px solid transparent',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    backgroundColor: isActive 
                      ? alpha(theme.palette.primary.main, 0.15)
                      : alpha(theme.palette.action.hover, 0.04),
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive 
                      ? theme.palette.primary.main 
                      : theme.palette.text.secondary,
                    transition: 'color 0.2s ease',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: isActive ? 600 : 500,
                          color: isActive 
                            ? theme.palette.primary.main 
                            : theme.palette.text.primary,
                          transition: 'all 0.2s ease',
                        }}
                      >
                        {item.title}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {item.badge && (
                          <Chip
                            label={item.badge}
                            size="small"
                            color={item.color || 'primary'}
                            sx={{
                              height: 20,
                              fontSize: '0.75rem',
                              fontWeight: 600,
                            }}
                          />
                        )}
                        {hasChildren && (
                          isExpanded ? <ExpandLess /> : <ExpandMore />
                        )}
                      </Box>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          </HoverScale>
        </FadeIn>

        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderMenuItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 3,
          background: isDark 
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 100,
            height: 100,
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.1)',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.05)',
          }}
        />
        
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              CRM/ERP
            </Typography>
            <IconButton
              onClick={onToggle}
              sx={{ color: 'white' }}
              size="small"
            >
              {open ? <ChevronLeft /> : <ChevronRight />}
            </IconButton>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 600,
              }}
            >
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </Avatar>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {user?.first_name} {user?.last_name}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                {user?.email}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 2 }}>
        <List>
          {menuItems.map(item => renderMenuItem(item))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          نسخه 2.0.0
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          © 2024 CRM/ERP System
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onToggle}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          background: isDark 
            ? 'linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;