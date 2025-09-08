import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Chip,
  Card,
  CardContent,
  Fab,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Gavel as GavelIcon,
  Receipt as ReceiptIcon,
  AccountBalance as AccountBalanceIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

interface TaxPayer {
  id: number;
  name: string;
  national_id: string;
  economic_code: string;
  tax_code: string;
  registration_date: string;
  status: 'active' | 'inactive' | 'suspended';
  last_payment: string;
  balance: number;
}

interface TaxReturn {
  id: number;
  taxpayer_id: number;
  period: string;
  type: 'monthly' | 'quarterly' | 'annual';
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  amount: number;
  due_date: string;
}

const TaxSystem: React.FC = () => {
  const [taxPayers, setTaxPayers] = useState<TaxPayer[]>([
    {
      id: 1,
      name: 'شرکت نمونه',
      national_id: '1234567890',
      economic_code: '1234567890123',
      tax_code: 'T123456789',
      registration_date: '1400/01/01',
      status: 'active',
      last_payment: '1402/12/01',
      balance: 5000000,
    },
    {
      id: 2,
      name: 'شرکت تجاری',
      national_id: '0987654321',
      economic_code: '9876543210987',
      tax_code: 'T987654321',
      registration_date: '1400/06/15',
      status: 'active',
      last_payment: '1402/11/15',
      balance: 3000000,
    },
  ]);

  const [taxReturns, setTaxReturns] = useState<TaxReturn[]>([
    {
      id: 1,
      taxpayer_id: 1,
      period: '1402/12',
      type: 'monthly',
      status: 'submitted',
      amount: 1000000,
      due_date: '1403/01/15',
    },
    {
      id: 2,
      taxpayer_id: 2,
      period: '1402/11',
      type: 'monthly',
      status: 'approved',
      amount: 800000,
      due_date: '1402/12/15',
    },
  ]);

  const [open, setOpen] = useState(false);
  const [editingTaxPayer, setEditingTaxPayer] = useState<TaxPayer | null>(null);
  const [formData, setFormData] = useState<Partial<TaxPayer>>({});

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'error';
      case 'submitted': return 'info';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'draft': return 'warning';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'فعال';
      case 'inactive': return 'غیرفعال';
      case 'suspended': return 'معلق';
      case 'submitted': return 'ارسال شده';
      case 'approved': return 'تایید شده';
      case 'rejected': return 'رد شده';
      case 'draft': return 'پیش‌نویس';
      default: return status;
    }
  };

  const handleOpen = (taxPayer?: TaxPayer) => {
    if (taxPayer) {
      setEditingTaxPayer(taxPayer);
      setFormData(taxPayer);
    } else {
      setEditingTaxPayer(null);
      setFormData({});
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingTaxPayer(null);
    setFormData({});
  };

  const handleSave = () => {
    if (editingTaxPayer) {
      setTaxPayers(prev => 
        prev.map(t => t.id === editingTaxPayer.id ? { ...t, ...formData } : t)
      );
    } else {
      const newTaxPayer: TaxPayer = {
        id: Date.now(),
        name: formData.name || '',
        national_id: formData.national_id || '',
        economic_code: formData.economic_code || '',
        tax_code: formData.tax_code || '',
        registration_date: formData.registration_date || '',
        status: formData.status || 'active',
        last_payment: formData.last_payment || '',
        balance: formData.balance || 0,
      };
      setTaxPayers(prev => [...prev, newTaxPayer]);
    }
    handleClose();
  };

  const handleDelete = (id: number) => {
    setTaxPayers(prev => prev.filter(t => t.id !== id));
  };

  const totalBalance = taxPayers.reduce((sum, t) => sum + t.balance, 0);
  const pendingReturns = taxReturns.filter(r => r.status === 'submitted').length;
  const overdueReturns = taxReturns.filter(r => 
    r.status === 'submitted' && new Date(r.due_date) < new Date()
  ).length;

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          سیستم مالیاتی
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          افزودن مودی
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    کل مودیان
                  </Typography>
                  <Typography variant="h5" component="div">
                    {taxPayers.length}
                  </Typography>
                </Box>
                <GavelIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    کل بدهی مالیاتی
                  </Typography>
                  <Typography variant="h5" component="div">
                    {totalBalance.toLocaleString()} ریال
                  </Typography>
                </Box>
                <AccountBalanceIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    اظهارنامه‌های در انتظار
                  </Typography>
                  <Typography variant="h5" component="div">
                    {pendingReturns}
                  </Typography>
                </Box>
                <ReceiptIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    اظهارنامه‌های معوق
                  </Typography>
                  <Typography variant="h5" component="div">
                    {overdueReturns}
                  </Typography>
                </Box>
                <WarningIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ width: '100%', overflow: 'hidden', mb: 3 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">لیست مودیان مالیاتی</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام مودی</TableCell>
                <TableCell>شناسه ملی</TableCell>
                <TableCell>کد اقتصادی</TableCell>
                <TableCell>کد مالیاتی</TableCell>
                <TableCell>تاریخ ثبت</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>بدهی</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {taxPayers.map((taxPayer) => (
                <TableRow key={taxPayer.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {taxPayer.name}
                    </Typography>
                  </TableCell>
                  <TableCell>{taxPayer.national_id}</TableCell>
                  <TableCell>{taxPayer.economic_code}</TableCell>
                  <TableCell>{taxPayer.tax_code}</TableCell>
                  <TableCell>{taxPayer.registration_date}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(taxPayer.status)}
                      color={getStatusColor(taxPayer.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      color={taxPayer.balance > 0 ? 'error.main' : 'success.main'}
                    >
                      {taxPayer.balance.toLocaleString()} ریال
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpen(taxPayer)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(taxPayer.id)}
                        color="error"
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

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">اظهارنامه‌های مالیاتی</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>دوره</TableCell>
                <TableCell>نوع</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>مبلغ</TableCell>
                <TableCell>تاریخ سررسید</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {taxReturns.map((taxReturn) => (
                <TableRow key={taxReturn.id}>
                  <TableCell>{taxReturn.period}</TableCell>
                  <TableCell>
                    <Chip
                      label={taxReturn.type === 'monthly' ? 'ماهانه' : 
                             taxReturn.type === 'quarterly' ? 'فصلی' : 'سالانه'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(taxReturn.status)}
                      color={getStatusColor(taxReturn.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {taxReturn.amount.toLocaleString()} ریال
                    </Typography>
                  </TableCell>
                  <TableCell>{taxReturn.due_date}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button size="small" variant="outlined">
                        مشاهده
                      </Button>
                      <Button size="small" variant="contained">
                        ویرایش
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTaxPayer ? 'ویرایش مودی' : 'افزودن مودی جدید'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="نام مودی"
                value={formData.name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="شناسه ملی"
                value={formData.national_id || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, national_id: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="کد اقتصادی"
                value={formData.economic_code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, economic_code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="کد مالیاتی"
                value={formData.tax_code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, tax_code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="تاریخ ثبت"
                value={formData.registration_date || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, registration_date: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="وضعیت"
                value={formData.status || 'active'}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as any }))}
                SelectProps={{ native: true }}
              >
                <option value="active">فعال</option>
                <option value="inactive">غیرفعال</option>
                <option value="suspended">معلق</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="آخرین پرداخت"
                value={formData.last_payment || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, last_payment: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="بدهی فعلی"
                type="number"
                value={formData.balance || 0}
                onChange={(e) => setFormData(prev => ({ ...prev, balance: Number(e.target.value) }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>انصراف</Button>
          <Button onClick={handleSave} variant="contained">
            {editingTaxPayer ? 'ویرایش' : 'افزودن'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaxSystem;