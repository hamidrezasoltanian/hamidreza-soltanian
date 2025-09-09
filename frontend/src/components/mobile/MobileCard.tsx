import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  IconButton,
  Chip,
  Avatar,
  Stack,
  useTheme,
  alpha,
  SwipeableDrawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  MoreVert,
  Share,
  Bookmark,
  Delete,
  Edit,
  Phone,
  Email,
  LocationOn,
  AccessTime,
  Star,
  StarBorder,
} from '@mui/icons-material';
import { FadeIn, HoverScale, SwipeIn } from '../animations/FadeIn';

interface MobileCardProps {
  title: string;
  subtitle?: string;
  description?: string;
  avatar?: string;
  image?: string;
  tags?: string[];
  actions?: React.ReactNode;
  onEdit?: () => void;
  onDelete?: () => void;
  onShare?: () => void;
  onBookmark?: () => void;
  onCall?: () => void;
  onEmail?: () => void;
  onLocation?: () => void;
  rating?: number;
  timestamp?: string;
  status?: 'active' | 'inactive' | 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  variant?: 'default' | 'compact' | 'detailed';
  swipeable?: boolean;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

export const MobileCard: React.FC<MobileCardProps> = ({
  title,
  subtitle,
  description,
  avatar,
  image,
  tags = [],
  actions,
  onEdit,
  onDelete,
  onShare,
  onBookmark,
  onCall,
  onEmail,
  onLocation,
  rating,
  timestamp,
  status = 'active',
  priority = 'medium',
  variant = 'default',
  swipeable = false,
  onSwipeLeft,
  onSwipeRight,
}) => {
  const theme = useTheme();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'pending': return 'warning';
      case 'completed': return 'info';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
      <IconButton
        key={index}
        size="small"
        sx={{ p: 0.25 }}
      >
        {index < rating ? <Star color="warning" /> : <StarBorder />}
      </IconButton>
    ));
  };

  const renderActions = () => {
    if (actions) return actions;

    return (
      <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
        {onCall && (
          <IconButton size="small" onClick={onCall} color="primary">
            <Phone />
          </IconButton>
        )}
        {onEmail && (
          <IconButton size="small" onClick={onEmail} color="primary">
            <Email />
          </IconButton>
        )}
        {onLocation && (
          <IconButton size="small" onClick={onLocation} color="primary">
            <LocationOn />
          </IconButton>
        )}
        {onBookmark && (
          <IconButton size="small" onClick={onBookmark} color="secondary">
            <Bookmark />
          </IconButton>
        )}
        {onShare && (
          <IconButton size="small" onClick={onShare} color="primary">
            <Share />
          </IconButton>
        )}
        <IconButton size="small" onClick={() => setDrawerOpen(true)}>
          <MoreVert />
        </IconButton>
      </Stack>
    );
  };

  const cardContent = (
    <Card
      sx={{
        borderRadius: 3,
        boxShadow: theme.shadows[2],
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: theme.shadows[4],
          transform: 'translateY(-2px)',
        },
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Priority Indicator */}
      {priority !== 'medium' && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 4,
            height: '100%',
            backgroundColor: theme.palette[getPriorityColor(priority) as any]?.main || theme.palette.primary.main,
            zIndex: 1,
          }}
        />
      )}

      {/* Header */}
      <CardContent sx={{ p: 2, pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          {/* Avatar/Image */}
          <Box sx={{ position: 'relative' }}>
            {image ? (
              <Box
                sx={{
                  width: 56,
                  height: 56,
                  borderRadius: 2,
                  backgroundImage: `url(${image})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              />
            ) : (
              <Avatar
                sx={{
                  width: 56,
                  height: 56,
                  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  fontSize: '1.25rem',
                  fontWeight: 600,
                }}
              >
                {avatar || title[0]}
              </Avatar>
            )}
            
            {/* Status Badge */}
            <Chip
              label={status}
              size="small"
              color={getStatusColor(status) as any}
              sx={{
                position: 'absolute',
                top: -8,
                right: -8,
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          </Box>

          {/* Content */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                mb: 0.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {title}
            </Typography>
            
            {subtitle && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mb: 0.5,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {subtitle}
              </Typography>
            )}

            {/* Rating */}
            {rating && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                {renderStars(rating)}
                <Typography variant="caption" color="text.secondary">
                  ({rating}/5)
                </Typography>
              </Box>
            )}

            {/* Timestamp */}
            {timestamp && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                <AccessTime sx={{ fontSize: 14, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {timestamp}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>

        {/* Description */}
        {description && variant === 'detailed' && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 2,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {description}
          </Typography>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 1 }}>
            {tags.map((tag, index) => (
              <Chip
                key={index}
                label={tag}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            ))}
          </Stack>
        )}
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ p: 2, pt: 0 }}>
        {renderActions()}
      </CardActions>
    </Card>
  );

  if (swipeable) {
    return (
      <SwipeIn
        onSwipeLeft={onSwipeLeft}
        onSwipeRight={onSwipeRight}
      >
        {cardContent}
      </SwipeIn>
    );
  }

  return (
    <FadeIn>
      <HoverScale>
        {cardContent}
      </HoverScale>
    </FadeIn>
  );
};

// Swipeable Drawer for Actions
const ActionDrawer: React.FC<{
  open: boolean;
  onClose: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onShare?: () => void;
  onBookmark?: () => void;
}> = ({ open, onClose, onEdit, onDelete, onShare, onBookmark }) => {
  const actions = [
    { icon: <Edit />, text: 'ویرایش', action: onEdit },
    { icon: <Share />, text: 'اشتراک‌گذاری', action: onShare },
    { icon: <Bookmark />, text: 'نشان کردن', action: onBookmark },
    { icon: <Delete />, text: 'حذف', action: onDelete, color: 'error' },
  ];

  return (
    <SwipeableDrawer
      anchor="bottom"
      open={open}
      onClose={onClose}
      onOpen={() => {}}
      PaperProps={{
        sx: {
          borderTopLeftRadius: 16,
          borderTopRightRadius: 16,
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 2, textAlign: 'center' }}>
          عملیات
        </Typography>
        <List>
          {actions.map((action, index) => (
            <ListItem
              key={index}
              button
              onClick={() => {
                action.action?.();
                onClose();
              }}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                color: action.color === 'error' ? 'error.main' : 'text.primary',
              }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>
                {action.icon}
              </ListItemIcon>
              <ListItemText primary={action.text} />
            </ListItem>
          ))}
        </List>
      </Box>
    </SwipeableDrawer>
  );
};