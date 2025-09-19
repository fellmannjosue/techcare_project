from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Ticket, TicketComment
from .forms import TicketForm, TicketCommentForm
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
import json
from threading import Thread

PUBLIC_IMAGE_URL = ""

def send_email_async(subject, message, recipient_list):
    Thread(
        target=send_mail,
        args=(subject, '', 'techcare.app2024@gmail.com', recipient_list),
        kwargs={'html_message': message, 'fail_silently': False}
    ).start()

@csrf_exempt
def submit_ticket(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                name = data.get('name')
                grade = data.get('grade')
                description = data.get('description')
                email = request.user.email if request.user.is_authenticated else data.get('email')
                if not all([name, grade, email, description]):
                    return JsonResponse({'error': 'Todos los campos son obligatorios'}, status=400)
                ticket = Ticket.objects.create(
                    name=name,
                    grade=grade,
                    email=email,
                    description=description
                )
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
        else:
            form = TicketForm(request.POST, request.FILES)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.email = request.user.email
                ticket.save()
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
        if new_status and new_status != ticket.status:
            ticket.status = new_status
        if new_comments is not None:
            ticket.comments = new_comments
        ticket.save()
        subject_update = f'Ticket #{ticket.ticket_id} - Estado Actualizado'
        message_update = render_to_string(
            'tickets/email/ticket_update.html',
            {
                'ticket': ticket,
                'technician_name': 'Equipo Técnico',
                'comments': ticket.comments,
                'img_url': PUBLIC_IMAGE_URL
            }
        )
        send_email_async(subject_update, message_update, [ticket.email])
        messages.success(request, f'El estado del ticket #{ticket.ticket_id} se actualizó correctamente.')
        return redirect('technician_dashboard')
    return render(request, 'tickets/update_ticket.html', {'ticket': ticket})

@login_required
def ticket_comments(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')

    # MENSAJE AUTOMÁTICO SI NO HAY COMENTARIOS PREVIOS (corregido para evitar usuario=None)
    if not comentarios.exists():
        User = get_user_model()
        try:
            usuario_soporte = User.objects.get(username='soporte_tecnico')
        except User.DoesNotExist:
            # Fallback: primer staff, luego primer superuser, sino el primer usuario del sistema
            usuario_soporte = (
                User.objects.filter(is_staff=True).first() or
                User.objects.filter(is_superuser=True).first() or
                User.objects.all().first()
            )
        # Solo crear si se encuentra algún usuario
        if usuario_soporte:
            TicketComment.objects.create(
                ticket=ticket,
                usuario=usuario_soporte,
                mensaje="Soporte técnico de Asociación Nuevo Amanecer: ¿En qué le podemos ayudar? Descríbanos el problema que presenta.",
                fecha=timezone.now()
            )
            comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')
        # Si no hay ningún usuario, NO se crea el comentario para evitar error

    if request.method == 'POST':
        try:
            form = TicketCommentForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.ticket = ticket
                comentario.usuario = request.user
                comentario.save()
                # Enviar correo (manejo de error silencioso)
                try:
                    subject = f"Nuevo comentario en Ticket #{ticket.ticket_id}"
                    html_message = render_to_string(
                        'tickets/email/nuevo_comentario.html',
                        {'ticket': ticket, 'comentario': comentario, 'autor': request.user}
                    )
                    send_email_async(subject, html_message, [ticket.email])
                except Exception as e:
                    print("Error enviando correo:", e)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'ok': True, 'mensaje': 'Comentario agregado correctamente.'})
                else:
                    messages.success(request, "Comentario agregado y notificado por correo.")
                    return redirect('ticket_comments', ticket_id=ticket.id)
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'error': form.errors.as_json()}, status=400)
                else:
                    messages.error(request, "Error en el formulario.")
        except Exception as ex:
            import traceback
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': False,
                    'error': str(ex),
                    'trace': traceback.format_exc()
                }, status=500)
            else:
                raise ex
    else:
        form = TicketCommentForm()

    if request.user.is_staff or request.user.groups.filter(name__icontains='tecnico').exists():
        template = 'tickets/ticket_comments_tech.html'
    else:
        template = 'tickets/ticket_comments_user.html'

    return render(request, template, {
        'ticket': ticket,
        'comentarios': comentarios,
        'form': form,
    })

@login_required
def ticket_comments_ajax(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')
    if request.user.is_staff or request.user.groups.filter(name__icontains='tecnico').exists():
        partial_template = 'tickets/_comments_partial_tech.html'
    else:
        partial_template = 'tickets/_comments_partial_user.html'
    html = render_to_string(partial_template, {
        'comentarios': comentarios,
        'request': request,
    })
    return JsonResponse({'html': html})
