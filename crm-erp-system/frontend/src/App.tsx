import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { CustomThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import Invoices from './pages/Invoices';
import CRM from './pages/CRM';
import Personnel from './pages/Personnel';
import Accounting from './pages/Accounting';
import TaxSystem from './pages/TaxSystem';
import Reports from './pages/Reports';
import PrintSystem from './pages/PrintSystem';
import SystemStatus from './pages/SystemStatus';
import Notifications from './pages/Notifications';
import { useAuth } from './hooks/useAuth';

function App() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <CustomThemeProvider>
        <NotificationProvider>
          <Login />
        </NotificationProvider>
      </CustomThemeProvider>
    );
  }

  return (
    <CustomThemeProvider>
      <NotificationProvider>
        <Box sx={{ display: 'flex' }}>
          <Layout>
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
            </Routes>
          </Layout>
        </Box>
      </NotificationProvider>
    </CustomThemeProvider>
  );
}

export default App;