from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.inventory_dashboard, name='inventory_dashboard'),
    path('download_item_pdf/<int:item_id>/', views.download_item_pdf, name='download_item_pdf'),
    path('menu/', lambda request: redirect('/accounts/menu/'), name='inventory_menu'),
]
