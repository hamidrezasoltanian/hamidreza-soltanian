import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Slider,
} from '@mui/material';
import {
  ExpandMore,
  FilterList,
  Clear,
  DateRange,
  TrendingUp,
  TrendingDown,
  Refresh,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { faIR } from 'date-fns/locale';

export interface FilterOptions {
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  category: string[];
  status: string[];
  amountRange: [number, number];
  trend: 'all' | 'up' | 'down';
  showZeroValues: boolean;
  groupBy: 'none' | 'category' | 'status' | 'date';
}

interface DashboardFiltersProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  onApplyFilters: () => void;
  onResetFilters: () => void;
  onRefresh: () => void;
}

const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  filters,
  onFiltersChange,
  onApplyFilters,
  onResetFilters,
  onRefresh,
}) => {
  const [expanded, setExpanded] = useState(false);

  const handleDateRangeChange = (field: 'start' | 'end', value: Date | null) => {
    onFiltersChange({
      ...filters,
      dateRange: {
        ...filters.dateRange,
        [field]: value,
      },
    });
  };

  const handlePeriodChange = (period: 'daily' | 'weekly' | 'monthly' | 'yearly') => {
    onFiltersChange({
      ...filters,
      period,
    });
  };

  const handleCategoryChange = (category: string) => {
    const newCategories = filters.category.includes(category)
      ? filters.category.filter(c => c !== category)
      : [...filters.category, category];
    
    onFiltersChange({
      ...filters,
      category: newCategories,
    });
  };

  const handleStatusChange = (status: string) => {
    const newStatuses = filters.status.includes(status)
      ? filters.status.filter(s => s !== status)
      : [...filters.status, status];
    
    onFiltersChange({
      ...filters,
      status: newStatuses,
    });
  };

  const handleAmountRangeChange = (value: number | number[]) => {
    onFiltersChange({
      ...filters,
      amountRange: value as [number, number],
    });
  };

  const handleTrendChange = (trend: 'all' | 'up' | 'down') => {
    onFiltersChange({
      ...filters,
      trend,
    });
  };

  const handleShowZeroValuesChange = (show: boolean) => {
    onFiltersChange({
      ...filters,
      showZeroValues: show,
    });
  };

  const handleGroupByChange = (groupBy: 'none' | 'category' | 'status' | 'date') => {
    onFiltersChange({
      ...filters,
      groupBy,
    });
  };

  const categories = ['الکترونیک', 'پوشاک', 'کتاب', 'ورزشی', 'خانگی', 'اداری'];
  const statuses = ['فعال', 'غیرفعال', 'در انتظار', 'تایید شده', 'رد شده'];

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.dateRange.start || filters.dateRange.end) count++;
    if (filters.period !== 'monthly') count++;
    if (filters.category.length > 0) count++;
    if (filters.status.length > 0) count++;
    if (filters.amountRange[0] > 0 || filters.amountRange[1] < 1000000) count++;
    if (filters.trend !== 'all') count++;
    if (!filters.showZeroValues) count++;
    if (filters.groupBy !== 'none') count++;
    return count;
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={faIR as any}>
      <Paper sx={{ mb: 3 }}>
        <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center" width="100%">
              <FilterList sx={{ mr: 1 }} />
              <Typography variant="h6">فیلترها و تنظیمات</Typography>
              {getActiveFiltersCount() > 0 && (
                <Chip
                  label={getActiveFiltersCount()}
                  color="primary"
                  size="small"
                  sx={{ ml: 2 }}
                />
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Date Range */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  بازه زمانی
                </Typography>
                <Box display="flex" gap={2}>
                  <DatePicker
                    label="از تاریخ"
                    value={filters.dateRange.start}
                    onChange={(value) => handleDateRangeChange('start', value)}
                    slotProps={{ textField: { size: 'small', fullWidth: true } }}
                  />
                  <DatePicker
                    label="تا تاریخ"
                    value={filters.dateRange.end}
                    onChange={(value) => handleDateRangeChange('end', value)}
                    slotProps={{ textField: { size: 'small', fullWidth: true } }}
                  />
                </Box>
              </Grid>

              {/* Period */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>دوره</InputLabel>
                  <Select
                    value={filters.period}
                    onChange={(e) => handlePeriodChange(e.target.value as any)}
                    label="دوره"
                  >
                    <MenuItem value="daily">روزانه</MenuItem>
                    <MenuItem value="weekly">هفتگی</MenuItem>
                    <MenuItem value="monthly">ماهانه</MenuItem>
                    <MenuItem value="yearly">سالانه</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* Categories */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  دسته‌بندی
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {categories.map((category) => (
                    <Chip
                      key={category}
                      label={category}
                      clickable
                      color={filters.category.includes(category) ? 'primary' : 'default'}
                      onClick={() => handleCategoryChange(category)}
                      size="small"
                    />
                  ))}
                </Box>
              </Grid>

              {/* Status */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  وضعیت
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {statuses.map((status) => (
                    <Chip
                      key={status}
                      label={status}
                      clickable
                      color={filters.status.includes(status) ? 'primary' : 'default'}
                      onClick={() => handleStatusChange(status)}
                      size="small"
                    />
                  ))}
                </Box>
              </Grid>

              {/* Amount Range */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  محدوده مبلغ (تومان)
                </Typography>
                <Box px={2}>
                  <Slider
                    value={filters.amountRange}
                    onChange={(_, value) => handleAmountRangeChange(value)}
                    valueLabelDisplay="auto"
                    min={0}
                    max={10000000}
                    step={100000}
                    valueLabelFormat={(value) => `${value.toLocaleString('fa-IR')}`}
                  />
                  <Box display="flex" justifyContent="space-between" mt={1}>
                    <Typography variant="caption">
                      {filters.amountRange[0].toLocaleString('fa-IR')}
                    </Typography>
                    <Typography variant="caption">
                      {filters.amountRange[1].toLocaleString('fa-IR')}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Trend */}
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  روند
                </Typography>
                <Box display="flex" gap={1}>
                  <Button
                    variant={filters.trend === 'all' ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => handleTrendChange('all')}
                  >
                    همه
                  </Button>
                  <Button
                    variant={filters.trend === 'up' ? 'contained' : 'outlined'}
                    size="small"
                    startIcon={<TrendingUp />}
                    onClick={() => handleTrendChange('up')}
                  >
                    صعودی
                  </Button>
                  <Button
                    variant={filters.trend === 'down' ? 'contained' : 'outlined'}
                    size="small"
                    startIcon={<TrendingDown />}
                    onClick={() => handleTrendChange('down')}
                  >
                    نزولی
                  </Button>
                </Box>
              </Grid>

              {/* Group By */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>گروه‌بندی</InputLabel>
                  <Select
                    value={filters.groupBy}
                    onChange={(e) => handleGroupByChange(e.target.value as any)}
                    label="گروه‌بندی"
                  >
                    <MenuItem value="none">بدون گروه‌بندی</MenuItem>
                    <MenuItem value="category">بر اساس دسته</MenuItem>
                    <MenuItem value="status">بر اساس وضعیت</MenuItem>
                    <MenuItem value="date">بر اساس تاریخ</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* Options */}
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={filters.showZeroValues}
                      onChange={(e) => handleShowZeroValuesChange(e.target.checked)}
                    />
                  }
                  label="نمایش مقادیر صفر"
                />
              </Grid>

              {/* Action Buttons */}
              <Grid item xs={12}>
                <Box display="flex" gap={2} justifyContent="flex-end">
                  <Button
                    variant="outlined"
                    startIcon={<Clear />}
                    onClick={onResetFilters}
                  >
                    پاک کردن
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={onRefresh}
                  >
                    به‌روزرسانی
                  </Button>
                  <Button
                    variant="contained"
                    onClick={onApplyFilters}
                  >
                    اعمال فیلتر
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      </Paper>
    </LocalizationProvider>
  );
};

export default DashboardFilters;