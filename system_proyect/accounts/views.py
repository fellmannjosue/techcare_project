from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
import datetime

# ⬅️ Nuevo sistema de notificaciones globales
from core.utils_notifications import crear_notificacion

from .forms import MaestroRegisterForm
from tickets.models import Ticket


# =====================================================
# 🔐 LOGIN GENERAL DEL SISTEMA
# =====================================================
def login_view(request):
    """
    Login unificado para todos los usuarios.
    - Maestros → dashboard maestro
    - Técnicos → dashboard tickets
    - Superuser → menú principal
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        is_maestro = request.POST.get('is_maestro') == 'on'

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            request.session['show_welcome'] = True
            messages.success(request, f'¡Bienvenido {user.first_name}!')

            # Redirecciones
            if is_maestro or user.groups.filter(name__in=[
                'maestros_bilingue', 'maestros_colegio'
            ]).exists():
                return redirect('dashboard_maestro')

            if user.groups.filter(name='tecnicos').exists():
                return redirect('tickets_dashboard')

            if user.is_superuser:
                return redirect('menu')

            return redirect('menu')

        messages.error(request, 'Credenciales inválidas.')

    year = datetime.datetime.now().year
    return render(request, 'accounts/login.html', {'year': year})


# =====================================================
# 📝 REGISTRO DE MAESTROS / ADMIN / STAFF
# =====================================================
def register_maestro(request):
    """
    Registro completo con envío de correo y asignación de grupos.
    """
    if request.method == 'POST':
        form = MaestroRegisterForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            area = form.cleaned_data['area']
            cargo = form.cleaned_data['cargo']
            password = form.cleaned_data['password']

            # Crear usuario
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Asignar grupos
            if area == 'bilingue':
                group_name = 'maestros_bilingue' if cargo == 'docente' else 'admin_bilingue'
            elif area == 'colegio':
                group_name = 'maestros_colegio' if cargo == 'docente' else 'admin_colegio'
            else:
                group_name = 'administracion'
                user.is_staff = True

            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            user.save()

            # Enviar correo
            try:
                send_mail(
                    'Bienvenido al Sistema TechCare',
                    (
                        f'Se ha creado una cuenta para ti.\n\n'
                        f'Usuario: {email}\n'
                        f'Contraseña: {password}\n\n'
                        'Cambia tu contraseña en el primer inicio de sesión.'
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, f"Cuenta creada, pero no se envió el correo: {e}")

            messages.success(request, "¡Registro exitoso!")
            return redirect('login')

    else:
        form = MaestroRegisterForm()

    year = datetime.datetime.now().year
    return render(request, 'accounts/register.html', {'form': form, 'year': year})


# =====================================================
# 🖥 MENU PRINCIPAL
# =====================================================
@login_required
def menu_view(request):
    """
    Panel principal de TechCare, con tarjetas estadísticas
    y visibilidad por módulos.
    """
    user = request.user
    year = datetime.datetime.now().year

    # =====================================================
    # 🔥 TICKETS (todos los NO resueltos)
    # =====================================================
    tickets_pendientes = Ticket.objects.exclude(status__iexact="Resuelto").count()

    # =====================================================
    # 🔥 CITAS BL
    # =====================================================
    try:
        from citas_billingue.models import Appointment_bl
        citas_bl = Appointment_bl.objects.exclude(status__iexact="Resuelto").count()
    except:
        citas_bl = 0

    # =====================================================
    # 🔥 CITAS COL
    # =====================================================
    try:
        from citas_colegio.models import Appointment_col
        citas_col = Appointment_col.objects.exclude(status__iexact="Resuelto").count()
    except:
        citas_col = 0

    # =====================================================
    # 🔥 REPORTES DE CONDUCTA — BILINGÜE
    # =====================================================
    try:
        from conducta.models import ReporteInformativo, ReporteConductual, ProgressReport

        reportes_bl = (
            ReporteInformativo.objects.filter(area='bilingue', estado='enviado').count() +
            ReporteConductual.objects.filter(area='bilingue', estado='enviado').count() +
            ProgressReport.objects.filter(estado='enviado').count()
        )
    except:
        reportes_bl = 0

    # =====================================================
    # 🔥 REPORTES DE CONDUCTA — COLEGIO
    # =====================================================
    try:
        from conducta.models import ReporteInformativo, ReporteConductual

        reportes_col = (
            ReporteInformativo.objects.filter(area='colegio', estado='enviado').count() +
            ReporteConductual.objects.filter(area='colegio', estado='enviado').count()
        )
    except:
        reportes_col = 0

    # =====================================================
    # 🔥 RELOJ (compensatorios / permisos)
    # =====================================================
    try:
        from reloj.models import Solicitud
        reloj_pendientes = Solicitud.objects.exclude(estado__iexact="Aprobado").count()
    except:
        reloj_pendientes = 0

    # =====================================================
    # 🔰 ROLES Y PERMISOS
    # =====================================================
    is_admin            = user.is_superuser
    is_group_citas_bl   = user.groups.filter(name='citas bilingue').exists()
    is_group_citas_col  = user.groups.filter(name='citas colegio').exists()
    is_group_enfermeria = user.groups.filter(name='enfermeria').exists()
    is_group_inventario = user.groups.filter(name='inventario').exists()
    is_group_reloj      = user.groups.filter(name='reloj').exists()

    is_coord_bilingue = user.groups.filter(name='coordinador_bilingue').exists()
    is_coord_colegio  = user.groups.filter(name='coordinador_colegio').exists()

    # =====================================================
    # 🔐 PERMISOS
    # =====================================================
    can_view_inventory   = user.has_perm('inventario.view_inventariomedicamento')
    can_view_maintenance = user.has_perm('mantenimiento.view_mantenimiento')
    can_view_tickets     = user.has_perm('tickets.view_ticket')
    can_view_sponsors    = user.has_perm('sponsors.view_sponsor')
    can_view_seguridad   = user.has_perm('seguridad.view_seguridad')

    # =====================================================
    # 🚫 BLOQUEO DE TARJETAS PARA USUARIOS ESPECÍFICOS
    # =====================================================
    # admin2 y admin3 NO deben ver ninguna tarjeta
    blocked_users = ["admin2", "admin3"]
    show_cards = user.username not in blocked_users

    # =====================================================
    # CONTEXTO FINAL PARA EL HTML
    # =====================================================
    context = {
        'year': year,

        # ---------- Tarjetas del dashboard ----------
        'tickets_pendientes': tickets_pendientes,
        'citas_bl': citas_bl,
        'citas_col': citas_col,
        'reportes_bl': reportes_bl,
        'reportes_col': reportes_col,
        'reloj_pendientes': reloj_pendientes,

        # ---------- Mostrar/ocultar TODAS las tarjetas ----------
        'show_cards': show_cards,

        # ---------- Visibilidad según rol ----------
        'show_inventory':   is_admin or can_view_inventory or is_group_inventario,
        'show_maintenance': is_admin or can_view_maintenance,
        'show_tickets':     is_admin or can_view_tickets,
        'show_sponsors':    is_admin or can_view_sponsors,
        'show_seguridad':   is_admin or can_view_seguridad,
        'show_citas_bl':    is_admin or is_group_citas_bl,
        'show_citas_col':   is_admin or is_group_citas_col,
        'show_enfermeria':  is_admin or is_group_enfermeria,
        'show_reloj':       is_admin or is_group_reloj,

        'show_coordinador_bilingue': is_admin or is_coord_bilingue,
        'show_coordinador_colegio':  is_admin or is_coord_colegio,
    }

    return render(request, 'accounts/menu.html', context)




# =====================================================
# 🔔 NOTIFICACIONES AVANZADAS PARA EL MENÚ
# =====================================================
@login_required
def notify_tickets(request):
    """
    Devuelve tickets pendientes para la campana del menú.
    Se conecta con ticket_notify.js
    """
    abiertos = Ticket.objects.filter(status="pendiente").count()
    recientes = Ticket.objects.filter(status="pendiente").order_by('-id')[:5]

    return JsonResponse({
        "total": abiertos,
        "tickets": [
            {
                "id": t.id,
                "ticket_id": t.ticket_id,
                "name": t.name,
                "fecha": t.fecha_creacion.strftime("%d/%m/%Y %H:%M")
            }
            for t in recientes
        ]
    })


# =====================================================
# 🔚 LOGOUT GENERAL
# =====================================================
def logout_view(request):
    inactive = request.GET.get('inactive')
    logout(request)
    messages.info(request, 'Sesión cerrada por inactividad.' if inactive else 'Sesión cerrada correctamente.')
    return redirect('login')


# =====================================================
# 🔚 LOGOUT PARA MAESTROS
# =====================================================
def maestro_logout(request):
    inactive = request.GET.get('inactive')
    logout(request)
    messages.info(request, 'Sesión cerrada por inactividad.' if inactive else 'Sesión cerrada correctamente.')
    return redirect('login')
