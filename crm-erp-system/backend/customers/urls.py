from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerCategoryViewSet, CustomerCategoryMembershipViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'categories', CustomerCategoryViewSet)
router.register(r'memberships', CustomerCategoryMembershipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]