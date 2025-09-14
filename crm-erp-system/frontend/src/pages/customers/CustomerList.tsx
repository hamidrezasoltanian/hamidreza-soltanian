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
  Phone,
  Email,
  Business,
  Person,
  Download,
  Upload,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { motion } from 'framer-motion';

interface Customer {
  id: number;
  customer_code: string;
  customer_type: 'individual' | 'legal';
  first_name: string;
  last_name: string;
  company_name?: string;
  national_id: string;
  phone_number?: string;
  mobile_number: string;
  email?: string;
  address: string;
  city: string;
  state: string;
  credit_limit: number;
  status: string;
}

const CustomerList: React.FC = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/customers/');
      setCustomers(response.data.results || []);
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedCustomer) return;
    
    try {
      await apiService.delete(`/customers/${selectedCustomer.id}/`);
      await fetchCustomers();
      setDeleteDialogOpen(false);
      setSelectedCustomer(null);
    } catch (error) {
      console.error('Error deleting customer:', error);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, customer: Customer) => {
    setAnchorEl(event.currentTarget);
    setSelectedCustomer(customer);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const columns: GridColDef[] = [
    {
      field: 'customer_code',
      headerName: 'کد مشتری',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value} size="small" color="primary" variant="outlined" />
      ),
    },
    {
      field: 'name',
      headerName: 'نام',
      width: 200,
      renderCell: (params: GridRenderCellParams<Customer>) => {
        const customer = params.row;
        const displayName = customer.customer_type === 'legal'
          ? customer.company_name
          : `${customer.first_name} ${customer.last_name}`;
        
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ width: 32, height: 32 }}>
              {customer.customer_type === 'legal' ? <Business /> : <Person />}
            </Avatar>
            <Box>
              <Typography variant="body2">{displayName}</Typography>
              <Typography variant="caption" color="textSecondary">
                {customer.customer_type === 'legal' ? 'حقوقی' : 'حقیقی'}
              </Typography>
            </Box>
          </Box>
        );
      },
    },
    {
      field: 'national_id',
      headerName: 'کد ملی/شناسه',
      width: 150,
    },
    {
      field: 'contact',
      headerName: 'تماس',
      width: 200,
      renderCell: (params: GridRenderCellParams<Customer>) => {
        const customer = params.row;
        return (
          <Box sx={{ display: 'flex', gap: 1 }}>
            {customer.phone_number && (
              <Tooltip title={customer.phone_number}>
                <IconButton size="small">
                  <Phone fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {customer.mobile_number && (
              <Tooltip title={customer.mobile_number}>
                <Chip label={customer.mobile_number} size="small" />
              </Tooltip>
            )}
            {customer.email && (
              <Tooltip title={customer.email}>
                <IconButton size="small">
                  <Email fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        );
      },
    },
    {
      field: 'city',
      headerName: 'شهر',
      width: 120,
    },
    {
      field: 'credit_limit',
      headerName: 'اعتبار',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Intl.NumberFormat('fa-IR').format(params.value)} تومان
        </Typography>
      ),
    },
    {
      field: 'status',
      headerName: 'وضعیت',
      width: 100,
      renderCell: (params) => {
        const statusColors: { [key: string]: 'success' | 'error' | 'warning' } = {
          active: 'success',
          inactive: 'error',
          suspended: 'warning',
        };
        const statusLabels: { [key: string]: string } = {
          active: 'فعال',
          inactive: 'غیرفعال',
          suspended: 'معلق',
        };
        return (
          <Chip
            label={statusLabels[params.value] || params.value}
            color={statusColors[params.value] || 'default'}
            size="small"
          />
        );
      },
    },
    {
      field: 'actions',
      headerName: 'عملیات',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Customer>) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => navigate(`/customers/${params.row.id}`)}
          >
            <Visibility fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => navigate(`/customers/${params.row.id}/edit`)}
          >
            <Edit fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={(e) => handleMenuClick(e, params.row)}
          >
            <MoreVert fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = 
      customer.first_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      customer.last_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      customer.company_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      customer.customer_code.toLowerCase().includes(searchText.toLowerCase()) ||
      customer.national_id.includes(searchText);
    
    const matchesType = 
      filterType === 'all' || customer.customer_type === filterType;
    
    return matchesSearch && matchesType;
  });

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            مدیریت مشتریان
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Upload />}
              color="primary"
            >
              ورود اطلاعات
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              color="primary"
            >
              خروجی Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => navigate('/customers/new')}
            >
              مشتری جدید
            </Button>
          </Box>
        </Box>
      </motion.div>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="جستجو در مشتریان..."
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
              <InputLabel>نوع مشتری</InputLabel>
              <Select
                value={filterType}
                label="نوع مشتری"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="individual">حقیقی</MenuItem>
                <MenuItem value="legal">حقوقی</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              sx={{ height: '56px' }}
            >
              فیلترهای پیشرفته
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={filteredCustomers}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          checkboxSelection
          disableSelectionOnClick
          loading={loading}
          localeText={{
            noRowsLabel: 'داده‌ای یافت نشد',
            footerRowSelected: (count) => `${count} مشتری انتخاب شده`,
          }}
        />
      </Paper>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/customers/${selectedCustomer?.id}/edit`);
          handleMenuClose();
        }}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          ویرایش
        </MenuItem>
        <MenuItem onClick={() => {
          setDeleteDialogOpen(true);
          handleMenuClose();
        }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          حذف
        </MenuItem>
      </Menu>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>تایید حذف</DialogTitle>
        <DialogContent>
          آیا از حذف مشتری {selectedCustomer?.first_name} {selectedCustomer?.last_name} اطمینان دارید؟
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

export default CustomerList;