from django.db import models

class MaintenanceRecord(models.Model):
    id = models.AutoField(primary_key=True)
    equipment_name = models.CharField(max_length=255)
    problem_description = models.TextField()
    maintenance_date = models.DateField()  # Campo de fecha
    technician = models.CharField(max_length=255)
    maintenance_type = models.CharField(
        max_length=50,
        choices=[
            ('Preventivo', 'Preventivo'),
            ('Correctivo', 'Correctivo'),
            ('Predictivo', 'Predictivo'),
        ]
    )
    maintenance_status = models.CharField(
        max_length=50,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Proceso', 'En Proceso'),
            ('Completado', 'Completado'),
        ]
    )
    activities_done = models.TextField(blank=True, null=True)
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ID_ANA-{self.id:02d} - {self.equipment_name}"
