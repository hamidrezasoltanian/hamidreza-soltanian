import React, { useState, useRef, useEffect } from 'react';
import { Box, useTheme } from '@mui/material';

interface TouchGesturesProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinch?: (scale: number) => void;
  onTap?: () => void;
  onDoubleTap?: () => void;
  onLongPress?: () => void;
  swipeThreshold?: number;
  longPressDelay?: number;
  className?: string;
}

export const TouchGestures: React.FC<TouchGesturesProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinch,
  onTap,
  onDoubleTap,
  onLongPress,
  swipeThreshold = 50,
  longPressDelay = 500,
  className,
}) => {
  const theme = useTheme();
  const [touchStart, setTouchStart] = useState<{ x: number; y: number; time: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number; time: number } | null>(null);
  const [lastTap, setLastTap] = useState<number>(0);
  const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);
  const [pinchStart, setPinchStart] = useState<{ distance: number; scale: number } | null>(null);
  const [currentScale, setCurrentScale] = useState(1);
  
  const containerRef = useRef<HTMLDivElement>(null);

  const getDistance = (touch1: Touch, touch2: Touch) => {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  };

  const getAngle = (touch1: Touch, touch2: Touch) => {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.atan2(dy, dx) * 180 / Math.PI;
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    const now = Date.now();
    
    setTouchStart({ x: touch.clientX, y: touch.clientY, time: now });
    setTouchEnd(null);

    // Long press detection
    if (longPressDelay > 0) {
      const timer = setTimeout(() => {
        onLongPress?.();
      }, longPressDelay);
      setLongPressTimer(timer);
    }

    // Pinch detection
    if (e.touches.length === 2) {
      const distance = getDistance(e.touches[0], e.touches[1]);
      setPinchStart({ distance, scale: currentScale });
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchEnd({ x: touch.clientX, y: touch.clientY, time: Date.now() });

    // Cancel long press if moved
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }

    // Handle pinch
    if (e.touches.length === 2 && pinchStart) {
      const distance = getDistance(e.touches[0], e.touches[1]);
      const scale = (distance / pinchStart.distance) * pinchStart.scale;
      setCurrentScale(scale);
      onPinch?.(scale);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    // Clear long press timer
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }

    if (!touchStart || !touchEnd) return;

    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;
    const deltaTime = touchEnd.time - touchStart.time;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    const velocity = distance / deltaTime;

    // Reset pinch
    setPinchStart(null);

    // Swipe detection
    if (distance > swipeThreshold && velocity > 0.1) {
      const angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;
      
      if (Math.abs(angle) < 30) {
        // Horizontal swipe
        if (deltaX > 0) {
          onSwipeRight?.();
        } else {
          onSwipeLeft?.();
        }
      } else if (Math.abs(angle) > 150) {
        // Vertical swipe
        if (deltaY > 0) {
          onSwipeDown?.();
        } else {
          onSwipeUp?.();
        }
      }
    } else if (distance < 10 && deltaTime < 300) {
      // Tap detection
      const now = Date.now();
      if (now - lastTap < 300) {
        // Double tap
        onDoubleTap?.();
        setLastTap(0);
      } else {
        // Single tap
        onTap?.();
        setLastTap(now);
      }
    }
  };

  const handleTouchCancel = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
    setPinchStart(null);
  };

  useEffect(() => {
    return () => {
      if (longPressTimer) {
        clearTimeout(longPressTimer);
      }
    };
  }, [longPressTimer]);

  return (
    <Box
      ref={containerRef}
      className={className}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      onTouchCancel={handleTouchCancel}
      sx={{
        touchAction: 'pan-x pan-y pinch-zoom',
        userSelect: 'none',
        WebkitUserSelect: 'none',
        transform: `scale(${currentScale})`,
        transformOrigin: 'center center',
        transition: currentScale === 1 ? 'transform 0.2s ease' : 'none',
      }}
    >
      {children}
    </Box>
  );
};

