from django.contrib import admin
from .models import InventoryItem

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'details', 'created_at')
    search_fields = ('category', 'details')

admin.site.register(InventoryItem, InventoryAdmin)
