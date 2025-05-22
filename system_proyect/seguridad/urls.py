# seguridad/urls.py

from django.urls import path
from . import views

app_name = 'seguridad'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),

    # Inventario de Cámaras (listado + creación vía POST)
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('inventario/<int:pk>/editar/', views.inventario_update, name='inventario_update'),
    path('inventario/<int:pk>/eliminar/', views.inventario_delete, name='inventario_delete'),

    # Sistema Contable de Cámaras (listado + creación vía POST)
    path('contable/', views.contable_list, name='contable_list'),
    path('contable/<int:pk>/editar/', views.contable_update, name='contable_update'),
    path('contable/<int:pk>/eliminar/', views.contable_delete, name='contable_delete'),

    # Identificación de Cámaras y Gabinetes (listado + creación vía POST)
    path('identificacion/', views.identificacion_list, name='identificacion_list'),
    path('identificacion/<int:pk>/editar/', views.identificacion_update, name='identificacion_update'),
    path('identificacion/<int:pk>/eliminar/', views.identificacion_delete, name='identificacion_delete'),
]
