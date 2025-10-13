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
from django.views.decorators.http import require_POST, require_GET
import os
import traceback
import json
from threading import Thread
from core.utils_ai import consultar_ia  # 🚀 IA

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
def ticket_comments(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')

    # MENSAJE AUTOMÁTICO SI NO HAY COMENTARIOS PREVIOS
    if not comentarios.exists():
        User = get_user_model()
        try:
            usuario_soporte = User.objects.get(username='soporte_tecnico')
        except User.DoesNotExist:
            usuario_soporte = (
                User.objects.filter(is_staff=True).first() or
                User.objects.filter(is_superuser=True).first() or
                User.objects.all().first()
            )
        if usuario_soporte:
            TicketComment.objects.create(
                ticket=ticket,
                usuario=usuario_soporte,
                mensaje="Soporte técnico de Asociación Nuevo Amanecer: ¿En qué le podemos ayudar? Descríbanos el problema que presenta.",
                fecha=timezone.now(),
                tipo="tecnico"
            )
            comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')

    # ========== BLOQUEO SI TICKET RESUELTO ==========
    status_resuelto = ticket.status.strip().lower() == "resuelto"

    # ----- PROCESAR POST: Cambio de estado y/o mensaje -----
    if request.method == 'POST':
        # ---- Cambiar estado del ticket si viene en el POST ----
        new_status = request.POST.get('status')
        status_cambiado = False
        enviar_historial = False

        if new_status and new_status != ticket.status:
            ticket.status = new_status
            ticket.save()
            status_cambiado = True
            if new_status.strip().lower() == "resuelto":
                enviar_historial = True

        # ---- Procesar comentario (si existe) ----
        mensaje = request.POST.get('mensaje', '').strip()
        form = TicketCommentForm(request.POST)
        comentario = None

        if form.is_valid() and mensaje:
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.usuario = request.user
            comentario.tipo = "usuario" if not request.user.is_staff else "tecnico"
            comentario.save()
            try:
                subject = f"Nuevo comentario en Ticket #{ticket.ticket_id}"
                html_message = render_to_string(
                    'tickets/email/nuevo_comentario.html',
                    {'ticket': ticket, 'comentario': comentario, 'autor': request.user}
                )
                send_email_async(subject, html_message, [ticket.email])
            except Exception as e:
                print("Error enviando correo:", e)

        # ---- Si cambió el estado, enviar correo con historial de chat ----
        if status_cambiado:
            historial_chat = TicketComment.objects.filter(ticket=ticket).order_by('fecha')
            chat_conversacion = [
                {
                    "autor": c.usuario.username if c.usuario else c.get_tipo_display(),
                    "mensaje": c.mensaje,
                    "fecha": c.fecha.strftime("%d/%m/%Y %H:%M"),
                }
                for c in historial_chat
            ]
            subject_update = f'Ticket #{ticket.ticket_id} - Estado Actualizado ({ticket.status})'
            message_update = render_to_string(
                'tickets/email/ticket_update.html',
                {
                    'ticket': ticket,
                    'technician_name': 'Equipo Técnico',
                    'comments': ticket.comments,
                    'img_url': PUBLIC_IMAGE_URL,
                    'chat_conversacion': chat_conversacion,
                }
            )
            send_email_async(subject_update, message_update, [ticket.email])

        # ---- Redirección AJAX o normal ----
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'mensaje': 'Comentario y/o estado actualizado correctamente.'})
        else:
            messages.success(request, "Comentario y/o estado actualizado correctamente.")
            return redirect('ticket_comments', ticket_id=ticket.id)

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
        'status_resuelto': status_resuelto,
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

@require_POST
@login_required
def ticket_status_update_ajax(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    new_status = request.POST.get("status")
    comments = request.POST.get("comments", "").strip()
    correo_enviado = False

    if new_status and new_status in ["Pendiente", "En Proceso", "Resuelto"]:
        ticket.status = new_status
        ticket.comments = comments
        ticket.save()

        if new_status == "Resuelto":
            historial_chat = TicketComment.objects.filter(ticket=ticket).order_by('fecha')
            chat_conversacion = [
                {
                    "autor": c.usuario.username if c.usuario else c.get_tipo_display(),
                    "mensaje": c.mensaje,
                    "fecha": c.fecha.strftime("%d/%m/%Y %H:%M"),
                }
                for c in historial_chat
            ]
            subject_update = f'Ticket #{ticket.ticket_id} - Estado Actualizado (Resuelto)'
            message_update = render_to_string(
                'tickets/email/ticket_update.html',
                {
                    'ticket': ticket,
                    'technician_name': 'Equipo Técnico',
                    'comments': ticket.comments,
                    'img_url': PUBLIC_IMAGE_URL,
                    'chat_conversacion': chat_conversacion,
                }
            )
            send_email_async(subject_update, message_update, [ticket.email])
            correo_enviado = True

        return JsonResponse({
            "ok": True,
            "status": ticket.status,
            "comments": ticket.comments,
            "correo_enviado": correo_enviado
        })
    return JsonResponse({"ok": False, "error": "Estado inválido"}, status=400)

@require_GET
@login_required
def ticket_status_get_ajax(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return JsonResponse({
        "status": ticket.status,
        "comments": ticket.comments
    })



@csrf_exempt
@require_POST
@login_required
def ticket_chat_ai_ajax(request, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        mensaje_usuario = request.POST.get("mensaje", "").strip()

        if not mensaje_usuario:
            return JsonResponse({"ok": False, "error": "Mensaje vacío."}, status=400)

        # Guarda el mensaje del usuario
        comentario_user = TicketComment.objects.create(
            ticket=ticket,
            usuario=request.user,
            mensaje=mensaje_usuario,
            tipo="usuario"
        )

        # Prepara mensajes para la IA
        mensajes_ia = [
            {"role": "system", "content": "Eres un asistente técnico amigable..."},
            {"role": "user", "content": mensaje_usuario}
        ]
        respuesta_ia = consultar_ia(mensajes_ia)

        if not respuesta_ia:
            return JsonResponse({"ok": False, "error": "No se pudo obtener respuesta de la IA."}, status=500)

        # Guarda la respuesta IA
        comentario_ai = TicketComment.objects.create(
            ticket=ticket,
            usuario=None,
            mensaje=respuesta_ia,
            tipo="ia"
        )

        return JsonResponse({
            "ok": True,
            "mensaje_usuario": {
                "id": comentario_user.id,
                "mensaje": comentario_user.mensaje,
                "fecha": comentario_user.fecha.strftime("%d/%m/%Y %H:%M"),
                "autor": request.user.username,
                "tipo": "usuario",
            },
            "mensaje_ia": {
                "id": comentario_ai.id,
                "mensaje": comentario_ai.mensaje,
                "fecha": comentario_ai.fecha.strftime("%d/%m/%Y %H:%M"),
                "autor": "IA TechCare",
                "tipo": "ia",
            }
        })

    except Exception as e:
        print("======= ERROR EN VIEW AJAX CHAT IA =======")
        traceback.print_exc()
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
