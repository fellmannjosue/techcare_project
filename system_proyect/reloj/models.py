from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────────────────────
# HORARIOS POR PLANTILLAS
# ─────────────────────────────────────────────────────────────

class ScheduleTemplate(models.Model):
    nombre = models.CharField("Nombre de plantilla", max_length=120, unique=True)
    descripcion = models.TextField("Descripción", blank=True)

    class Meta:
        db_table = "reloj_schedule_template"
        verbose_name = "Plantilla de horario"
        verbose_name_plural = "Plantillas de horario"
        ordering = ["nombre"]

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
    weekday  = models.IntegerField("Día", choices=WEEKDAYS)
    trabaja  = models.BooleanField("Trabaja este día", default=True)

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
        ordering = ["-activo", "emp_code", "-fecha_inicio"]

    def __str__(self):
        fin = self.fecha_fin.isoformat() if self.fecha_fin else "∞"
        return f"{self.emp_code} → {self.template} [{self.fecha_inicio} → {fin}]"


# ─────────────────────────────────────────────────────────────
# OVERTIME (autorización staff) — por día/empleado
# ─────────────────────────────────────────────────────────────

class OvertimeRequest(models.Model):
    """
    Registro diario de tiempo extra por empleado.
    - minutos_calculados: lo que calcula el sistema (post-proceso en la vista).
    - minutos_autorizados: lo que aprueba el staff desde el modal.
    - approved_by / approved_at: quién y cuándo autorizó (columna 'Autorizado por').
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


# ─────────────────────────────────────────────────────────────
# EXCEPCIONES / REGISTROS AUXILIARES
# ─────────────────────────────────────────────────────────────

class Feriado(models.Model):
    fecha = models.DateField("Fecha de feriado", unique=True)
    descripcion = models.CharField("Descripción", max_length=255)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="feriados_creados", verbose_name="Creado por"
    )
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        db_table = "reloj_feriado"
        verbose_name = "Feriado"
        verbose_name_plural = "Feriados"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"


class SabadoEspecial(models.Model):
    fecha = models.DateField("Fecha", unique=True)
    descripcion = models.CharField("Descripción", max_length=255, default="Escuela para padres")
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sabados_creados", verbose_name="Creado por"
    )
    creado_en = models.DateTimeField("Creado en", auto_now_add=True)

    class Meta:
        db_table = "reloj_sabado_especial"
        verbose_name = "Sábado especial"
        verbose_name_plural = "Sábados especiales"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"


class TiempoCompensatorio(models.Model):
    """
    Solicitudes de tiempo extra registradas por usuario (vía Google Form o UI).
    No autoriza: solo captura y queda en estado PEND hasta que staff apruebe minutos.
    """
    STATUS_CHOICES = [
        ("PEND", "Pendiente"),
        ("APPR", "Aprobado"),
        ("REJC", "Rechazado"),
    ]

    emp_code = models.CharField("Código empleado", max_length=20, db_index=True)
    nombre_empleado = models.CharField("Nombre empleado", max_length=120)
    fecha = models.DateField("Fecha", db_index=True)
    minutos_registrados = models.PositiveIntegerField("Minutos registrados", default=0)
    motivo = models.TextField("Motivo", blank=True)

    # Auditoría / autorización (opcional)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tiempos_compensatorio_creados", verbose_name="Registrado por"
    )
    autorizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tiempos_compensatorio_autorizados", verbose_name="Autorizado por"
    )
    autorizado_en = models.DateTimeField("Autorizado en", null=True, blank=True)
    estado = models.CharField("Estado", max_length=4, choices=STATUS_CHOICES, default="PEND")

    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        db_table = "reloj_tiempo_compensatorio"
        verbose_name = "Tiempo compensatorio"
        verbose_name_plural = "Tiempos compensatorios"
        indexes = [
            models.Index(fields=["emp_code", "fecha"]),
            models.Index(fields=["estado"]),
        ]
        ordering = ["-fecha", "-creado_en"]

    def __str__(self):
        return f"{self.emp_code} - {self.nombre_empleado} - {self.fecha} ({self.minutos_registrados} min)"


class PermisoEmpleado(models.Model):
    """
    Permisos (ausencias justificadas): médico, personal, etc.
    Se verán en una ventana/listado y pueden excluirse del cálculo de faltantes.
    """
    emp_code = models.CharField("Código empleado", max_length=20, db_index=True)
    nombre_empleado = models.CharField("Nombre empleado", max_length=120)

    fecha_inicio = models.DateField("Desde")
    fecha_fin    = models.DateField("Hasta")
    motivo       = models.CharField("Motivo", max_length=255)

    autorizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="permisos_autorizados", verbose_name="Autorizado por"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="permisos_registrados", verbose_name="Registrado por"
    )
    aprobado = models.BooleanField("Aprobado", default=False)
    comentario_autorizacion = models.TextField("Comentario autorización", blank=True)

    creado_en = models.DateTimeField("Creado en", auto_now_add=True)
    actualizado_en = models.DateTimeField("Actualizado en", auto_now=True)

    class Meta:
        db_table = "reloj_permiso_empleado"
        verbose_name = "Permiso de empleado"
        verbose_name_plural = "Permisos de empleados"
        indexes = [
            models.Index(fields=["emp_code", "fecha_inicio", "fecha_fin"]),
            models.Index(fields=["aprobado"]),
        ]
        ordering = ["-fecha_inicio", "emp_code"]

    def __str__(self):
        return f"{self.emp_code} - {self.nombre_empleado} ({self.fecha_inicio}→{self.fecha_fin})"
