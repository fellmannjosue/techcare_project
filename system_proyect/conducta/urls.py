from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('dashboard/maestro/', views.dashboard_maestro, name='dashboard_maestro'),
    path('coordinador/<str:area>/', views.dashboard_coordinador, name='dashboard_coordinador'),
    path('coordinador/historial/alumno/<str:alumno_id>/', views.historial_alumno_coordinador, name='historial_alumno_coordinador'),

    # Formularios de reportes
    path('reporte/conductual/bilingue/', views.reporte_conductual_bilingue, name='reporte_conductual_bilingue'),
    path('reporte/conductual/colegio/', views.reporte_conductual_colegio, name='reporte_conductual_colegio'),
    path('reporte/informativo/bilingue/', views.reporte_informativo_bilingue, name='reporte_informativo_bilingue'),
    path('reporte/informativo/colegio/', views.reporte_informativo_colegio, name='reporte_informativo_colegio'),
    path('progress_report/bilingue/', views.progress_report_bilingue, name='progress_report_bilingue'),

    # Historial
    path('historial/maestro/bilingue/', views.historial_maestro_bilingue, name='historial_maestro_bilingue'),
    path('historial/maestro/colegio/', views.historial_maestro_colegio, name='historial_maestro_colegio'),

    # -------------------------------
    # EDICIÓN Y PDF AGRUPADOS
    # -------------------------------

    # --- CONDUCTUAL ---
    path('reporte-conductual/<int:pk>/editar/', views.editar_reporte_conductual, name='editar_reporte_conductual'),
    path('reporte-conductual/<int:pk>/pdf/', views.descargar_pdf_conductual, name='descargar_pdf_conductual'),
    path('reporte-conductual/<int:pk>/pdf-3strikes/', views.descargar_pdf_conductual_3_strikes, name='descargar_pdf_conductual_3_strikes'),
    # --- INFORMATIVO ---
    path('reporte-informativo/<int:pk>/editar/', views.editar_reporte_informativo, name='editar_reporte_informativo'),
    path('reporte-informativo/<int:pk>/pdf/', views.descargar_pdf_informativo, name='descargar_pdf_informativo'),

        # --- PROGRESS ---
    path('progress-report/<int:pk>/editar/', views.editar_progress_report, name='editar_progress_report'),
    path('progress-report/<int:pk>/pdf/', views.descargar_pdf_progress, name='descargar_pdf_progress'),


    # Otros endpoints PDF y features especiales puedes ponerlos aquí...
]
