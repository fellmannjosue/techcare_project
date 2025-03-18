from django import forms
from .models import MaintenanceRecord

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'equipment_name',
            'problem_description',
            'maintenance_date',  # Se agrega aquí el campo de fecha
            'technician',
            'maintenance_type',
            'maintenance_status',
            'activities_done',
            'observations',
        ]
        widgets = {
            'maintenance_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),  # Se configura el widget como selector de fecha
        }
