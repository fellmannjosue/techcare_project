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
    list_display = [
        'alumno_nombre', 'materia', 'usuario', 'area', 'estado',
        'coordinador_firma', 'comentario_coordinador', 'fecha'
    ]
    list_filter = ['area', 'estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'materia', 'docente', 'usuario__username']
    readonly_fields = ['fecha']

@admin.register(ReporteInformativo)
class ReporteInformativoAdmin(admin.ModelAdmin):
    list_display = [
        'alumno_nombre', 'materia', 'usuario', 'area', 'estado',
        'coordinador_firma', 'comentario_coordinador', 'fecha'
    ]
    list_filter = ['area', 'estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'materia', 'docente', 'usuario__username']
    readonly_fields = ['fecha']

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = [
        'alumno_nombre', 'usuario', 'grado', 'semana_inicio', 'semana_fin',
        'estado', 'coordinador_firma', 'comentario_coordinador', 'fecha', 'materias_resumen'
    ]
    list_filter = ['estado', 'coordinador_firma']
    search_fields = ['alumno_nombre', 'usuario__username', 'grado']
    readonly_fields = ['fecha', 'materias_json']

    def materias_resumen(self, obj):
        """Muestra un resumen de materias en el listado admin."""
        if not obj.materias_json:
            return "-"
        # Si el JSON está vacío, muestra nada.
        if isinstance(obj.materias_json, list):
            nombres = [m.get('materia', '') for m in obj.materias_json if m.get('materia')]
            return ", ".join(nombres) if nombres else "-"
        return "-"
    materias_resumen.short_description = "Materias"

    # Opcional: para ver el JSON bonito en la vista detalle
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'materias_json':
            field.widget.attrs['style'] = 'font-family:monospace; min-width: 400px; min-height: 100px;'
        return field
