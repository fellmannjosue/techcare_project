from django.contrib import admin
from .models import InventarioCamara, ContableCamara, IdentificacionCamaraGabinete

@admin.register(InventarioCamara)
class InventarioCamaraAdmin(admin.ModelAdmin):
    list_display  = ('nombre','modelo','serie','tipo','ip_camara','nvr')
    search_fields = ('nombre','modelo','serie','tipo')
    list_filter   = ('tipo','nvr')


@admin.register(ContableCamara)
class ContableCamaraAdmin(admin.ModelAdmin):
    list_display  = ('modelo','nombre','cantidad_modelo','total')
    search_fields = ('modelo','nombre')
    list_filter   = ('modelo',)


@admin.register(IdentificacionCamaraGabinete)
class IdentificacionCamaraGabineteAdmin(admin.ModelAdmin):
    list_display  = ('numero_gabinete','puerto','camara','nvr')
    search_fields = ('numero_gabinete','puerto','camara__nombre')
    list_filter   = ('numero_gabinete',)
