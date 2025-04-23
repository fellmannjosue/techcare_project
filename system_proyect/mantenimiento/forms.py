from django import forms
from .models import MaintenanceRecord, TipoFalla

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = '__all__'

        widgets = {
            'equipment_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el ID del equipo'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el modelo'
            }),
            'serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la serie'
            }),
            'teacher_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del maestro'
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Grado del maestro'
            }),
            'tipo_falla': forms.Select(attrs={
                'class': 'form-select'
            }),
            'solution_applied': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa la solución aplicada',
                'rows': 3
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales (opcional)',
                'rows': 3
            }),
        }

        labels = {
            'equipment_id': 'ID del Equipo',
            'model': 'Modelo',
            'serie': 'Serie',
            'teacher_name': 'Nombre del Maestro',
            'grade': 'Grado',
            'tipo_falla': 'Tipo de Falla',
            'solution_applied': 'Solución Aplicada',
            'date': 'Fecha del Mantenimiento',
            'status': 'Estado',
            'observations': 'Observaciones',
        }

class TipoFallaForm(forms.ModelForm):
    class Meta:
        model = TipoFalla
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el tipo de falla'
            }),
        }
        labels = {
            'nombre': 'Nombre del Tipo de Falla',
        }
