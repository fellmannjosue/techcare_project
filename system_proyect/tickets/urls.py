from django.urls import path
from . import views
from django.contrib import admin
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('submit_ticket/', views.submit_ticket, name='submit_ticket'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('ticket/<int:ticket_id>/comentarios/', views.ticket_comments, name='ticket_comments'),
    path('update_ticket/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
    path('menu/', lambda request: redirect('/accounts/menu/'), name='tickets_menu'),
]
