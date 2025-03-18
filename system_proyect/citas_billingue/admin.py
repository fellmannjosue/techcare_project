from django.contrib import admin
from .models import Teacher_bl, Schedule_bl, Appointment_bl, Relationship_bl, Grade_bl, Subject_bl

# Configuración para el modelo Teacher
@admin.register(Teacher_bl)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'class_name')

# Configuración para el modelo Schedule
@admin.register(Schedule_bl)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'day_of_week', 'start_time', 'end_time')

# Configuración para el modelo Appointment
@admin.register(Appointment_bl)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'student_name', 'subject', 'teacher', 'grade', 'date', 'time', 'status')
    list_filter = ('status', 'teacher', 'date', 'grade', 'subject')
    search_fields = ('parent_name', 'student_name', 'teacher__name', 'subject__name')

# Configuración para el modelo Grade
@admin.register(Grade_bl)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Configuración para el modelo Subject
@admin.register(Subject_bl)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'teacher')
    list_filter = ('grade', 'teacher')
    search_fields = ('name', 'grade__name', 'teacher__name')

# Configuración para el modelo Relationship
@admin.register(Relationship_bl)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('name',)
