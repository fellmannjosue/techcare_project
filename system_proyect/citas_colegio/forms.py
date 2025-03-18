from django import forms
from .models import Appointment_col

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment_col
        fields = ['parent_name', 'student_name', 'grade', 'relationship', 'teacher', 'reason']
