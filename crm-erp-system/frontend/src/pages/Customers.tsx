import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import { Add } from '@mui/icons-material';

const Customers: React.FC = () => {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          مدیریت مشتریان
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
        >
          افزودن مشتری
        </Button>
      </Box>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          لیست مشتریان
        </Typography>
        <Typography color="textSecondary">
          جدول مشتریان در اینجا نمایش داده می‌شود
        </Typography>
      </Paper>
    </Box>
  );
};

export default Customers;