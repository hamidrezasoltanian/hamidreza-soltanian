import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
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
  Assessment,
  People,
  Inventory,
  ShoppingCart,
  Business,
  AccountBalance,
  Gavel,
  BarChart,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { exportService } from '../services/exportService';
import { useNotifications } from '../contexts/NotificationContext';
import ExportImport from '../components/ExportImport';

const ExportImportPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [showEntityDialog, setShowEntityDialog] = useState(false);

  const { addNotification } = useNotifications();

  const { data: statistics } = useQuery({
    queryKey: ['export-statistics'],
    queryFn: () => exportService.getExportStatistics(),
  });

  const entities = [
    {
      id: 'customers',
      name: 'مشتریان',
      icon: <People />,
      description: 'صادرات و واردات اطلاعات مشتریان',
      color: '#1976d2',
    },
    {
      id: 'products',
      name: 'محصولات',
      icon: <Inventory />,
      description: 'صادرات و واردات کاتالوگ محصولات',
      color: '#388e3c',
    },
    {
      id: 'invoices',
      name: 'فاکتورها',
      icon: <ShoppingCart />,
      description: 'صادرات و واردات فاکتورها و پیش‌فاکتورها',
      color: '#f57c00',
    },
    {
      id: 'inventory',
      name: 'انبار',
      icon: <Inventory />,
      description: 'صادرات و واردات موجودی انبار',
      color: '#9c27b0',
    },
    {
      id: 'personnel',
      name: 'پرسنل',
      icon: <Business />,
      description: 'صادرات و واردات اطلاعات پرسنل',
      color: '#795548',
    },
    {
      id: 'accounting',
      name: 'حسابداری',
      icon: <AccountBalance />,
      description: 'صادرات و واردات سندهای حسابداری',
      color: '#607d8b',
    },
    {
      id: 'tax',
      name: 'مالیات',
      icon: <Gavel />,
      description: 'صادرات و واردات اطلاعات مالیاتی',
      color: '#ff5722',
    },
    {
      id: 'reports',
      name: 'گزارش‌ها',
      icon: <BarChart />,
      description: 'صادرات و واردات گزارش‌ها',
      color: '#3f51b5',
    },
  ];

  const handleEntitySelect = (entityId: string) => {
    setSelectedEntity(entityId);
    setShowEntityDialog(true);
  };

  const handleDownloadTemplate = async (entityId: string) => {
    try {
      await exportService.downloadExportTemplate(entityId, 'excel');
      addNotification({
        title: 'قالب دانلود شد',
        message: `قالب ${entities.find(e => e.id === entityId)?.name} با موفقیت دانلود شد`,
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

  const tabs = [
    { label: 'انتخاب ماژول', value: 0 },
    { label: 'آمار کلی', value: 1 },
    { label: 'کارهای اخیر', value: 2 },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          صادرات و واردات داده‌ها
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Settings />}
          onClick={() => {
            // Open settings dialog
          }}
        >
          تنظیمات
        </Button>
      </Box>

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        {tabs.map((tab) => (
          <Tab key={tab.value} label={tab.label} />
        ))}
      </Tabs>

      {activeTab === 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            انتخاب ماژول برای صادرات/واردات
          </Typography>
          <Grid container spacing={3}>
            {entities.map((entity) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={entity.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                  onClick={() => handleEntitySelect(entity.id)}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                      <Box sx={{ color: entity.color }}>
                        {entity.icon}
                      </Box>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownloadTemplate(entity.id);
                        }}
                      >
                        <GetApp />
                      </IconButton>
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      {entity.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {entity.description}
                    </Typography>
                    <Button
                      variant="contained"
                      fullWidth
                      startIcon={<FileDownload />}
                      sx={{ backgroundColor: entity.color }}
                    >
                      شروع صادرات/واردات
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            آمار کلی صادرات و واردات
          </Typography>
          {statistics ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          کل صادرات
                        </Typography>
                        <Typography variant="h4">
                          {statistics.totalExports}
                        </Typography>
                      </Box>
                      <Download color="primary" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          صادرات موفق
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {statistics.successfulExports}
                        </Typography>
                      </Box>
                      <CheckCircle color="success" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          کل واردات
                        </Typography>
                        <Typography variant="h4">
                          {statistics.totalImports}
                        </Typography>
                      </Box>
                      <Upload color="primary" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="textSecondary" gutterBottom>
                          واردات موفق
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {statistics.successfulImports}
                        </Typography>
                      </Box>
                      <CheckCircle color="success" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <LinearProgress />
          )}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            کارهای اخیر صادرات و واردات
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            این بخش کارهای اخیر صادرات و واردات را نمایش می‌دهد
          </Alert>
        </Box>
      )}

      {/* Entity Dialog */}
      <Dialog
        open={showEntityDialog}
        onClose={() => setShowEntityDialog(false)}
        maxWidth="xl"
        fullWidth
      >
        <DialogTitle>
          صادرات و واردات {entities.find(e => e.id === selectedEntity)?.name}
        </DialogTitle>
        <DialogContent>
          {selectedEntity && (
            <ExportImport
              entity={selectedEntity}
              entityName={entities.find(e => e.id === selectedEntity)?.name || ''}
              onClose={() => setShowEntityDialog(false)}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEntityDialog(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExportImportPage;