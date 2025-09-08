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
  Fab,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AccountBalance as AccountBalanceIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';

interface Account {
  id: number;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  parent_code?: string;
  balance: number;
  is_active: boolean;
}

const Accounting: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([
    {
      id: 1,
      code: '1000',
      name: 'دارایی‌های جاری',
      type: 'asset',
      balance: 5000000,
      is_active: true,
    },
    {
      id: 2,
      code: '1100',
      name: 'موجودی نقد',
      type: 'asset',
      parent_code: '1000',
      balance: 2000000,
      is_active: true,
    },
    {
      id: 3,
      code: '2000',
      name: 'بدهی‌های جاری',
      type: 'liability',
      balance: 3000000,
      is_active: true,
    },
    {
      id: 4,
      code: '4000',
      name: 'درآمدها',
      type: 'revenue',
      balance: 10000000,
      is_active: true,
    },
  ]);

  const [open, setOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState<Partial<Account>>({});

  const accountTypes = [
    { value: 'asset', label: 'دارایی', color: 'success' },
    { value: 'liability', label: 'بدهی', color: 'error' },
    { value: 'equity', label: 'حقوق صاحبان سهام', color: 'info' },
    { value: 'revenue', label: 'درآمد', color: 'primary' },
    { value: 'expense', label: 'هزینه', color: 'warning' },
  ];

  const getAccountTypeLabel = (type: string) => {
    return accountTypes.find(t => t.value === type)?.label || type;
  };

  const getAccountTypeColor = (type: string) => {
    return accountTypes.find(t => t.value === type)?.color || 'default';
  };

  const handleOpen = (account?: Account) => {
    if (account) {
      setEditingAccount(account);
      setFormData(account);
    } else {
      setEditingAccount(null);
      setFormData({});
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingAccount(null);
    setFormData({});
  };

  const handleSave = () => {
    if (editingAccount) {
      setAccounts(prev => 
        prev.map(a => a.id === editingAccount.id ? { ...a, ...formData } : a)
      );
    } else {
      const newAccount: Account = {
        id: Date.now(),
        code: formData.code || '',
        name: formData.name || '',
        type: formData.type || 'asset',
        parent_code: formData.parent_code,
        balance: formData.balance || 0,
        is_active: true,
      };
      setAccounts(prev => [...prev, newAccount]);
    }
    handleClose();
  };

  const handleDelete = (id: number) => {
    setAccounts(prev => prev.filter(a => a.id !== id));
  };

  const totalAssets = accounts
    .filter(a => a.type === 'asset')
    .reduce((sum, a) => sum + a.balance, 0);

  const totalLiabilities = accounts
    .filter(a => a.type === 'liability')
    .reduce((sum, a) => sum + a.balance, 0);

  const totalRevenue = accounts
    .filter(a => a.type === 'revenue')
    .reduce((sum, a) => sum + a.balance, 0);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          سیستم حسابداری
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          افزودن حساب
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
                    کل دارایی‌ها
                  </Typography>
                  <Typography variant="h5" component="div">
                    {totalAssets.toLocaleString()} ریال
                  </Typography>
                </Box>
                <AccountBalanceIcon color="success" sx={{ fontSize: 40 }} />
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
                    کل بدهی‌ها
                  </Typography>
                  <Typography variant="h5" component="div">
                    {totalLiabilities.toLocaleString()} ریال
                  </Typography>
                </Box>
                <TrendingDownIcon color="error" sx={{ fontSize: 40 }} />
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
                    کل درآمدها
                  </Typography>
                  <Typography variant="h5" component="div">
                    {totalRevenue.toLocaleString()} ریال
                  </Typography>
                </Box>
                <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
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
                    خالص دارایی
                  </Typography>
                  <Typography variant="h5" component="div">
                    {(totalAssets - totalLiabilities).toLocaleString()} ریال
                  </Typography>
                </Box>
                <MoneyIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>کد حساب</TableCell>
                <TableCell>نام حساب</TableCell>
                <TableCell>نوع</TableCell>
                <TableCell>کد والد</TableCell>
                <TableCell>موجودی</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {accounts.map((account) => (
                <TableRow key={account.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {account.code}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {account.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getAccountTypeLabel(account.type)}
                      color={getAccountTypeColor(account.type) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{account.parent_code || '-'}</TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      color={account.balance >= 0 ? 'success.main' : 'error.main'}
                    >
                      {account.balance.toLocaleString()} ریال
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={account.is_active ? 'فعال' : 'غیرفعال'}
                      color={account.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpen(account)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(account.id)}
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

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAccount ? 'ویرایش حساب' : 'افزودن حساب جدید'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="کد حساب"
                value={formData.code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="نام حساب"
                value={formData.name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="نوع حساب"
                value={formData.type || 'asset'}
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as any }))}
                SelectProps={{ native: true }}
              >
                {accountTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="کد والد (اختیاری)"
                value={formData.parent_code || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, parent_code: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="موجودی اولیه"
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
            {editingAccount ? 'ویرایش' : 'افزودن'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Accounting;