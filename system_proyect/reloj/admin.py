from django.contrib import admin
from .models import (
    ScheduleTemplate, ScheduleRule, EmployeeScheduleAssignment,
    OvertimeRequest, Feriado, SabadoEspecial, TiempoCompensatorio, PermisoEmpleado
)

# ─────────────────────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────────────────────

class ScheduleRuleInline(admin.TabularInline):
    model = ScheduleRule
    extra = 0
    fields = ("weekday", "trabaja", "entrada_manana", "salida_manana", "entrada_tarde", "salida_tarde")
    ordering = ("weekday",)


# ─────────────────────────────────────────────────────────────
# Admin: Plantillas y Reglas
# ─────────────────────────────────────────────────────────────

@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "descripcion")
    search_fields = ("nombre",)
    ordering      = ("nombre",)
    inlines       = [ScheduleRuleInline]
    list_per_page = 25


@admin.register(EmployeeScheduleAssignment)
class EmployeeScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display  = ("emp_code", "nombre_empleado", "template", "fecha_inicio", "fecha_fin", "activo")
    list_filter   = ("activo", "template")
    search_fields = ("emp_code", "nombre_empleado")
    ordering      = ("-activo", "emp_code", "-fecha_inicio")
    list_per_page = 30


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display  = ("emp_code", "fecha", "minutos_calculados", "minutos_autorizados", "status", "approved_by", "approved_at")
    list_filter   = ("status", "approved_by")
    search_fields = ("emp_code",)
    date_hierarchy = "fecha"
    ordering      = ("-fecha", "emp_code")
    list_per_page = 50


# ─────────────────────────────────────────────────────────────
# Admin: Feriados / Sábados / Compensatorio / Permisos
# ─────────────────────────────────────────────────────────────

@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display  = ("fecha", "descripcion", "creado_por", "creado_en")
    search_fields = ("descripcion",)
    date_hierarchy = "fecha"
    ordering      = ("-fecha",)


@admin.register(SabadoEspecial)
class SabadoEspecialAdmin(admin.ModelAdmin):
    list_display  = ("fecha", "descripcion", "creado_por", "creado_en")
    search_fields = ("descripcion",)
    date_hierarchy = "fecha"
    ordering      = ("-fecha",)


@admin.register(TiempoCompensatorio)
class TiempoCompensatorioAdmin(admin.ModelAdmin):
    list_display  = ("emp_code", "nombre_empleado", "fecha", "minutos_registrados", "estado", "registrado_por", "autorizado_por", "autorizado_en")
    list_filter   = ("estado", "autorizado_por")
    search_fields = ("emp_code", "nombre_empleado", "motivo")
    date_hierarchy = "fecha"
    ordering      = ("-fecha", "-creado_en")


@admin.register(PermisoEmpleado)
class PermisoEmpleadoAdmin(admin.ModelAdmin):
    list_display  = ("emp_code", "nombre_empleado", "fecha_inicio", "fecha_fin", "motivo", "aprobado", "autorizado_por")
    list_filter   = ("aprobado", "autorizado_por")
    search_fields = ("emp_code", "nombre_empleado", "motivo")
    date_hierarchy = "fecha_inicio"
    ordering      = ("-fecha_inicio",)
