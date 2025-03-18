from django.db import models
from datetime import datetime

class Ticket(models.Model):
    ticket_id = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=50)
    email = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    status = models.CharField(max_length=50, default='Enviado')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tickets'

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            date_part = datetime.now().strftime("%Y%m%d")  # Genera la fecha en formato YYYYMMDD
            last_ticket = Ticket.objects.filter(ticket_id__startswith=f"TICKET-{date_part}") \
                                        .order_by('-created_at') \
                                        .first()

            if last_ticket:
                last_number = int(last_ticket.ticket_id.split('-')[-1]) + 1
            else:
                last_number = 1

            self.ticket_id = f"TICKET-{date_part}-{last_number:04d}"  # Ej: TICKET-20250128-0001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.name}"
