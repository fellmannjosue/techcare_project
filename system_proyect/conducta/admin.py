from django.contrib import admin
from .models import IncisoConductual, ReporteConductual, ReporteInformativo, ProgressReport

@admin.register(IncisoConductual)
class IncisoConductualAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('descripcion',)

@admin.register(ReporteConductual)
class ReporteConductualAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno_nombre', 'grado', 'materia', 'docente', 'area', 'usuario', 'fecha')
    search_fields = ('alumno_nombre', 'materia', 'docente', 'usuario__username')
    list_filter = ('area', 'fecha', 'materia', 'docente', 'usuario')
    readonly_fields = ('fecha',)

@admin.register(ReporteInformativo)
class ReporteInformativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno_nombre', 'grado', 'materia', 'docente', 'area', 'usuario', 'fecha')
    search_fields = ('alumno_nombre', 'materia', 'docente', 'usuario__username')
    list_filter = ('area', 'fecha', 'materia', 'docente', 'usuario')
    readonly_fields = ('fecha',)

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno_nombre', 'grado', 'usuario', 'semana_inicio', 'semana_fin', 'fecha')
    search_fields = ('alumno_nombre', 'usuario__username')
    list_filter = ('fecha', 'grado', 'usuario')
    readonly_fields = ('fecha',)
