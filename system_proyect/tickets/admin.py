from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'name', 'email', 'description', 'attachment_link', 'status', 'created_at')

    def attachment_link(self, obj):
        """Muestra el archivo adjunto como un enlace en el panel de administración."""
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">Ver Adjunto</a>', obj.attachment.url)
        return "No disponible"
    
    attachment_link.short_description = "Adjunto"

admin.site.register(Ticket, TicketAdmin)
