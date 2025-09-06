from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalesProcessViewSet, ProcessStageViewSet, ProcessActivityViewSet,
    LeadViewSet, TaskViewSet
)

router = DefaultRouter()
router.register(r'sales-processes', SalesProcessViewSet)
router.register(r'process-stages', ProcessStageViewSet)
router.register(r'process-activities', ProcessActivityViewSet)
router.register(r'leads', LeadViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]