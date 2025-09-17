from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketComment

class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    readonly_fields = ('usuario', 'fecha',)
    fields = ('usuario', 'mensaje', 'fecha')

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'name', 'email', 'description', 'attachment_link', 'status', 'created_at')
    inlines = [TicketCommentInline]

    def attachment_link(self, obj):
        """Muestra el archivo adjunto como un enlace en el panel de administración."""
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">Ver Adjunto</a>', obj.attachment.url)
        return "No disponible"
    attachment_link.short_description = "Adjunto"

class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'usuario', 'mensaje', 'fecha')
    list_filter = ('ticket', 'usuario', 'fecha')
    search_fields = ('mensaje', 'usuario__username', 'ticket__ticket_id')
    readonly_fields = ('usuario', 'fecha')

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketComment, TicketCommentAdmin)
