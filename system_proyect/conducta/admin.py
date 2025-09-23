from django.contrib import admin
from .models import (
    IncisoConductual, MateriaDocenteBilingue, MateriaDocenteColegio,
    ReporteConductual, ReporteInformativo, ProgressReport
)

@admin.register(IncisoConductual)
class IncisoConductualAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'descripcion', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['descripcion']

@admin.register(MateriaDocenteBilingue)
class MateriaDocenteBilingueAdmin(admin.ModelAdmin):
    list_display = ['materia', 'docente', 'activo']
    list_filter = ['activo']
    search_fields = ['materia', 'docente']

@admin.register(MateriaDocenteColegio)
class MateriaDocenteColegioAdmin(admin.ModelAdmin):
    list_display = ['materia', 'docente', 'activo']
    list_filter = ['activo']
    search_fields = ['materia', 'docente']

@admin.register(ReporteConductual)
class ReporteConductualAdmin(admin.ModelAdmin):
    list_display = ['alumno_nombre', 'materia', 'usuario', 'area', 'estado', 'coordinador_firma', 'comentario_coordinador', 'fecha']
    list_filter = ['area', 'estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'materia', 'docente', 'usuario__username']

@admin.register(ReporteInformativo)
class ReporteInformativoAdmin(admin.ModelAdmin):
    list_display = ['alumno_nombre', 'materia', 'usuario', 'area', 'estado', 'coordinador_firma', 'comentario_coordinador', 'fecha']
    list_filter = ['area', 'estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'materia', 'docente', 'usuario__username']

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ['alumno_nombre', 'usuario', 'grado', 'semana_inicio', 'semana_fin', 'estado', 'coordinador_firma', 'comentario_coordinador', 'fecha']
    list_filter = ['estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'usuario__username', 'grado']
