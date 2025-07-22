from django import forms
from django.forms import inlineformset_factory
from django.db import connection
from .models import ProgressReport, ReportEntry, SQL_OBTENER_ALUMNOS

def obtener_alumnos():
    with connection.cursor() as cursor:
        cursor.execute(SQL_OBTENER_ALUMNOS)
        return cursor.fetchall()  # lista de tuplas (PersonaID, NombreCompl)

class ProgressReportForm(forms.ModelForm):
    persona_id = forms.ChoiceField(label="Alumno", choices=[])

    class Meta:
        model  = ProgressReport
        fields = ['persona_id', 'semana_inicio', 'semana_fin']
        widgets = {
            'semana_inicio': forms.DateInput(attrs={'type':'date'}),
            'semana_fin'   : forms.DateInput(attrs={'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        alumnos = obtener_alumnos()
        self.fields['persona_id'].choices = [
            (str(pid), nombre) for pid, nombre in alumnos
        ]
        # si estamos editando, mantener el valor actual
        if self.instance.pk:
            self.fields['persona_id'].initial = str(self.instance.persona_id)

# El formset de materias sigue igual
ReportEntryFormSet = inlineformset_factory(
    ProgressReport, ReportEntry,
    fields=['materia','asignacion','observacion'],
    extra=8,
    can_delete=False
)
