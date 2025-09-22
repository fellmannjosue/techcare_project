from django.urls import path
from . import views
from django.shortcuts import redirect
from django.contrib import admin

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Enviar/crear ticket
    path('submit_ticket/', views.submit_ticket, name='submit_ticket'),

    # Dashboard de técnico
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),

    # Comentarios del ticket (vista principal y AJAX)
    path('ticket/<int:ticket_id>/comentarios/', views.ticket_comments, name='ticket_comments'),
    path('ticket_comments/ajax/<int:ticket_id>/', views.ticket_comments_ajax, name='ticket_comments_ajax'),

    # Menú (redirige a accounts/menu)
    path('menu/', lambda request: redirect('/accounts/menu/'), name='tickets_menu'),

    # =======================
    # RUTAS AJAX DE ESTADO
    # =======================
    path('ticket_status_update_ajax/<int:ticket_id>/', views.ticket_status_update_ajax, name='ticket_status_update_ajax'),
    path('ticket_status_get_ajax/<int:ticket_id>/', views.ticket_status_get_ajax, name='ticket_status_get_ajax'),
]
