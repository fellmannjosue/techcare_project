from django.contrib import admin
from .models import MaintenanceRecord

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment_name', 'maintenance_date', 'technician', 'maintenance_status')
    search_fields = ('equipment_name', 'technician', 'maintenance_status')
    list_filter = ('maintenance_status', 'maintenance_type', 'maintenance_date')

