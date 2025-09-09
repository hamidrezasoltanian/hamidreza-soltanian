import React from 'react';
import {
  Card,
  CardContent,
  CardProps,
  Box,
  alpha,
  useTheme,
} from '@mui/material';
import { motion, MotionProps } from 'framer-motion';
import { FadeIn } from '../animations/FadeIn';

interface AnimatedCardProps extends Omit<CardProps, 'component'> {
  children: React.ReactNode;
  delay?: number;
  hover?: boolean;
  gradient?: boolean;
  glow?: boolean;
  glowColor?: string;
  motionProps?: MotionProps;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  delay = 0,
  hover = true,
  gradient = false,
  glow = false,
  glowColor,
  motionProps,
  sx,
  ...props
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 20,
      scale: 0.95,
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: {
        duration: 0.6,
        delay,
        ease: [0.4, 0, 0.2, 1],
      },
    },
    hover: hover ? {
      y: -8,
      scale: 1.02,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1],
      },
    } : {},
  };

  const gradientSx = gradient ? {
    background: isDark 
      ? `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`
      : `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
  } : {};

  const glowSx = glow ? {
    position: 'relative',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      borderRadius: 'inherit',
      padding: '2px',
      background: glowColor 
        ? `linear-gradient(135deg, ${glowColor}, transparent)`
        : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
      mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
      maskComposite: 'xor',
      WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
      WebkitMaskComposite: 'xor',
    },
  } : {};

  return (
    <FadeIn delay={delay}>
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        whileHover="hover"
        {...motionProps}
      >
        <Card
          sx={{
            borderRadius: 3,
            boxShadow: isDark 
              ? '0 4px 20px rgba(0, 0, 0, 0.3)' 
              : '0 4px 20px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden',
            position: 'relative',
            ...gradientSx,
            ...glowSx,
            ...sx,
          }}
          {...props}
        >
          {children}
        </Card>
      </motion.div>
    </FadeIn>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  delay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'primary',
  delay = 0,
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const colorMap = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    success: theme.palette.success.main,
    warning: theme.palette.warning.main,
    error: theme.palette.error.main,
  };

  const selectedColor = colorMap[color];

  return (
    <AnimatedCard delay={delay} hover>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Box
              sx={{
                fontSize: '0.875rem',
                fontWeight: 500,
                color: isDark ? theme.palette.text.secondary : theme.palette.text.primary,
                mb: 0.5,
              }}
            >
              {title}
            </Box>
            <Box
              sx={{
                fontSize: '2rem',
                fontWeight: 700,
                color: selectedColor,
                lineHeight: 1,
              }}
            >
              {value}
            </Box>
          </Box>
          {icon && (
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                backgroundColor: alpha(selectedColor, 0.1),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: selectedColor,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
        
        {subtitle && (
          <Box
            sx={{
              fontSize: '0.875rem',
              color: theme.palette.text.secondary,
              mb: 1,
            }}
          >
            {subtitle}
          </Box>
        )}
        
        {trend && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              fontSize: '0.875rem',
              color: trend.isPositive ? theme.palette.success.main : theme.palette.error.main,
              fontWeight: 500,
            }}
          >
            <Box
              sx={{
                mr: 0.5,
                transform: trend.isPositive ? 'rotate(0deg)' : 'rotate(180deg)',
              }}
            >
              ↗
            </Box>
            {Math.abs(trend.value)}%
          </Box>
        )}
      </CardContent>
    </AnimatedCard>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  delay?: number;
  onClick?: () => void;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  color = 'primary',
  delay = 0,
  onClick,
}) => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const colorMap = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    success: theme.palette.success.main,
    warning: theme.palette.warning.main,
    error: theme.palette.error.main,
  };

  const selectedColor = colorMap[color];

  return (
    <AnimatedCard 
      delay={delay} 
      hover 
      gradient 
      glow 
      glowColor={selectedColor}
      onClick={onClick}
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        height: '100%',
      }}
    >
      <CardContent sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box
          sx={{
            width: 64,
            height: 64,
            borderRadius: 3,
            backgroundColor: alpha(selectedColor, 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: selectedColor,
            mx: 'auto',
            mb: 2,
          }}
        >
          {icon}
        </Box>
        
        <Box
          sx={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1,
          }}
        >
          {title}
        </Box>
        
        <Box
          sx={{
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
            lineHeight: 1.6,
            flex: 1,
          }}
        >
          {description}
        </Box>
      </CardContent>
    </AnimatedCard>
  );
};