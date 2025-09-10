from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('dashboard/maestro/', views.dashboard_maestro, name='dashboard_maestro'),
    path('dashboard/coordinador/bilingue/', views.dashboard_coordinador_bilingue, name='dashboard_coordinador_bilingue'),
    path('dashboard/coordinador/colegio/', views.dashboard_coordinador_colegio, name='dashboard_coordinador_colegio'),

    # Formularios de reportes
    path('reporte/conductual/bilingue/', views.reporte_conductual_bilingue, name='reporte_conductual_bilingue'),
    path('reporte/conductual/colegio/', views.reporte_conductual_colegio, name='reporte_conductual_colegio'),
    path('reporte/informativo/bilingue/', views.reporte_informativo_bilingue, name='reporte_informativo_bilingue'),
    path('reporte/informativo/colegio/', views.reporte_informativo_colegio, name='reporte_informativo_colegio'),
    path('progress_report/bilingue/', views.progress_report_bilingue, name='progress_report_bilingue'),

    # Historial
    path('historial/maestro/bilingue/', views.historial_maestro_bilingue, name='historial_maestro_bilingue'),
    path('historial/maestro/colegio/', views.historial_maestro_colegio, name='historial_maestro_colegio'),

    # Coordinador - Historial y Reportes Generales
    path('coordinador/historial/conductual/bilingue/', views.historial_conductual_coordinador_bilingue, name='historial_conductual_coordinador_bilingue'),
    path('coordinador/historial/conductual/colegio/', views.historial_conductual_coordinador_colegio, name='historial_conductual_coordinador_colegio'),
    path('coordinador/historial/informativo/bilingue/', views.historial_informativo_coordinador_bilingue, name='historial_informativo_coordinador_bilingue'),
    path('coordinador/historial/informativo/colegio/', views.historial_informativo_coordinador_colegio, name='historial_informativo_coordinador_colegio'),
    path('coordinador/historial/progress/bilingue/', views.historial_progress_coordinador_bilingue, name='historial_progress_coordinador_bilingue'),
    path('coordinador/reporte_general/tres_faltas/bilingue/', views.reporte_general_tres_faltas_bilingue, name='reporte_general_tres_faltas_bilingue'),
    path('coordinador/reporte_general/tres_faltas/colegio/', views.reporte_general_tres_faltas_colegio, name='reporte_general_tres_faltas_colegio'),

    # AJAX (Grado automático y docentes por materia)
    #path('ajax/grado/', views.ajax_grado_alumno, name='ajax_grado_alumno'),
    #path('ajax/docentes/', views.ajax_docentes_por_materia, name='ajax_docentes_por_materia'),

    # Detalle, editar y PDF
    path('detalle/<int:pk>/', views.detalle_reporte, name='detalle_reporte'),
    path('editar/<int:pk>/', views.editar_reporte, name='editar_reporte'),
    path('descargar_pdf/<int:pk>/', views.descargar_pdf_reporte, name='descargar_pdf_reporte'),
]
