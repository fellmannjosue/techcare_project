from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Agregado para autenticación
    path('tickets/', include('tickets.urls')),
    path('inventario/', include('inventario.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
    path('citas_billingue/', include('citas_billingue.urls')),
    path('citas_colegio/', include('citas_colegio.urls')),
    path('sponsors/', include ('sponsors.urls')),
]
