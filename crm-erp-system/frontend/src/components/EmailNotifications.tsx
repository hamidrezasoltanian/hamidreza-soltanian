import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Email,
  Send,
  Schedule,
  Refresh,
  Delete,
  Edit,
  Visibility,
  CheckCircle,
  Error,
  Warning,
  Info,
  Add,
  FilterList,
  Search,
  Download,
  Upload,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { emailService, EmailNotification, EmailTemplate } from '../services/emailService';
import { useNotifications } from '../contexts/NotificationContext';

interface EmailNotificationsProps {
  onClose?: () => void;
}

const EmailNotifications: React.FC<EmailNotificationsProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedEmail, setSelectedEmail] = useState<EmailNotification | null>(null);
  const [showSendDialog, setShowSendDialog] = useState(false);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  const { addNotification } = useNotifications();
  const queryClient = useQueryClient();

  // Queries
  const { data: emails, isLoading: emailsLoading } = useQuery({
    queryKey: ['emails', { status: statusFilter, priority: priorityFilter, search: searchTerm }],
    queryFn: () => emailService.getNotifications({
      status: statusFilter !== 'all' ? statusFilter : undefined,
      priority: priorityFilter !== 'all' ? priorityFilter : undefined,
    }),
  });

  const { data: templates } = useQuery({
    queryKey: ['email-templates'],
    queryFn: () => emailService.getTemplates(),
  });

  const { data: queueStatus } = useQuery({
    queryKey: ['email-queue-status'],
    queryFn: () => emailService.getQueueStatus(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Mutations
  const sendEmailMutation = useMutation({
    mutationFn: emailService.sendEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      addNotification({
        title: 'ایمیل ارسال شد',
        message: 'ایمیل با موفقیت ارسال شد',
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
    },
    onError: (error: any) => {
      addNotification({
        title: 'خطا در ارسال ایمیل',
        message: error.response?.data?.message || 'خطایی در ارسال ایمیل رخ داد',
        type: 'error',
        category: 'system',
        priority: 'high',
      });
    },
  });

  const retryEmailMutation = useMutation({
    mutationFn: emailService.retryEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      addNotification({
        title: 'ایمیل مجدداً ارسال شد',
        message: 'ایمیل با موفقیت مجدداً ارسال شد',
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
    },
  });

  const deleteEmailMutation = useMutation({
    mutationFn: emailService.cancelEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      addNotification({
        title: 'ایمیل حذف شد',
        message: 'ایمیل با موفقیت حذف شد',
        type: 'success',
        category: 'system',
        priority: 'medium',
      });
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent': return 'success';
      case 'delivered': return 'success';
      case 'opened': return 'info';
      case 'clicked': return 'info';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent': return <CheckCircle />;
      case 'delivered': return <CheckCircle />;
      case 'opened': return <Visibility />;
      case 'clicked': return <Visibility />;
      case 'failed': return <Error />;
      case 'pending': return <Schedule />;
      default: return <Info />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'normal': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const filteredEmails = emails?.results?.filter(email => {
    const matchesSearch = searchTerm === '' || 
      email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      email.to.some(email => email.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  }) || [];

  const tabs = [
    { label: 'همه', value: 0 },
    { label: 'ارسال شده', value: 1 },
    { label: 'در انتظار', value: 2 },
    { label: 'ناموفق', value: 3 },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    // Update filters based on tab
    switch (newValue) {
      case 0: setStatusFilter('all'); break;
      case 1: setStatusFilter('sent'); break;
      case 2: setStatusFilter('pending'); break;
      case 3: setStatusFilter('failed'); break;
    }
  };

  const handleRetryEmail = (id: string) => {
    retryEmailMutation.mutate(id);
  };

  const handleDeleteEmail = (id: string) => {
    if (window.confirm('آیا مطمئن هستید که می‌خواهید این ایمیل را حذف کنید؟')) {
      deleteEmailMutation.mutate(id);
    }
  };

  const handleViewDetails = (email: EmailNotification) => {
    setSelectedEmail(email);
    setShowDetailsDialog(true);
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">مدیریت ایمیل‌ها</Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowSendDialog(true)}
          >
            ارسال ایمیل جدید
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => queryClient.invalidateQueries({ queryKey: ['emails'] })}
          >
            به‌روزرسانی
          </Button>
        </Box>
      </Box>

      {/* Queue Status */}
      {queueStatus && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>وضعیت صف ایمیل</Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {queueStatus.pending}
                  </Typography>
                  <Typography variant="body2">در انتظار</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="info.main">
                    {queueStatus.processing}
                  </Typography>
                  <Typography variant="body2">در حال پردازش</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error.main">
                    {queueStatus.failed}
                  </Typography>
                  <Typography variant="body2">ناموفق</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main">
                    {queueStatus.total}
                  </Typography>
                  <Typography variant="body2">کل</Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="جستجو در ایمیل‌ها..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>وضعیت</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="وضعیت"
                >
                  <MenuItem value="all">همه</MenuItem>
                  <MenuItem value="pending">در انتظار</MenuItem>
                  <MenuItem value="sent">ارسال شده</MenuItem>
                  <MenuItem value="delivered">تحویل داده شده</MenuItem>
                  <MenuItem value="opened">باز شده</MenuItem>
                  <MenuItem value="clicked">کلیک شده</MenuItem>
                  <MenuItem value="failed">ناموفق</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>اولویت</InputLabel>
                <Select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  label="اولویت"
                >
                  <MenuItem value="all">همه</MenuItem>
                  <MenuItem value="urgent">فوری</MenuItem>
                  <MenuItem value="high">بالا</MenuItem>
                  <MenuItem value="normal">عادی</MenuItem>
                  <MenuItem value="low">پایین</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setPriorityFilter('all');
                }}
              >
                پاک کردن
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        {tabs.map((tab) => (
          <Tab key={tab.value} label={tab.label} />
        ))}
      </Tabs>

      {/* Emails Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>گیرنده</TableCell>
                <TableCell>موضوع</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>اولویت</TableCell>
                <TableCell>تاریخ ارسال</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {emailsLoading ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <LinearProgress />
                  </TableCell>
                </TableRow>
              ) : filteredEmails.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="textSecondary">
                      هیچ ایمیلی یافت نشد
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredEmails.map((email) => (
                  <TableRow key={email.id}>
                    <TableCell>
                      <Typography variant="body2">
                        {email.to.join(', ')}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={email.status === 'pending' ? 600 : 400}>
                        {email.subject}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(email.status)}
                        label={email.status}
                        color={getStatusColor(email.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={email.priority}
                        color={getPriorityColor(email.priority) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {email.sentAt ? new Date(email.sentAt).toLocaleString('fa-IR') : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="مشاهده جزئیات">
                          <IconButton
                            size="small"
                            onClick={() => handleViewDetails(email)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {email.status === 'failed' && (
                          <Tooltip title="تلاش مجدد">
                            <IconButton
                              size="small"
                              onClick={() => handleRetryEmail(email.id)}
                              disabled={retryEmailMutation.isPending}
                            >
                              <Refresh />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="حذف">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteEmail(email.id)}
                            disabled={deleteEmailMutation.isPending}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onClose={() => setShowDetailsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>جزئیات ایمیل</DialogTitle>
        <DialogContent>
          {selectedEmail && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>گیرنده:</Typography>
                  <Typography variant="body2">{selectedEmail.to.join(', ')}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>موضوع:</Typography>
                  <Typography variant="body2">{selectedEmail.subject}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>وضعیت:</Typography>
                  <Chip
                    icon={getStatusIcon(selectedEmail.status)}
                    label={selectedEmail.status}
                    color={getStatusColor(selectedEmail.status) as any}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>اولویت:</Typography>
                  <Chip
                    label={selectedEmail.priority}
                    color={getPriorityColor(selectedEmail.priority) as any}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>متن ایمیل:</Typography>
                  <Box
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      p: 2,
                      maxHeight: 300,
                      overflow: 'auto',
                    }}
                  >
                    <div dangerouslySetInnerHTML={{ __html: selectedEmail.body }} />
                  </Box>
                </Grid>
                {selectedEmail.errorMessage && (
                  <Grid item xs={12}>
                    <Alert severity="error">
                      <Typography variant="subtitle2">خطا:</Typography>
                      <Typography variant="body2">{selectedEmail.errorMessage}</Typography>
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDetailsDialog(false)}>بستن</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailNotifications;