# inventario/urls.py

from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard principal del módulo de inventario
    path('', views.dashboard, name='dashboard'),

    # Listado y edición inline de categorías de todos los ítems
    path('por_categoria/', views.inventario_por_categoria, name='inventario_por_categoria'),

    # Listado y creación de Computadoras
    path('computadoras/', views.inventario_computadoras, name='inventario_computadoras'),
    # Listado de Computadoras con formulario de filtrado por campos
    path('computadoras/filtro/', views.computadoras_list, name='filtro_computadoras'),

    # Listado y creación de Televisores
    path('televisores/', views.inventario_televisores, name='inventario_televisores'),

    # Listado y creación de Impresoras
    path('impresoras/', views.inventario_impresoras, name='inventario_impresoras'),

    # Listado y creación de Routers
    path('routers/', views.inventario_routers, name='inventario_routers'),

    # Listado y creación de DataShows
    path('datashows/', views.inventario_datashows, name='inventario_datashows'),

    # Listado consolidado de todos los registros (sin edición inline)
    path('registros/', views.inventario_registros, name='inventario_registros'),

    # Generar y descargar ficha PDF para cualquier tipo de ítem
    path('download/<str:tipo>/<int:pk>/', views.download_model_pdf, name='download_model_pdf'),

    # Generar y descargar código QR que apunta al PDF de ficha
    path('registros/qr/<str:tipo>/<int:pk>/', views.descargar_qr, name='descargar_qr'),

    # Atajo para volver al menú principal de cuentas
    path('menu/', lambda req: redirect('accounts:menu'), name='menu'),
]
