from django import forms
from .models import IncisoConductual, ESTADO_CHOICES
from django.utils import timezone
from django.contrib.auth.models import User

def get_coordinadores_choices():
    qs = User.objects.filter(groups__name="Coordinador")
    return [('', '---------')] + [(u.get_full_name() or u.username, u.get_full_name() or u.username) for u in qs]

class ReporteConductualForm(forms.Form):
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    alumno = forms.ChoiceField(label="Estudiante", widget=forms.Select(attrs={'class': 'form-select'}))
    grado = forms.CharField(
        label="Grado",
        required=False,
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    materia_docente = forms.ChoiceField(
        label="Materia / Docente",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    leve = forms.BooleanField(label="Leve", required=False)
    inciso_leve = forms.ModelChoiceField(
        label="Inciso Leve",
        queryset=IncisoConductual.objects.filter(tipo='leve', activo=True),
        required=False,
        empty_label="---"
    )
    grave = forms.BooleanField(label="Grave", required=False)
    inciso_grave = forms.ModelChoiceField(
        label="Inciso Grave",
        queryset=IncisoConductual.objects.filter(tipo='grave', activo=True),
        required=False,
        empty_label="---"
    )
    muy_grave = forms.BooleanField(label="Muy grave", required=False)
    inciso_muy_grave = forms.ModelChoiceField(
        label="Inciso Muy Grave",
        queryset=IncisoConductual.objects.filter(tipo='muy_grave', activo=True),
        required=False,
        empty_label="---"
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False,
        label="Comentario"
    )
    coordinador_firma = forms.ChoiceField(
        label="Coordinador que aprueba",
        choices=get_coordinadores_choices(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=ESTADO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comentario_coordinador = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label="Comentario del Coordinador"
    )

    def __init__(self, *args, es_coordinador=False, **kwargs):
        alumnos_choices = kwargs.pop('alumnos_choices', [])
        materia_docente_choices = kwargs.pop('materia_docente_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices = alumnos_choices
        self.fields['materia_docente'].choices = materia_docente_choices
        # Solo permite edición a los coordinadores
        if not es_coordinador:
            for name, field in self.fields.items():
                if name not in ('coordinador_firma', 'estado', 'comentario_coordinador'):
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['disabled'] = True

class ReporteInformativoForm(forms.Form):
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    alumno = forms.ChoiceField(label="Estudiante", widget=forms.Select(attrs={'class': 'form-select'}))
    grado = forms.CharField(
        label="Grado",
        required=False,
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    materia_docente = forms.ChoiceField(
        label="Materia / Docente",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comentario = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False,
        label="Comentario"
    )
    coordinador_firma = forms.ChoiceField(
        label="Coordinador que aprueba",
        choices=get_coordinadores_choices(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=ESTADO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comentario_coordinador = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label="Comentario del Coordinador"
    )

    def __init__(self, *args, es_coordinador=False, **kwargs):
        alumnos_choices = kwargs.pop('alumnos_choices', [])
        materia_docente_choices = kwargs.pop('materia_docente_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices = alumnos_choices
        self.fields['materia_docente'].choices = materia_docente_choices
        if not es_coordinador:
            for name, field in self.fields.items():
                if name not in ('coordinador_firma', 'estado', 'comentario_coordinador'):
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['disabled'] = True

class ProgressReportForm(forms.Form):
    alumno = forms.ChoiceField(
        label="Estudiante",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    grado = forms.CharField(
        label="Grado",
        required=False,
        widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
    )
    semana_inicio = forms.DateField(
        label="Semana inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    semana_fin = forms.DateField(
        label="Semana fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    comentario_general = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False,
        label="Comentario General"
    )
    # Solo coordinador puede editar estos
    coordinador_firma = forms.ChoiceField(
        label="Coordinador que aprueba",
        choices=get_coordinadores_choices(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=ESTADO_CHOICES,
        required=False,  # Cambia a False; solo coordinador puede requerir
        widget=forms.HiddenInput()
    )
    comentario_coordinador = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label="Comentario del Coordinador"
    )

    def __init__(self, *args, alumnos_choices=None, modo_coordinador=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices = alumnos_choices or []
        # Solo coordinador puede editar estado y firma
        if not modo_coordinador:
            self.fields['estado'].widget = forms.HiddenInput()
            self.fields['coordinador_firma'].widget = forms.HiddenInput()
            self.fields['comentario_coordinador'].widget = forms.HiddenInput()
        else:
            self.fields['estado'].required = True