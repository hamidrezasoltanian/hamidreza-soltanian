import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
} from '@mui/material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  RadialBarChart,
  RadialBar,
  ScatterChart,
  Scatter,
  ComposedChart,
} from 'recharts';

interface ChartProps {
  title: string;
  data: any[];
  type: 'line' | 'area' | 'bar' | 'pie' | 'radial' | 'scatter' | 'composed';
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  colorScheme?: string[];
}

const AdvancedChart: React.FC<ChartProps> = ({
  title,
  data,
  type,
  height = 300,
  showLegend = true,
  showGrid = true,
  colorScheme = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00'],
}) => {
  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            <RechartsTooltip />
            {showLegend && <Legend />}
            <Line type="monotone" dataKey="value" stroke={colorScheme[0]} strokeWidth={2} />
            <Line type="monotone" dataKey="value2" stroke={colorScheme[1]} strokeWidth={2} />
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            <RechartsTooltip />
            {showLegend && <Legend />}
            <Area type="monotone" dataKey="value" stackId="1" stroke={colorScheme[0]} fill={colorScheme[0]} />
            <Area type="monotone" dataKey="value2" stackId="1" stroke={colorScheme[1]} fill={colorScheme[1]} />
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            <RechartsTooltip />
            {showLegend && <Legend />}
            <Bar dataKey="value" fill={colorScheme[0]} />
            <Bar dataKey="value2" fill={colorScheme[1]} />
          </BarChart>
        );

      case 'pie':
        return (
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
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colorScheme[index % colorScheme.length]} />
              ))}
            </Pie>
            <RechartsTooltip />
            {showLegend && <Legend />}
          </PieChart>
        );

      case 'radial':
        return (
          <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" data={data}>
            <RadialBar dataKey="value" />
            <RechartsTooltip />
            {showLegend && <Legend />}
          </RadialBarChart>
        );

      case 'scatter':
        return (
          <ScatterChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="x" />
            <YAxis dataKey="y" />
            <RechartsTooltip />
            {showLegend && <Legend />}
            <Scatter dataKey="value" fill={colorScheme[0]} />
          </ScatterChart>
        );

      case 'composed':
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            <RechartsTooltip />
            {showLegend && <Legend />}
            <Bar dataKey="value" fill={colorScheme[0]} />
            <Line type="monotone" dataKey="value2" stroke={colorScheme[1]} strokeWidth={2} />
          </ComposedChart>
        );

      default:
        return <LineChart {...commonProps}><Line dataKey="value" /></LineChart>;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box height={height}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

// Sample data generators
export const generateSalesData = () => [
  { name: 'فروردین', value: 4000, value2: 2400, x: 1, y: 4000 },
  { name: 'اردیبهشت', value: 3000, value2: 1398, x: 2, y: 3000 },
  { name: 'خرداد', value: 2000, value2: 9800, x: 3, y: 2000 },
  { name: 'تیر', value: 2780, value2: 3908, x: 4, y: 2780 },
  { name: 'مرداد', value: 1890, value2: 4800, x: 5, y: 1890 },
  { name: 'شهریور', value: 2390, value2: 3800, x: 6, y: 2390 },
];

export const generateCategoryData = () => [
  { name: 'الکترونیک', value: 400, color: '#0088FE' },
  { name: 'پوشاک', value: 300, color: '#00C49F' },
  { name: 'کتاب', value: 300, color: '#FFBB28' },
  { name: 'ورزشی', value: 200, color: '#FF8042' },
  { name: 'خانگی', value: 150, color: '#8884d8' },
];

export const generatePerformanceData = () => [
  { name: 'Q1', value: 85, value2: 78 },
  { name: 'Q2', value: 92, value2: 85 },
  { name: 'Q3', value: 88, value2: 90 },
  { name: 'Q4', value: 95, value2: 88 },
];

// Chart Collection Component
export const ChartCollection: React.FC = () => {
  const [selectedChart, setSelectedChart] = React.useState('line');

  const charts = [
    { value: 'line', label: 'نمودار خطی' },
    { value: 'area', label: 'نمودار منطقه‌ای' },
    { value: 'bar', label: 'نمودار ستونی' },
    { value: 'pie', label: 'نمودار دایره‌ای' },
    { value: 'radial', label: 'نمودار شعاعی' },
    { value: 'scatter', label: 'نمودار پراکندگی' },
    { value: 'composed', label: 'نمودار ترکیبی' },
  ];

  const getDataForChart = (chartType: string) => {
    switch (chartType) {
      case 'pie':
      case 'radial':
        return generateCategoryData();
      case 'scatter':
        return generateSalesData();
      default:
        return generateSalesData();
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">مجموعه نمودارهای پیشرفته</Typography>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>نوع نمودار</InputLabel>
          <Select
            value={selectedChart}
            onChange={(e) => setSelectedChart(e.target.value)}
            label="نوع نمودار"
          >
            {charts.map((chart) => (
              <MenuItem key={chart.value} value={chart.value}>
                {chart.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <AdvancedChart
            title="نمودار فروش ماهانه"
            data={getDataForChart(selectedChart)}
            type={selectedChart as any}
            height={400}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Box display="flex" flexDirection="column" gap={2}>
            <Typography variant="h6">نمودارهای موجود</Typography>
            {charts.map((chart) => (
              <Chip
                key={chart.value}
                label={chart.label}
                clickable
                color={selectedChart === chart.value ? 'primary' : 'default'}
                onClick={() => setSelectedChart(chart.value)}
              />
            ))}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedChart;