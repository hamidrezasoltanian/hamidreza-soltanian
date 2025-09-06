from rest_framework import permissions
from django.contrib.auth.models import Group


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the snippet.
        return obj.created_by == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admins.
        return request.user.is_staff


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow managers to edit objects.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to managers.
        return request.user.groups.filter(name='Managers').exists()


class IsSalesTeam(permissions.BasePermission):
    """
    Custom permission to only allow sales team members.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Sales', 'Managers']).exists()


class IsAccountingTeam(permissions.BasePermission):
    """
    Custom permission to only allow accounting team members.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Accounting', 'Managers']).exists()


class IsInventoryTeam(permissions.BasePermission):
    """
    Custom permission to only allow inventory team members.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Inventory', 'Managers']).exists()


class CanApproveInvoices(permissions.BasePermission):
    """
    Custom permission to only allow users who can approve invoices.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Managers', 'Accounting']).exists()


class CanManageUsers(permissions.BasePermission):
    """
    Custom permission to only allow users who can manage other users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name='Managers').exists()


class CanViewReports(permissions.BasePermission):
    """
    Custom permission to only allow users who can view reports.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['Managers', 'Accounting', 'Reports']).exists()


class CanManageSettings(permissions.BasePermission):
    """
    Custom permission to only allow users who can manage system settings.
    """
    
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name='Managers').exists()