from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    # Ventana 1: Datos del usuario
    path('user-data_col/', views.user_data_col, name='user_data_col'),

    # Ventana 2: Motivo de la cita
    path('motivo_col/', views.motivo_col, name='motivo_col'),

    # Ventana 3: Selección de fecha y hora
    path('select-date_col/<int:appointment_id>/', views.select_date_col, name='select_date_col'),

    # API: Obtener materias por grado
    path('get-subjects-by-grade_col/', views.get_subjects_by_grade_col, name='get_subjects_by_grade_col'),

    # API: Obtener maestro y área por materia
    path('get-teacher-by-subject_col/', views.get_teacher_by_subject_col, name='get_teacher_by_subject_col'),

    # Vista del Dashboard
    path('dashboard_col/', views.dashboard_col, name='dashboard_col'),

    # API: Obtener horarios disponibles
    path('get-available-slots_col/', views.get_available_slots_col, name='get_available_slots_col'),

    path('admin/', admin.site.urls),
]
