import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Tooltip,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  ToggleButton,
  ToggleButtonGroup,
  Badge,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  Add,
  Search,
  FilterList,
  MoreVert,
  Edit,
  Delete,
  Visibility,
  GridView,
  ViewList,
  Inventory,
  LocalOffer,
  Category,
  Download,
  Upload,
  QrCode,
  ShoppingCart,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { motion } from 'framer-motion';

interface Product {
  id: number;
  product_code: string;
  name: string;
  name_en?: string;
  barcode: string;
  category: number;
  category_name?: string;
  base_unit: string;
  cost_price: number;
  sale_price: number;
  wholesale_price?: number;
  min_stock: number;
  max_stock: number;
  current_stock: number;
  description?: string;
  status: string;
  image?: string;
}

const ProductList: React.FC = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [quickViewOpen, setQuickViewOpen] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/products/');
      setProducts(response.data.results || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedProduct) return;
    
    try {
      await apiService.delete(`/products/${selectedProduct.id}/`);
      await fetchProducts();
      setDeleteDialogOpen(false);
      setSelectedProduct(null);
    } catch (error) {
      console.error('Error deleting product:', error);
    }
  };

  const handleQuickView = (product: Product) => {
    setSelectedProduct(product);
    setQuickViewOpen(true);
  };

  const getStockStatus = (product: Product) => {
    const stockPercentage = (product.current_stock / product.max_stock) * 100;
    if (product.current_stock <= product.min_stock) {
      return { color: 'error', label: 'موجودی کم' };
    } else if (stockPercentage > 80) {
      return { color: 'success', label: 'موجودی کافی' };
    } else {
      return { color: 'warning', label: 'موجودی متوسط' };
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'product_code',
      headerName: 'کد محصول',
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          color="primary" 
          variant="outlined"
          icon={<QrCode />}
        />
      ),
    },
    {
      field: 'name',
      headerName: 'نام محصول',
      width: 250,
      renderCell: (params: GridRenderCellParams<Product>) => {
        const product = params.row;
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar 
              src={product.image} 
              sx={{ width: 40, height: 40 }}
              variant="rounded"
            >
              <ShoppingCart />
            </Avatar>
            <Box>
              <Typography variant="body2" fontWeight="medium">
                {product.name}
              </Typography>
              {product.name_en && (
                <Typography variant="caption" color="textSecondary">
                  {product.name_en}
                </Typography>
              )}
            </Box>
          </Box>
        );
      },
    },
    {
      field: 'category_name',
      headerName: 'دسته‌بندی',
      width: 150,
      renderCell: (params) => (
        <Chip 
          label={params.value || 'بدون دسته'} 
          size="small"
          icon={<Category />}
        />
      ),
    },
    {
      field: 'barcode',
      headerName: 'بارکد',
      width: 150,
    },
    {
      field: 'prices',
      headerName: 'قیمت‌ها',
      width: 200,
      renderCell: (params: GridRenderCellParams<Product>) => {
        const product = params.row;
        return (
          <Box>
            <Typography variant="body2">
              فروش: {new Intl.NumberFormat('fa-IR').format(product.sale_price)}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              خرید: {new Intl.NumberFormat('fa-IR').format(product.cost_price)}
            </Typography>
          </Box>
        );
      },
    },
    {
      field: 'stock',
      headerName: 'موجودی',
      width: 180,
      renderCell: (params: GridRenderCellParams<Product>) => {
        const product = params.row;
        const status = getStockStatus(product);
        return (
          <Box sx={{ width: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">
                {product.current_stock} / {product.max_stock}
              </Typography>
              <Chip 
                label={status.label} 
                size="small" 
                color={status.color as any}
              />
            </Box>
            <Box sx={{ 
              width: '100%', 
              height: 4, 
              bgcolor: 'grey.300', 
              borderRadius: 2,
              overflow: 'hidden'
            }}>
              <Box sx={{ 
                width: `${(product.current_stock / product.max_stock) * 100}%`,
                height: '100%',
                bgcolor: `${status.color}.main`,
              }} />
            </Box>
          </Box>
        );
      },
    },
    {
      field: 'status',
      headerName: 'وضعیت',
      width: 100,
      renderCell: (params) => {
        const statusMap: { [key: string]: { color: any, label: string } } = {
          active: { color: 'success', label: 'فعال' },
          inactive: { color: 'error', label: 'غیرفعال' },
          discontinued: { color: 'warning', label: 'توقف تولید' },
        };
        const status = statusMap[params.value] || { color: 'default', label: params.value };
        return (
          <Chip
            label={status.label}
            color={status.color}
            size="small"
          />
        );
      },
    },
    {
      field: 'actions',
      headerName: 'عملیات',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Product>) => (
        <Box>
          <Tooltip title="مشاهده سریع">
            <IconButton
              size="small"
              onClick={() => handleQuickView(params.row)}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="ویرایش">
            <IconButton
              size="small"
              onClick={() => navigate(`/products/${params.row.id}/edit`)}
            >
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="حذف">
            <IconButton
              size="small"
              onClick={() => {
                setSelectedProduct(params.row);
                setDeleteDialogOpen(true);
              }}
            >
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  const filteredProducts = products.filter(product => {
    const matchesSearch = 
      product.name?.toLowerCase().includes(searchText.toLowerCase()) ||
      product.product_code.toLowerCase().includes(searchText.toLowerCase()) ||
      product.barcode?.includes(searchText);
    
    const matchesCategory = 
      selectedCategory === 'all' || product.category_name === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
    const status = getStockStatus(product);
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardMedia
            component="img"
            height="200"
            image={product.image || '/placeholder-product.png'}
            alt={product.name}
            sx={{ objectFit: 'cover' }}
          />
          <CardContent sx={{ flexGrow: 1 }}>
            <Typography gutterBottom variant="h6" component="div">
              {product.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              کد: {product.product_code}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" color="primary">
                {new Intl.NumberFormat('fa-IR').format(product.sale_price)} تومان
              </Typography>
              <Badge 
                badgeContent={product.current_stock} 
                color={status.color as any}
                sx={{ mt: 1 }}
              >
                <Chip 
                  icon={<Inventory />}
                  label="موجودی"
                  size="small"
                />
              </Badge>
            </Box>
          </CardContent>
          <CardActions>
            <Button size="small" onClick={() => handleQuickView(product)}>
              مشاهده
            </Button>
            <Button size="small" onClick={() => navigate(`/products/${product.id}/edit`)}>
              ویرایش
            </Button>
          </CardActions>
        </Card>
      </motion.div>
    );
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            مدیریت محصولات
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
            >
              <ToggleButton value="list">
                <ViewList />
              </ToggleButton>
              <ToggleButton value="grid">
                <GridView />
              </ToggleButton>
            </ToggleButtonGroup>
            <Button
              variant="outlined"
              startIcon={<Upload />}
              color="primary"
            >
              ورود اطلاعات
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              color="primary"
            >
              خروجی Excel
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => navigate('/products/new')}
            >
              محصول جدید
            </Button>
          </Box>
        </Box>
      </motion.div>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="جستجو در محصولات..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>دسته‌بندی</InputLabel>
              <Select
                value={selectedCategory}
                label="دسته‌بندی"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="الکترونیک">الکترونیک</MenuItem>
                <MenuItem value="لوازم خانگی">لوازم خانگی</MenuItem>
                <MenuItem value="موبایل و تبلت">موبایل و تبلت</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              sx={{ height: '56px' }}
            >
              فیلترهای پیشرفته
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {viewMode === 'list' ? (
        <Paper sx={{ height: 600, width: '100%' }}>
          <DataGrid
            rows={filteredProducts}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            checkboxSelection
            disableSelectionOnClick
            loading={loading}
            localeText={{
              noRowsLabel: 'محصولی یافت نشد',
              footerRowSelected: (count) => `${count} محصول انتخاب شده`,
            }}
          />
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredProducts.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <ProductCard product={product} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Quick View Dialog */}
      <Dialog
        open={quickViewOpen}
        onClose={() => setQuickViewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar src={selectedProduct?.image} variant="rounded">
              <ShoppingCart />
            </Avatar>
            {selectedProduct?.name}
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedProduct && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">کد محصول</Typography>
                <Typography variant="body1" gutterBottom>{selectedProduct.product_code}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">بارکد</Typography>
                <Typography variant="body1" gutterBottom>{selectedProduct.barcode}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">قیمت خرید</Typography>
                <Typography variant="body1" gutterBottom>
                  {new Intl.NumberFormat('fa-IR').format(selectedProduct.cost_price)} تومان
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">قیمت فروش</Typography>
                <Typography variant="body1" gutterBottom>
                  {new Intl.NumberFormat('fa-IR').format(selectedProduct.sale_price)} تومان
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">موجودی فعلی</Typography>
                <Typography variant="body1" gutterBottom>
                  {selectedProduct.current_stock} {selectedProduct.base_unit}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">حداقل - حداکثر موجودی</Typography>
                <Typography variant="body1" gutterBottom>
                  {selectedProduct.min_stock} - {selectedProduct.max_stock}
                </Typography>
              </Grid>
              {selectedProduct.description && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">توضیحات</Typography>
                  <Typography variant="body1">{selectedProduct.description}</Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuickViewOpen(false)}>بستن</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              navigate(`/products/${selectedProduct?.id}/edit`);
              setQuickViewOpen(false);
            }}
          >
            ویرایش محصول
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>تایید حذف</DialogTitle>
        <DialogContent>
          آیا از حذف محصول "{selectedProduct?.name}" اطمینان دارید؟
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>انصراف</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            حذف
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductList;