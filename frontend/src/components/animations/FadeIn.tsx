import React from 'react';
import { Fade, FadeProps } from '@mui/material';
import { motion, MotionProps } from 'framer-motion';

interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  duration = 0.6,
  direction = 'up',
  distance = 20,
}) => {
  const directionMap = {
    up: { y: distance, x: 0 },
    down: { y: -distance, x: 0 },
    left: { y: 0, x: distance },
    right: { y: 0, x: -distance },
  };

  const initial = directionMap[direction];

  return (
    <motion.div
      initial={{ 
        opacity: 0, 
        ...initial 
      }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        y: 0 
      }}
      transition={{
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
    >
      {children}
    </motion.div>
  );
};

interface StaggerContainerProps {
  children: React.ReactNode;
  staggerDelay?: number;
}

export const StaggerContainer: React.FC<StaggerContainerProps> = ({
  children,
  staggerDelay = 0.1,
}) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }}
    >
      {children}
    </motion.div>
  );
};

interface StaggerItemProps {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
}

export const StaggerItem: React.FC<StaggerItemProps> = ({
  children,
  direction = 'up',
  distance = 20,
}) => {
  const directionMap = {
    up: { y: distance, x: 0 },
    down: { y: -distance, x: 0 },
    left: { y: 0, x: distance },
    right: { y: 0, x: -distance },
  };

  const initial = directionMap[direction];

  return (
    <motion.div
      variants={{
        hidden: { 
          opacity: 0, 
          ...initial 
        },
        visible: { 
          opacity: 1, 
          x: 0, 
          y: 0,
          transition: {
            duration: 0.6,
            ease: [0.4, 0, 0.2, 1],
          },
        },
      }}
    >
      {children}
    </motion.div>
  );
};

interface ScaleInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  scale?: number;
}

export const ScaleIn: React.FC<ScaleInProps> = ({
  children,
  delay = 0,
  duration = 0.5,
  scale = 0.8,
}) => {
  return (
    <motion.div
      initial={{ 
        opacity: 0, 
        scale 
      }}
      animate={{ 
        opacity: 1, 
        scale: 1 
      }}
      transition={{
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
    >
      {children}
    </motion.div>
  );
};

interface SlideInProps {
  children: React.ReactNode;
  direction?: 'left' | 'right' | 'up' | 'down';
  delay?: number;
  duration?: number;
  distance?: number;
}

export const SlideIn: React.FC<SlideInProps> = ({
  children,
  direction = 'left',
  delay = 0,
  duration = 0.6,
  distance = 100,
}) => {
  const directionMap = {
    left: { x: -distance, y: 0 },
    right: { x: distance, y: 0 },
    up: { x: 0, y: -distance },
    down: { x: 0, y: distance },
  };

  const initial = directionMap[direction];

  return (
    <motion.div
      initial={{ 
        opacity: 0, 
        ...initial 
      }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        y: 0 
      }}
      transition={{
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
    >
      {children}
    </motion.div>
  );
};

interface BounceInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}

export const BounceIn: React.FC<BounceInProps> = ({
  children,
  delay = 0,
  duration = 0.8,
}) => {
  return (
    <motion.div
      initial={{ 
        opacity: 0, 
        scale: 0.3 
      }}
      animate={{ 
        opacity: 1, 
        scale: 1 
      }}
      transition={{
        duration,
        delay,
        ease: [0.68, -0.55, 0.265, 1.55],
      }}
    >
      {children}
    </motion.div>
  );
};

interface RotateInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  angle?: number;
}

export const RotateIn: React.FC<RotateInProps> = ({
  children,
  delay = 0,
  duration = 0.6,
  angle = 180,
}) => {
  return (
    <motion.div
      initial={{ 
        opacity: 0, 
        rotate: angle 
      }}
      animate={{ 
        opacity: 1, 
        rotate: 0 
      }}
      transition={{
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }}
    >
      {children}
    </motion.div>
  );
};

interface HoverScaleProps {
  children: React.ReactNode;
  scale?: number;
  duration?: number;
}

export const HoverScale: React.FC<HoverScaleProps> = ({
  children,
  scale = 1.05,
  duration = 0.2,
}) => {
  return (
    <motion.div
      whileHover={{ 
        scale,
        transition: { duration }
      }}
      whileTap={{ 
        scale: 0.95,
        transition: { duration: 0.1 }
      }}
    >
      {children}
    </motion.div>
  );
};

interface PulseProps {
  children: React.ReactNode;
  duration?: number;
  scale?: number;
}

export const Pulse: React.FC<PulseProps> = ({
  children,
  duration = 2,
  scale = 1.1,
}) => {
  return (
    <motion.div
      animate={{ 
        scale: [1, scale, 1],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {children}
    </motion.div>
  );
};