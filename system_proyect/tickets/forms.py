from django import forms
from .models import Ticket,TicketComment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['name', 'grade', 'email', 'description', 'comments', 'attachment']  # Agrega 'attachment'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escribe tu comentario aquí...',
            }),
        }
        labels = {
            'mensaje': 'Comentario',
        }