from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet, ReportExecutionViewSet, ReportScheduleViewSet,
    DashboardViewSet, DashboardWidgetViewSet
)

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet)
router.register(r'executions', ReportExecutionViewSet)
router.register(r'schedules', ReportScheduleViewSet)
router.register(r'dashboards', DashboardViewSet)
router.register(r'widgets', DashboardWidgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]