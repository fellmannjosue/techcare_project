from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    Appointment_bl,
    Teacher_bl,
    Grade_bl,
    Subject_bl,
    Relationship_bl,
    Schedule_bl
)
from .forms import AppointmentForm
from datetime import datetime, timedelta

# IMPORTS PARA EL ENVÍO DE CORREOS
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# ================================================
# ============ FUNCIÓN DE NOTIFICACIÓN ===========
# ================================================
def enviar_notificacion_cita_bl(appointment):
    """
    Envía un correo al coordinador con los detalles de la cita bilingüe creada.
    Ajusta la plantilla y destinatarios de acuerdo a tu caso.
    """
    subject = "Nueva Cita Bilingüe Programada"
    # Lista de destinatarios (ajusta según tus necesidades)
    to_email = ["coordinacion_bl@ana-hn.org"]  
    
    # Diccionario con la info que usarás en la plantilla de correo
    context = {
        'appointment': appointment,
    }

    # Asegúrate de que existe la plantilla 'emails/nueva_cita.html'
    html_content = render_to_string("email/nueva_cita_bl.html", context)
    text_content = strip_tags(html_content)  # Versión texto plano

    # Configura from_email de acuerdo a tu settings.py o alias que uses
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email='coordinacion_bl@ana-hn.org',  
        to=to_email
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

# ================================================
# ============= VISTAS PRINCIPALES ==============
# ================================================

def user_data_bl(request):
    """Primera ventana: captura de datos del usuario."""
    if request.method == 'POST':
        parent_name = request.POST.get('parent_name')
        student_name = request.POST.get('student_name')
        relationship_id = request.POST.get('relationship')

        if parent_name and student_name and relationship_id:
            # Guardar los datos en sesión
            request.session['parent_name'] = parent_name
            request.session['student_name'] = student_name
            request.session['relationship_id'] = relationship_id
            return redirect('motivo_bl')
        else:
            return render(request, 'citas_billingue/user_data_bl.html', {
                'error': 'Por favor, complete todos los campos.',
                'relationships': Relationship_bl.objects.all(),
            })

    return render(request, 'citas_billingue/user_data_bl.html', {
        'relationships': Relationship_bl.objects.all(),
    })


def motivo_bl(request):
    """Segunda ventana: selección del motivo y detalles."""
    if request.method == 'POST':
        grade_id = request.POST.get('grade')
        subject_id = request.POST.get('subject')
        reason = request.POST.get('reason')

        if grade_id and subject_id and reason:
            parent_name = request.session.get('parent_name')
            student_name = request.session.get('student_name')
            relationship_id = request.session.get('relationship_id')

            if not all([parent_name, student_name, relationship_id]):
                return JsonResponse({'error': 'Faltan datos del usuario. Por favor, regrese al paso anterior.'}, status=400)

            try:
                subject = Subject_bl.objects.get(id=subject_id)
            except Subject_bl.DoesNotExist:
                return JsonResponse({'error': 'La materia seleccionada no existe.'}, status=400)

            appointment = Appointment_bl.objects.create(
                parent_name=parent_name,
                student_name=student_name,
                relationship_id=relationship_id,
                grade_id=grade_id,
                subject=subject,
                teacher=subject.teacher,
                area=subject.teacher.area,
                reason=reason
            )

            return JsonResponse({'appointment_id': appointment.id}, status=200)

        return JsonResponse({'error': 'Por favor, complete todos los campos del formulario.'}, status=400)

    return render(request, 'citas_billingue/motivo_bl.html', {
        'grades': Grade_bl.objects.all(),
    })


def select_date_bl(request, appointment_id):
    """Tercera ventana: selección de fecha y hora."""
    appointment = get_object_or_404(Appointment_bl, id=appointment_id)

    if request.method == 'POST':
        date = request.POST.get('selected_date')
        time = request.POST.get('selected_time')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if date and time and email and phone:
            appointment.date = date
            appointment.time = time
            appointment.email = email
            appointment.phone = phone
            appointment.save()

            # ================================================
            # Llamada a la función que envía el correo
            enviar_notificacion_cita_bl(appointment)
            # ================================================

            return redirect('dashboard_bl')
        else:
            return render(request, 'citas_billingue/select-date_bl.html', {
                'error': 'Todos los campos son obligatorios.',
                'appointment': appointment,
            })

    return render(request, 'citas_billingue/select-date_bl.html', {
        'appointment': appointment,
    })


def get_available_slots(request):
    """API para obtener horarios disponibles."""
    teacher_id = request.GET.get('teacher_id')
    date_str = request.GET.get('date')

    if not teacher_id or not date_str:
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Traducción al español
        dias_es = {
            'Monday': 'lunes',
            'Tuesday': 'martes',
            'Wednesday': 'miércoles',
            'Thursday': 'jueves',
            'Friday': 'viernes',
            'Saturday': 'sábado',
            'Sunday': 'domingo'
        }
        day_of_week = dias_es[selected_date.strftime('%A')]

        schedules = Schedule_bl.objects.filter(teacher_id=teacher_id, day_of_week=day_of_week)
        reserved_slots = Appointment_bl.objects.filter(teacher_id=teacher_id, date=selected_date).values_list('time', flat=True)

        available_slots = []
        for schedule in schedules:
            start_time = schedule.start_time
            end_time = schedule.end_time

            while start_time < end_time:
                next_time = (
                    datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)
                ).time()
                slot_range = f"{start_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"

                if start_time not in reserved_slots:
                    available_slots.append({'time': slot_range, 'available': True})
                else:
                    available_slots.append({'time': slot_range, 'available': False})

                start_time = next_time

        return JsonResponse({'slots': available_slots})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def dashboard_bl(request):
    """Vista del Dashboard para mostrar citas."""
    appointments = Appointment_bl.objects.all().order_by('date', 'time')
    return render(request, 'citas_billingue/dashboard_bl.html', {
        'appointments': appointments,
    })


@login_required
def delete_appointment_bl(request, appointment_id):
    """Elimina una cita y notifica con un mensaje de éxito."""
    cita = get_object_or_404(Appointment_bl, id=appointment_id)
    cita.delete()
    messages.success(request, 'Cita eliminada exitosamente.')
    return redirect('dashboard_bl')


def get_subjects_by_grade(request):
    """API para obtener las materias relacionadas con un grado."""
    grade_id = request.GET.get('grade_id')
    if not grade_id:
        return JsonResponse({'error': 'Grado no proporcionado'}, status=400)

    try:
        subjects = Subject_bl.objects.filter(grade_id=grade_id)
        data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_teacher_by_subject(request):
    """API para obtener el maestro y el área relacionada con una materia."""
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Materia no proporcionada'}, status=400)

    try:
        subject = Subject_bl.objects.get(id=subject_id)
        teacher = subject.teacher
        data = {
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'area': teacher.area,
            }
        }
        return JsonResponse(data)
    except Subject_bl.DoesNotExist:
        return JsonResponse({'error': 'Materia no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
