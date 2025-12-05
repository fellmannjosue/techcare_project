from django.urls import path
from .views_notifications import notificaciones_usuario, marcar_notificaciones_leidas

urlpatterns = [
    path("api/notificaciones/", notificaciones_usuario, name="api_notificaciones"),
    path("api/notificaciones/marcar/", marcar_notificaciones_leidas, name="api_notificaciones_marcar"),
]
