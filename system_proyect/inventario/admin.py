from django.contrib import admin
from .models import (
    InventoryItem,
    Computadora,
    Televisor,
    Impresora,
    Router,
    DataShow,
)

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'details')
    search_fields = ('category', 'details')


@admin.register(Computadora)
class ComputadoraAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'modelo', 'serie', 'ip', 'asignado_a', 'area', 'grado', 'fecha_instalado')
    search_fields = ('asset_id', 'modelo', 'serie', 'ip', 'asignado_a', 'area', 'grado')


@admin.register(Televisor)
class TelevisorAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'modelo', 'serie', 'ip', 'grado', 'area')
    search_fields = ('asset_id', 'modelo', 'serie', 'ip', 'grado', 'area')


@admin.register(Impresora)
class ImpresoraAdmin(admin.ModelAdmin):
    list_display = (
        'asset_id', 'nombre', 'modelo', 'serie', 'asignado_a',
        'nivel_tinta', 'ultima_vez_llenado', 'cantidad_impresiones', 'a_color'
    )
    list_filter = ('a_color',)
    search_fields = ('asset_id', 'nombre', 'modelo', 'serie', 'asignado_a')


@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'modelo', 'serie', 'nombre_router', 'ip_asignada', 'ip_uso', 'ubicado')
    search_fields = ('asset_id', 'modelo', 'serie', 'nombre_router', 'ubicado')


@admin.register(DataShow)
class DataShowAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'nombre', 'modelo', 'serie', 'estado')
    list_filter = ('estado', 'cable_corriente', 'hdmi', 'vga', 'extension')
    search_fields = ('asset_id', 'nombre', 'modelo', 'serie')
