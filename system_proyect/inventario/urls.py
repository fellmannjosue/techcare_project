# inventario/urls.py
from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'inventario'

urlpatterns = [
    # 1) Dashboard con los 8 botones
    path('', views.dashboard, name='dashboard'),

    # 2) Formulario + lista genérica por categoría
    path('por_categoria/', views.inventario_por_categoria, name='inventario_por_categoria'),

    # 3) Descargar PDF de un item concreto
    path('download_item_pdf/<int:item_id>/', views.download_item_pdf, name='download_item_pdf'),

    # 4) Formularios individuales
    path('computadoras/', views.inventario_computadoras, name='inventario_computadoras'),
    path('televisores/',  views.inventario_televisores,  name='inventario_televisores'),
    path('impresoras/',   views.inventario_impresoras,   name='inventario_impresoras'),
    path('routers/',      views.inventario_routers,      name='inventario_routers'),
    path('datashows/',    views.inventario_datashows,    name='inventario_datashows'),

    # 5) Ver registros en tabla desplegable
    path('registros/', views.inventario_registros, name='inventario_registros'),

    # 6) Regresar al menú principal de Cuentas
    path('menu/', lambda req: redirect('accounts:menu'), name='menu'),
]
