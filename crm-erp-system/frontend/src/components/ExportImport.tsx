import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Checkbox,
  FormControlLabel,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Download,
  Upload,
  FileDownload,
  FileUpload,
  CheckCircle,
  Error,
  Warning,
  Info,
  Delete,
  Refresh,
  Settings,
  Visibility,
  GetApp,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { exportService, ExportOptions, ImportOptions, ExportJob, ImportJob } from '../services/exportService';
import { useNotifications } from '../contexts/NotificationContext';

interface ExportImportProps {
  entity: string;
  entityName: string;
  onClose?: () => void;
}

const throwError = (message: string): never => {
  throw (Error as any)(message);
};

const ExportImport: React.FC<ExportImportProps> = ({ entity, entityName, onClose }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'excel',
    fields: [],
    filters: {},
  });
  const [importOptions, setImportOptions] = useState<ImportOptions>({
    format: 'excel',
    mapping: {},
    skipErrors: false,
    updateExisting: false,
    validateData: true,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showJobsDialog, setShowJobsDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { addNotification } = useNotifications();
  const queryClient = useQueryClient();

  // Queries
  const { data: fieldMapping } = useQuery({
    queryKey: ['field-mapping', entity],
    queryFn: () => exportService.getFieldMapping(entity),
  });

  const { data: exportJobs } = useQuery({
    queryKey: ['export-jobs'],
    queryFn: () => exportService.getExportJobs(),
    refetchInterval: 5000,
  });

  const { data: importJobs } = useQuery({
    queryKey: ['import-jobs'],
    queryFn: () => exportService.getImportJobs(),
    refetchInterval: 5000,
  });

  const { data: statistics } = useQuery({
    queryKey: ['export-statistics'],
    queryFn: () => exportService.getExportStatistics(),
  });

  // Mutations
  const exportMutation = useMutation({
    mutationFn: async (options: ExportOptions) => {
      switch (entity) {
        case 'customers': return await exportService.exportCustomers(options);
        case 'products': return await exportService.exportProducts(options);
        case 'invoices': return await exportService.exportInvoices(options);
        case 'inventory': return await exportService.exportInventory(options);
        case 'personnel': return await exportService.exportPersonnel(options);
        case 'accounting': return await exportService.exportAccounting(options);
        case 'tax': return await exportService.exportTax(options);
        case 'reports': return await exportService.exportReports(options);
        default: 
          throwError('Unknown entity');
      }
    },
    onSuccess: (job) => {
      addNotification({
        title: 'صادرات شروع شد',
        message: `صادرات ${entityName} با موفقیت شروع شد`,
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
      queryClient.invalidateQueries({ queryKey: ['export-jobs'] });
    },
    onError: (error: any) => {
      addNotification({
        title: 'خطا در صادرات',
        message: error.response?.data?.message || 'خطایی در صادرات رخ داد',
        type: 'error',
        category: 'system',
        priority: 'high',
      });
    },
  });

  const importMutation = useMutation({
    mutationFn: async ({ file, options }: { file: File; options: ImportOptions }) => {
      switch (entity) {
        case 'customers': return await exportService.importCustomers(file, options);
        case 'products': return await exportService.importProducts(file, options);
        case 'invoices': return await exportService.importInvoices(file, options);
        case 'inventory': return await exportService.importInventory(file, options);
        default: 
          throwError('Import not supported for this entity');
      }
    },
    onSuccess: (job) => {
      addNotification({
        title: 'واردات شروع شد',
        message: `واردات ${entityName} با موفقیت شروع شد`,
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
      queryClient.invalidateQueries({ queryKey: ['import-jobs'] });
    },
    onError: (error: any) => {
      addNotification({
        title: 'خطا در واردات',
        message: error.response?.data?.message || 'خطایی در واردات رخ داد',
        type: 'error',
        category: 'system',
        priority: 'high',
      });
    },
  });

  const handleExport = () => {
    exportMutation.mutate(exportOptions);
    setShowExportDialog(false);
  };

  const handleImport = () => {
    if (selectedFile) {
      importMutation.mutate({ file: selectedFile, options: importOptions });
      setShowImportDialog(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      await exportService.downloadExportTemplate(entity, exportOptions.format);
      addNotification({
        title: 'قالب دانلود شد',
        message: `قالب ${entityName} با موفقیت دانلود شد`,
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
    } catch (error) {
      addNotification({
        title: 'خطا در دانلود قالب',
        message: 'خطایی در دانلود قالب رخ داد',
        type: 'error',
        category: 'system',
        priority: 'high',
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'failed': return <Error color="error" />;
      case 'processing': return <Refresh color="info" />;
      case 'pending': return <Warning color="warning" />;
      default: return <Info />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'info';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const steps = [
    {
      label: 'انتخاب نوع عملیات',
      content: (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  صادرات داده‌ها
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  داده‌های {entityName} را در فرمت‌های مختلف صادر کنید
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Download />}
                  onClick={() => setShowExportDialog(true)}
                  fullWidth
                >
                  شروع صادرات
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  واردات داده‌ها
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  داده‌های {entityName} را از فایل وارد کنید
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Upload />}
                  onClick={() => setShowImportDialog(true)}
                  fullWidth
                >
                  شروع واردات
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ),
    },
    {
      label: 'مدیریت کارها',
      content: (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">کارهای صادرات و واردات</Typography>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['export-jobs'] });
                queryClient.invalidateQueries({ queryKey: ['import-jobs'] });
              }}
            >
              به‌روزرسانی
            </Button>
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>کارهای صادرات</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>وضعیت</TableCell>
                      <TableCell>فرمت</TableCell>
                      <TableCell>تاریخ</TableCell>
                      <TableCell>عملیات</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {exportJobs?.slice(0, 5).map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(job.status)}
                            label={job.status}
                            color={getStatusColor(job.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{job.downloadUrl ? 'Excel' : 'Unknown'}</TableCell>
                        <TableCell>
                          {new Date(job.createdAt).toLocaleString('fa-IR')}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>کارهای واردات</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>وضعیت</TableCell>
                      <TableCell>رکوردها</TableCell>
                      <TableCell>تاریخ</TableCell>
                      <TableCell>عملیات</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {importJobs?.slice(0, 5).map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(job.status)}
                            label={job.status}
                            color={getStatusColor(job.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {job.processedRecords}/{job.totalRecords}
                        </TableCell>
                        <TableCell>
                          {new Date(job.createdAt).toLocaleString('fa-IR')}
                        </TableCell>
                        <TableCell>
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </Box>
      ),
    },
    {
      label: 'آمار و گزارش‌ها',
      content: (
        <Box>
          <Typography variant="h6" gutterBottom>آمار صادرات و واردات</Typography>
          {statistics && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      کل صادرات
                    </Typography>
                    <Typography variant="h4">
                      {statistics.totalExports}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      صادرات موفق
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {statistics.successfulExports}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      کل واردات
                    </Typography>
                    <Typography variant="h4">
                      {statistics.totalImports}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      واردات موفق
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {statistics.successfulImports}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          صادرات و واردات {entityName}
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => setShowSettingsDialog(true)}
          >
            تنظیمات
          </Button>
          <Button
            variant="outlined"
            startIcon={<GetApp />}
            onClick={handleDownloadTemplate}
          >
            دانلود قالب
          </Button>
        </Box>
      </Box>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label}>
            <StepLabel>{step.label}</StepLabel>
            <StepContent>
              {step.content}
              <Box sx={{ mb: 2 }}>
                <div>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(index + 1)}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {index === steps.length - 1 ? 'پایان' : 'ادامه'}
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={() => setActiveStep(index - 1)}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    قبلی
                  </Button>
                </div>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>

      {/* Export Dialog */}
      <Dialog open={showExportDialog} onClose={() => setShowExportDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>تنظیمات صادرات</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>فرمت فایل</InputLabel>
                <Select
                  value={exportOptions.format}
                  onChange={(e) => setExportOptions(prev => ({ ...prev, format: e.target.value as any }))}
                  label="فرمت فایل"
                >
                  <MenuItem value="excel">Excel (.xlsx)</MenuItem>
                  <MenuItem value="csv">CSV (.csv)</MenuItem>
                  <MenuItem value="pdf">PDF (.pdf)</MenuItem>
                  <MenuItem value="json">JSON (.json)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>فیلدها</InputLabel>
                <Select
                  multiple
                  value={exportOptions.fields}
                  onChange={(e) => setExportOptions(prev => ({ ...prev, fields: e.target.value as string[] }))}
                  label="فیلدها"
                >
                  {fieldMapping && Object.keys(fieldMapping).map((field) => (
                    <MenuItem key={field} value={field}>
                      {field}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExportDialog(false)}>انصراف</Button>
          <Button variant="contained" onClick={handleExport}>
            شروع صادرات
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={showImportDialog} onClose={() => setShowImportDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>تنظیمات واردات</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<FileUpload />}
                fullWidth
                sx={{ py: 2 }}
              >
                انتخاب فایل
                <input
                  ref={fileInputRef}
                  type="file"
                  hidden
                  accept=".xlsx,.csv,.json"
                  onChange={handleFileSelect}
                />
              </Button>
              {selectedFile && (
                <Alert severity="info" sx={{ mt: 1 }}>
                  فایل انتخاب شده: {selectedFile.name}
                </Alert>
              )}
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>فرمت فایل</InputLabel>
                <Select
                  value={importOptions.format}
                  onChange={(e) => setImportOptions(prev => ({ ...prev, format: e.target.value as any }))}
                  label="فرمت فایل"
                >
                  <MenuItem value="excel">Excel (.xlsx)</MenuItem>
                  <MenuItem value="csv">CSV (.csv)</MenuItem>
                  <MenuItem value="json">JSON (.json)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={importOptions.skipErrors}
                    onChange={(e) => setImportOptions(prev => ({ ...prev, skipErrors: e.target.checked }))}
                  />
                }
                label="رد کردن خطاها"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={importOptions.updateExisting}
                    onChange={(e) => setImportOptions(prev => ({ ...prev, updateExisting: e.target.checked }))}
                  />
                }
                label="به‌روزرسانی رکوردهای موجود"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={importOptions.validateData}
                    onChange={(e) => setImportOptions(prev => ({ ...prev, validateData: e.target.checked }))}
                  />
                }
                label="اعتبارسنجی داده‌ها"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowImportDialog(false)}>انصراف</Button>
          <Button 
            variant="contained" 
            onClick={handleImport}
            disabled={!selectedFile}
          >
            شروع واردات
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={showSettingsDialog} onClose={() => setShowSettingsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>تنظیمات صادرات و واردات</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary">
            تنظیمات پیشرفته صادرات و واردات در اینجا قرار می‌گیرد
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettingsDialog(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExportImport;