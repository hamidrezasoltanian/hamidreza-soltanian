import React, { useState } from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import Sidebar from './layout/Sidebar';
import TopBar from './layout/TopBar';
import { FadeIn } from './animations/FadeIn';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onToggle={handleSidebarToggle}
        variant={isMobile ? 'temporary' : 'persistent'}
      />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: isMobile ? 0 : sidebarOpen ? '280px' : 0,
        }}
      >
        {/* Top Bar */}
        <TopBar onMenuToggle={handleSidebarToggle} />

        {/* Page Content */}
        <FadeIn>
          <Box
            sx={{
              flexGrow: 1,
              p: { xs: 2, sm: 3 },
              background: theme.palette.mode === 'dark' 
                ? 'linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%)'
                : 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)',
              minHeight: 'calc(100vh - 64px)',
            }}
          >
            {children}
          </Box>
        </FadeIn>
      </Box>
    </Box>
  );
};

export default Layout;