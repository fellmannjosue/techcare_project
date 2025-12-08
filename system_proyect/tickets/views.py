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

# 🚀 IA
from core.utils_ai import consultar_ia  

# 🔔 Notificaciones globales
from core.utils_notifications import crear_notificacion

PUBLIC_IMAGE_URL = ""

# ======================================================
# ASYNC EMAIL
# ======================================================
def send_email_async(subject, message, recipient_list):
    Thread(
        target=send_mail,
        args=(subject, '', 'techcare.app2024@gmail.com', recipient_list),
        kwargs={'html_message': message, 'fail_silently': False}
    ).start()



# ======================================================
# 🔥 SUBMIT TICKET
# ======================================================
@csrf_exempt
def submit_ticket(request):
    User = get_user_model()

    if request.method == 'POST':

        # JSON request (API / chatbot / móvil)
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

                # 🔔 Notificar a técnicos
                tecnicos = User.objects.filter(groups__name__icontains="tecnico")
                for tech in tecnicos:
                    crear_notificacion(
                        usuario=tech,
                        mensaje=f"Nuevo ticket #{ticket.ticket_id} creado por {ticket.name}.",
                        modulo="tickets",
                        tipo="info"
                    )

                # 🔔 Notificar al usuario
                if request.user.is_authenticated:
                    crear_notificacion(
                        usuario=request.user,
                        mensaje=f"Tu ticket #{ticket.ticket_id} ha sido recibido.",
                        modulo="tickets",
                        tipo="exito"
                    )

                # 📧 Correos
                subject_technician = f'Nuevo Ticket #{ticket.ticket_id} - {ticket.name}'
                html_msg = render_to_string('tickets/email/email_notification.html',
                                            {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL})
                send_email_async(subject_technician, html_msg, ['techcare.app2024@gmail.com'])

                subject_user = f'Ticket #{ticket.ticket_id} - Confirmación de Recepción'
                send_email_async(subject_user, html_msg, [ticket.email])

                return JsonResponse({'message': f'Ticket #{ticket.ticket_id} creado exitosamente'}, status=201)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Error al procesar data JSON'}, status=400)



        # FORM request (web)
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.email = request.user.email
            ticket.save()

            # 🔔 Notificaciones
            tecnicos = User.objects.filter(groups__name__icontains="tecnico")
            for tech in tecnicos:
                crear_notificacion(
                    usuario=tech,
                    mensaje=f"Nuevo ticket #{ticket.ticket_id} creado por {ticket.name}.",
                    modulo="tickets",
                    tipo="info"
                )

            crear_notificacion(
                usuario=request.user,
                mensaje=f"Tu ticket #{ticket.ticket_id} ha sido recibido.",
                modulo="tickets",
                tipo="exito"
            )

            # 📧 Correos
            subject = f'Nuevo Ticket #{ticket.ticket_id} - {ticket.name}'
            html_msg = render_to_string('tickets/email/email_notification.html',
                                        {'ticket': ticket, 'img_url': PUBLIC_IMAGE_URL})
            send_email_async(subject, html_msg, ['techcare.app2024@gmail.com'])
            send_email_async(subject, html_msg, [ticket.email])

            return JsonResponse({'message': f'Ticket #{ticket.ticket_id} creado exitosamente'}, status=201)

        else:
            return JsonResponse({'error': 'Error en formulario', 'details': form.errors.as_json()}, status=400)

    else:
        form = TicketForm()
        return render(request, 'tickets/submit_ticket.html', {
            'form': form,
            'user_email': request.user.email if request.user.is_authenticated else ""
        })



