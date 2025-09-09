import React, { useState, useEffect } from 'react';
import {
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Dashboard,
  Add,
  MoreVert,
  Refresh,
  Download,
  Share,
  Settings,
  Timeline,
  TrendingUp,
  People,
  AttachMoney,
  ShoppingCart,
} from '@mui/icons-material';
import { RevenueChart, PieChartComponent } from '../charts/RevenueChart';
import { AnimatedCard, StatCard } from '../ui/AnimatedCard';
import { FadeIn, StaggerContainer, StaggerItem } from '../animations/FadeIn';

interface DashboardWidget {
  id: string;
  type: 'chart' | 'stat' | 'table' | 'custom';
  title: string;
  position: { x: number; y: number; w: number; h: number };
  data: any;
  config: any;
}

interface InteractiveDashboardProps {
  widgets?: DashboardWidget[];
  onWidgetUpdate?: (widgets: DashboardWidget[]) => void;
}

const sampleData = {
  revenue: [
    { name: 'فروردین', revenue: 12000000, profit: 8000000, customers: 45 },
    { name: 'اردیبهشت', revenue: 15000000, profit: 10000000, customers: 52 },
    { name: 'خرداد', revenue: 18000000, profit: 12000000, customers: 61 },
    { name: 'تیر', revenue: 16000000, profit: 11000000, customers: 58 },
    { name: 'مرداد', revenue: 20000000, profit: 14000000, customers: 67 },
    { name: 'شهریور', revenue: 22000000, profit: 15000000, customers: 73 },
  ],
  pieData: [
    { name: 'مشتریان حقیقی', value: 65, color: '#2196F3' },
    { name: 'مشتریان حقوقی', value: 35, color: '#4CAF50' },
  ],
  stats: [
    {
      title: 'کل درآمد',
      value: '۲۵,۰۰۰,۰۰۰',
      subtitle: 'تومان',
      icon: <AttachMoney />,
      color: 'success' as const,
      trend: { value: 15, isPositive: true },
    },
    {
      title: 'مشتریان فعال',
      value: '۱,۲۴۷',
      subtitle: 'نفر',
      icon: <People />,
      color: 'primary' as const,
      trend: { value: 8, isPositive: true },
    },
    {
      title: 'فاکتورهای صادر شده',
      value: '۳,۴۵۶',
      subtitle: 'عدد',
      icon: <ShoppingCart />,
      color: 'secondary' as const,
      trend: { value: 12, isPositive: true },
    },
    {
      title: 'نرخ تبدیل',
      value: '۲۳.۵',
      subtitle: 'درصد',
      icon: <TrendingUp />,
      color: 'warning' as const,
      trend: { value: 5, isPositive: false },
    },
  ],
};

