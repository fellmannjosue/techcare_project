from django.contrib import admin
from .models import ProgressReport, ReportEntry

class ReportEntryInline(admin.TabularInline):
    model = ReportEntry
    extra = 0

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display  = ('alumno_nombre','semana_inicio','semana_fin','creado')
    list_filter   = ('semana_inicio','semana_fin')
    inlines       = [ReportEntryInline]

    # Mostrar la propiedad alumno_nombre en vez de persona_id
    def alumno_nombre(self, obj):
        return obj.alumno_nombre
    alumno_nombre.short_description = "Alumno"
