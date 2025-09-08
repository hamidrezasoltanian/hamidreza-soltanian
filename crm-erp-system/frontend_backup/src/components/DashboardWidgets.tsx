import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Tooltip,
  Grid,
  Paper,
} from '@mui/material';
import {
  MoreVert,
  DragIndicator,
  Visibility,
  VisibilityOff,
  Settings,
  TrendingUp,
  TrendingDown,
  People,
  Inventory,
  ShoppingCart,
  Assessment,
  AttachMoney,
  Schedule,
  Warning,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';

interface WidgetProps {
  id: string;
  title: string;
  type: 'chart' | 'stat' | 'table' | 'list';
  size: 'small' | 'medium' | 'large';
  visible: boolean;
  onToggleVisibility: (id: string) => void;
  onConfigure: (id: string) => void;
  data?: any;
}

const StatWidget: React.FC<WidgetProps> = ({ title, data, size }) => {
  const getIcon = (title: string) => {
    switch (title) {
      case 'مشتریان': return <People sx={{ fontSize: 40 }} />;
      case 'محصولات': return <Inventory sx={{ fontSize: 40 }} />;
      case 'فاکتورها': return <ShoppingCart sx={{ fontSize: 40 }} />;
      case 'فروش': return <AttachMoney sx={{ fontSize: 40 }} />;
      default: return <Assessment sx={{ fontSize: 40 }} />;
    }
  };

  const getColor = (title: string) => {
    switch (title) {
      case 'مشتریان': return '#1976d2';
      case 'محصولات': return '#388e3c';
      case 'فاکتورها': return '#f57c00';
      case 'فروش': return '#d32f2f';
      default: return '#9c27b0';
    }
  };

  return (
    <Card sx={{ height: size === 'small' ? 120 : size === 'medium' ? 160 : 200 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {data?.value?.toLocaleString('fa-IR') || '0'}
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              {data?.trend > 0 ? (
                <TrendingUp color="success" sx={{ fontSize: 16, mr: 0.5 }} />
              ) : (
                <TrendingDown color="error" sx={{ fontSize: 16, mr: 0.5 }} />
              )}
              <Typography variant="body2" color={data?.trend > 0 ? 'success.main' : 'error.main'}>
                {data?.trend > 0 ? '+' : ''}{data?.trend || 0}%
              </Typography>
            </Box>
          </Box>
          <Box sx={{ color: getColor(title) }}>
            {getIcon(title)}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const ChartWidget: React.FC<WidgetProps> = ({ title, data, size }) => {
  const chartHeight = size === 'small' ? 150 : size === 'medium' ? 200 : 300;

  return (
    <Card sx={{ height: chartHeight + 60 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box height={chartHeight}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <RechartsTooltip />
              <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

const TableWidget: React.FC<WidgetProps> = ({ title, data, size }) => {
  return (
    <Card sx={{ height: size === 'small' ? 200 : size === 'medium' ? 300 : 400 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box>
          {data?.map((item: any, index: number) => (
            <Box key={index} display="flex" justifyContent="space-between" alignItems="center" py={1} borderBottom="1px solid #eee">
              <Typography variant="body2">{item.name}</Typography>
              <Chip label={item.value} size="small" color="primary" />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

const ListWidget: React.FC<WidgetProps> = ({ title, data, size }) => {
  return (
    <Card sx={{ height: size === 'small' ? 200 : size === 'medium' ? 300 : 400 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box>
          {data?.map((item: any, index: number) => (
            <Box key={index} display="flex" alignItems="center" py={1}>
              <Box mr={2}>
                {item.icon}
              </Box>
              <Box flex={1}>
                <Typography variant="body2">{item.title}</Typography>
                <Typography variant="caption" color="textSecondary">{item.subtitle}</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">{item.time}</Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

const DashboardWidget: React.FC<WidgetProps> = (props) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleToggleVisibility = () => {
    props.onToggleVisibility(props.id);
    handleMenuClose();
  };

  const handleConfigure = () => {
    props.onConfigure(props.id);
    handleMenuClose();
  };

  const renderWidget = () => {
    switch (props.type) {
      case 'chart':
        return <ChartWidget {...props} />;
      case 'stat':
        return <StatWidget {...props} />;
      case 'table':
        return <TableWidget {...props} />;
      case 'list':
        return <ListWidget {...props} />;
      default:
        return <StatWidget {...props} />;
    }
  };

  if (!props.visible) return null;

  return (
    <Box sx={{ position: 'relative' }}>
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          zIndex: 1,
          display: 'flex',
          gap: 0.5,
        }}
      >
        <Tooltip title="تنظیمات">
          <IconButton size="small" onClick={handleMenuClick}>
            <MoreVert fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="جابجایی">
          <IconButton size="small">
            <DragIndicator fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      {renderWidget()}
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleToggleVisibility}>
          <VisibilityOff fontSize="small" sx={{ mr: 1 }} />
          مخفی کردن
        </MenuItem>
        <MenuItem onClick={handleConfigure}>
          <Settings fontSize="small" sx={{ mr: 1 }} />
          تنظیمات
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default DashboardWidget;