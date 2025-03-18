from django.urls import path
from . import views
from accounts.views import menu_view  # Importa correctamente la vista de `accounts`

urlpatterns = [
    path('', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('download_maintenance_pdf/<int:record_id>/', views.download_maintenance_pdf, name='download_maintenance_pdf'),
    path('menu/', menu_view, name='menu'),  # Usa `menu_view` como callable
]
