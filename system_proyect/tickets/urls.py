from django.urls import path
from . import views
from django.shortcuts import redirect
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    path('submit_ticket/', views.submit_ticket, name='submit_ticket'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('ticket/<int:ticket_id>/comentarios/', views.ticket_comments, name='ticket_comments'),
    path('ticket_comments/ajax/<int:ticket_id>/', views.ticket_comments_ajax, name='ticket_comments_ajax'),
    path('menu/', lambda request: redirect('/accounts/menu/'), name='tickets_menu'),

    path('ticket_status_update_ajax/<int:ticket_id>/', views.ticket_status_update_ajax, name='ticket_status_update_ajax'),
    path('ticket_status_get_ajax/<int:ticket_id>/', views.ticket_status_get_ajax, name='ticket_status_get_ajax'),

    # 🚀 IA — Endpoint AJAX para chat IA
    path('ticket/<int:ticket_id>/chat_ai/', views.ticket_chat_ai_ajax, name='ticket_chat_ai_ajax'),
]
