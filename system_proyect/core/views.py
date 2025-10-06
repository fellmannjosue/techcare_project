from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .models import Notificacion
import json

@require_GET
@login_required
def notificaciones_usuario(request):
    """
    Devuelve las notificaciones NO leídas del usuario actual (máximo 20).
    """
    notis = Notificacion.objects.filter(destinatario=request.user, leida=False).order_by('-fecha')[:20]
    data = [{
        'id': n.id,
        'mensaje': n.mensaje,
        'modulo': n.modulo,
        'tipo': n.tipo,
        'fecha': n.fecha.strftime('%d-%m-%Y %H:%M'),
        'extra': n.extra
    } for n in notis]
    return JsonResponse({'notificaciones': data})

@require_POST
@login_required
def marcar_notificaciones_leidas(request):
    """
    Marca notificaciones como leídas.
    Recibe JSON POST: {'ids': [1,2,3]}
    """
    try:
        ids = json.loads(request.body).get('ids', [])
        Notificacion.objects.filter(destinatario=request.user, id__in=ids).update(leida=True)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
