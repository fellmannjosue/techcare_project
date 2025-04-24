from django.contrib import admin
from .models import (
    Grado, Medico, AtencionMedica,
    Proveedor, Responsable,
    InventarioMedicamento, UsoMedicamento
)

@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(AtencionMedica)
class AtencionMedicaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'grado', 'fecha_hora', 'atendido_por')
    list_filter = ('grado', 'atendido_por', 'fecha_hora')
    search_fields = ('estudiante', 'motivo', 'tratamiento')
    date_hierarchy = 'fecha_hora'


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(InventarioMedicamento)
class InventarioMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_ingreso', 'proveedor', 'cantidad_existente', 'modificado_por')
    list_filter = ('proveedor', 'fecha_ingreso')
    search_fields = ('nombre',)


@admin.register(UsoMedicamento)
class UsoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'cantidad_usada', 'responsable', 'fecha_uso')
    list_filter = ('responsable', 'fecha_uso')
    search_fields = ('medicamento__nombre', 'responsable__nombre', 'comentario')
    date_hierarchy = 'fecha_uso'
