from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        # Create groups
        groups = [
            'Managers',
            'Sales',
            'Accounting',
            'Inventory',
            'Reports',
            'Customers',
        ]
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created group: {group_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group already exists: {group_name}')
                )
        
        # Assign permissions to Managers group
        managers_group = Group.objects.get(name='Managers')
        
        # Get all permissions
        all_permissions = Permission.objects.all()
        managers_group.permissions.set(all_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned all permissions to Managers group')
        )
        
        # Assign specific permissions to other groups
        self.assign_sales_permissions()
        self.assign_accounting_permissions()
        self.assign_inventory_permissions()
        self.assign_reports_permissions()
        self.assign_customers_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all groups and assigned permissions')
        )

    def assign_sales_permissions(self):
        """Assign permissions to Sales group"""
        sales_group = Group.objects.get(name='Sales')
        
        # Customer permissions
        customer_permissions = Permission.objects.filter(
            content_type__app_label='customers'
        )
        sales_group.permissions.add(*customer_permissions)
        
        # Personnel permissions
        personnel_permissions = Permission.objects.filter(
            content_type__app_label='personnel'
        )
        sales_group.permissions.add(*personnel_permissions)
        
        # CRM permissions
        crm_permissions = Permission.objects.filter(
            content_type__app_label='crm'
        )
        sales_group.permissions.add(*crm_permissions)
        
        # Invoice permissions (view and add only)
        invoice_permissions = Permission.objects.filter(
            content_type__app_label='invoices',
            codename__in=['view_invoice', 'add_invoice', 'view_quotation', 'add_quotation']
        )
        sales_group.permissions.add(*invoice_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned permissions to Sales group')
        )

    def assign_accounting_permissions(self):
        """Assign permissions to Accounting group"""
        accounting_group = Group.objects.get(name='Accounting')
        
        # Accounting permissions
        accounting_permissions = Permission.objects.filter(
            content_type__app_label='accounting'
        )
        accounting_group.permissions.add(*accounting_permissions)
        
        # Tax system permissions
        tax_permissions = Permission.objects.filter(
            content_type__app_label='tax_system'
        )
        accounting_group.permissions.add(*tax_permissions)
        
        # Invoice permissions (all)
        invoice_permissions = Permission.objects.filter(
            content_type__app_label='invoices'
        )
        accounting_group.permissions.add(*invoice_permissions)
        
        # Customer permissions (view only)
        customer_permissions = Permission.objects.filter(
            content_type__app_label='customers',
            codename='view_customer'
        )
        accounting_group.permissions.add(*customer_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned permissions to Accounting group')
        )

    def assign_inventory_permissions(self):
        """Assign permissions to Inventory group"""
        inventory_group = Group.objects.get(name='Inventory')
        
        # Inventory permissions
        inventory_permissions = Permission.objects.filter(
            content_type__app_label='inventory'
        )
        inventory_group.permissions.add(*inventory_permissions)
        
        # Product permissions
        product_permissions = Permission.objects.filter(
            content_type__app_label='products'
        )
        inventory_group.permissions.add(*product_permissions)
        
        # Invoice permissions (view only)
        invoice_permissions = Permission.objects.filter(
            content_type__app_label='invoices',
            codename='view_invoice'
        )
        inventory_group.permissions.add(*invoice_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned permissions to Inventory group')
        )

    def assign_reports_permissions(self):
        """Assign permissions to Reports group"""
        reports_group = Group.objects.get(name='Reports')
        
        # Reports permissions
        reports_permissions = Permission.objects.filter(
            content_type__app_label='reports'
        )
        reports_group.permissions.add(*reports_permissions)
        
        # View permissions for all models
        view_permissions = Permission.objects.filter(
            codename__startswith='view_'
        )
        reports_group.permissions.add(*view_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned permissions to Reports group')
        )

    def assign_customers_permissions(self):
        """Assign permissions to Customers group"""
        customers_group = Group.objects.get(name='Customers')
        
        # Limited permissions for customers
        customer_permissions = Permission.objects.filter(
            content_type__app_label='customers',
            codename__in=['view_customer', 'change_customer']
        )
        customers_group.permissions.add(*customer_permissions)
        
        # Personnel permissions (view and change own)
        personnel_permissions = Permission.objects.filter(
            content_type__app_label='personnel',
            codename__in=['view_personnel', 'change_personnel']
        )
        customers_group.permissions.add(*personnel_permissions)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully assigned permissions to Customers group')
        )