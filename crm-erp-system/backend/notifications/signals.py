from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from customers.models import Customer
from invoices.models import Invoice
from products.models import Product
import json


channel_layer = get_channel_layer()


def send_notification_to_user(user, notification_data):
    """Send notification to specific user via WebSocket"""
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"notifications_user_{user.id}",
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )


def send_dashboard_update_to_user(user, update_type, data):
    """Send dashboard update to specific user via WebSocket"""
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"dashboard_dashboard_{user.id}",
            {
                'type': 'dashboard_update',
                'update_type': update_type,
                'data': data
            }
        )


@receiver(post_save, sender=Customer)
def customer_created_updated(sender, instance, created, **kwargs):
    """Send notification when customer is created or updated"""
    if created:
        # Notify all admin users about new customer
        admin_users = User.objects.filter(is_staff=True)
        for user in admin_users:
            notification = Notification.objects.create(
                user=user,
                title="مشتری جدید",
                message=f"مشتری جدید '{instance.get_full_name()}' اضافه شد",
                notification_type="customer_created",
                data={
                    'customer_id': instance.id,
                    'customer_name': instance.get_full_name()
                }
            )
            
            # Send real-time notification
            from .serializers import NotificationSerializer
            notification_data = NotificationSerializer(notification).data
            send_notification_to_user(user, notification_data)
            
            # Send dashboard update
            send_dashboard_update_to_user(user, 'customer_update', {
                'action': 'created',
                'customer': {
                    'id': instance.id,
                    'name': instance.get_full_name(),
                    'type': instance.customer_type
                }
            })
    else:
        # Notify about customer update
        if hasattr(instance, '_updated_fields'):
            updated_fields = instance._updated_fields
            if updated_fields:
                # Send dashboard update to relevant users
                send_dashboard_update_to_user(instance.created_by, 'customer_update', {
                    'action': 'updated',
                    'customer': {
                        'id': instance.id,
                        'name': instance.get_full_name(),
                        'updated_fields': updated_fields
                    }
                })


@receiver(post_save, sender=Invoice)
def invoice_created_updated(sender, instance, created, **kwargs):
    """Send notification when invoice is created or updated"""
    if created:
        # Notify customer owner and admin users
        users_to_notify = [instance.customer.created_by]
        users_to_notify.extend(User.objects.filter(is_staff=True))
        
        for user in users_to_notify:
            notification = Notification.objects.create(
                user=user,
                title="فاکتور جدید",
                message=f"فاکتور جدید برای مشتری '{instance.customer.get_full_name()}' ایجاد شد",
                notification_type="invoice_created",
                data={
                    'invoice_id': instance.id,
                    'customer_name': instance.customer.get_full_name(),
                    'amount': str(instance.total_amount)
                }
            )
            
            # Send real-time notification
            from .serializers import NotificationSerializer
            notification_data = NotificationSerializer(notification).data
            send_notification_to_user(user, notification_data)
            
            # Send dashboard update
            send_dashboard_update_to_user(user, 'invoice_update', {
                'action': 'created',
                'invoice': {
                    'id': instance.id,
                    'customer_name': instance.customer.get_full_name(),
                    'amount': str(instance.total_amount),
                    'status': instance.status
                }
            })


@receiver(post_save, sender=Product)
def product_created_updated(sender, instance, created, **kwargs):
    """Send notification when product is created or updated"""
    if created:
        # Notify all admin users about new product
        admin_users = User.objects.filter(is_staff=True)
        for user in admin_users:
            notification = Notification.objects.create(
                user=user,
                title="محصول جدید",
                message=f"محصول جدید '{instance.name}' اضافه شد",
                notification_type="product_created",
                data={
                    'product_id': instance.id,
                    'product_name': instance.name
                }
            )
            
            # Send real-time notification
            from .serializers import NotificationSerializer
            notification_data = NotificationSerializer(notification).data
            send_notification_to_user(user, notification_data)
            
            # Send dashboard update
            send_dashboard_update_to_user(user, 'product_update', {
                'action': 'created',
                'product': {
                    'id': instance.id,
                    'name': instance.name,
                    'category': instance.category.name if instance.category else None
                }
            })


@receiver(post_delete, sender=Customer)
def customer_deleted(sender, instance, **kwargs):
    """Send notification when customer is deleted"""
    # Notify admin users about customer deletion
    admin_users = User.objects.filter(is_staff=True)
    for user in admin_users:
        notification = Notification.objects.create(
            user=user,
            title="حذف مشتری",
            message=f"مشتری '{instance.get_full_name()}' حذف شد",
            notification_type="customer_deleted",
            data={
                'customer_name': instance.get_full_name()
            }
        )
        
        # Send real-time notification
        from .serializers import NotificationSerializer
        notification_data = NotificationSerializer(notification).data
        send_notification_to_user(user, notification_data)
        
        # Send dashboard update
        send_dashboard_update_to_user(user, 'customer_update', {
            'action': 'deleted',
            'customer': {
                'id': instance.id,
                'name': instance.get_full_name()
            }
        })