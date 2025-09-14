import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  Add,
  Search,
  FilterList,
  MoreVert,
  Edit,
  Delete,
  Visibility,
  Print,
  Email,
  Receipt,
  CheckCircle,
  Cancel,
  Schedule,
  AttachMoney,
  Download,
  Upload,
  Description,
  Person,
  CalendarToday,
  LocalShipping,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { motion } from 'framer-motion';

interface Invoice {
  id: number;
  invoice_number: string;
  customer: number;
  customer_name: string;
  invoice_date: string;
  due_date: string;
  status: string;
  payment_method: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  paid_amount: number;
  items_count: number;
  notes?: string;
}

interface InvoiceItem {
  id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  tax_rate: number;
  total: number;
}

const InvoiceList: React.FC = () => {
  const navigate = useNavigate();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDateRange, setFilterDateRange] = useState('all');
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [invoiceItems, setInvoiceItems] = useState<InvoiceItem[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/invoices/');
      setInvoices(response.data.results || []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoiceItems = async (invoiceId: number) => {
    try {
      const response = await apiService.get(`/invoices/${invoiceId}/items/`);
      setInvoiceItems(response.data || []);
    } catch (error) {
      console.error('Error fetching invoice items:', error);
    }
  };

  const handleViewDetails = async (invoice: Invoice) => {
    setSelectedInvoice(invoice);
    await fetchInvoiceItems(invoice.id);
    setDetailDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedInvoice) return;
    
    try {
      await apiService.delete(`/invoices/${selectedInvoice.id}/`);
      await fetchInvoices();
      setDeleteDialogOpen(false);
      setSelectedInvoice(null);
    } catch (error) {
      console.error('Error deleting invoice:', error);
    }
  };

  const handlePrint = (invoice: Invoice) => {
    window.open(`/invoices/${invoice.id}/print`, '_blank');
  };

  const handleEmail = (invoice: Invoice) => {
    // Send invoice via email
    console.log('Sending invoice via email:', invoice);
  };

  const getStatusColor = (status: string) => {
    const statusColors: { [key: string]: any } = {
      draft: 'default',
      pending: 'warning',
      approved: 'info',
      paid: 'success',
      cancelled: 'error',
      overdue: 'error',
    };
    return statusColors[status] || 'default';
  };

  const getStatusLabel = (status: string) => {
    const statusLabels: { [key: string]: string } = {
      draft: 'پیش‌نویس',
      pending: 'در انتظار',
      approved: 'تایید شده',
      paid: 'پرداخت شده',
      cancelled: 'لغو شده',
      overdue: 'سررسید گذشته',
    };
    return statusLabels[status] || status;
  };

  const getPaymentMethodLabel = (method: string) => {
    const methods: { [key: string]: string } = {
      cash: 'نقدی',
      credit: 'اعتباری',
      check: 'چک',
      transfer: 'حواله',
      online: 'آنلاین',
    };
    return methods[method] || method;
  };

  const columns: GridColDef[] = [
    {
      field: 'invoice_number',
      headerName: 'شماره فاکتور',
      width: 130,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          color="primary" 
          variant="outlined"
          icon={<Receipt />}
        />
      ),
    },
    {
      field: 'customer_name',
      headerName: 'مشتری',
      width: 200,
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32 }}>
            <Person />
          </Avatar>
          <Typography variant="body2">{params.value}</Typography>
        </Box>
      ),
    },
    {
      field: 'invoice_date',
      headerName: 'تاریخ فاکتور',
      width: 120,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <CalendarToday fontSize="small" color="action" />
          <Typography variant="body2">
            {new Date(params.value).toLocaleDateString('fa-IR')}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'due_date',
      headerName: 'سررسید',
      width: 120,
      renderCell: (params) => {
        const dueDate = new Date(params.value);
        const today = new Date();
        const isOverdue = dueDate < today && params.row.status !== 'paid';
        
        return (
          <Typography 
            variant="body2" 
            color={isOverdue ? 'error' : 'textPrimary'}
          >
            {dueDate.toLocaleDateString('fa-IR')}
          </Typography>
        );
      },
    },
    {
      field: 'total_amount',
      headerName: 'مبلغ کل',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {new Intl.NumberFormat('fa-IR').format(params.value)} تومان
        </Typography>
      ),
    },
    {
      field: 'payment_status',
      headerName: 'وضعیت پرداخت',
      width: 180,
      renderCell: (params: GridRenderCellParams<Invoice>) => {
        const invoice = params.row;
        const paidPercentage = (invoice.paid_amount / invoice.total_amount) * 100;
        
        return (
          <Box sx={{ width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">
                {new Intl.NumberFormat('fa-IR').format(invoice.paid_amount)} از {new Intl.NumberFormat('fa-IR').format(invoice.total_amount)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {Math.round(paidPercentage)}%
              </Typography>
            </Box>
            <Box sx={{ 
              width: '100%', 
              height: 4, 
              bgcolor: 'grey.300', 
              borderRadius: 2,
              overflow: 'hidden'
            }}>
              <Box sx={{ 
                width: `${paidPercentage}%`,
                height: '100%',
                bgcolor: paidPercentage === 100 ? 'success.main' : 'warning.main',
              }} />
            </Box>
          </Box>
        );
      },
    },
    {
      field: 'status',
      headerName: 'وضعیت',
      width: 120,
      renderCell: (params) => {
        const icons: { [key: string]: React.ReactNode } = {
          draft: <Edit fontSize="small" />,
          pending: <Schedule fontSize="small" />,
          approved: <CheckCircle fontSize="small" />,
          paid: <AttachMoney fontSize="small" />,
          cancelled: <Cancel fontSize="small" />,
        };
        
        return (
          <Chip
            label={getStatusLabel(params.value)}
            color={getStatusColor(params.value)}
            size="small"
            icon={icons[params.value] as any}
          />
        );
      },
    },
    {
      field: 'payment_method',
      headerName: 'روش پرداخت',
      width: 100,
      renderCell: (params) => (
        <Chip 
          label={getPaymentMethodLabel(params.value)} 
          size="small" 
          variant="outlined"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'عملیات',
      width: 180,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Invoice>) => (
        <Box>
          <Tooltip title="مشاهده جزئیات">
            <IconButton
              size="small"
              onClick={() => handleViewDetails(params.row)}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="چاپ">
            <IconButton
              size="small"
              onClick={() => handlePrint(params.row)}
            >
              <Print fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="ارسال ایمیل">
            <IconButton
              size="small"
              onClick={() => handleEmail(params.row)}
            >
              <Email fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="ویرایش">
            <IconButton
              size="small"
              onClick={() => navigate(`/invoices/${params.row.id}/edit`)}
              disabled={params.row.status === 'paid'}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="حذف">
            <IconButton
              size="small"
              onClick={() => {
                setSelectedInvoice(params.row);
                setDeleteDialogOpen(true);
              }}
              disabled={params.row.status === 'paid'}
            >
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = 
      invoice.invoice_number?.toLowerCase().includes(searchText.toLowerCase()) ||
      invoice.customer_name?.toLowerCase().includes(searchText.toLowerCase());
    
    const matchesStatus = 
      filterStatus === 'all' || invoice.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Summary Cards
  const summaryData = {
    total: invoices.length,
    paid: invoices.filter(i => i.status === 'paid').length,
    pending: invoices.filter(i => i.status === 'pending').length,
    totalAmount: invoices.reduce((sum, i) => sum + i.total_amount, 0),
    paidAmount: invoices.reduce((sum, i) => sum + i.paid_amount, 0),
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            مدیریت فاکتورها
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Description />}
              onClick={() => navigate('/quotations')}
            >
              پیش‌فاکتورها
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              color="primary"
            >
              گزارش Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => navigate('/invoices/new')}
            >
              فاکتور جدید
            </Button>
          </Box>
        </Box>
      </motion.div>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    کل فاکتورها
                  </Typography>
                  <Typography variant="h4">
                    {summaryData.total}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.main' }}>
                  <Receipt />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    پرداخت شده
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {summaryData.paid}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.light', color: 'success.main' }}>
                  <CheckCircle />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    در انتظار
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {summaryData.pending}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.light', color: 'warning.main' }}>
                  <Schedule />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    مجموع مبالغ
                  </Typography>
                  <Typography variant="h6">
                    {new Intl.NumberFormat('fa-IR').format(summaryData.totalAmount)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.light', color: 'info.main' }}>
                  <AttachMoney />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="جستجو در فاکتورها..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>وضعیت</InputLabel>
              <Select
                value={filterStatus}
                label="وضعیت"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="draft">پیش‌نویس</MenuItem>
                <MenuItem value="pending">در انتظار</MenuItem>
                <MenuItem value="approved">تایید شده</MenuItem>
                <MenuItem value="paid">پرداخت شده</MenuItem>
                <MenuItem value="cancelled">لغو شده</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>بازه زمانی</InputLabel>
              <Select
                value={filterDateRange}
                label="بازه زمانی"
                onChange={(e) => setFilterDateRange(e.target.value)}
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="today">امروز</MenuItem>
                <MenuItem value="week">این هفته</MenuItem>
                <MenuItem value="month">این ماه</MenuItem>
                <MenuItem value="year">امسال</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              sx={{ height: '56px' }}
            >
              فیلتر پیشرفته
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Data Grid */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={filteredInvoices}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          checkboxSelection
          disableSelectionOnClick
          loading={loading}
          localeText={{
            noRowsLabel: 'فاکتوری یافت نشد',
            footerRowSelected: (count) => `${count} فاکتور انتخاب شده`,
          }}
        />
      </Paper>

      {/* Invoice Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              جزئیات فاکتور {selectedInvoice?.invoice_number}
            </Typography>
            <Chip 
              label={getStatusLabel(selectedInvoice?.status || '')} 
              color={getStatusColor(selectedInvoice?.status || '')}
            />
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedInvoice && (
            <>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">مشتری</Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedInvoice.customer_name}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">روش پرداخت</Typography>
                  <Typography variant="body1" gutterBottom>
                    {getPaymentMethodLabel(selectedInvoice.payment_method)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">تاریخ فاکتور</Typography>
                  <Typography variant="body1" gutterBottom>
                    {new Date(selectedInvoice.invoice_date).toLocaleDateString('fa-IR')}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">تاریخ سررسید</Typography>
                  <Typography variant="body1" gutterBottom>
                    {new Date(selectedInvoice.due_date).toLocaleDateString('fa-IR')}
                  </Typography>
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom>
                اقلام فاکتور
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>محصول</TableCell>
                      <TableCell align="center">تعداد</TableCell>
                      <TableCell align="right">قیمت واحد</TableCell>
                      <TableCell align="center">تخفیف</TableCell>
                      <TableCell align="center">مالیات</TableCell>
                      <TableCell align="right">جمع</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {invoiceItems.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.product_name}</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="right">
                          {new Intl.NumberFormat('fa-IR').format(item.unit_price)}
                        </TableCell>
                        <TableCell align="center">{item.discount_percentage}%</TableCell>
                        <TableCell align="center">{item.tax_rate}%</TableCell>
                        <TableCell align="right">
                          {new Intl.NumberFormat('fa-IR').format(item.total)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ mt: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    {selectedInvoice.notes && (
                      <>
                        <Typography variant="subtitle2" color="textSecondary">
                          یادداشت
                        </Typography>
                        <Typography variant="body2">
                          {selectedInvoice.notes}
                        </Typography>
                      </>
                    )}
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <List dense>
                      <ListItem>
                        <ListItemText primary="جمع کل" />
                        <Typography>
                          {new Intl.NumberFormat('fa-IR').format(selectedInvoice.subtotal)} تومان
                        </Typography>
                      </ListItem>
                      <ListItem>
                        <ListItemText primary="تخفیف" />
                        <Typography color="error">
                          -{new Intl.NumberFormat('fa-IR').format(selectedInvoice.discount_amount)} تومان
                        </Typography>
                      </ListItem>
                      <ListItem>
                        <ListItemText primary="مالیات" />
                        <Typography>
                          {new Intl.NumberFormat('fa-IR').format(selectedInvoice.tax_amount)} تومان
                        </Typography>
                      </ListItem>
                      <Divider />
                      <ListItem>
                        <ListItemText 
                          primary={
                            <Typography variant="h6">مبلغ نهایی</Typography>
                          } 
                        />
                        <Typography variant="h6" color="primary">
                          {new Intl.NumberFormat('fa-IR').format(selectedInvoice.total_amount)} تومان
                        </Typography>
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>بستن</Button>
          <Button 
            variant="outlined" 
            startIcon={<Print />}
            onClick={() => handlePrint(selectedInvoice!)}
          >
            چاپ
          </Button>
          <Button 
            variant="contained" 
            startIcon={<Email />}
            onClick={() => handleEmail(selectedInvoice!)}
          >
            ارسال ایمیل
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>تایید حذف</DialogTitle>
        <DialogContent>
          آیا از حذف فاکتور شماره {selectedInvoice?.invoice_number} اطمینان دارید؟
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>انصراف</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            حذف
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InvoiceList;