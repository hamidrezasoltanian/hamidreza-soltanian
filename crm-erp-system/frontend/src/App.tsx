import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ThemeProvider as CustomThemeProvider } from './contexts/ThemeContext';

// Pages
import Login from './pages/auth/Login';
import Dashboard from './pages/Dashboard';
import CustomerList from './pages/customers/CustomerList';
import MainLayout from './components/layout/MainLayout';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Create theme
const theme = createTheme({
  direction: 'rtl',
  typography: {
    fontFamily: [
      'IRANSans',
      'Vazir',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#f50057',
      dark: '#c51162',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  shape: {
    borderRadius: 8,
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <NotificationProvider>
            <CustomThemeProvider>
              <Router>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/login" element={<Login />} />

                  {/* Protected Routes */}
                  <Route
                    path="/"
                    element={
                      <ProtectedRoute>
                        <MainLayout />
                      </ProtectedRoute>
                    }
                  >
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    
                    {/* Customer Routes */}
                    <Route path="customers" element={<CustomerList />} />
                    <Route path="customers/new" element={<div>New Customer Form</div>} />
                    <Route path="customers/:id" element={<div>Customer Detail</div>} />
                    <Route path="customers/:id/edit" element={<div>Edit Customer</div>} />
                    
                    {/* Product Routes */}
                    <Route path="products" element={<div>Product List</div>} />
                    <Route path="products/new" element={<div>New Product</div>} />
                    <Route path="products/:id" element={<div>Product Detail</div>} />
                    
                    {/* Inventory Routes */}
                    <Route path="inventory" element={<div>Inventory</div>} />
                    
                    {/* Invoice Routes */}
                    <Route path="invoices" element={<div>Invoice List</div>} />
                    <Route path="invoices/new" element={<div>New Invoice</div>} />
                    <Route path="invoices/:id" element={<div>Invoice Detail</div>} />
                    
                    {/* CRM Routes */}
                    <Route path="crm/leads" element={<div>Leads</div>} />
                    <Route path="crm/opportunities" element={<div>Opportunities</div>} />
                    <Route path="crm/activities" element={<div>Activities</div>} />
                    
                    {/* Accounting Routes */}
                    <Route path="accounting/ledger" element={<div>General Ledger</div>} />
                    <Route path="accounting/trial-balance" element={<div>Trial Balance</div>} />
                    <Route path="accounting/entries" element={<div>Journal Entries</div>} />
                    
                    {/* Reports */}
                    <Route path="reports" element={<div>Reports</div>} />
                    
                    {/* Settings */}
                    <Route path="settings" element={<div>Settings</div>} />
                    <Route path="profile" element={<div>Profile</div>} />
                  </Route>

                  {/* Catch all */}
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Router>
            </CustomThemeProvider>
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;