# mantenimiento/urls.py
from django.urls import path
from . import views
from django.shortcuts import redirect



urlpatterns = [
    path('',                        views.maintenance_dashboard,    name='maintenance_dashboard'),
    path('download/<int:record_id>/', views.download_maintenance_pdf, name='download_maintenance_pdf'),
    path('menu/',                    lambda request: redirect('/accounts/menu/'), name='maintenance_menu'),
]
