import React from 'react';
import {
  Box,
  Typography,
  Paper,
} from '@mui/material';

const CRM: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        مدیریت CRM
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          فرایندهای فروش
        </Typography>
        <Typography color="textSecondary">
          کانبان فرایندهای فروش در اینجا نمایش داده می‌شود
        </Typography>
      </Paper>
    </Box>
  );
};

export default CRM;