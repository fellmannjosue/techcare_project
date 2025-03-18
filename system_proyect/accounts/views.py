from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime

def login_view(request):
    """
    Vista para el inicio de sesión de usuarios.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('menu')  # Asegura que el name='menu' esté en urls.py
        else:
            messages.error(request, 'Credenciales inválidas, inténtalo de nuevo.')

    return render(request, 'accounts/login.html')

@login_required
def menu_view(request):
    """
    Vista del menú principal después de iniciar sesión.
    """
    year = datetime.datetime.now().year  # Para mostrar el año en el footer dinámicamente
    return render(request, 'accounts/menu.html', {'year': year})

def logout_view(request):
    """
    Cierra la sesión y redirige al login.
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')
