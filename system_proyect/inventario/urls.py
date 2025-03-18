from django.urls import path
from . import views
from accounts.views import menu_view  # Importa correctamente la vista de `accounts`

urlpatterns = [
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    path('download_item_pdf/<int:item_id>/', views.download_item_pdf, name='download_item_pdf'),
    path('menu/', menu_view, name='menu'),  # Usa `menu_view` como callable
]