// Swipeable List Item
interface SwipeableListItemProps {
  children: React.ReactNode;
  leftAction?: {
    icon: React.ReactNode;
    label: string;
    color?: string;
    onClick: () => void;
  };
  rightAction?: {
    icon: React.ReactNode;
    label: string;
    color?: string;
    onClick: () => void;
  };
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

export const SwipeableListItem: React.FC<SwipeableListItemProps> = ({
  children,
  leftAction,
  rightAction,
  onSwipeLeft,
  onSwipeRight,
}) => {
  const theme = useTheme();
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isSwiping, setIsSwiping] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY, time: Date.now() });
    setIsSwiping(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isSwiping) return;
    
    const touch = e.touches[0];
    const deltaX = touch.clientX - (touchStart?.x || 0);
    const deltaY = touch.clientY - (touchStart?.y || 0);
    
    // Only handle horizontal swipes
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      e.preventDefault();
      setSwipeOffset(deltaX);
      setSwipeDirection(deltaX > 0 ? 'right' : 'left');
    }
  };

  const handleTouchEnd = () => {
    if (!isSwiping) return;
    
    const threshold = 100;
    
    if (Math.abs(swipeOffset) > threshold) {
      if (swipeDirection === 'left' && onSwipeLeft) {
        onSwipeLeft();
      } else if (swipeDirection === 'right' && onSwipeRight) {
        onSwipeRight();
      }
    }
    
    setSwipeOffset(0);
    setIsSwiping(false);
    setSwipeDirection(null);
  };

  return (
    <Box
      sx={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 2,
      }}
    >
      {/* Action Buttons */}
      {(leftAction || rightAction) && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: 2,
            zIndex: 1,
          }}
        >
          {leftAction && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                color: leftAction.color || 'white',
                backgroundColor: leftAction.color || theme.palette.primary.main,
                padding: 1,
                borderRadius: 1,
                opacity: swipeDirection === 'right' ? 1 : 0,
                transform: `translateX(${swipeDirection === 'right' ? swipeOffset - 100 : -100}px)`,
                transition: 'all 0.2s ease',
              }}
            >
              {leftAction.icon}
              <span>{leftAction.label}</span>
            </Box>
          )}
          
          {rightAction && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                color: rightAction.color || 'white',
                backgroundColor: rightAction.color || theme.palette.error.main,
                padding: 1,
                borderRadius: 1,
                opacity: swipeDirection === 'left' ? 1 : 0,
                transform: `translateX(${swipeDirection === 'left' ? swipeOffset + 100 : 100}px)`,
                transition: 'all 0.2s ease',
              }}
            >
              {rightAction.icon}
              <span>{rightAction.label}</span>
            </Box>
          )}
        </Box>
      )}

      {/* Content */}
      <Box
        sx={{
          transform: `translateX(${swipeOffset}px)`,
          transition: isSwiping ? 'none' : 'transform 0.2s ease',
          backgroundColor: theme.palette.background.paper,
          borderRadius: 2,
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {children}
      </Box>
    </Box>
  );
};

// Pull to Refresh
interface PullToRefreshProps {
  children: React.ReactNode;
  onRefresh: () => Promise<void>;
  threshold?: number;
  disabled?: boolean;
}

export const PullToRefresh: React.FC<PullToRefreshProps> = ({
  children,
  onRefresh,
  threshold = 80,
  disabled = false,
}) => {
  const theme = useTheme();
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [canPull, setCanPull] = useState(true);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled || isRefreshing) return;
    
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY, time: Date.now() });
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (disabled || isRefreshing || !canPull) return;
    
    const touch = e.touches[0];
    const deltaY = touch.clientY - (touchStart?.y || 0);
    
    if (deltaY > 0 && window.scrollY === 0) {
      e.preventDefault();
      const distance = Math.min(deltaY * 0.5, threshold * 1.5);
      setPullDistance(distance);
    }
  };

  const handleTouchEnd = async () => {
    if (disabled || isRefreshing) return;
    
    if (pullDistance > threshold) {
      setIsRefreshing(true);
      setCanPull(false);
      
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
        setPullDistance(0);
        setTimeout(() => setCanPull(true), 1000);
      }
    } else {
      setPullDistance(0);
    }
  };

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Pull Indicator */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: pullDistance,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: theme.palette.primary.main,
          color: 'white',
          transform: `translateY(${Math.max(0, pullDistance - threshold)}px)`,
          transition: 'transform 0.2s ease',
        }}
      >
        {isRefreshing ? (
          <Typography variant="body2">در حال به‌روزرسانی...</Typography>
        ) : pullDistance > threshold ? (
          <Typography variant="body2">رها کنید تا به‌روزرسانی شود</Typography>
        ) : (
          <Typography variant="body2">کشیدن برای به‌روزرسانی</Typography>
        )}
      </Box>

      {/* Content */}
      <Box
        sx={{
          transform: `translateY(${pullDistance}px)`,
          transition: isRefreshing ? 'none' : 'transform 0.2s ease',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};