import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useCustomers, useCreateCustomer, useUpdateCustomer, useDeleteCustomer, useCustomerCategories } from '../hooks/useCustomers';
import CustomerTable from '../components/CustomerTable';
import CustomerForm from '../components/CustomerForm';

const Customers: React.FC = () => {
  const [openForm, setOpenForm] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});

  const { data: customersData, isLoading: customersLoading, error: customersError } = useCustomers(filters);
  const { data: categoriesData, isLoading: categoriesLoading } = useCustomerCategories();
  const { data: statsData } = useCustomers({ stats: true });

  const createCustomerMutation = useCreateCustomer();
  const updateCustomerMutation = useUpdateCustomer();
  const deleteCustomerMutation = useDeleteCustomer();

  const customers = customersData?.results || [];
  const categories = categoriesData || [];

  const handleCreateCustomer = () => {
    setSelectedCustomer(null);
    setOpenForm(true);
  };

  const handleEditCustomer = (customer: any) => {
    setSelectedCustomer(customer);
    setOpenForm(true);
  };

  const handleViewCustomer = (customer: any) => {
    // TODO: Implement view customer modal
    console.log('View customer:', customer);
  };

  const handleDeleteCustomer = (id: number) => {
    if (window.confirm('آیا از حذف این مشتری اطمینان دارید؟')) {
      deleteCustomerMutation.mutate(id);
    }
  };

  const handleSubmitCustomer = (data: any) => {
    if (selectedCustomer) {
      updateCustomerMutation.mutate({ id: selectedCustomer.id, data });
    } else {
      createCustomerMutation.mutate(data);
    }
    setOpenForm(false);
    setSelectedCustomer(null);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setFilters({ search: event.target.value });
  };

  if (customersError) {
    return (
      <Box>
        <Alert severity="error">
          خطا در بارگذاری مشتریان: {customersError.message}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          مدیریت مشتریان
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateCustomer}
        >
          افزودن مشتری
        </Button>
      </Box>

      {/* Stats Cards */}
      {statsData && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  کل مشتریان
                </Typography>
                <Typography variant="h4">
                  {statsData.total_customers || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  مشتریان فعال
                </Typography>
                <Typography variant="h4">
                  {statsData.active_customers || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  مشتریان جدید (ماه)
                </Typography>
                <Typography variant="h4">
                  {statsData.new_customers_this_month || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  مشتریان حقوقی
                </Typography>
                <Typography variant="h4">
                  {statsData.legal_customers || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            fullWidth
            placeholder="جستجو در مشتریان..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
          >
            فیلتر
          </Button>
        </Box>
      </Paper>

      {/* Customers Table */}
      {customersLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <CustomerTable
          customers={customers}
          onEdit={handleEditCustomer}
          onDelete={handleDeleteCustomer}
          onView={handleViewCustomer}
          loading={createCustomerMutation.isPending || updateCustomerMutation.isPending || deleteCustomerMutation.isPending}
        />
      )}

      {/* Customer Form Modal */}
      <CustomerForm
        open={openForm}
        onClose={() => {
          setOpenForm(false);
          setSelectedCustomer(null);
        }}
        onSubmit={handleSubmitCustomer}
        customer={selectedCustomer}
        categories={categories}
        loading={createCustomerMutation.isPending || updateCustomerMutation.isPending}
      />
    </Box>
  );
};

export default Customers;