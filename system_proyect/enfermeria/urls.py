from django.urls import path
from . import views

app_name = 'enfermeria'

urlpatterns = [
    # Dashboard principal
    path('', views.enfermeria_dashboard, name='enfermeria_dashboard'),

    # Atención Médica (una sola vista y su PDF)
    path('atencion/', views.atencion_form, name='atencion_form'),
    path('atencion/pdf/<int:pk>/', views.atencion_download_pdf, name='atencion_pdf'),

    # Inventario de Medicamentos
    path('inventario/', views.inventario_list, name='inventario_list'),
    path('inventario/nuevo/', views.inventario_create, name='inventario_create'),
    path('inventario/<int:pk>/editar/', views.inventario_edit_cantidad, name='inventario_edit'),
    path('inventario/uso/', views.uso_create, name='uso_create'),
    path('inventario/pdf/<int:pk>/', views.inventario_pdf, name='inventario_pdf'),
]
