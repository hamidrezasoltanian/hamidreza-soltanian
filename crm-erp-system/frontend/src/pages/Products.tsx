import React from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import { Add } from '@mui/icons-material';

const Products: React.FC = () => {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          مدیریت محصولات
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
        >
          افزودن محصول
        </Button>
      </Box>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          لیست محصولات
        </Typography>
        <Typography color="textSecondary">
          جدول محصولات در اینجا نمایش داده می‌شود
        </Typography>
      </Paper>
    </Box>
  );
};

export default Products;