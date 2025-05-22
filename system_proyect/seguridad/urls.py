# seguridad/urls.py

from django.urls import path
from . import views

app_name = 'seguridad'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),

    # Inventario de cámaras
    path(
        'inventario/',
        views.inventario_list,
        name='inventario_list'
    ),
    path(
        'inventario/nuevo/',
        views.inventario_create,
        name='inventario_create'
    ),

    # Sistema contable de cámaras
    path(
        'contable/',
        views.contable_list,
        name='contable_list'
    ),
    path(
        'contable/nuevo/',
        views.contable_create,
        name='contable_create'
    ),

    # Identificación de cámaras y gabinetes
    path(
        'identificacion/',
        views.identificacion_list,
        name='identificacion_list'
    ),
    path(
        'identificacion/nuevo/',
        views.identificacion_create,
        name='identificacion_create'
    ),
]
