from django.contrib import admin
from .models import (
    IncisoConductual,
    MateriaDocenteBilingue,
    MateriaDocenteColegio,
    ReporteConductual,
    ReporteInformativo,
    ProgressReport,
)

@admin.register(ReporteConductual)
class ReporteConductualAdmin(admin.ModelAdmin):
    list_display = (
        'alumno_nombre', 'grado', 'materia', 'docente', 'fecha', 'area',
        'coordinador_firma', 'estado'
    )
    search_fields = ('alumno_nombre', 'grado', 'materia', 'docente', 'comentario')
    list_filter = ('area', 'grado', 'fecha', 'docente', 'coordinador_firma', 'estado')
    readonly_fields = ('fecha',)

@admin.register(ReporteInformativo)
class ReporteInformativoAdmin(admin.ModelAdmin):
    list_display = (
        'alumno_nombre', 'grado', 'materia', 'docente', 'fecha', 'area',
        'coordinador_firma', 'estado'
    )
    search_fields = ('alumno_nombre', 'grado', 'materia', 'docente', 'comentario')
    list_filter = ('area', 'grado', 'fecha', 'docente', 'coordinador_firma', 'estado')
    readonly_fields = ('fecha',)

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = (
        'alumno_nombre', 'grado', 'semana_inicio', 'semana_fin', 'fecha',
        'coordinador_firma', 'estado'
    )
    search_fields = ('alumno_nombre', 'grado', 'comentario_general')
    list_filter = ('grado', 'semana_inicio', 'semana_fin', 'fecha', 'coordinador_firma', 'estado')
    readonly_fields = ('fecha',)

# Los registros básicos
admin.site.register(IncisoConductual)
admin.site.register(MateriaDocenteBilingue)
admin.site.register(MateriaDocenteColegio)
