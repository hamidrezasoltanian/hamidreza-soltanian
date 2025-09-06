from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonnelViewSet, PersonnelContactViewSet, PersonnelDocumentViewSet

router = DefaultRouter()
router.register(r'personnel', PersonnelViewSet)
router.register(r'contacts', PersonnelContactViewSet)
router.register(r'documents', PersonnelDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]