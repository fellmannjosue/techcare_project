from django.urls import path
from . import views

urlpatterns = [

    # ───────────────────────────────
    # 1. DASHBOARDS PRINCIPALES
    # ───────────────────────────────
    path('dashboard/maestro/', views.dashboard_maestro, name='dashboard_maestro'),
    # Dashboard de coordinador (por área: bilingue o colegio)
    path('coordinador/<str:area>/', views.dashboard_coordinador, name='dashboard_coordinador'),

    # ──────────────────────────────────────────────
    # 2. HISTORIAL MODAL (AJAX) POR ALUMNO
    # ──────────────────────────────────────────────
    # Endpoint AJAX para historial de reportes de un alumno (modal en dashboard coordinador)
    path('coordinador/historial/alumno/<str:alumno_id>/', views.historial_alumno_coordinador, name='historial_alumno_coordinador'),

    # ───────────────────────────────
    # 3. FORMULARIOS DE REPORTES
    # ───────────────────────────────
    # Conductual
    path('reporte/conductual/bilingue/', views.reporte_conductual_bilingue, name='reporte_conductual_bilingue'),
    path('reporte/conductual/colegio/', views.reporte_conductual_colegio, name='reporte_conductual_colegio'),
    # Informativo
    path('reporte/informativo/bilingue/', views.reporte_informativo_bilingue, name='reporte_informativo_bilingue'),
    path('reporte/informativo/colegio/', views.reporte_informativo_colegio, name='reporte_informativo_colegio'),
    # Progress (solo bilingue)
    path('progress_report/bilingue/', views.progress_report_bilingue, name='progress_report_bilingue'),

    # ───────────────────────────────
    # 4. HISTORIAL GLOBAL (MAESTROS)
    # ───────────────────────────────
    path('historial/maestro/bilingue/', views.historial_maestro_bilingue, name='historial_maestro_bilingue'),
    path('historial/maestro/colegio/', views.historial_maestro_colegio, name='historial_maestro_colegio'),

    # ─────────────────────────────────────────────────
    # 5. DETALLE, EDITAR Y PDF – POR TIPO DE REPORTE
    # ─────────────────────────────────────────────────
    # INFORMÁTIVO
    path('reporte-informativo/<int:pk>/editar/', views.editar_reporte_informativo, name='editar_reporte_informativo'),
    path('reporte-informativo/<int:pk>/pdf/', views.descargar_pdf_informativo, name='descargar_pdf_informativo'),
    # CONDUCTUAL
    path('reporte-conductual/<int:pk>/editar/', views.editar_reporte_conductual, name='editar_reporte_conductual'),
    path('reporte-conductual/<int:pk>/pdf/', views.descargar_pdf_conductual, name='descargar_pdf_conductual'),
    # PROGRESS (solo bilingue)
    path('progress-report/<int:pk>/editar/', views.editar_progress_report, name='editar_progress_report'),
    path('progress-report/<int:pk>/pdf/', views.descargar_pdf_progress, name='descargar_pdf_progress'),

    # ───────────────────────────────
    # 6. OPCIONALES / COMPATIBILIDAD
    # ───────────────────────────────
    path('detalle/<int:pk>/', views.detalle_reporte, name='detalle_reporte'),
    path('editar/<int:pk>/', views.editar_reporte, name='editar_reporte'),
    path('descargar_pdf/<int:pk>/', views.descargar_pdf_reporte, name='descargar_pdf_reporte'),
]
