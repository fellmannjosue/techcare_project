from django.db import models

class TipoFalla(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Tipo de Falla")

    class Meta:
        db_table = 'tipo_falla'
        verbose_name = "Tipo de Falla"
        verbose_name_plural = "Tipos de Falla"

    def __str__(self):
        return self.nombre

class MaintenanceRecord(models.Model):
    equipment_id = models.CharField(max_length=50, verbose_name="ID del Equipo")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    serie = models.CharField(max_length=100, verbose_name="Serie")
    teacher_name = models.CharField(max_length=100, verbose_name="Nombre del Maestro")
    grade = models.CharField(max_length=100, verbose_name="Grado")
    tipo_falla = models.ForeignKey(TipoFalla, on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Falla")
    solucion = models.TextField(verbose_name="Solución Aplicada", null=True, blank=True)
    date = models.DateField(verbose_name="Fecha del Mantenimiento")
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Proceso', 'En Proceso'),
            ('Completado', 'Completado'),
        ],
        verbose_name="Estado"
    )
    observaciones = models.TextField(null=True, blank=True, verbose_name="Observaciones")

    class Meta:
        db_table = 'maintenance_record'
        verbose_name = "Registro de Mantenimiento"
        verbose_name_plural = "Registros de Mantenimiento"

    def __str__(self):
        return f"{self.equipment_id} - {self.teacher_name}"
