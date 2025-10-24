from django import forms
from .models import EmployeeSchedule

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = [
            'emp_code', 'nombre',
            'entrada_manana', 'salida_manana',
            'entrada_tarde', 'salida_tarde'
        ]
        widgets = {
            'entrada_manana': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'salida_manana': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'entrada_tarde': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'salida_tarde': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'emp_code': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'emp_code': 'ID Empleado',
            'nombre': 'Nombre Empleado',
            'entrada_manana': 'Entrada Mañana',
            'salida_manana': 'Salida Mañana',
            'entrada_tarde': 'Entrada Tarde',
            'salida_tarde': 'Salida Tarde',
        }
