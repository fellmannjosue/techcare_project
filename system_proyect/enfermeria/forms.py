from django import forms
from .models import AtencionMedica, InventarioMedicamento

class AtencionMedicaForm(forms.ModelForm):
    class Meta:
        model = AtencionMedica
        fields = '__all__'
        widgets = {
            'estudiante':   forms.TextInput(attrs={'class':'form-control'}),
            'grado':        forms.Select(attrs={'class':'form-select'}),
            'fecha_hora':   forms.DateTimeInput(attrs={'type':'datetime-local','class':'form-control'}),
            'atendido_por': forms.Select(attrs={'class':'form-select'}),
            'motivo':       forms.Textarea(attrs={'class':'form-control','rows':3}),
            'tratamiento':  forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class InventarioMedicamentoForm(forms.ModelForm):
    class Meta:
        model = InventarioMedicamento
        fields = '__all__'
        widgets = {
            'nombre':             forms.TextInput(attrs={'class':'form-control'}),
            'fecha_ingreso':      forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'proveedor':          forms.TextInput(attrs={'class':'form-control'}),
            'cantidad_existente': forms.NumberInput(attrs={'class':'form-control'}),
            'cantidad_usado':     forms.NumberInput(attrs={'class':'form-control'}),
            'responsable':        forms.TextInput(attrs={'class':'form-control'}),
            'total':              forms.NumberInput(attrs={'class':'form-control'}),
        }
