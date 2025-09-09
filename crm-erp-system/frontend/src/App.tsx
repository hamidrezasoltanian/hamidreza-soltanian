import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { CustomThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Layout from './components/Layout';
import { useAuth } from './hooks/useAuth';

// Lazy load pages for better performance
const Login = lazy(() => import('./pages/Login'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Customers = lazy(() => import('./pages/Customers'));
const Products = lazy(() => import('./pages/Products'));
const Inventory = lazy(() => import('./pages/Inventory'));
const Invoices = lazy(() => import('./pages/Invoices'));
const CRM = lazy(() => import('./pages/CRM'));
const Personnel = lazy(() => import('./pages/Personnel'));
const Accounting = lazy(() => import('./pages/Accounting'));
const TaxSystem = lazy(() => import('./pages/TaxSystem'));
const Reports = lazy(() => import('./pages/Reports'));
const PrintSystem = lazy(() => import('./pages/PrintSystem'));
const SystemStatus = lazy(() => import('./pages/SystemStatus'));
const Notifications = lazy(() => import('./pages/Notifications'));
const ExportImport = lazy(() => import('./pages/ExportImport'));

// Loading component
const PageLoader = () => (
  <Box 
    display="flex" 
    justifyContent="center" 
    alignItems="center" 
    minHeight="400px"
  >
    <CircularProgress />
  </Box>
);

function App() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <CustomThemeProvider>
        <NotificationProvider>
          <Suspense fallback={<PageLoader />}>
            <Login />
          </Suspense>
        </NotificationProvider>
      </CustomThemeProvider>
    );
  }

  return (
    <CustomThemeProvider>
      <NotificationProvider>
        <Box sx={{ display: 'flex' }}>
          <Layout>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/customers" element={<Customers />} />
                <Route path="/products" element={<Products />} />
                <Route path="/inventory" element={<Inventory />} />
                <Route path="/invoices" element={<Invoices />} />
                <Route path="/crm" element={<CRM />} />
                <Route path="/personnel" element={<Personnel />} />
                <Route path="/accounting" element={<Accounting />} />
                <Route path="/tax" element={<TaxSystem />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/print" element={<PrintSystem />} />
                <Route path="/status" element={<SystemStatus />} />
                <Route path="/notifications" element={<Notifications />} />
                <Route path="/export-import" element={<ExportImport />} />
              </Routes>
            </Suspense>
          </Layout>
        </Box>
      </NotificationProvider>
    </CustomThemeProvider>
  );
}

export default App;