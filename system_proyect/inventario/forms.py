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


class ComputadoraForm(forms.ModelForm):
    class Meta:
        model = Computadora
        fields = '__all__'


class TelevisorForm(forms.ModelForm):
    class Meta:
        model = Televisor
        fields = '__all__'


class ImpresoraForm(forms.ModelForm):
    class Meta:
        model = Impresora
        fields = '__all__'


class RouterForm(forms.ModelForm):
    class Meta:
        model = Router
        fields = '__all__'


class DataShowForm(forms.ModelForm):
    class Meta:
        model = DataShow
        fields = '__all__'
