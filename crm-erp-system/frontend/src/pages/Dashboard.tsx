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
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Slider,
  Divider,
} from '@mui/material';
import {
  People,
  Inventory,
  ShoppingCart,
  Assessment,
  TrendingUp,
  TrendingDown,
  Refresh,
  Warning,
  CheckCircle,
  Schedule,
  Add,
  Settings,
  ViewModule,
  ViewList,
  Palette,
  FilterList,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { useCustomers } from '../hooks/useCustomers';
import { useProducts } from '../hooks/useProducts';
import { useInvoices } from '../hooks/useInvoices';
import { useInventory } from '../hooks/useInventory';
import { useDashboard, FilterOptions } from '../hooks/useDashboard';
import DashboardWidget from '../components/DashboardWidgets';
import DashboardFilters from '../components/DashboardFilters';

const Dashboard: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAddWidget, setShowAddWidget] = useState(false);
  
  const { data: customers, isLoading: customersLoading } = useCustomers();
  const { data: products, isLoading: productsLoading } = useProducts();
  const { data: invoices, isLoading: invoicesLoading } = useInvoices();
  const { data: warehouses, isLoading: warehousesLoading } = useInventory();
  
  const {
    config,
    visibleWidgets,
    isConfiguring,
    toggleWidgetVisibility,
    updateConfig,
    resetDashboard,
    addWidget,
  } = useDashboard();

  const [filters, setFilters] = useState<FilterOptions>({
    dateRange: { start: null, end: null },
    period: 'monthly',
    category: [],
    status: [],
    amountRange: [0, 10000000],
    trend: 'all',
    showZeroValues: true,
    groupBy: 'none',
  });

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleFiltersChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
  };

  const handleApplyFilters = () => {
    // Apply filters logic here
    console.log('Applying filters:', filters);
  };

  const handleResetFilters = () => {
    setFilters({
      dateRange: { start: null, end: null },
      period: 'monthly',
      category: [],
      status: [],
      amountRange: [0, 10000000],
      trend: 'all',
      showZeroValues: true,
      groupBy: 'none',
    });
  };

  const handleConfigureWidget = (widgetId: string) => {
    console.log('Configuring widget:', widgetId);
  };

  const handleAddWidget = (type: 'chart' | 'stat' | 'table' | 'list') => {
    const newWidget = {
      title: `ویجت جدید ${type}`,
      type,
      size: 'medium' as const,
      visible: true,
    };
    addWidget(newWidget);
    setShowAddWidget(false);
  };

  // Update widget data with real data
  const updateWidgetData = () => {
    const updatedWidgets = config.widgets.map(widget => {
      switch (widget.id) {
        case 'customers-stat':
          return { ...widget, data: { value: customers?.length || 0, trend: 12 } };
        case 'products-stat':
          return { ...widget, data: { value: products?.length || 0, trend: 8 } };
        case 'invoices-stat':
          return { ...widget, data: { value: invoices?.length || 0, trend: 23 } };
        case 'sales-stat':
          return { ...widget, data: { value: 12345000, trend: 15 } };
        default:
          return widget;
      }
    });
    updateConfig({ widgets: updatedWidgets });
  };

  useEffect(() => {
    updateWidgetData();
  }, [customers, products, invoices, warehouses]);

  const getGridSize = (size: 'small' | 'medium' | 'large') => {
    switch (size) {
      case 'small': return 3;
      case 'medium': return 6;
      case 'large': return 12;
      default: return 6;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          داشبورد پیشرفته
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="فیلترها">
            <IconButton 
              onClick={() => setShowFilters(!showFilters)} 
              color={showFilters ? 'primary' : 'default'}
            >
              <FilterList />
            </IconButton>
          </Tooltip>
          <Tooltip title="تنظیمات">
            <IconButton onClick={() => setShowSettings(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
          <Tooltip title="به‌روزرسانی">
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filters */}
      {showFilters && (
        <DashboardFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onApplyFilters={handleApplyFilters}
          onResetFilters={handleResetFilters}
          onRefresh={handleRefresh}
        />
      )}

      {/* Widgets Grid */}
      <Grid container spacing={3}>
        {visibleWidgets.map((widget) => (
          <Grid 
            item 
            xs={12} 
            sm={getGridSize(widget.size) * 2} 
            md={getGridSize(widget.size)} 
            key={widget.id}
          >
            <DashboardWidget
              {...widget}
              onToggleVisibility={toggleWidgetVisibility}
              onConfigure={handleConfigureWidget}
            />
          </Grid>
        ))}
      </Grid>

      {/* Add Widget FAB */}
      <Fab
        color="primary"
        aria-label="add widget"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setShowAddWidget(true)}
      >
        <Add />
      </Fab>

      {/* Add Widget Dialog */}
      <Dialog open={showAddWidget} onClose={() => setShowAddWidget(false)}>
        <DialogTitle>افزودن ویجت جدید</DialogTitle>
        <DialogContent>
          <List>
            <ListItem button onClick={() => handleAddWidget('stat')}>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="آمار" secondary="نمایش آمار عددی" />
            </ListItem>
            <ListItem button onClick={() => handleAddWidget('chart')}>
              <ListItemIcon><TrendingUp /></ListItemIcon>
              <ListItemText primary="نمودار" secondary="نمایش نمودار خطی" />
            </ListItem>
            <ListItem button onClick={() => handleAddWidget('table')}>
              <ListItemIcon><ViewList /></ListItemIcon>
              <ListItemText primary="جدول" secondary="نمایش داده در جدول" />
            </ListItem>
            <ListItem button onClick={() => handleAddWidget('list')}>
              <ListItemIcon><Schedule /></ListItemIcon>
              <ListItemText primary="لیست" secondary="نمایش لیست فعالیت‌ها" />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddWidget(false)}>انصراف</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="md" fullWidth>
        <DialogTitle>تنظیمات داشبورد</DialogTitle>
        <DialogContent>
          <Box mb={3}>
            <Typography variant="h6" gutterBottom>چیدمان</Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={config.layout === 'grid'}
                  onChange={(e) => updateConfig({ layout: e.target.checked ? 'grid' : 'list' })}
                />
              }
              label="چیدمان شبکه‌ای"
            />
          </Box>
          
          <Box mb={3}>
            <Typography variant="h6" gutterBottom>تم</Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={config.theme === 'dark'}
                  onChange={(e) => updateConfig({ theme: e.target.checked ? 'dark' : 'light' })}
                />
              }
              label="حالت تاریک"
            />
          </Box>

          <Box mb={3}>
            <Typography variant="h6" gutterBottom>فاصله به‌روزرسانی (ثانیه)</Typography>
            <Slider
              value={config.refreshInterval / 1000}
              onChange={(_, value) => updateConfig({ refreshInterval: (value as number) * 1000 })}
              min={10}
              max={300}
              step={10}
              marks={[
                { value: 10, label: '10s' },
                { value: 60, label: '1m' },
                { value: 300, label: '5m' },
              ]}
              valueLabelDisplay="auto"
            />
          </Box>

          <Divider sx={{ my: 2 }} />
          
          <Box>
            <Typography variant="h6" gutterBottom>بازنشانی</Typography>
            <Button 
              variant="outlined" 
              color="warning" 
              onClick={resetDashboard}
              fullWidth
            >
              بازنشانی داشبورد به حالت پیش‌فرض
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;