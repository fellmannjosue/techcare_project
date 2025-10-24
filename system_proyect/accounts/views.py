from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
import datetime

from .forms import MaestroRegisterForm
from citas_billingue.models import Appointment_bl
from tickets.models import Ticket

def login_view(request):
    """
    Login unificado para todos los usuarios. Usa el checkbox 'is_maestro' para lógica especial.
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
            # Redirección según checkbox/grupo
            if is_maestro or user.groups.filter(name__in=['maestros_bilingue', 'maestros_colegio']).exists():
                return redirect('dashboard_maestro')
            elif user.groups.filter(name='tecnicos').exists():
                return redirect('tickets_dashboard')
            elif user.is_superuser:
                return redirect('menu')
            return redirect('menu')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    year = datetime.datetime.now().year
    return render(request, 'accounts/login.html', {'year': year})


def register_maestro(request):
    """
    Registro moderno para maestros, administrativos y staff.
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

            # Username será igual a email
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Asignar grupo y staff según área
            if area == 'bilingue':
                group_name = 'maestros_bilingue' if cargo == 'docente' else 'admin_bilingue'
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            elif area == 'colegio':
                group_name = 'maestros_colegio' if cargo == 'docente' else 'admin_colegio'
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            elif area == 'administracion':
                user.is_staff = True
                group, _ = Group.objects.get_or_create(name='administracion')
                user.groups.add(group)
            user.save()

            # Enviar correo automático con datos de acceso
            try:
                send_mail(
        'Bienvenido al Sistema TechCare',
        (
            f'Se ha creado una cuenta para ti en el sistema TechCare.\n\n'
            f'Usuario: {email}\n'
            f'Contraseña: {password}\n\n'
            'Por seguridad, te recomendamos cambiar tu contraseña en tu primer acceso.\n\n'
            'Saludos,\nSoporte Técnico ANA-HN'
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
            except Exception as e:
                messages.warning(request, f"Usuario creado, pero no se pudo enviar el correo: {e}")

            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            return redirect('login')
    else:
        form = MaestroRegisterForm()
    year = datetime.datetime.now().year
    return render(request, 'accounts/register.html', {'form': form, 'year': year})

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
    is_group_reloj = user.groups.filter(name='reloj').exists()


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
        'show_coordinador_bilingue': is_admin or is_coordinador_bilingue,
        'show_coordinador_colegio':  is_admin or is_coordinador_colegio,
        'show_reloj': is_admin or is_group_reloj,

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

def maestro_logout(request):
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
