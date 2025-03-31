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
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('menu')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    return render(request, 'accounts/login.html')

def user_login_view(request):
    """
    NUEVA vista de login para usuarios específicos que deben ir directamente a tickets.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('/tickets/submit_ticket/')
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')
    return render(request, 'accounts/user_login.html')

@login_required
def menu_view(request):
    """
    Vista del menú principal después de iniciar sesión.
    Incluye notificaciones y nombre del usuario.
    """
    year = datetime.datetime.now().year

    # Contadores de notificaciones pendientes
    citas_pendientes = Appointment_bl.objects.filter(status='pendiente').count()
    tickets_pendientes = Ticket.objects.filter(status='pendiente').count()

    context = {
        'year': year,
        'user': request.user,
        'citas_pendientes': citas_pendientes,
        'tickets_pendientes': tickets_pendientes,
    }

    return render(request, 'accounts/menu.html', context)

@login_required
def check_new_notifications(request):
    citas_pendientes = Appointment_bl.objects.filter(status='pendiente').count()
    tickets_pendientes = Ticket.objects.filter(status='pendiente').count()

    return JsonResponse({
        'citas_pendientes': citas_pendientes,
        'tickets_pendientes': tickets_pendientes
    })

def logout_view(request):
    """
    Cierra la sesión y redirige al login.
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')
