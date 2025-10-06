from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=300)
    modulo = models.CharField(max_length=50)   # Ejemplo: 'tickets', 'enfermeria', 'citas'
    tipo = models.CharField(max_length=30, default='info')  # Ejemplo: 'info', 'alerta', 'exito', 'error'
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    extra = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Notificación para {self.destinatario} - {self.mensaje[:50]}'
