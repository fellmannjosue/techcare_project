from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Ticket(models.Model):
    ticket_id = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=50)
    email = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    status = models.CharField(max_length=50, default='Enviado')
    comments = models.TextField(blank=True, null=True)

    # ⭐ CAMPO NUEVO PARA BLOQUEAR A LA IA
    ia_bloqueada = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tickets'

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            date_part = datetime.now().strftime("%Y%m%d")
            last_ticket = Ticket.objects.filter(ticket_id__startswith=f"TICKET-{date_part}") \
                                        .order_by('-created_at') \
                                        .first()
            if last_ticket:
                last_number = int(last_ticket.ticket_id.split('-')[-1]) + 1
            else:
                last_number = 1

            self.ticket_id = f"TICKET-{date_part}-{last_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.name}"


class TicketComment(models.Model):
    TIPO_CHOICES = (
        ('usuario', 'Usuario'),
        ('tecnico', 'Técnico'),
        ('ia', 'IA'),
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje = models.TextField("Comentario")
    fecha = models.DateTimeField("Fecha", auto_now_add=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='usuario'
    )

    class Meta:
        verbose_name = "Comentario de Ticket"
        verbose_name_plural = "Comentarios de Tickets"
        ordering = ['fecha']

    def __str__(self):
        autor = self.usuario.username if self.usuario else self.get_tipo_display()
        return f"{autor} – {self.fecha.strftime('%d/%m/%Y %H:%M')}: {self.mensaje[:40]}"
