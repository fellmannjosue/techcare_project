from django.urls import path
from . import views
from django.contrib import admin
from accounts.views import menu_view  # Importar correctamente la vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('submit_ticket/', views.submit_ticket, name='submit_ticket'),
    path('success/', views.success, name='success'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('update_ticket/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
    path('menu/', menu_view, name='menu'),  # Usar la vista correctamente importada
]
