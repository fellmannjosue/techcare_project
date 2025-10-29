# reloj/models.py
from django.db import models

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
