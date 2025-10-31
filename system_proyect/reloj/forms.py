from django import forms
from .models import (
    ScheduleTemplate, ScheduleRule, EmployeeScheduleAssignment,
    Feriado, SabadoEspecial, TiempoCompensatorio, PermisoEmpleado
)

# ---------------------------------------------------------------------
# Constantes reutilizables
# ---------------------------------------------------------------------
WEEKDAYS = [
    (0, "Lunes"),
    (1, "Martes"),
    (2, "Miércoles"),
    (3, "Jueves"),
    (4, "Viernes"),
    (5, "Sábado"),
    (6, "Domingo"),
]

# ─────────────────────────────────────────────────────────────
# Plantilla base
# ─────────────────────────────────────────────────────────────

class ScheduleTemplateForm(forms.ModelForm):
    class Meta:
        model = ScheduleTemplate
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej.: LV_5_15 / LV_5_16_48"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Descripción general del horario"}),
        }
        labels = {"nombre": "Nombre de la Plantilla", "descripcion": "Descripción"}


# ─────────────────────────────────────────────────────────────
# Regla de día (individual)
# ─────────────────────────────────────────────────────────────

class ScheduleRuleForm(forms.ModelForm):
    weekday = forms.ChoiceField(
        label="Día de la Semana",
        choices=WEEKDAYS,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = ScheduleRule
        fields = ["weekday", "trabaja", "entrada_manana", "salida_manana", "entrada_tarde", "salida_tarde"]
        widgets = {
            "trabaja": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "entrada_manana": forms.TimeInput(format="%H:%M", attrs={"type": "time", "class": "form-control"}),
            "salida_manana": forms.TimeInput(format="%H:%M", attrs={"type": "time", "class": "form-control"}),
            "entrada_tarde": forms.TimeInput(format="%H:%M", attrs={"type": "time", "class": "form-control"}),
            "salida_tarde": forms.TimeInput(format="%H:%M", attrs={"type": "time", "class": "form-control"}),
        }
        labels = {
            "trabaja": "Trabaja",
            "entrada_manana": "Entrada Mañana",
            "salida_manana": "Salida Mañana",
            "entrada_tarde": "Entrada Tarde",
            "salida_tarde": "Salida Tarde",
        }

    def clean(self):
        cleaned = super().clean()
        trabaja = cleaned.get("trabaja")
        em, sm = cleaned.get("entrada_manana"), cleaned.get("salida_manana")
        et, st = cleaned.get("entrada_tarde"), cleaned.get("salida_tarde")

        if trabaja:
            if (em and not sm) or (sm and not em):
                self.add_error("salida_manana", "Completa Entrada/Salida de la mañana (si usas mañana).")
            if (et and not st) or (st and not et):
                self.add_error("salida_tarde", "Completa Entrada/Salida de la tarde (si usas tarde).")
        else:
            cleaned["entrada_manana"] = None
            cleaned["salida_manana"] = None
            cleaned["entrada_tarde"] = None
            cleaned["salida_tarde"] = None

        try:
            cleaned["weekday"] = int(cleaned.get("weekday"))
        except Exception:
            pass

        return cleaned


# ─────────────────────────────────────────────────────────────
# Reglas en lote (checkbox múltiples días)
# ─────────────────────────────────────────────────────────────

class RuleBulkForm(forms.Form):
    weekdays = forms.MultipleChoiceField(
        label="Días de la semana",
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Marca uno o varios días."
    )
    trabaja = forms.BooleanField(label="Trabaja estos días", required=False, initial=True)
    entrada_manana = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}))
    salida_manana  = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}))
    entrada_tarde  = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}))
    salida_tarde   = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}))

    def clean(self):
        cleaned = super().clean()
        trabaja = cleaned.get("trabaja")
        em, sm = cleaned.get("entrada_manana"), cleaned.get("salida_manana")
        et, st = cleaned.get("entrada_tarde"), cleaned.get("salida_tarde")

        if trabaja:
            if (em and not sm) or (sm and not em):
                self.add_error("salida_manana", "Completa Entrada/Salida de la mañana (si usas mañana).")
            if (et and not st) or (st and not et):
                self.add_error("salida_tarde", "Completa Entrada/Salida de la tarde (si usas tarde).")
        else:
            cleaned["entrada_manana"] = None
            cleaned["salida_manana"] = None
            cleaned["entrada_tarde"] = None
            cleaned["salida_tarde"] = None

        try:
            cleaned["weekdays"] = [int(x) for x in cleaned.get("weekdays", [])]
        except Exception:
            pass

        return cleaned


# ─────────────────────────────────────────────────────────────
# Asignación de plantilla a empleado
# ─────────────────────────────────────────────────────────────

class EmployeeScheduleAssignmentForm(forms.ModelForm):
    emp_code = forms.ChoiceField(
        label="Empleado",
        choices=[],  # se inyectan desde la vista
        widget=forms.Select(attrs={"class": "form-select", "data-widget": "select2"}),
        required=True,
        help_text="Busca por código o nombre"
    )

    class Meta:
        model = EmployeeScheduleAssignment
        fields = ["emp_code", "nombre_empleado", "template", "fecha_inicio", "fecha_fin", "activo"]
        widgets = {
            "nombre_empleado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Se completa automáticamente", "readonly": "readonly"}),
            "template": forms.Select(attrs={"class": "form-select"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "emp_code": "Empleado (código - nombre)",
            "nombre_empleado": "Nombre Empleado",
            "template": "Plantilla Asignada",
            "fecha_inicio": "Vigente Desde",
            "fecha_fin": "Vigente Hasta",
            "activo": "Activo",
        }

    def __init__(self, *args, **kwargs):
        empleados_choices = kwargs.pop("empleados_choices", None)
        super().__init__(*args, **kwargs)

        if empleados_choices is not None:
            self.fields["emp_code"].choices = [("", "— Selecciona —")] + list(empleados_choices)

        if self.instance and getattr(self.instance, "emp_code", None):
            code = str(self.instance.emp_code)
            if code and code not in [c[0] for c in self.fields["emp_code"].choices]:
                label = f"{code} - {getattr(self.instance, 'nombre_empleado', '')}".strip()
                self.fields["emp_code"].choices = [(code, label)] + list(self.fields["emp_code"].choices)

    def clean(self):
        cleaned = super().clean()
        fi = cleaned.get("fecha_inicio")
        ff = cleaned.get("fecha_fin")
        if fi and ff and ff < fi:
            self.add_error("fecha_fin", "La fecha fin debe ser mayor o igual a la fecha inicio.")
        return cleaned


# ─────────────────────────────────────────────────────────────
# Feriados / Sábados / Compensatorio / Permisos
# ─────────────────────────────────────────────────────────────

class FeriadoForm(forms.ModelForm):
    class Meta:
        model = Feriado
        fields = ["fecha", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
        }


class SabadoEspecialForm(forms.ModelForm):
    class Meta:
        model = SabadoEspecial
        fields = ["fecha", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
        }


class TiempoCompensatorioForm(forms.ModelForm):
    class Meta:
        model = TiempoCompensatorio
        fields = ["emp_code", "nombre_empleado", "fecha", "minutos_registrados", "motivo"]
        widgets = {
            "emp_code": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_empleado": forms.TextInput(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "minutos_registrados": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PermisoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = PermisoEmpleado
        fields = ["emp_code", "nombre_empleado", "fecha_inicio", "fecha_fin", "motivo"]
        widgets = {
            "emp_code": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_empleado": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
