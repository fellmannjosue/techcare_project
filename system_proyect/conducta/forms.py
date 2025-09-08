from django import forms
from .models import IncisoConductual
from django.utils import timezone

class ReporteConductualForm(forms.Form):
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    alumno = forms.ChoiceField(label="Estudiante", widget=forms.Select(attrs={'class': 'form-select'}))
    grado = forms.CharField(label="Grado", required=False, widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}))
    materia = forms.ChoiceField(label="Materia", widget=forms.Select(attrs={'class': 'form-select'}))
    docente = forms.ChoiceField(label="Docente", widget=forms.Select(attrs={'class': 'form-select'}))

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
    comentario = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False, label="Comentario")

    def __init__(self, *args, **kwargs):
        alumnos_choices  = kwargs.pop('alumnos_choices', [])
        materias_choices = kwargs.pop('materias_choices', [])
        docentes_choices = kwargs.pop('docentes_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices  = alumnos_choices
        self.fields['materia'].choices = materias_choices
        self.fields['docente'].choices = docentes_choices

class ReporteInformativoForm(forms.Form):
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    alumno = forms.ChoiceField(label="Estudiante", widget=forms.Select(attrs={'class': 'form-select'}))
    grado = forms.CharField(label="Grado", required=False, widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}))
    materia = forms.ChoiceField(label="Materia", widget=forms.Select(attrs={'class': 'form-select'}))
    docente = forms.ChoiceField(label="Docente", widget=forms.Select(attrs={'class': 'form-select'}))
    comentario = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False, label="Comentario")

    def __init__(self, *args, **kwargs):
        alumnos_choices  = kwargs.pop('alumnos_choices', [])
        materias_choices = kwargs.pop('materias_choices', [])
        docentes_choices = kwargs.pop('docentes_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices  = alumnos_choices
        self.fields['materia'].choices = materias_choices
        self.fields['docente'].choices = docentes_choices

class ProgressReportForm(forms.Form):
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    alumno = forms.ChoiceField(label="Estudiante", widget=forms.Select(attrs={'class': 'form-select'}))
    grado = forms.CharField(label="Grado", required=False, widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'}))
    semana_inicio = forms.DateField(label="Semana inicio", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    semana_fin = forms.DateField(label="Semana fin", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    comentario_general = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False, label="Comentario General")

    def __init__(self, *args, **kwargs):
        alumnos_choices = kwargs.pop('alumnos_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['alumno'].choices = alumnos_choices
