import React from 'react';
import {
  Box,
  Typography,
  Paper,
} from '@mui/material';

const Inventory: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        مدیریت انبار
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          موجودی انبار
        </Typography>
        <Typography color="textSecondary">
          جدول موجودی در اینجا نمایش داده می‌شود
        </Typography>
      </Paper>
    </Box>
  );
};

export default Inventory;