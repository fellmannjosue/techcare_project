from django.db import models

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

class InventarioMedicamento(models.Model):
    nombre             = models.CharField("Medicamento", max_length=100)
    fecha_ingreso      = models.DateField("Fecha de Ingreso")
    proveedor          = models.CharField("Proveedor", max_length=100)
    cantidad_existente = models.PositiveIntegerField("Cantidad Existente")
    cantidad_usado     = models.PositiveIntegerField("Cantidad Usada")
    responsable        = models.CharField("Responsable", max_length=100)
    total              = models.DecimalField("Total", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Inventario"
        verbose_name_plural = "Inventarios de Medicamentos"

    def __str__(self):
        return f"{self.nombre} ({self.cantidad_existente} disp.)"
