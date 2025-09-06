from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaxPayerViewSet, TaxRateViewSet, TaxTransactionViewSet

router = DefaultRouter()
router.register(r'taxpayers', TaxPayerViewSet)
router.register(r'tax-rates', TaxRateViewSet)
router.register(r'tax-transactions', TaxTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]