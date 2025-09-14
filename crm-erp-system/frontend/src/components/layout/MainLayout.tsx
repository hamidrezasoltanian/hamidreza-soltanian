import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Collapse,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  People,
  Inventory,
  Receipt,
  Assessment,
  Settings,
  Logout,
  Notifications,
  ExpandLess,
  ExpandMore,
  ShoppingCart,
  AccountBalance,
  LocalShipping,
  Description,
  BusinessCenter,
  ChevronLeft,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 280;

interface MenuItemType {
  title: string;
  icon: React.ReactNode;
  path?: string;
  children?: MenuItemType[];
}

const menuItems: MenuItemType[] = [
  {
    title: 'داشبورد',
    icon: <Dashboard />,
    path: '/dashboard',
  },
  {
    title: 'مشتریان',
    icon: <People />,
    children: [
      { title: 'لیست مشتریان', icon: <People />, path: '/customers' },
      { title: 'افزودن مشتری', icon: <People />, path: '/customers/new' },
      { title: 'دسته‌بندی مشتریان', icon: <People />, path: '/customers/categories' },
    ],
  },
  {
    title: 'محصولات',
    icon: <ShoppingCart />,
    children: [
      { title: 'لیست محصولات', icon: <ShoppingCart />, path: '/products' },
      { title: 'افزودن محصول', icon: <ShoppingCart />, path: '/products/new' },
      { title: 'دسته‌بندی محصولات', icon: <ShoppingCart />, path: '/products/categories' },
    ],
  },
  {
    title: 'انبارداری',
    icon: <Inventory />,
    children: [
      { title: 'موجودی انبار', icon: <Inventory />, path: '/inventory' },
      { title: 'ورود کالا', icon: <LocalShipping />, path: '/inventory/in' },
      { title: 'خروج کالا', icon: <LocalShipping />, path: '/inventory/out' },
    ],
  },
  {
    title: 'فاکتورها',
    icon: <Receipt />,
    children: [
      { title: 'لیست فاکتورها', icon: <Receipt />, path: '/invoices' },
      { title: 'فاکتور جدید', icon: <Receipt />, path: '/invoices/new' },
      { title: 'پیش‌فاکتورها', icon: <Description />, path: '/quotations' },
    ],
  },
  {
    title: 'حسابداری',
    icon: <AccountBalance />,
    children: [
      { title: 'دفتر کل', icon: <AccountBalance />, path: '/accounting/ledger' },
      { title: 'تراز آزمایشی', icon: <AccountBalance />, path: '/accounting/trial-balance' },
      { title: 'سند حسابداری', icon: <Description />, path: '/accounting/entries' },
    ],
  },
  {
    title: 'CRM',
    icon: <BusinessCenter />,
    children: [
      { title: 'سرنخ‌ها', icon: <BusinessCenter />, path: '/crm/leads' },
      { title: 'فرصت‌ها', icon: <BusinessCenter />, path: '/crm/opportunities' },
      { title: 'فعالیت‌ها', icon: <BusinessCenter />, path: '/crm/activities' },
    ],
  },
  {
    title: 'گزارش‌ها',
    icon: <Assessment />,
    path: '/reports',
  },
  {
    title: 'تنظیمات',
    icon: <Settings />,
    path: '/settings',
  },
];

const MainLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [openMenus, setOpenMenus] = useState<{ [key: string]: boolean }>({});

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleMenuClick = (title: string) => {
    setOpenMenus(prev => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  const handleNavigation = (path?: string) => {
    if (path) {
      navigate(path);
      if (isMobile) {
        setMobileOpen(false);
      }
    }
  };

  const renderMenuItem = (item: MenuItemType, depth = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isOpen = openMenus[item.title] || false;
    const isActive = item.path === location.pathname;

    return (
      <React.Fragment key={item.title}>
        <ListItem disablePadding sx={{ display: 'block' }}>
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                handleMenuClick(item.title);
              } else {
                handleNavigation(item.path);
              }
            }}
            sx={{
              minHeight: 48,
              justifyContent: 'initial',
              px: 2.5 + depth * 2,
              backgroundColor: isActive ? 'action.selected' : 'transparent',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: 3,
                justifyContent: 'center',
                color: isActive ? 'primary.main' : 'inherit',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.title} 
              primaryTypographyProps={{
                fontWeight: isActive ? 600 : 400,
              }}
            />
            {hasChildren && (
              <>{isOpen ? <ExpandLess /> : <ExpandMore />}</>
            )}
          </ListItemButton>
        </ListItem>
        {hasChildren && (
          <Collapse in={isOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderMenuItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          CRM/ERP System
        </Typography>
        {isMobile && (
          <IconButton color="inherit" onClick={handleDrawerToggle}>
            <ChevronLeft />
          </IconButton>
        )}
      </Toolbar>
      <Divider />
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List>
          {menuItems.map(item => renderMenuItem(item))}
        </List>
      </Box>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          نسخه 1.0.0
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'background.paper',
          color: 'text.primary',
          boxShadow: 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {location.pathname === '/dashboard' ? 'داشبورد' : ''}
          </Typography>

          <IconButton color="inherit" sx={{ mr: 2 }}>
            <Badge badgeContent={4} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          <IconButton onClick={handleProfileMenuOpen} sx={{ p: 0 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              {user?.first_name?.[0] || 'U'}
            </Avatar>
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem disabled>
              <Typography variant="body2">
                {user?.first_name} {user?.last_name}
              </Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => navigate('/profile')}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              پروفایل
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              خروج
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: 'grey.50',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;