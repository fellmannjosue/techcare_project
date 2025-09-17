from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket
from .forms import TicketForm
import os
import json
from threading import Thread

# Ruta de URL pública para imágenes
PUBLIC_IMAGE_URL = ""

def send_email_async(subject, message, recipient_list):
    """Función para enviar correos de forma asíncrona."""
    Thread(
        target=send_mail,
        args=(subject, '', 'techcare.app2024@gmail.com', recipient_list),
        kwargs={'html_message': message, 'fail_silently': False}
    ).start()

@csrf_exempt
def submit_ticket(request):
    """
    Maneja la creación de tickets desde usuarios web o PyQt5 (JSON).
    Permite adjuntar archivos y envía correos de notificación.
    """
    if request.method == 'POST':
        # Manejar solicitudes JSON desde PyQt5
        if request.headers.get('Content-Type') == 'application/json':
            try:
                # Parsear los datos JSON
                data = json.loads(request.body)
                name = data.get('name')
                grade = data.get('grade')
                description = data.get('description')

                # Obtén SIEMPRE el email del usuario autenticado
                email = request.user.email if request.user.is_authenticated else data.get('email')

                # Validar que todos los campos estén completos
                if not all([name, grade, email, description]):
                    return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)

                # Crear el ticket
                ticket = Ticket.objects.create(
                    name=name,
                    grade=grade,
                    email=email,  # Siempre el del usuario autenticado (si está logueado)
                    description=description
                )

                # Enviar correos
                subject_technician = f'Nuevo Ticket #{ticket.ticket_id} - {ticket.name}'
                message_technician = render_to_string(
                    'tickets/email/email_notification.html',
                    {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL}
                )
                send_email_async(subject_technician, message_technician, ['techcare.app2024@gmail.com'])

                subject_user = f'Ticket #{ticket.ticket_id} - Confirmación de Recepción'
                message_user = render_to_string(
                    'tickets/email/email_notification.html',
                    {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL}
                )
                send_email_async(subject_user, message_user, [ticket.email])

                return JsonResponse({'message': f'Ticket #{ticket.ticket_id} creado exitosamente'}, status=201)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Error al procesar los datos JSON'}, status=400)

        # Manejar solicitudes estándar desde formularios web
        else:
            form = TicketForm(request.POST, request.FILES)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.email = request.user.email   # ← SIEMPRE el email del usuario autenticado
                ticket.save()

                # Enviar correos
                subject_technician = f'Nuevo Ticket #{ticket.ticket_id} - {ticket.name}'
                message_technician = render_to_string(
                    'tickets/email/email_notification.html',
                    {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL}
                )
                send_email_async(subject_technician, message_technician, ['techcare.app2024@gmail.com'])

                subject_user = f'Ticket #{ticket.ticket_id} - Confirmación de Recepción'
                message_user = render_to_string(
                    'tickets/email/email_notification.html',
                    {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL}
                )
                send_email_async(subject_user, message_user, [ticket.email])

                messages.success(request, f'Ticket #{ticket.ticket_id} creado exitosamente.')
                return JsonResponse({'message': f'Ticket #{ticket.ticket_id} creado exitosamente'}, status=201)

            else:
                errors = form.errors.as_json()
                return JsonResponse({'error': 'Error en el formulario', 'details': errors}, status=400)

    else:
        form = TicketForm()
        # Pasa el email del usuario logueado al formulario para autollenar (opcional)
        user_email = request.user.email if request.user.is_authenticated else ""
        return render(request, 'tickets/submit_ticket.html', {'form': form, 'user_email': user_email})
@login_required
def technician_dashboard(request):
    tickets = Ticket.objects.all()
    messages.info(request, 'Bienvenido al Dashboard de Técnico.')
    return render(request, 'tickets/technician_dashboard.html', {'tickets': tickets})



@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_comments = request.POST.get('comments')

        # Actualizar el estado
        if new_status and new_status != ticket.status:
            ticket.status = new_status

        # Actualizar los comentarios
        if new_comments is not None:  # Permite vaciar comentarios
            ticket.comments = new_comments

        # Guardar cambios
        ticket.save()

        # Notificación al usuario
        subject_update = f'Ticket #{ticket.ticket_id} - Estado Actualizado'
        message_update = render_to_string(
            'tickets/email/ticket_update.html',
            {
                'ticket': ticket,
                'technician_name': 'Equipo Técnico',
                'comments': ticket.comments,  # Incluir comentarios en el contexto
                'img_url': PUBLIC_IMAGE_URL
            }
        )
        send_email_async(subject_update, message_update, [ticket.email])

        # Mensaje de éxito
        messages.success(request, f'El estado del ticket #{ticket.ticket_id} se actualizó correctamente.')
        return redirect('technician_dashboard')

    return render(request, 'tickets/update_ticket.html', {'ticket': ticket})
