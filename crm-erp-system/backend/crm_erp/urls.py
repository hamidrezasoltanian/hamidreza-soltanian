from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/customers/', include('customers.urls')),
    path('api/v1/personnel/', include('personnel.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/invoices/', include('invoices.urls')),
    path('api/v1/crm/', include('crm.urls')),
    path('api/v1/accounting/', include('accounting.urls')),
    path('api/v1/tax/', include('tax_system.urls')),
    path('api/v1/reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)