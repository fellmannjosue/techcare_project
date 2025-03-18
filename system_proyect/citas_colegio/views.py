from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Appointment_col, Teacher_col, Grade_col, Subject_col, Relationship_col, Schedule_col
from .forms import AppointmentForm
from datetime import datetime, timedelta

def user_data_col(request):
    """Primera ventana: captura de datos del usuario."""
    if request.method == 'POST':
        parent_name = request.POST.get('parent_name')
        student_name = request.POST.get('student_name')
        relationship_id = request.POST.get('relationship')

        if parent_name and student_name and relationship_id:
            request.session['parent_name'] = parent_name
            request.session['student_name'] = student_name
            request.session['relationship_id'] = relationship_id
            return redirect('motivo_col')
        else:
            return render(request, 'citas_colegio/user_data_col.html', {
                'error': 'Por favor, complete todos los campos.',
                'relationships': Relationship_col.objects.all(),
            })

    return render(request, 'citas_colegio/user_data_col.html', {
        'relationships': Relationship_col.objects.all(),
    })

def motivo_col(request):
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
                return JsonResponse({'error': 'Faltan datos del usuario. Regrese al paso anterior.'}, status=400)

            try:
                subject = Subject_col.objects.get(id=subject_id)
            except Subject_col.DoesNotExist:
                return JsonResponse({'error': 'La materia seleccionada no existe.'}, status=400)

            appointment = Appointment_col.objects.create(
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

        return JsonResponse({'error': 'Complete todos los campos del formulario.'}, status=400)

    return render(request, 'citas_colegio/motivo_col.html', {
        'grades': Grade_col.objects.all(),
    })

def select_date_col(request, appointment_id):
    """Tercera ventana: selección de fecha y hora."""
    appointment = get_object_or_404(Appointment_col, id=appointment_id)

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
            return redirect('dashboard_col')
        else:
            return render(request, 'citas_colegio/select-date_col.html', {
                'error': 'Todos los campos son obligatorios.',
                'appointment': appointment,
            })

    return render(request, 'citas_colegio/select-date_col.html', {
        'appointment': appointment,
    })

def get_available_slots_col(request):
    """API para obtener horarios disponibles."""
    teacher_id = request.GET.get('teacher_id')
    date_str = request.GET.get('date')

    if not teacher_id or not date_str:
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = selected_date.strftime('%A')

        schedules = Schedule_col.objects.filter(teacher_id=teacher_id, day_of_week=day_of_week)
        reserved_slots = Appointment_col.objects.filter(teacher_id=teacher_id, date=selected_date).values_list('time', flat=True)

        available_slots = []
        for schedule in schedules:
            start_time = schedule.start_time
            end_time = schedule.end_time

            while start_time < end_time:
                next_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)).time()
                slot_range = f"{start_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                available_slots.append({'time': slot_range, 'available': start_time not in reserved_slots})
                start_time = next_time

        return JsonResponse({'slots': available_slots})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def dashboard_col(request):
    """Vista del Dashboard para mostrar citas."""
    appointments = Appointment_col.objects.all().order_by('date', 'time')
    return render(request, 'citas_colegio/dashboard_col.html', {
        'appointments': appointments,
    })

def get_subjects_by_grade_col(request):
    """API para obtener las materias relacionadas con un grado."""
    grade_id = request.GET.get('grade_id')
    if not grade_id:
        return JsonResponse({'error': 'Grado no proporcionado'}, status=400)

    try:
        subjects = Subject_col.objects.filter(grade_id=grade_id)
        data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_teacher_by_subject_col(request):
    """API para obtener el maestro y el área relacionada con una materia."""
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'Materia no proporcionada'}, status=400)

    try:
        subject = Subject_col.objects.get(id=subject_id)
        teacher = subject.teacher
        data = {
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'area': teacher.area,
            }
        }
        return JsonResponse(data)
    except Subject_col.DoesNotExist:
        return JsonResponse({'error': 'Materia no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
