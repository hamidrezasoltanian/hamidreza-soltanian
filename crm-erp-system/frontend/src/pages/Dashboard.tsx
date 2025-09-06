import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
} from '@mui/material';
import {
  People,
  Inventory,
  ShoppingCart,
  Assessment,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const stats = [
    {
      title: 'مشتریان',
      value: '1,234',
      icon: <People sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: 'محصولات',
      value: '567',
      icon: <Inventory sx={{ fontSize: 40 }} />,
      color: '#388e3c',
    },
    {
      title: 'فاکتورها',
      value: '89',
      icon: <ShoppingCart sx={{ fontSize: 40 }} />,
      color: '#f57c00',
    },
    {
      title: 'فروش',
      value: '12,345,000',
      icon: <Assessment sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        داشبورد
      </Typography>
      
      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: stat.color }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              نمودار فروش
            </Typography>
            <Box height={300} display="flex" alignItems="center" justifyContent="center">
              <Typography color="textSecondary">
                نمودار فروش در اینجا نمایش داده می‌شود
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              فعالیت‌های اخیر
            </Typography>
            <Box>
              <Typography variant="body2" color="textSecondary">
                • فاکتور جدید ایجاد شد
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • مشتری جدید اضافه شد
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • محصول جدید ثبت شد
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;