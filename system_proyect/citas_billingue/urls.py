from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    # Ventana 1: Datos del usuario
    path('user-data_bl/', views.user_data_bl, name='user_data_bl'),

    # Ventana 2: Motivo de la cita
    path('motivo_bl/', views.motivo_bl, name='motivo_bl'),

    # Ventana 3: Selección de fecha y hora
    path('select-date_bl/<int:appointment_id>/', views.select_date_bl, name='select_date_bl'),

    # API: Obtener materias por grado
    path('get-subjects-by-grade/', views.get_subjects_by_grade, name='get_subjects_by_grade'),

    # API: Obtener maestro y área por materia
    path('get-teacher-by-subject/', views.get_teacher_by_subject, name='get_teacher_by_subject'),

    # Vista del Dashboard
    path('dashboard_bl/', views.dashboard_bl, name='dashboard_bl'),

    # API: Obtener horarios disponibles
    path('get-available-slots/', views.get_available_slots, name='get_available_slots'),

    path('admin/', admin.site.urls),
]