export const InteractiveDashboard: React.FC<InteractiveDashboardProps> = ({
  widgets = [],
  onWidgetUpdate,
}) => {
  const theme = useTheme();
  const [dashboardWidgets, setDashboardWidgets] = useState<DashboardWidget[]>(widgets);
  const [selectedWidget, setSelectedWidget] = useState<DashboardWidget | null>(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [addWidgetDialogOpen, setAddWidgetDialogOpen] = useState(false);
  const [newWidgetType, setNewWidgetType] = useState('chart');

  useEffect(() => {
    if (widgets.length === 0) {
      // Initialize with default widgets
      const defaultWidgets: DashboardWidget[] = [
        {
          id: 'revenue-chart',
          type: 'chart',
          title: 'نمودار درآمد',
          position: { x: 0, y: 0, w: 6, h: 4 },
          data: sampleData.revenue,
          config: { type: 'area', animated: true },
        },
        {
          id: 'stats-grid',
          type: 'stat',
          title: 'آمار کلی',
          position: { x: 6, y: 0, w: 6, h: 4 },
          data: sampleData.stats,
          config: {},
        },
        {
          id: 'pie-chart',
          type: 'chart',
          title: 'توزیع مشتریان',
          position: { x: 0, y: 4, w: 4, h: 3 },
          data: sampleData.pieData,
          config: { type: 'pie' },
        },
        {
          id: 'recent-activity',
          type: 'table',
          title: 'فعالیت‌های اخیر',
          position: { x: 4, y: 4, w: 8, h: 3 },
          data: [],
          config: {},
        },
      ];
      setDashboardWidgets(defaultWidgets);
    }
  }, [widgets]);

  const handleWidgetConfig = (widget: DashboardWidget) => {
    setSelectedWidget(widget);
    setConfigDialogOpen(true);
  };

  const handleAddWidget = () => {
    setAddWidgetDialogOpen(true);
  };

  const handleWidgetUpdate = (updatedWidget: DashboardWidget) => {
    const newWidgets = dashboardWidgets.map(w => 
      w.id === updatedWidget.id ? updatedWidget : w
    );
    setDashboardWidgets(newWidgets);
    onWidgetUpdate?.(newWidgets);
  };

  const handleAddNewWidget = () => {
    const newWidget: DashboardWidget = {
      id: `widget-${Date.now()}`,
      type: newWidgetType as any,
      title: 'ویجت جدید',
      position: { x: 0, y: 0, w: 4, h: 3 },
      data: {},
      config: {},
    };
    setDashboardWidgets([...dashboardWidgets, newWidget]);
    setAddWidgetDialogOpen(false);
  };

  const renderWidget = (widget: DashboardWidget) => {
    switch (widget.type) {
      case 'chart':
        if (widget.config.type === 'pie') {
          return <PieChartComponent data={widget.data} />;
        }
        return (
          <RevenueChart
            data={widget.data}
            type={widget.config.type || 'area'}
            animated={widget.config.animated}
          />
        );
      
      case 'stat':
        return (
          <Grid container spacing={2}>
            {widget.data.map((stat: any, index: number) => (
              <Grid item xs={6} key={index}>
                <StatCard
                  title={stat.title}
                  value={stat.value}
                  subtitle={stat.subtitle}
                  icon={stat.icon}
                  color={stat.color}
                  trend={stat.trend}
                />
              </Grid>
            ))}
          </Grid>
        );
      
      case 'table':
        return (
          <Box>
            <Typography variant="body2" color="text.secondary">
              جدول داده‌ها
            </Typography>
          </Box>
        );
      
      default:
        return (
          <Box>
            <Typography variant="body2" color="text.secondary">
              ویجت سفارشی
            </Typography>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <FadeIn>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
              داشبورد تعاملی
            </Typography>
            <Typography variant="body1" color="text.secondary">
              مدیریت و سفارشی‌سازی ویجت‌های داشبورد
            </Typography>
          </Box>
          
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={handleAddWidget}
              sx={{ borderRadius: 2 }}
            >
              افزودن ویجت
            </Button>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              sx={{ borderRadius: 2 }}
            >
              به‌روزرسانی
            </Button>
          </Stack>
        </Box>
      </FadeIn>

      {/* Dashboard Grid */}
      <StaggerContainer staggerDelay={0.1}>
        <Grid container spacing={3}>
          {dashboardWidgets.map((widget, index) => (
            <Grid 
              item 
              xs={12} 
              sm={widget.position.w * 2} 
              md={widget.position.w} 
              key={widget.id}
            >
              <StaggerItem>
                <AnimatedCard
                  delay={index * 0.1}
                  sx={{ height: '100%', position: 'relative' }}
                >
                  {/* Widget Header */}
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      borderBottom: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {widget.title}
                    </Typography>
                    
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small">
                        <Refresh />
                      </IconButton>
                      <IconButton size="small">
                        <Download />
                      </IconButton>
                      <IconButton size="small">
                        <Share />
                      </IconButton>
                      <IconButton 
                        size="small"
                        onClick={() => handleWidgetConfig(widget)}
                      >
                        <Settings />
                      </IconButton>
                      <IconButton size="small">
                        <MoreVert />
                      </IconButton>
                    </Stack>
                  </Box>

                  {/* Widget Content */}
                  <CardContent sx={{ p: 2 }}>
                    {renderWidget(widget)}
                  </CardContent>
                </AnimatedCard>
              </StaggerItem>
            </Grid>
          ))}
        </Grid>
      </StaggerContainer>

      {/* Add Widget Dialog */}
      <Dialog
        open={addWidgetDialogOpen}
        onClose={() => setAddWidgetDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>افزودن ویجت جدید</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>نوع ویجت</InputLabel>
            <Select
              value={newWidgetType}
              onChange={(e) => setNewWidgetType(e.target.value)}
            >
              <MenuItem value="chart">نمودار</MenuItem>
              <MenuItem value="stat">آمار</MenuItem>
              <MenuItem value="table">جدول</MenuItem>
              <MenuItem value="custom">سفارشی</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddWidgetDialogOpen(false)}>
            انصراف
          </Button>
          <Button onClick={handleAddNewWidget} variant="contained">
            افزودن
          </Button>
        </DialogActions>
      </Dialog>

      {/* Widget Config Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>تنظیمات ویجت</DialogTitle>
        <DialogContent>
          {selectedWidget && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="عنوان ویجت"
                value={selectedWidget.title}
                onChange={(e) => setSelectedWidget({
                  ...selectedWidget,
                  title: e.target.value
                })}
                sx={{ mb: 2 }}
              />
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="عرض"
                    type="number"
                    value={selectedWidget.position.w}
                    onChange={(e) => setSelectedWidget({
                      ...selectedWidget,
                      position: {
                        ...selectedWidget.position,
                        w: parseInt(e.target.value)
                      }
                    })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="ارتفاع"
                    type="number"
                    value={selectedWidget.position.h}
                    onChange={(e) => setSelectedWidget({
                      ...selectedWidget,
                      position: {
                        ...selectedWidget.position,
                        h: parseInt(e.target.value)
                      }
                    })}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>
            انصراف
          </Button>
          <Button 
            onClick={() => {
              if (selectedWidget) {
                handleWidgetUpdate(selectedWidget);
                setConfigDialogOpen(false);
              }
            }} 
            variant="contained"
          >
            ذخیره
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};