from django.contrib import admin
from .models import ScheduleTemplate, ScheduleRule, EmployeeScheduleAssignment,OvertimeRequest


# ──────────────────────────────────────────────
#  INLINE de reglas (días) dentro de cada plantilla
# ──────────────────────────────────────────────
class ScheduleRuleInline(admin.TabularInline):
    model = ScheduleRule
    extra = 0
    fields = (
        "weekday", "trabaja",
        "entrada_manana", "salida_manana",
        "entrada_tarde", "salida_tarde",
    )
    ordering = ("weekday",)


# ──────────────────────────────────────────────
#  PLANTILLAS (con inline de reglas)
# ──────────────────────────────────────────────
@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)
    inlines = [ScheduleRuleInline]
    ordering = ("nombre",)
    list_per_page = 20


# ──────────────────────────────────────────────
#  ASIGNACIONES DE PLANTILLA A EMPLEADOS
# ──────────────────────────────────────────────
@admin.register(EmployeeScheduleAssignment)
class EmployeeScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "emp_code", "nombre_empleado", "template",
        "fecha_inicio", "fecha_fin", "activo",
    )
    list_filter = ("activo", "template")
    search_fields = ("emp_code", "nombre_empleado")
    ordering = ("-activo", "emp_code")
    list_per_page = 30

@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "emp_code", "fecha",
        "minutos_calculados", "minutos_autorizados",
        "status", "approved_by", "approved_at",
    )
    list_filter = ("status", "fecha")
    search_fields = ("emp_code", "comentario")
    ordering = ("-fecha", "emp_code")
    list_per_page = 30