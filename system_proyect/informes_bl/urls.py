# informes_bl/urls.py
from django.urls import path
from . import views

app_name = 'informes_bl'

urlpatterns = [
    # 1) Sub-dashboard de “Notas y Informes”
    path('', views.notas_dashboard, name='notas_dashboard'),

    # 2) CRUD Progress Report
    path('progress/',               views.progress_list,   name='progress_list'),
    path('progress/crear/',         views.progress_edit,   name='progress_create'),
    path('progress/editar/<int:pk>/', views.progress_edit, name='progress_edit'),
    path('progress/borrar/<int:pk>/', views.progress_delete, name='progress_delete'),
    path('progress/imprimir/<int:pk>/', views.progress_print, name='progress_print'),
]
