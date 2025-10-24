from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='reloj_dashboard'),
    path('reporte/', views.reporte, name='reloj_reporte'),
    path('grafica/', views.grafica, name='reloj_grafica'),
    path('pdf/', views.exportar_pdf, name='reloj_exportar_pdf'),
    path('test_sql/', views.test_sqlserver_connection, name='test_sqlserver_connection'),

    # Gestión de Horarios de empleados
    path('horarios/', views.horarios_list, name='horarios_list'),
    path('horarios/agregar/', views.horarios_add, name='horarios_add'),
    path('horarios/editar/<int:pk>/', views.horarios_edit, name='horarios_edit'),

    # (Opcional) Ruta para "tiempo por hora" si decides usarla
    path('tiempo-por-hora/', views.tiempo_por_hora, name='tiempo_por_hora'),
]
