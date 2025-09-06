import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { faIR } from 'date-fns/locale';

interface CustomerFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  customer?: any;
  categories: any[];
  loading?: boolean;
}

const CustomerForm: React.FC<CustomerFormProps> = ({
  open,
  onClose,
  onSubmit,
  customer,
  categories,
  loading = false,
}) => {
  const { control, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: customer || {
      customer_code: '',
      customer_type: 'individual',
      first_name: '',
      last_name: '',
      company_name: '',
      phone_number: '',
      email: '',
      address: '',
      postal_code: '',
      city: '',
      state: '',
      country: 'Iran',
      economic_code: '',
      national_id: '',
      registration_number: '',
      status: 'active',
      category: '',
    },
  });

  React.useEffect(() => {
    if (customer) {
      reset(customer);
    } else {
      reset({
        customer_code: '',
        customer_type: 'individual',
        first_name: '',
        last_name: '',
        company_name: '',
        phone_number: '',
        email: '',
        address: '',
        postal_code: '',
        city: '',
        state: '',
        country: 'Iran',
        economic_code: '',
        national_id: '',
        registration_number: '',
        status: 'active',
        category: '',
      });
    }
  }, [customer, reset]);

  const handleFormSubmit = (data: any) => {
    onSubmit(data);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {customer ? 'ویرایش مشتری' : 'افزودن مشتری جدید'}
      </DialogTitle>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="customer_code"
                control={control}
                rules={{ required: 'کد مشتری الزامی است' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="کد مشتری"
                    error={!!errors.customer_code}
                    helperText={errors.customer_code?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="customer_type"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>نوع مشتری</InputLabel>
                    <Select {...field} label="نوع مشتری">
                      <MenuItem value="individual">حقیقی</MenuItem>
                      <MenuItem value="legal">حقوقی</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="first_name"
                control={control}
                rules={{ required: 'نام الزامی است' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="نام"
                    error={!!errors.first_name}
                    helperText={errors.first_name?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="last_name"
                control={control}
                rules={{ required: 'نام خانوادگی الزامی است' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="نام خانوادگی"
                    error={!!errors.last_name}
                    helperText={errors.last_name?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="company_name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="نام شرکت"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="phone_number"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="شماره تلفن"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="ایمیل"
                    type="email"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="category"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>دسته‌بندی</InputLabel>
                    <Select {...field} label="دسته‌بندی">
                      {categories.map((category) => (
                        <MenuItem key={category.id} value={category.id}>
                          {category.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="آدرس"
                    multiline
                    rows={3}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Controller
                name="postal_code"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="کد پستی"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Controller
                name="city"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="شهر"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Controller
                name="state"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="استان"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="economic_code"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="کد اقتصادی"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="national_id"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="شناسه ملی"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="registration_number"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="شماره ثبت"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>وضعیت</InputLabel>
                    <Select {...field} label="وضعیت">
                      <MenuItem value="active">فعال</MenuItem>
                      <MenuItem value="inactive">غیرفعال</MenuItem>
                      <MenuItem value="suspended">معلق</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            انصراف
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'در حال ذخیره...' : 'ذخیره'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CustomerForm;