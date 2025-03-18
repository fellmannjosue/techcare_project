from django import forms
from .models import Appointment_bl

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment_bl
        fields = ['parent_name', 'student_name', 'grade', 'relationship', 'teacher', 'reason']
