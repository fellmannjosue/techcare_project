from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
import datetime

from .forms import MaestroRegisterForm
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
    Vista de login para usuarios que van directamente a tickets o dashboard de maestros.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['show_welcome'] = True
            messages.success(request, f'¡Bienvenido {user.username}!')

            # REDIRECCIÓN SEGÚN GRUPO
            if user.groups.filter(name__in=['maestros_bilingue', 'maestros_colegio']).exists():
                return redirect('dashboard_maestro')
            return redirect('/tickets/submit_ticket/')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    return render(request, 'accounts/user_login.html')


def register_maestro(request):
    """
    Registro de nuevos maestros (solo permite correo @ana-hn.org).
    """
    if request.method == 'POST':
        form = MaestroRegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            area = form.cleaned_data['area']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Asignar grupo según área
            if area == 'bilingue':
                group, _ = Group.objects.get_or_create(name='maestros_bilingue')
            else:
                group, _ = Group.objects.get_or_create(name='maestros_colegio')
            user.groups.add(group)

            user.save()
            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            return redirect('user_login')
    else:
        form = MaestroRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def menu_view(request):
    """
    Dashboard principal:  
    Muestra botones solo según grupo/permiso/superuser.
    """
    user = request.user
    year = datetime.datetime.now().year

    # Notificaciones
    citas_pendientes   = Appointment_bl.objects.filter(status='pendiente').count()
    tickets_pendientes = Ticket.objects.filter(status='pendiente').count()

    # Roles / Grupos
    is_admin            = user.is_superuser
    is_group_citas_bl   = user.groups.filter(name='citas bilingue').exists()
    is_group_citas_col  = user.groups.filter(name='citas colegio').exists()
    is_group_enfermeria = user.groups.filter(name='enfermeria').exists()
    is_group_inventario = user.groups.filter(name='inventario').exists()

    # Permisos individuales
    can_view_inventario   = user.has_perm('inventario.view_inventariomedicamento')
    can_view_maintenance  = user.has_perm('mantenimiento.view_mantenimiento')
    can_view_tickets      = user.has_perm('tickets.view_ticket')
    can_view_sponsors     = user.has_perm('sponsors.view_sponsor')
    can_view_seguridad    = user.has_perm('seguridad.view_seguridad')

    # NUEVO: Coordinadores
    is_coordinador_bilingue = user.groups.filter(name='coordinador_bilingue').exists()
    is_coordinador_colegio  = user.groups.filter(name='coordinador_colegio').exists()

    context = {
        'year':               year,
        'citas_pendientes':   citas_pendientes,
        'tickets_pendientes': tickets_pendientes,
        'show_inventory':   is_admin or can_view_inventario or is_group_inventario,
        'show_maintenance': is_admin or can_view_maintenance,
        'show_tickets':     is_admin or can_view_tickets,
        'show_sponsors':    is_admin or can_view_sponsors,
        'show_seguridad':   is_admin or can_view_seguridad,
        'show_citas_bl':    is_admin or is_group_citas_bl,
        'show_citas_col':   is_admin or is_group_citas_col,
        'show_enfermeria':  is_admin or is_group_citas_bl or is_group_enfermeria,
        # Coordinador Conducta
        'show_coordinador_bilingue': is_admin or is_coordinador_bilingue,
        'show_coordinador_colegio':  is_admin or is_coordinador_colegio,
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
