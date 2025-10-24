from django.contrib import admin
from .models import EmployeeSchedule

@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'emp_code', 'nombre', 
        'entrada_manana', 'salida_manana',
        'entrada_tarde', 'salida_tarde'
    )
    search_fields = ('emp_code', 'nombre')
    list_filter = ('entrada_manana', 'salida_manana')
