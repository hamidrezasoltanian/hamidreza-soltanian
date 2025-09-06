import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import { Add } from '@mui/icons-material';

const Invoices: React.FC = () => {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          مدیریت فاکتورها
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
        >
          ایجاد فاکتور
        </Button>
      </Box>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          لیست فاکتورها
        </Typography>
        <Typography color="textSecondary">
          جدول فاکتورها در اینجا نمایش داده می‌شود
        </Typography>
      </Paper>
    </Box>
  );
};

export default Invoices;