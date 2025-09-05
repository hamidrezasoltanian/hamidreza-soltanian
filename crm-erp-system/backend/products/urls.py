from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, ProductCategoryViewSet, ProductImageViewSet,
    ProductAttributeViewSet, ProductAttributeValueViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'images', ProductImageViewSet)
router.register(r'attributes', ProductAttributeViewSet)
router.register(r'attribute-values', ProductAttributeValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]