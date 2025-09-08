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
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Print as PrintIcon,
  Settings as SettingsIcon,
  Preview as PreviewIcon,
  Download as DownloadIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Receipt as ReceiptIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';

interface PrintTemplate {
  id: number;
  name: string;
  type: 'invoice' | 'proforma' | 'receipt' | 'report' | 'label';
  format: 'A4' | 'A5' | 'A6' | 'thermal' | 'custom';
  orientation: 'portrait' | 'landscape';
  is_default: boolean;
  created_date: string;
  last_modified: string;
  description: string;
}

interface PrintJob {
  id: number;
  template_id: number;
  document_type: string;
  document_id: number;
  status: 'pending' | 'printing' | 'completed' | 'failed';
  created_date: string;
  completed_date?: string;
  error_message?: string;
}

const PrintSystem: React.FC = () => {
  const [templates, setTemplates] = useState<PrintTemplate[]>([
    {
      id: 1,
      name: 'فاکتور فروش A4',
      type: 'invoice',
      format: 'A4',
      orientation: 'portrait',
      is_default: true,
      created_date: '1402/12/01',
      last_modified: '1402/12/15',
      description: 'قالب پیش‌فرض فاکتور فروش',
    },
    {
      id: 2,
      name: 'پیش‌فاکتور A5',
      type: 'proforma',
      format: 'A5',
      orientation: 'portrait',
      is_default: false,
      created_date: '1402/12/05',
      last_modified: '1402/12/10',
      description: 'قالب پیش‌فاکتور در سایز A5',
    },
    {
      id: 3,
      name: 'رسید انبار حرارتی',
      type: 'receipt',
      format: 'thermal',
      orientation: 'portrait',
      is_default: true,
      created_date: '1402/11/20',
      last_modified: '1402/12/01',
      description: 'رسید چاپ حرارتی برای انبار',
    },
  ]);

  const [printJobs] = useState<PrintJob[]>([
    {
      id: 1,
      template_id: 1,
      document_type: 'فاکتور',
      document_id: 1001,
      status: 'completed',
      created_date: '1402/12/15 10:30',
      completed_date: '1402/12/15 10:32',
    },
    {
      id: 2,
      template_id: 2,
      document_type: 'پیش‌فاکتور',
      document_id: 2001,
      status: 'printing',
      created_date: '1402/12/15 11:15',
    },
    {
      id: 3,
      template_id: 3,
      document_type: 'رسید انبار',
      document_id: 3001,
      status: 'failed',
      created_date: '1402/12/15 11:45',
      error_message: 'خطا در اتصال به چاپگر',
    },
  ]);

  const [open, setOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PrintTemplate | null>(null);
  const [formData, setFormData] = useState<Partial<PrintTemplate>>({});

  const templateTypes = [
    { value: 'invoice', label: 'فاکتور', color: 'primary' },
    { value: 'proforma', label: 'پیش‌فاکتور', color: 'info' },
    { value: 'receipt', label: 'رسید', color: 'success' },
    { value: 'report', label: 'گزارش', color: 'warning' },
    { value: 'label', label: 'برچسب', color: 'error' },
  ];

  const getTypeLabel = (type: string) => {
    return templateTypes.find(t => t.value === type)?.label || type;
  };

  const getTypeColor = (type: string) => {
    return templateTypes.find(t => t.value === type)?.color || 'default';
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'در انتظار';
      case 'printing': return 'در حال چاپ';
      case 'completed': return 'تکمیل شده';
      case 'failed': return 'ناموفق';
      default: return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'printing': return 'info';
      case 'completed': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const handleOpen = (template?: PrintTemplate) => {
    if (template) {
      setEditingTemplate(template);
      setFormData(template);
    } else {
      setEditingTemplate(null);
      setFormData({});
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingTemplate(null);
    setFormData({});
  };

  const handleSave = () => {
    if (editingTemplate) {
      setTemplates(prev => 
        prev.map(t => t.id === editingTemplate.id ? { ...t, ...formData } : t)
      );
    } else {
      const newTemplate: PrintTemplate = {
        id: Date.now(),
        name: formData.name || '',
        type: formData.type || 'invoice',
        format: formData.format || 'A4',
        orientation: formData.orientation || 'portrait',
        is_default: formData.is_default || false,
        created_date: new Date().toLocaleDateString('fa-IR'),
        last_modified: new Date().toLocaleDateString('fa-IR'),
        description: formData.description || '',
      };
      setTemplates(prev => [...prev, newTemplate]);
    }
    handleClose();
  };

  const handleDelete = (id: number) => {
    setTemplates(prev => prev.filter(t => t.id !== id));
  };

  const handlePrint = (template: PrintTemplate) => {
    console.log('Printing with template:', template.name);
  };

  const handlePreview = (template: PrintTemplate) => {
    console.log('Previewing template:', template.name);
  };

  const handleDownload = (template: PrintTemplate) => {
    console.log('Downloading template:', template.name);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          سیستم چاپ
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          افزودن قالب
        </Button>
      </Box>

      {/* Print Templates */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">قالب‌های چاپ</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام قالب</TableCell>
                <TableCell>نوع</TableCell>
                <TableCell>فرمت</TableCell>
                <TableCell>جهت</TableCell>
                <TableCell>پیش‌فرض</TableCell>
                <TableCell>تاریخ ایجاد</TableCell>
                <TableCell>آخرین تغییر</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {templates.map((template) => (
                <TableRow key={template.id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {template.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {template.description}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getTypeLabel(template.type)}
                      color={getTypeColor(template.type) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{template.format}</TableCell>
                  <TableCell>
                    <Chip
                      label={template.orientation === 'portrait' ? 'عمودی' : 'افقی'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={template.is_default ? 'بله' : 'خیر'}
                      color={template.is_default ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{template.created_date}</TableCell>
                  <TableCell>{template.last_modified}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handlePreview(template)}
                        title="پیش‌نمایش"
                      >
                        <PreviewIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handlePrint(template)}
                        title="چاپ"
                      >
                        <PrintIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(template)}
                        title="دانلود"
                      >
                        <DownloadIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleOpen(template)}
                        title="ویرایش"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(template.id)}
                        color="error"
                        title="حذف"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Print Jobs */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">وظایف چاپ</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نوع سند</TableCell>
                <TableCell>شناسه سند</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>تاریخ ایجاد</TableCell>
                <TableCell>تاریخ تکمیل</TableCell>
                <TableCell>پیام خطا</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {printJobs.map((job) => (
                <TableRow key={job.id}>
                  <TableCell>{job.document_type}</TableCell>
                  <TableCell>{job.document_id}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(job.status)}
                      color={getStatusColor(job.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{job.created_date}</TableCell>
                  <TableCell>{job.completed_date || '-'}</TableCell>
                  <TableCell>
                    {job.error_message && (
                      <Typography variant="caption" color="error">
                        {job.error_message}
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Template Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTemplate ? 'ویرایش قالب' : 'افزودن قالب جدید'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="نام قالب"
                value={formData.name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>نوع قالب</InputLabel>
                <Select
                  value={formData.type || 'invoice'}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as any }))}
                >
                  {templateTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>فرمت</InputLabel>
                <Select
                  value={formData.format || 'A4'}
                  onChange={(e) => setFormData(prev => ({ ...prev, format: e.target.value as any }))}
                >
                  <MenuItem value="A4">A4</MenuItem>
                  <MenuItem value="A5">A5</MenuItem>
                  <MenuItem value="A6">A6</MenuItem>
                  <MenuItem value="thermal">حرارتی</MenuItem>
                  <MenuItem value="custom">سفارشی</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>جهت</InputLabel>
                <Select
                  value={formData.orientation || 'portrait'}
                  onChange={(e) => setFormData(prev => ({ ...prev, orientation: e.target.value as any }))}
                >
                  <MenuItem value="portrait">عمودی</MenuItem>
                  <MenuItem value="landscape">افقی</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="توضیحات"
                multiline
                rows={3}
                value={formData.description || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_default || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_default: e.target.checked }))}
                  />
                }
                label="قالب پیش‌فرض"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>انصراف</Button>
          <Button onClick={handleSave} variant="contained">
            {editingTemplate ? 'ویرایش' : 'افزودن'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PrintSystem;