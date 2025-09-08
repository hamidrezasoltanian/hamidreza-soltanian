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
  Avatar,
  Tooltip,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Work as WorkIcon,
} from '@mui/icons-material';

interface Personnel {
  id: number;
  first_name: string;
  last_name: string;
  position: string;
  phone: string;
  email: string;
  customer: string;
  is_active: boolean;
}

const Personnel: React.FC = () => {
  const [personnel, setPersonnel] = useState<Personnel[]>([
    {
      id: 1,
      first_name: 'احمد',
      last_name: 'محمدی',
      position: 'مدیر فروش',
      phone: '09123456789',
      email: 'ahmad@example.com',
      customer: 'شرکت نمونه',
      is_active: true,
    },
    {
      id: 2,
      first_name: 'فاطمه',
      last_name: 'احمدی',
      position: 'کارشناس فروش',
      phone: '09123456790',
      email: 'fateme@example.com',
      customer: 'شرکت نمونه',
      is_active: true,
    },
  ]);

  const [open, setOpen] = useState(false);
  const [editingPersonnel, setEditingPersonnel] = useState<Personnel | null>(null);
  const [formData, setFormData] = useState<Partial<Personnel>>({});

  const handleOpen = (personnel?: Personnel) => {
    if (personnel) {
      setEditingPersonnel(personnel);
      setFormData(personnel);
    } else {
      setEditingPersonnel(null);
      setFormData({});
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingPersonnel(null);
    setFormData({});
  };

  const handleSave = () => {
    if (editingPersonnel) {
      setPersonnel(prev => 
        prev.map(p => p.id === editingPersonnel.id ? { ...p, ...formData } : p)
      );
    } else {
      const newPersonnel: Personnel = {
        id: Date.now(),
        first_name: formData.first_name || '',
        last_name: formData.last_name || '',
        position: formData.position || '',
        phone: formData.phone || '',
        email: formData.email || '',
        customer: formData.customer || '',
        is_active: true,
      };
      setPersonnel(prev => [...prev, newPersonnel]);
    }
    handleClose();
  };

  const handleDelete = (id: number) => {
    setPersonnel(prev => prev.filter(p => p.id !== id));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت پرسنل
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          افزودن پرسنل
        </Button>
      </Box>

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>نام</TableCell>
                <TableCell>سمت</TableCell>
                <TableCell>تماس</TableCell>
                <TableCell>ایمیل</TableCell>
                <TableCell>مشتری</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {personnel.map((person) => (
                <TableRow key={person.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 32, height: 32 }}>
                        <PersonIcon />
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {person.first_name} {person.last_name}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <WorkIcon fontSize="small" color="action" />
                      {person.position}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PhoneIcon fontSize="small" color="action" />
                      {person.phone}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <EmailIcon fontSize="small" color="action" />
                      {person.email}
                    </Box>
                  </TableCell>
                  <TableCell>{person.customer}</TableCell>
                  <TableCell>
                    <Chip
                      label={person.is_active ? 'فعال' : 'غیرفعال'}
                      color={person.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="ویرایش">
                        <IconButton
                          size="small"
                          onClick={() => handleOpen(person)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(person.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
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
          {editingPersonnel ? 'ویرایش پرسنل' : 'افزودن پرسنل جدید'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="نام"
                value={formData.first_name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="نام خانوادگی"
                value={formData.last_name || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="سمت"
                value={formData.position || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, position: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="شماره تلفن"
                value={formData.phone || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="ایمیل"
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="مشتری"
                value={formData.customer || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, customer: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>انصراف</Button>
          <Button onClick={handleSave} variant="contained">
            {editingPersonnel ? 'ویرایش' : 'افزودن'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Personnel;