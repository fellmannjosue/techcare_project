from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Por categoría
    path('por_categoria/', views.inventario_por_categoria, name='inventario_por_categoria'),

    # Formularios individuales
    path('computadoras/', views.inventario_computadoras, name='inventario_computadoras'),
    path('televisores/',  views.inventario_televisores,  name='inventario_televisores'),
    path('impresoras/',   views.inventario_impresoras,   name='inventario_impresoras'),
    path('routers/',      views.inventario_routers,      name='inventario_routers'),
    path('datashows/',    views.inventario_datashows,    name='inventario_datashows'),

    # Ver registros
    path('registros/', views.inventario_registros, name='inventario_registros'),

    # Generar PDF dinámico para cualquier modelo
    path(
        'download/<str:tipo>/<int:pk>/',
        views.download_model_pdf,
        name='download_model_pdf'
    ),

    # Generar QR que apunta al PDF
    path(
        'registros/qr/<str:tipo>/<int:pk>/',
        views.descargar_qr,
        name='descargar_qr'
    ),

    # Volver al menú
    path('menu/', lambda req: redirect('accounts:menu'), name='menu'),
]
