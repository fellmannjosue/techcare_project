# reloj/models.py
from django.db import models
from django.conf import settings

class ScheduleTemplate(models.Model):
    nombre = models.CharField("Nombre de plantilla", max_length=120, unique=True)
    descripcion = models.TextField("Descripción", blank=True)

    class Meta:
        db_table = "reloj_schedule_template"
        verbose_name = "Plantilla de horario"
        verbose_name_plural = "Plantillas de horario"

    def __str__(self):
        return self.nombre


class ScheduleRule(models.Model):
    WEEKDAYS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]
    template = models.ForeignKey(ScheduleTemplate, on_delete=models.CASCADE, related_name="reglas")
    weekday = models.IntegerField("Día", choices=WEEKDAYS)
    trabaja = models.BooleanField("Trabaja este día", default=True)

    # Soporte de turno partido
    entrada_manana = models.TimeField("Entrada mañana", null=True, blank=True)
    salida_manana  = models.TimeField("Salida mañana",  null=True, blank=True)
    entrada_tarde  = models.TimeField("Entrada tarde",  null=True, blank=True)
    salida_tarde   = models.TimeField("Salida tarde",   null=True, blank=True)

    class Meta:
        db_table = "reloj_schedule_rule"
        verbose_name = "Regla de día"
        verbose_name_plural = "Reglas de día"
        unique_together = ("template", "weekday")
        ordering = ["template", "weekday"]

    def __str__(self):
        return f"{self.template} - {self.get_weekday_display()}"


class EmployeeScheduleAssignment(models.Model):
    emp_code = models.CharField("Código empleado", max_length=20, db_index=True)
    nombre_empleado = models.CharField("Nombre empleado (cache)", max_length=200, blank=True)

    template = models.ForeignKey(ScheduleTemplate, on_delete=models.PROTECT, related_name="asignaciones")
    fecha_inicio = models.DateField("Vigente desde")
    fecha_fin    = models.DateField("Vigente hasta", null=True, blank=True)  # null = indefinida
    activo       = models.BooleanField("Activo", default=True)

    class Meta:
        db_table = "reloj_employee_schedule_assignment"
        verbose_name = "Asignación de plantilla"
        verbose_name_plural = "Asignaciones de plantilla"
        indexes = [
            models.Index(fields=["emp_code", "fecha_inicio", "fecha_fin"]),
        ]

    def __str__(self):
        fin = self.fecha_fin.isoformat() if self.fecha_fin else "∞"
        return f"{self.emp_code} → {self.template} [{self.fecha_inicio} → {fin}]"

class OvertimeRequest(models.Model):
    """
    Registro diario de tiempo extra por empleado.
    - minutos_calculados: lo que calcula el sistema (post-proceso en la vista).
    - minutos_autorizados: lo que aprueba el staff desde el modal.
    - approved_by / approved_at: quién y cuándo autorizó (columna "Autorizado por").
    """
    STATUS_CHOICES = [
        ("PEND", "Pendiente"),
        ("APPR", "Aprobado"),
        ("REJC", "Rechazado"),
    ]

    emp_code = models.CharField("Código empleado", max_length=20, db_index=True)
    fecha = models.DateField("Fecha", db_index=True)

    minutos_calculados  = models.PositiveIntegerField("Minutos extra calculados", default=0)
    minutos_autorizados = models.PositiveIntegerField("Minutos extra autorizados", default=0)

    comentario = models.CharField("Comentario", max_length=255, blank=True)
    status     = models.CharField("Estado", max_length=4, choices=STATUS_CHOICES, default="PEND")

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Autorizado por",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="overtime_aprobados"
    )
    approved_at = models.DateTimeField("Fecha de autorización", null=True, blank=True)

    created_at  = models.DateTimeField("Creado en", auto_now_add=True)
    updated_at  = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        db_table = "reloj_overtime_request"
        verbose_name = "Tiempo extra"
        verbose_name_plural = "Tiempos extra"
        unique_together = ("emp_code", "fecha")
        indexes = [
            models.Index(fields=["emp_code", "fecha"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-fecha", "emp_code"]

    def __str__(self):
        return f"{self.emp_code} {self.fecha} - {self.get_status_display()}"

    @property
    def approver_display(self) -> str:
        """Nombre bonito para mostrar en la columna 'Autorizado por'."""
        if self.approved_by:
            full = (self.approved_by.get_full_name() or "").strip()
            return full or self.approved_by.username
        return ""