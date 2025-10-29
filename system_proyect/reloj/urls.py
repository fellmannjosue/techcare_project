from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='reloj_dashboard'),

    # Reportes
    path('reporte/', views.reporte, name='reloj_reporte'),
    path('pdf/', views.exportar_pdf, name='reloj_exportar_pdf'),

    # Gráfica (pie) + detalle para modal
    path('grafica/', views.grafica, name='reloj_grafica'),
    path('grafica/detalle/', views.grafica_detalle, name='reloj_grafica_detalle'),

    # Diagnóstico conexión
    path('test_sql/', views.test_sqlserver_connection, name='test_sqlserver_connection'),

    # ─────────────────────────────────────────────
    # Gestión de PLANTILLAS y REGLAS
    # ─────────────────────────────────────────────
    path('plantillas/', views.plantilla_list, name='reloj_plantilla_list'),
    path('plantillas/nueva/', views.plantilla_edit, name='reloj_plantilla_new'),
    path('plantillas/<int:pk>/', views.plantilla_edit, name='reloj_plantilla_edit'),
    path('plantillas/<int:template_pk>/regla/nueva/', views.regla_add, name='reloj_regla_add'),
    path('regla/<int:pk>/', views.regla_edit, name='reloj_regla_edit'),

    # ─────────────────────────────────────────────
    # Gestión de Horarios por Empleado (ASIGNACIONES)
    # (Se mantienen los nombres para no romper enlaces previos)
    # ─────────────────────────────────────────────
    path('horarios/', views.horarios_list, name='horarios_list'),
    path('horarios/agregar/', views.horarios_add, name='horarios_add'),
    path('horarios/editar/<int:pk>/', views.horarios_edit, name='horarios_edit'),

    # Tiempo por hora
    path('tiempo-por-hora/', views.tiempo_por_hora, name='tiempo_por_hora'),
]
