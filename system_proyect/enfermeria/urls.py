# enfermeria/urls.py

from django.urls import path
from . import views

app_name = 'enfermeria'

urlpatterns = [
    # Dashboard de Enfermería
    path('', views.enfermeria_dashboard, name='enfermeria_dashboard'),

    # Atención Médica
    path('atencion/', views.atencion_list, name='atencion_list'),
    path('atencion/nuevo/', views.atencion_create, name='atencion_create'),
    path('atencion/<int:pk>/edit/', views.atencion_edit, name='atencion_edit'),
    path('atencion/<int:pk>/delete/', views.atencion_delete, name='atencion_delete'),
    path('atencion/<int:pk>/pdf/', views.atencion_download_pdf, name='atencion_pdf'),

    # Inventario de Medicamentos (sólo listado inicial)
    path('inventario/', views.inventario_list, name='inventario_list'),
]
