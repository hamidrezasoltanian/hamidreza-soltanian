import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  Bar,
  BarChart,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Stack,
  IconButton,
  Menu,
  MenuItem,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  Refresh,
  Download,
  Fullscreen,
} from '@mui/icons-material';
import { FadeIn, HoverScale } from '../animations/FadeIn';

interface ChartData {
  name: string;
  value: number;
  revenue: number;
  profit: number;
  customers: number;
  color?: string;
}

interface RevenueChartProps {
  data: ChartData[];
  type?: 'line' | 'area' | 'bar';
  height?: number;
  showLegend?: boolean;
  showTooltip?: boolean;
  animated?: boolean;
}

const COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#00BCD4'];

export const RevenueChart: React.FC<RevenueChartProps> = ({
  data,
  type = 'area',
  height = 300,
  showLegend = true,
  showTooltip = true,
  animated = true,
}) => {
  const theme = useTheme();
  const [chartType, setChartType] = React.useState(type);
  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleTypeChange = (newType: 'line' | 'area' | 'bar') => {
    setChartType(newType);
    handleMenuClose();
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          elevation={8}
          sx={{
            p: 2,
            borderRadius: 2,
            background: alpha(theme.palette.background.paper, 0.95),
            backdropFilter: 'blur(10px)',
            border: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: entry.color,
                }}
              />
              <Typography variant="caption">
                {entry.name}: {entry.value.toLocaleString()}
              </Typography>
            </Box>
          ))}
        </Paper>
      );
    }
    return null;
  };

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 5 },
    };

    switch (chartType) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
            <XAxis 
              dataKey="name" 
              stroke={theme.palette.text.secondary}
              fontSize={12}
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize={12}
              tickFormatter={(value) => value.toLocaleString()}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            <Line
              type="monotone"
              dataKey="revenue"
              stroke={theme.palette.primary.main}
              strokeWidth={3}
              dot={{ fill: theme.palette.primary.main, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: theme.palette.primary.main, strokeWidth: 2 }}
              animationDuration={animated ? 1000 : 0}
            />
            <Line
              type="monotone"
              dataKey="profit"
              stroke={theme.palette.success.main}
              strokeWidth={3}
              dot={{ fill: theme.palette.success.main, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: theme.palette.success.main, strokeWidth: 2 }}
              animationDuration={animated ? 1000 : 0}
            />
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            <defs>
              <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
                <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
                <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
            <XAxis 
              dataKey="name" 
              stroke={theme.palette.text.secondary}
              fontSize={12}
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize={12}
              tickFormatter={(value) => value.toLocaleString()}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            <Area
              type="monotone"
              dataKey="revenue"
              stroke={theme.palette.primary.main}
              fill="url(#revenueGradient)"
              strokeWidth={2}
              animationDuration={animated ? 1000 : 0}
            />
            <Area
              type="monotone"
              dataKey="profit"
              stroke={theme.palette.success.main}
              fill="url(#profitGradient)"
              strokeWidth={2}
              animationDuration={animated ? 1000 : 0}
            />
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
            <XAxis 
              dataKey="name" 
              stroke={theme.palette.text.secondary}
              fontSize={12}
            />
            <YAxis 
              stroke={theme.palette.text.secondary}
              fontSize={12}
              tickFormatter={(value) => value.toLocaleString()}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            <Bar
              dataKey="revenue"
              fill={theme.palette.primary.main}
              radius={[4, 4, 0, 0]}
              animationDuration={animated ? 1000 : 0}
            />
            <Bar
              dataKey="profit"
              fill={theme.palette.success.main}
              radius={[4, 4, 0, 0]}
              animationDuration={animated ? 1000 : 0}
            />
          </BarChart>
        );

      default:
        return null;
    }
  };

  return (
    <FadeIn>
      <Paper
        elevation={0}
        sx={{
          p: 3,
          borderRadius: 3,
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              نمودار درآمد
            </Typography>
            <Stack direction="row" spacing={1}>
              <Chip
                label="12% افزایش"
                size="small"
                color="success"
                icon={<TrendingUp />}
              />
              <Chip
                label="ماه جاری"
                size="small"
                variant="outlined"
              />
            </Stack>
          </Box>
          
          <Stack direction="row" spacing={1}>
            <HoverScale>
              <IconButton size="small">
                <Refresh />
              </IconButton>
            </HoverScale>
            <HoverScale>
              <IconButton size="small">
                <Download />
              </IconButton>
            </HoverScale>
            <HoverScale>
              <IconButton size="small">
                <Fullscreen />
              </IconButton>
            </HoverScale>
            <HoverScale>
              <IconButton size="small" onClick={handleMenuOpen}>
                <MoreVert />
              </IconButton>
            </HoverScale>
          </Stack>
        </Box>

        {/* Chart */}
        <Box sx={{ height, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>

        {/* Type Selection Menu */}
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleMenuClose}
          PaperProps={{
            sx: {
              borderRadius: 2,
              minWidth: 120,
            },
          }}
        >
          <MenuItem onClick={() => handleTypeChange('line')}>
            <Typography variant="body2">خطی</Typography>
          </MenuItem>
          <MenuItem onClick={() => handleTypeChange('area')}>
            <Typography variant="body2">ناحیه‌ای</Typography>
          </MenuItem>
          <MenuItem onClick={() => handleTypeChange('bar')}>
            <Typography variant="body2">ستونی</Typography>
          </MenuItem>
        </Menu>
      </Paper>
    </FadeIn>
  );
};

export const PieChartComponent: React.FC<{ data: ChartData[]; height?: number }> = ({
  data,
  height = 300,
}) => {
  const theme = useTheme();

  return (
    <FadeIn>
      <Paper
        elevation={0}
        sx={{
          p: 3,
          borderRadius: 3,
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
          توزیع فروش
        </Typography>
        
        <Box sx={{ height, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                animationDuration={1000}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    </FadeIn>
  );
};