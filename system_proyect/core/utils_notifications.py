# ============================================
#  utils_notifications.py – Notificaciones + Envío de correo
# ============================================

from django.core.mail import send_mail
from django.conf import settings
from core.models import Notificacion


def crear_notificacion(usuario, mensaje, modulo, tipo='info', extra=None, enviar_correo=True):
    """
    Crea una notificación en BD y opcionalmente envía un correo al usuario.

    Parámetros:
    - usuario: User destinatario
    - mensaje: Texto principal de la notificación
    - modulo: tickets, citas_bl, citas_col, reloj, coordinacion, etc.
    - tipo: info | alerta | exito | error  (para el badge de color)
    - extra: Diccionario adicional (opcional)
    - enviar_correo: True = enviará correo automáticamente
    """

    if usuario is None:
        return

    # Guardar notificación en BD
    Notificacion.objects.create(
        destinatario=usuario,
        mensaje=mensaje,
        modulo=modulo,
        tipo=tipo,
        extra=extra
    )

    # ----------------------------
    # ✉️ Enviar correo (si aplica)
    # ----------------------------
    if enviar_correo:
        try:
            send_mail(
                subject=f"[TechCare] Notificación de {modulo.capitalize()}",
                message=f"""
Hola {usuario.first_name or usuario.username},

{mensaje}

Este es un aviso automático del sistema TechCare.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=True,  # Para evitar que un error de correo rompa el sistema
            )
        except Exception:
            pass  # Seguridad adicional
