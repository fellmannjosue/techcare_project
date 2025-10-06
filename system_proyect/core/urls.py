from django.urls import path
from . import views

urlpatterns = [
    path('notificaciones/', views.notificaciones_usuario, name='notificaciones_usuario'),
    path('notificaciones/marcar-leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
]
