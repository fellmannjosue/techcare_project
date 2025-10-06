from core.models import Notificacion

def crear_notificacion(usuario, mensaje, modulo, tipo='info', extra=None):
    Notificacion.objects.create(
        destinatario=usuario,
        mensaje=mensaje,
        modulo=modulo,
        tipo=tipo,
        extra=extra
    )
