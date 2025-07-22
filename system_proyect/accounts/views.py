# accounts/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime

# Importar modelos para notificaciones
from citas_billingue.models import Appointment_bl
from tickets.models import Ticket

def login_view(request):
    """
    Vista para el inicio de sesión de usuarios (login general).
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['show_welcome'] = True
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('menu')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    return render(request, 'accounts/login.html')


def user_login_view(request):
    """
    Vista de login para usuarios que van directamente a tickets.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['show_welcome'] = True
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('/tickets/submit_ticket/')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    return render(request, 'accounts/user_login.html')


@login_required
def menu_view(request):
    """
    Dashboard principal:
      - superuser ve todo.
      - 'citas bilingue' ve Citas BL + Enfermería.
      - 'citas colegio' ve Citas COL/VOC.
      - 'enfermeria' ve Enfermería.
      - Inventario se muestra si el usuario tiene permiso o pertenece al grupo.
      - Sponsors, Mantenimiento, Tickets y Seguridad controlados por permiso.
      - Notas e Informes (BL y COL) controlados por grupo o superuser.
    """
    user = request.user
    year = datetime.datetime.now().year

    # ——— Notificaciones ———
    citas_pendientes   = Appointment_bl.objects.filter(status='pendiente').count()
    tickets_pendientes = Ticket.objects.filter(status='pendiente').count()

    # ——— Roles / Grupos ———
    is_admin            = user.is_superuser
    is_group_citas_bl   = user.groups.filter(name='citas bilingue').exists()
    is_group_citas_col  = user.groups.filter(name='citas colegio').exists()
    is_group_enfermeria = user.groups.filter(name='enfermeria').exists()
    is_group_inventario = user.groups.filter(name='inventario').exists()
    is_group_notas_bl   = user.groups.filter(name='informes_bl').exists()
    is_group_notas_col  = user.groups.filter(name='informes_col').exists()

    # ——— Permisos individuales ———
    can_view_inventario   = user.has_perm('inventario.view_inventariomedicamento')
    can_view_maintenance  = user.has_perm('mantenimiento.view_mantenimiento')
    can_view_tickets      = user.has_perm('tickets.view_ticket')
    can_view_sponsors     = user.has_perm('sponsors.view_sponsor')
    can_view_seguridad    = user.has_perm('seguridad.view_seguridad')

    context = {
        'year':               year,
        'citas_pendientes':   citas_pendientes,
        'tickets_pendientes': tickets_pendientes,

        # ——— Módulos controlados por permiso o grupo (o superuser) ———
        'show_inventory':   is_admin or can_view_inventario or is_group_inventario,
        'show_maintenance': is_admin or can_view_maintenance,
        'show_tickets':     is_admin or can_view_tickets,
        'show_sponsors':    is_admin or can_view_sponsors,
        'show_seguridad':   is_admin or can_view_seguridad,

        # ——— Módulos controlados por rol/grupo (o superuser) ———
        'show_citas_bl':    is_admin or is_group_citas_bl,
        'show_citas_col':   is_admin or is_group_citas_col,
        'show_enfermeria':  is_admin or is_group_citas_bl or is_group_enfermeria,

        # ——— Notas e Informes ———
        'show_notas_bl':    is_admin or is_group_notas_bl,
        'show_notas_col':   is_admin or is_group_notas_col,
    }

    return render(request, 'accounts/menu.html', context)

@login_required
def check_new_notifications(request):
    """
    Devuelve JSON con los totales de citas y tickets pendientes.
    """
    citas_pendientes   = Appointment_bl.objects.filter(status='pendiente').count()
    tickets_pendientes = Ticket.objects.filter(status='pendiente').count()
    return JsonResponse({
        'citas_pendientes':   citas_pendientes,
        'tickets_pendientes': tickets_pendientes
    })


def logout_view(request):
    """
    Cierra la sesión y redirige al login.
    """
    inactive = request.GET.get('inactive')
    logout(request)
    if inactive:
        messages.info(request, 'Sesión cerrada por inactividad.')
    else:
        messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')
