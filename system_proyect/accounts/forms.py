from django import forms
from django.contrib.auth.models import User

AREA_CHOICES = (
    ('bilingue', 'Bilingüe'),
    ('colegio', 'Colegio/CFP'),
    ('administracion', 'Administración'),
)

CARGO_CHOICES = (
    ('docente', 'Docente'),
    ('administrativo', 'Administrativo'),
)

class MaestroRegisterForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=30)
    last_name = forms.CharField(label='Apellido', max_length=30)
    email = forms.EmailField(label='Correo institucional')
    area = forms.ChoiceField(label='Área', choices=AREA_CHOICES)
    cargo = forms.ChoiceField(label='Cargo', choices=CARGO_CHOICES, required=False)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email.endswith('@ana-hn.org'):
            raise forms.ValidationError('Debe usar su correo institucional @ana-hn.org')
        if any(domain in email for domain in ['gmail.com', 'hotmail.com', 'outlook.com']):
            raise forms.ValidationError('No se permiten correos de gmail, hotmail ni outlook.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        area = cleaned_data.get('area')
        cargo = cleaned_data.get('cargo')
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        # Cargo requerido solo en bilingue o colegio
        if area in ['bilingue', 'colegio'] and not cargo:
            self.add_error('cargo', 'Debes seleccionar el cargo para esta área.')
        # Si es administración, el cargo no debe seleccionarse (lo puedes ocultar en el frontend)
        if area == 'administracion':
            cleaned_data['cargo'] = None  # Opcional: lo puedes ignorar al guardar

        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data
