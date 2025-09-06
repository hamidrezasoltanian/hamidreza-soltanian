import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useAuth } from '../hooks/useAuth';

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    setError('');
    
    try {
      await login(data.username, data.password);
    } catch (err: any) {
      setError(err.response?.data?.error || 'خطا در ورود');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', mx: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            ورود به سیستم
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            سیستم مدیریت مشتریان و منابع سازمانی
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              {...register('username', { required: 'نام کاربری الزامی است' })}
              fullWidth
              label="نام کاربری"
              margin="normal"
              error={!!errors.username}
              helperText={errors.username?.message}
              disabled={loading}
            />
            
            <TextField
              {...register('password', { required: 'رمز عبور الزامی است' })}
              fullWidth
              label="رمز عبور"
              type="password"
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message}
              disabled={loading}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'ورود'}
            </Button>
          </form>
          
          <Typography variant="body2" color="text.secondary" align="center">
            نام کاربری پیش‌فرض: admin | رمز عبور: admin123
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Login;