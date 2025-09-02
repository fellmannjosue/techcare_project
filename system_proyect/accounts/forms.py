from django import forms
from django.contrib.auth.models import User

AREA_CHOICES = (
    ('bilingue', 'Bilingüe'),
    ('colegio', 'Colegio/CFP'),
)

class MaestroRegisterForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=30)
    last_name = forms.CharField(label='Apellido', max_length=30)
    email = forms.EmailField(label='Correo institucional')
    area = forms.ChoiceField(label='Área', choices=AREA_CHOICES)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@ana-hn.org'):
            raise forms.ValidationError('Debe usar su correo institucional @ana-hn.org')
        # Opcional: bloquear gmail, hotmail, outlook explícitamente
        if any(domain in email for domain in ['gmail.com', 'hotmail.com', 'outlook.com']):
            raise forms.ValidationError('No se permiten correos de gmail, hotmail, ni outlook.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data