# ======================================================
# DASHBOARD TÉCNICO
# ======================================================
@login_required
def technician_dashboard(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/technician_dashboard.html', {'tickets': tickets})



# ======================================================
# 🔥 COMENTARIOS DE TICKET (CHAT HUMANO)
# ======================================================
@login_required
def ticket_comments(request, ticket_id):
    User = get_user_model()
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')

    # MENSAJE AUTOMÁTICO INICIAL
    if not comentarios.exists():
        default_staff = User.objects.filter(is_staff=True).first() or User.objects.first()
        TicketComment.objects.create(
            ticket=ticket,
            usuario=default_staff,
            mensaje="Soporte técnico: ¿En qué podemos ayudarte?",
            tipo="tecnico"
        )

    status_resuelto = ticket.status.lower() == "resuelto"

    # POST → Nuevo comentario o cambio de estado
    if request.method == 'POST':
        new_status = request.POST.get("status")
        mensaje = request.POST.get("mensaje", "").strip()

        # -------------------- CAMBIO DE ESTADO --------------------
        if new_status and new_status != ticket.status:
            ticket.status = new_status
            ticket.save()

            # 🔔 Notificaciones por estado
            if new_status.lower() == "en proceso":
                crear_notificacion(
                    usuario=ticket.usuario,
                    mensaje=f"Tu ticket #{ticket.ticket_id} está en proceso.",
                    modulo="tickets",
                    tipo="info"
                )

            if new_status.lower() == "resuelto":
                crear_notificacion(
                    usuario=ticket.usuario,
                    mensaje=f"Tu ticket #{ticket.ticket_id} ha sido resuelto.",
                    modulo="tickets",
                    tipo="exito"
                )

                for tech in User.objects.filter(groups__name__icontains="tecnico"):
                    crear_notificacion(
                        usuario=tech,
                        mensaje=f"El ticket #{ticket.ticket_id} fue marcado como resuelto.",
                        modulo="tickets",
                        tipo="info"
                    )

        # -------------------- NUEVO COMENTARIO --------------------
        form = TicketCommentForm(request.POST)
        if form.is_valid() and mensaje:
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.usuario = request.user
            comentario.tipo = "usuario" if not request.user.is_staff else "tecnico"
            comentario.save()

            # 🔔 Notificar según quién comenta
            if comentario.tipo == "usuario":
                for tech in User.objects.filter(groups__name__icontains="tecnico"):
                    crear_notificacion(
                        usuario=tech,
                        mensaje=f"Nuevo mensaje en ticket #{ticket.ticket_id} por {request.user.username}.",
                        modulo="tickets",
                        tipo="info"
                    )
            else:
                crear_notificacion(
                    usuario=ticket.usuario,
                    mensaje=f"Un técnico respondió en tu ticket #{ticket.ticket_id}.",
                    modulo="tickets",
                    tipo="info"
                )

        return redirect('ticket_comments', ticket_id=ticket.id)

    # GET → Render
    form = TicketCommentForm()
    template = 'tickets/ticket_comments_tech.html' if request.user.is_staff else 'tickets/ticket_comments_user.html'

    return render(request, template, {
        'ticket': ticket,
        'comentarios': comentarios,
        'form': form,
        'status_resuelto': status_resuelto,
    })



# ======================================================
# AJAX → Render parcial de comentarios
# ======================================================
@login_required
def ticket_comments_ajax(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comentarios = TicketComment.objects.filter(ticket=ticket).order_by('fecha')

    template = 'tickets/_comments_partial_tech.html' if request.user.is_staff else 'tickets/_comments_partial_user.html'
    html = render_to_string(template, {"comentarios": comentarios, "request": request})

    return JsonResponse({'html': html})



# ======================================================
# AJAX → Actualizar estado
# ======================================================
@require_POST
@login_required
def ticket_status_update_ajax(request, ticket_id):
    User = get_user_model()
    ticket = get_object_or_404(Ticket, id=ticket_id)

    new_status = request.POST.get("status")
    comments = request.POST.get("comments", "").strip()

    if new_status not in ["Pendiente", "En Proceso", "Resuelto"]:
        return JsonResponse({"ok": False}, status=400)

    ticket.status = new_status
    ticket.comments = comments
    ticket.save()

    # 🔔 Notificaciones
    if new_status == "En Proceso":
        crear_notificacion(
            usuario=ticket.usuario,
            mensaje=f"Tu ticket #{ticket.ticket_id} está en proceso.",
            modulo="tickets",
            tipo="info"
        )

    if new_status == "Resuelto":
        crear_notificacion(
            usuario=ticket.usuario,
            mensaje=f"Tu ticket #{ticket.ticket_id} ha sido resuelto.",
            modulo="tickets",
            tipo="exito"
        )

    return JsonResponse({"ok": True})



# ======================================================
# AJAX → Obtener estado
# ======================================================
@require_GET
@login_required
def ticket_status_get_ajax(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return JsonResponse({"status": ticket.status, "comments": ticket.comments})



# ======================================================
# 🔥🚨 BOTÓN: "NO ME AYUDÓ, CONTACTAR TÉCNICO"
# ======================================================
@require_POST
@login_required
def ticket_contact_technician(request, ticket_id):
    User = get_user_model()
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # 1️⃣ Bloquear IA
    ticket.ia_bloqueada = True
    ticket.save()

    # 2️⃣ Último mensaje de IA
    mensaje_ia = (
        "Gracias por tu consulta. "
        "Ahora te pasaré con un técnico humano para continuar asistiendo tu ticket."
    )

    TicketComment.objects.create(
        ticket=ticket,
        usuario=None,
        mensaje=mensaje_ia,
        tipo="ia"
    )

    # 3️⃣ Notificación a técnicos
    tecnicos = User.objects.filter(groups__name__icontains="tecnico")
    for tech in tecnicos:
        crear_notificacion(
            usuario=tech,
            mensaje=f"El usuario solicita asistencia humana en el ticket #{ticket.ticket_id}.",
            modulo="tickets",
            tipo="alerta"
        )

    return JsonResponse({"ok": True})



# ======================================================
# 🚀 CHAT IA (respeta ia_bloqueada)
# ======================================================
@csrf_exempt
@require_POST
@login_required
def ticket_chat_ai_ajax(request, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)

        # IA bloqueada → no responder
        if ticket.ia_bloqueada:
            return JsonResponse({
                "ok": False,
                "error": "La IA está bloqueada en este ticket. Un técnico continuará la atención."
            }, status=403)

        mensaje_usuario = request.POST.get("mensaje", "").strip()
        if not mensaje_usuario:
            return JsonResponse({"ok": False, "error": "Mensaje vacío"}, status=400)

        # Guardar mensaje del usuario
        comentario_user = TicketComment.objects.create(
            ticket=ticket,
            usuario=request.user,
            mensaje=mensaje_usuario,
            tipo="usuario"
        )

        mensajes_ia = [
            {"role": "system", "content": "Eres un asistente técnico amigable y útil de ANA-HN."},
            {"role": "user", "content": mensaje_usuario}
        ]

        respuesta_ia = consultar_ia(mensajes_ia)

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
        traceback.print_exc()
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
