from django import forms
from .models import InventarioCamara, ContableCamara, IdentificacionCamaraGabinete

class InventarioCamaraForm(forms.ModelForm):
    class Meta:
        model = InventarioCamara
        fields = '__all__'
        widgets = {
            'nombre':        forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':        forms.TextInput(attrs={'class': 'form-control'}),
            'serie':         forms.TextInput(attrs={'class': 'form-control'}),
            'tipo':          forms.TextInput(attrs={'class': 'form-control'}),
            'ip_camara':     forms.TextInput(attrs={'class': 'form-control'}),
            'ip_acceso':     forms.TextInput(attrs={'class': 'form-control'}),
            'ubic_gabinete': forms.TextInput(attrs={'class': 'form-control'}),
            'canal':         forms.TextInput(attrs={'class': 'form-control'}),
            'nvr':           forms.TextInput(attrs={'class': 'form-control'}),
        }

class ContableCamaraForm(forms.ModelForm):
    class Meta:
        model = ContableCamara
        fields = '__all__'
        widgets = {
            'modelo':          forms.TextInput(attrs={'class': 'form-control'}),
            'nombre':          forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_modelo': forms.NumberInput(attrs={'class': 'form-control'}),
            'total':           forms.NumberInput(attrs={'class': 'form-control'}),
        }

class IdentificacionCamaraGabineteForm(forms.ModelForm):
    class Meta:
        model = IdentificacionCamaraGabinete
        fields = '__all__'
        widgets = {
            'numero_gabinete': forms.TextInput(attrs={'class': 'form-control'}),
            'switches':        forms.NumberInput(attrs={'class': 'form-control'}),
            'patchcords':      forms.NumberInput(attrs={'class': 'form-control'}),
            'puerto':          forms.TextInput(attrs={'class': 'form-control'}),
            'camara':          forms.Select(attrs={'class': 'form-control'}),
            'nvr':             forms.TextInput(attrs={'class': 'form-control'}),
        }
