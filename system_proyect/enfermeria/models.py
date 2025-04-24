from django.db import models
from django.conf import settings  # Para AUTH_USER_MODEL

class Grado(models.Model):
    nombre = models.CharField("Grado", max_length=50)
    def __str__(self): return self.nombre


class Medico(models.Model):
    nombre = models.CharField("Nombre del Profesional", max_length=100)
    def __str__(self): return self.nombre


class AtencionMedica(models.Model):
    estudiante     = models.CharField("Nombre del Estudiante", max_length=100)
    grado          = models.ForeignKey(Grado,    on_delete=models.PROTECT, verbose_name="Grado")
    fecha_hora     = models.DateTimeField("Fecha y Hora")
    atendido_por   = models.ForeignKey(Medico,   on_delete=models.PROTECT, verbose_name="Atendido por")
    motivo         = models.TextField("Motivo")
    tratamiento    = models.TextField("Tratamiento")
    creado         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Atención Médica"
        verbose_name_plural = "Atenciones Médicas"

    def __str__(self):
        return f"{self.estudiante} – {self.fecha_hora:%d-%m-%Y %H:%M}"


class Proveedor(models.Model):
    nombre = models.CharField("Nombre del Proveedor", max_length=100)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


class Responsable(models.Model):
    nombre = models.CharField("Nombre del Responsable", max_length=100)

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"

    def __str__(self):
        return self.nombre


class InventarioMedicamento(models.Model):
    nombre = models.CharField("Medicamento", max_length=100)
    fecha_ingreso = models.DateField("Fecha de Ingreso")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    cantidad_existente = models.PositiveIntegerField("Cantidad Existente")
    modificado_por = models.ForeignKey(  # << NUEVO CAMPO
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modificado por"
    )

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_existente} disp.)"


class UsoMedicamento(models.Model):
    medicamento = models.ForeignKey(InventarioMedicamento, on_delete=models.CASCADE, related_name='usos')
    cantidad_usada = models.PositiveIntegerField("Cantidad Usada")
    responsable = models.ForeignKey(Responsable, on_delete=models.PROTECT, verbose_name="Responsable")
    comentario = models.TextField("Comentario", blank=True, null=True)
    fecha_uso = models.DateTimeField("Fecha de Uso", auto_now_add=True)

    class Meta:
        verbose_name = "Uso de Medicamento"
        verbose_name_plural = "Usos de Medicamentos"

    def __str__(self):
        return f"{self.medicamento.nombre} - {self.cantidad_usada} usado(s)"
