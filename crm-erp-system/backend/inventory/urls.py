from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, InventoryItemViewSet, LotNumberViewSet,
    StockMovementViewSet, StockAdjustmentViewSet, StockAdjustmentItemViewSet
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'inventory-items', InventoryItemViewSet)
router.register(r'lot-numbers', LotNumberViewSet)
router.register(r'stock-movements', StockMovementViewSet)
router.register(r'stock-adjustments', StockAdjustmentViewSet)
router.register(r'adjustment-items', StockAdjustmentItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]