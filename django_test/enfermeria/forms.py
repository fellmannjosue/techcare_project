# forms.py

from django import forms
from .models import AtencionMedica, InventarioMedicamento, UsoMedicamento

class AtencionMedicaForm(forms.ModelForm):
    class Meta:
        model  = AtencionMedica
        fields = '__all__'
        widgets = {
            'estudiante':   forms.TextInput(attrs={'class': 'form-control'}),
            'grado':        forms.Select(attrs={'class': 'form-select'}),
            'fecha_hora':   forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'atendido_por': forms.Select(attrs={'class': 'form-select'}),
            'motivo':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InventarioMedicamentoForm(forms.ModelForm):
    class Meta:
        model   = InventarioMedicamento
        exclude = ['modificado_por']
        fields  = [
            'nombre',
            'proveedor',
            'presentacion',         # ← Incluimos el nuevo campo
            'cantidad_existente',
            'fecha_ingreso',
        ]
        widgets = {
            'nombre':             forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso':      forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'proveedor':          forms.Select(attrs={'class': 'form-select'}),
            'presentacion':       forms.Select(attrs={'class': 'form-select'}),  # dropdown Bootstrap
            'cantidad_existente': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class UsoMedicamentoForm(forms.ModelForm):
    class Meta:
        model  = UsoMedicamento
        fields = ['medicamento', 'cantidad_usada', 'responsable', 'comentario']
        widgets = {
            'medicamento':    forms.Select(attrs={'class': 'form-select'}),
            'cantidad_usada': forms.NumberInput(attrs={'class': 'form-control'}),
            'responsable':    forms.Select(attrs={'class': 'form-select'}),
            'comentario':     forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones u otros detalles...'
            }),
        }
