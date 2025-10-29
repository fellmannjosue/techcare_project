from django import forms
from .models import (
    ScheduleTemplate, ScheduleRule, EmployeeScheduleAssignment,
    OvertimeRequest,   # ← agregado
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


# ---------------------------------------------------------------------
# FORM: Plantilla base
# ---------------------------------------------------------------------
class ScheduleTemplateForm(forms.ModelForm):
    class Meta:
        model = ScheduleTemplate
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: LV_7_16_SAB_7_11"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control", "rows": 2,
                "placeholder": "Descripción general del horario"
            }),
        }
        labels = {
            "nombre": "Nombre de la Plantilla",
            "descripcion": "Descripción",
        }


# ---------------------------------------------------------------------
# FORM: Regla de día (individual, para EDITAR una sola)
# ---------------------------------------------------------------------
class ScheduleRuleForm(forms.ModelForm):
    # forzamos el select con nombres de día
    weekday = forms.ChoiceField(
        label="Día de la Semana",
        choices=WEEKDAYS,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = ScheduleRule
        fields = [
            "weekday", "trabaja",
            "entrada_manana", "salida_manana",
            "entrada_tarde", "salida_tarde",
        ]
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
        """
        Si 'trabaja' está activo y se llena una de las horas de un turno,
        exige que se complete la pareja (entrada/salida).
        """
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
            # si NO trabaja, borra horas (evita basura)
            cleaned["entrada_manana"] = None
            cleaned["salida_manana"] = None
            cleaned["entrada_tarde"] = None
            cleaned["salida_tarde"] = None

        # normaliza weekday a int
        try:
            cleaned["weekday"] = int(cleaned.get("weekday"))
        except Exception:
            pass

        return cleaned


# ---------------------------------------------------------------------
# FORM: Regla de día en LOTE (checkbox múltiples días)
#   - Para crear/actualizar varios días con un solo submit.
# ---------------------------------------------------------------------
class RuleBulkForm(forms.Form):
    weekdays = forms.MultipleChoiceField(
        label="Días de la semana",
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Marca uno o varios días."
    )
    trabaja = forms.BooleanField(
        label="Trabaja estos días", required=False, initial=True
    )
    entrada_manana = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )
    salida_manana = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )
    entrada_tarde = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )
    salida_tarde = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

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

        # normaliza weekdays a ints
        try:
            cleaned["weekdays"] = [int(x) for x in cleaned.get("weekdays", [])]
        except Exception:
            pass

        return cleaned


# ---------------------------------------------------------------------
# FORM: Asignación de plantilla a empleado
#   - 'emp_code' como ChoiceField para usar Select2 (las choices se pasan desde la vista)
#   - Validación de fechas (fin >= inicio)
# ---------------------------------------------------------------------
class EmployeeScheduleAssignmentForm(forms.ModelForm):
    # Emp_code como SELECT (Select2-ready). Las 'choices' se inyectan en __init__.
    emp_code = forms.ChoiceField(
        label="Empleado",
        choices=[],  # se llenan en __init__
        widget=forms.Select(attrs={"class": "form-select", "data-widget": "select2"}),
        required=True,
        help_text="Busca por código o nombre"
    )

    class Meta:
        model = EmployeeScheduleAssignment
        fields = [
            "emp_code", "nombre_empleado",
            "template", "fecha_inicio", "fecha_fin", "activo"
        ]
        widgets = {
            "nombre_empleado": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Se completa automáticamente",
                "readonly": "readonly",
            }),
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
        """
        Espera opcionalmente 'empleados_choices' en kwargs con la forma:
        [("0001", "0001 - Juan Pérez"), ("0002","0002 - Ana Díaz"), ...]
        De esa manera evitamos consultas a SQL Server desde el form.
        """
        empleados_choices = kwargs.pop("empleados_choices", None)
        super().__init__(*args, **kwargs)

        if empleados_choices is not None:
            self.fields["emp_code"].choices = [("", "— Selecciona —")] + list(empleados_choices)

        # Si hay instancia con emp_code, úsalo como seleccionado
        if self.instance and getattr(self.instance, "emp_code", None):
            code = str(self.instance.emp_code)
            if code and code not in [c[0] for c in self.fields["emp_code"].choices]:
                # inyecta la opción actual por si no está en la lista
                label = f"{code} - {getattr(self.instance, 'nombre_empleado', '')}".strip()
                self.fields["emp_code"].choices = [(code, label)] + list(self.fields["emp_code"].choices)

    def clean(self):
        cleaned = super().clean()
        fi = cleaned.get("fecha_inicio")
        ff = cleaned.get("fecha_fin")
        if fi and ff and ff < fi:
            self.add_error("fecha_fin", "La fecha fin debe ser mayor o igual a la fecha inicio.")
        return cleaned


# ---------------------------------------------------------------------
# TIEMPO EXTRA: Formularios
# ---------------------------------------------------------------------
class OvertimeApproveForm(forms.ModelForm):
    """
    Usado en el modal de autorización (solo staff).
    """
    class Meta:
        model = OvertimeRequest
        fields = ["minutos_autorizados", "status", "comentario"]
        widgets = {
            "minutos_autorizados": forms.NumberInput(attrs={
                "class": "form-control", "min": 0, "step": 1
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
            "comentario": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Comentario (opcional)"
            }),
        }
        labels = {
            "minutos_autorizados": "Minutos autorizados",
            "status": "Estado",
            "comentario": "Comentario",
        }

    def clean_minutos_autorizados(self):
        v = self.cleaned_data.get("minutos_autorizados") or 0
        if v < 0:
            raise forms.ValidationError("Los minutos autorizados no pueden ser negativos.")
        # Si deseas forzar: autorizados <= calculados, descomenta:
        # calc = self.instance.minutos_calculados if self.instance else 0
        # if v > calc:
        #     raise forms.ValidationError(f"No puede autorizar más de los {calc} minutos calculados.")
        return v


class OvertimeRequestForm(forms.ModelForm):
    """
    CRUD completo de tiempos extra (opcional, por si quieres una vista admin/light).
    """
    class Meta:
        model = OvertimeRequest
        fields = [
            "emp_code", "fecha",
            "minutos_calculados", "minutos_autorizados",
            "status", "comentario",
        ]
        widgets = {
            "emp_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Código empleado"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "minutos_calculados": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": 1}),
            "minutos_autorizados": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": 1}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "comentario": forms.TextInput(attrs={"class": "form-control", "placeholder": "Comentario (opcional)"}),
        }
        labels = {
            "emp_code": "Código empleado",
            "fecha": "Fecha",
            "minutos_calculados": "Minutos extra calculados",
            "minutos_autorizados": "Minutos extra autorizados",
            "status": "Estado",
            "comentario": "Comentario",
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("minutos_calculados", 0) < 0:
            self.add_error("minutos_calculados", "No puede ser negativo.")
        if cleaned.get("minutos_autorizados", 0) < 0:
            self.add_error("minutos_autorizados", "No puede ser negativo.")
        # Forzar que autorizados <= calculados (opcional):
        # if cleaned.get("minutos_autorizados", 0) > cleaned.get("minutos_calculados", 0):
        #     self.add_error("minutos_autorizados", "No puede exceder los minutos calculados.")
        return cleaned
