from django.db import models

class EmployeeSchedule(models.Model):
    emp_code = models.CharField(
        'ID Empleado', max_length=20, unique=True,
        help_text="ID exacto del empleado (BioTime/zkbiotime)"
    )
    nombre = models.CharField(
        'Nombre Empleado', max_length=100, blank=True,
        help_text="Solo referencia, se puede llenar automáticamente al guardar"
    )
    entrada_manana = models.TimeField('Entrada Mañana')
    salida_manana = models.TimeField('Salida Mañana')
    entrada_tarde = models.TimeField('Entrada Tarde', null=True, blank=True)
    salida_tarde = models.TimeField('Salida Tarde', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre or self.emp_code} ({self.emp_code})"

    class Meta:
        verbose_name = "Horario de Empleado"
        verbose_name_plural = "Horarios de Empleados"
