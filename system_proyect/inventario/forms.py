# inventario/forms.py

from django import forms
from .models import (
    InventoryItem,
    Computadora,
    Televisor,
    Impresora,
    Router,
    DataShow,
)

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['category', 'details']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'details':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ComputadoraForm(forms.ModelForm):
    class Meta:
        model = Computadora
        fields = [
            'asset_id',
            'modelo',
            'serie',
            'ip',
            'asignado_a',
            'area',
            'grado',
            'fecha_instalado',
            'observaciones',
        ]
        widgets = {
            'asset_id':      forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':        forms.TextInput(attrs={'class': 'form-control'}),
            'serie':         forms.TextInput(attrs={'class': 'form-control'}),
            'ip':            forms.TextInput(attrs={'class': 'form-control'}),
            'asignado_a':    forms.TextInput(attrs={'class': 'form-control'}),
            'area':          forms.TextInput(attrs={'class': 'form-control'}),
            'grado':         forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_instalado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TelevisorForm(forms.ModelForm):
    class Meta:
        model = Televisor
        fields = [
            'asset_id',
            'modelo',
            'serie',
            'ip',
            'grado',
            'area',
            'observaciones',
        ]
        widgets = {
            'asset_id':   forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':     forms.TextInput(attrs={'class': 'form-control'}),
            'serie':      forms.TextInput(attrs={'class': 'form-control'}),
            'ip':         forms.TextInput(attrs={'class': 'form-control'}),
            'grado':      forms.TextInput(attrs={'class': 'form-control'}),
            'area':       forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ImpresoraForm(forms.ModelForm):
    class Meta:
        model = Impresora
        fields = [
            'asset_id',
            'nombre',
            'modelo',
            'serie',
            'asignado_a',
            'nivel_tinta',
            'ultima_vez_llenado',
            'cantidad_impresiones',
            'a_color',
            'observaciones',
        ]
        widgets = {
            'asset_id':         forms.TextInput(attrs={'class': 'form-control'}),
            'nombre':           forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':           forms.TextInput(attrs={'class': 'form-control'}),
            'serie':            forms.TextInput(attrs={'class': 'form-control'}),
            'asignado_a':       forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_tinta':      forms.TextInput(attrs={'class': 'form-control'}),
            'ultima_vez_llenado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidad_impresiones': forms.NumberInput(attrs={'class': 'form-control'}),
            'a_color':          forms.CheckboxInput(),
            'observaciones':    forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = [
            'asset_id',
            'modelo',
            'serie',
            'nombre_router',
            'clave_router',
            'ip_asignada',
            'ip_uso',
            'ubicado',
            'observaciones',
        ]
        widgets = {
            'asset_id':     forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':       forms.TextInput(attrs={'class': 'form-control'}),
            'serie':        forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_router': forms.TextInput(attrs={'class': 'form-control'}),
            'clave_router': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_asignada':  forms.TextInput(attrs={'class': 'form-control'}),
            'ip_uso':       forms.TextInput(attrs={'class': 'form-control'}),
            'ubicado':      forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DataShowForm(forms.ModelForm):
    class Meta:
        model = DataShow
        fields = [
            'asset_id',
            'nombre',
            'modelo',
            'serie',
            'estado',
            'cable_corriente',
            'hdmi',
            'vga',
            'extension',
            'observaciones',
        ]
        widgets = {
            'asset_id':        forms.TextInput(attrs={'class': 'form-control'}),
            'nombre':          forms.TextInput(attrs={'class': 'form-control'}),
            'modelo':          forms.TextInput(attrs={'class': 'form-control'}),
            'serie':           forms.TextInput(attrs={'class': 'form-control'}),
            'estado':          forms.TextInput(attrs={'class': 'form-control'}),
            'cable_corriente': forms.CheckboxInput(),
            'hdmi':            forms.CheckboxInput(),
            'vga':             forms.CheckboxInput(),
            'extension':       forms.CheckboxInput(),
            'observaciones':   forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CategoryUpdateForm(forms.Form):
    item_type = forms.ChoiceField(
        choices=[
            ('Computadora', 'Computadora'),
            ('Televisor',   'Televisor'),
            ('Impresora',   'Impresora'),
            ('Router',      'Router'),
            ('DataShow',    'DataShow'),
        ],
        widget=forms.HiddenInput
    )
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    categoria = forms.ChoiceField(
        label='Categoría',
        choices=InventoryItem.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    def save(self):
        tipo = self.cleaned_data['item_type']
        pk   = self.cleaned_data['item_id']
        cat  = self.cleaned_data['categoria']
        modelo_map = {
            'Computadora': Computadora,
            'Televisor':   Televisor,
            'Impresora':   Impresora,
            'Router':      Router,
            'DataShow':    DataShow,
        }
        obj = modelo_map[tipo].objects.get(pk=pk)
        obj.category = cat
        obj.save()
