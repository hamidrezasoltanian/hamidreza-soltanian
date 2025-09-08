import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  Divider,
} from '@mui/material';
import {
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  TableChart as TableChartIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  Email as EmailIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

interface Report {
  id: number;
  name: string;
  type: 'financial' | 'sales' | 'inventory' | 'customer' | 'tax';
  format: 'pdf' | 'excel' | 'csv';
  status: 'draft' | 'generated' | 'scheduled';
  created_date: string;
  last_run: string;
  description: string;
}

interface ReportTemplate {
  id: number;
  name: string;
  category: string;
  description: string;
  parameters: string[];
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([
    {
      id: 1,
      name: 'گزارش فروش ماهانه',
      type: 'sales',
      format: 'pdf',
      status: 'generated',
      created_date: '1402/12/01',
      last_run: '1402/12/15',
      description: 'گزارش جامع فروش ماه جاری',
    },
    {
      id: 2,
      name: 'گزارش موجودی انبار',
      type: 'inventory',
      format: 'excel',
      status: 'generated',
      created_date: '1402/12/05',
      last_run: '1402/12/10',
      description: 'لیست کامل موجودی‌های انبار',
    },
    {
      id: 3,
      name: 'گزارش مالیاتی فصلی',
      type: 'tax',
      format: 'pdf',
      status: 'scheduled',
      created_date: '1402/11/20',
      last_run: '-',
      description: 'گزارش مالیاتی سه ماهه',
    },
  ]);

  const [templates] = useState<ReportTemplate[]>([
    {
      id: 1,
      name: 'گزارش فروش',
      category: 'فروش',
      description: 'گزارش جامع فروشات',
      parameters: ['تاریخ شروع', 'تاریخ پایان', 'مشتری', 'محصول'],
    },
    {
      id: 2,
      name: 'گزارش موجودی',
      category: 'انبار',
      description: 'گزارش موجودی‌های انبار',
      parameters: ['انبار', 'دسته‌بندی', 'وضعیت'],
    },
    {
      id: 3,
      name: 'گزارش مالی',
      category: 'حسابداری',
      description: 'گزارش‌های مالی',
      parameters: ['دوره', 'حساب', 'نوع تراکنش'],
    },
  ]);

  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [reportParams, setReportParams] = useState<Record<string, string>>({});

  const reportTypes = [
    { value: 'financial', label: 'مالی', color: 'primary' },
    { value: 'sales', label: 'فروش', color: 'success' },
    { value: 'inventory', label: 'انبار', color: 'info' },
    { value: 'customer', label: 'مشتری', color: 'warning' },
    { value: 'tax', label: 'مالیاتی', color: 'error' },
  ];

  const getTypeLabel = (type: string) => {
    return reportTypes.find(t => t.value === type)?.label || type;
  };

  const getTypeColor = (type: string) => {
    return reportTypes.find(t => t.value === type)?.color || 'default';
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft': return 'پیش‌نویس';
      case 'generated': return 'تولید شده';
      case 'scheduled': return 'زمان‌بندی شده';
      default: return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'warning';
      case 'generated': return 'success';
      case 'scheduled': return 'info';
      default: return 'default';
    }
  };

  const handleGenerateReport = (template: ReportTemplate) => {
    setSelectedTemplate(template);
    setReportParams({});
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedTemplate(null);
    setReportParams({});
  };

  const handleRunReport = () => {
    if (selectedTemplate) {
      const newReport: Report = {
        id: Date.now(),
        name: selectedTemplate.name,
        type: 'sales', // Default type
        format: 'pdf',
        status: 'generated',
        created_date: new Date().toLocaleDateString('fa-IR'),
        last_run: new Date().toLocaleDateString('fa-IR'),
        description: selectedTemplate.description,
      };
      setReports(prev => [...prev, newReport]);
      handleClose();
    }
  };

  const handleDownload = (report: Report) => {
    console.log('Downloading report:', report.name);
  };

  const handlePrint = (report: Report) => {
    console.log('Printing report:', report.name);
  };

  const handleEmail = (report: Report) => {
    console.log('Emailing report:', report.name);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          سیستم گزارش‌گیری
        </Typography>
      </Box>

      {/* Report Templates */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">قالب‌های گزارش</Typography>
        </Box>
        <Box sx={{ p: 2 }}>
          <Grid container spacing={2}>
            {templates.map((template) => (
              <Grid item xs={12} sm={6} md={4} key={template.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {template.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      {template.category}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {template.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {template.parameters.map((param, index) => (
                        <Chip key={index} label={param} size="small" />
                      ))}
                    </Box>
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => handleGenerateReport(template)}
                      >
                        تولید گزارش
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Paper>

      {/* Generated Reports */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">گزارش‌های تولید شده</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام گزارش</TableCell>
                <TableCell>نوع</TableCell>
                <TableCell>فرمت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>تاریخ ایجاد</TableCell>
                <TableCell>آخرین اجرا</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {report.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {report.description}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getTypeLabel(report.type)}
                      color={getTypeColor(report.type) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={report.format.toUpperCase()}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(report.status)}
                      color={getStatusColor(report.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{report.created_date}</TableCell>
                  <TableCell>{report.last_run}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(report)}
                        title="دانلود"
                      >
                        <DownloadIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handlePrint(report)}
                        title="چاپ"
                      >
                        <PrintIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleEmail(report)}
                        title="ارسال ایمیل"
                      >
                        <EmailIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Report Generation Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          تولید گزارش: {selectedTemplate?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTemplate && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {selectedTemplate.description}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Grid container spacing={2}>
                {selectedTemplate.parameters.map((param, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <TextField
                      fullWidth
                      label={param}
                      value={reportParams[param] || ''}
                      onChange={(e) => setReportParams(prev => ({
                        ...prev,
                        [param]: e.target.value
                      }))}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>انصراف</Button>
          <Button onClick={handleRunReport} variant="contained">
            تولید گزارش
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Reports;