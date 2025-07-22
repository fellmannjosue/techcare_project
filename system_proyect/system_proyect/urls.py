# system_proyect/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [

    # ──────────────────────────────────────────────────────────────────────────
    # 1) Ruta raíz: redirige al login
    # ──────────────────────────────────────────────────────────────────────────
    path('', lambda request: redirect('/accounts/login/')),

    # ──────────────────────────────────────────────────────────────────────────
    # 2) Admin de Django
    # ──────────────────────────────────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ──────────────────────────────────────────────────────────────────────────
    # 3) Autenticación y perfil de usuario
    # ──────────────────────────────────────────────────────────────────────────
    path('accounts/', include('accounts.urls')),

    # ──────────────────────────────────────────────────────────────────────────
    # 4) Módulos principales de la aplicación
    # ──────────────────────────────────────────────────────────────────────────
    path('tickets/',       include('tickets.urls')),
    path('inventario/',    include('inventario.urls')),
    path('mantenimiento/', include(('mantenimiento.urls', 'mantenimiento'), namespace='mantenimiento')),

    # ──────────────────────────────────────────────────────────────────────────
    # 5) Módulos agro-sanitarios y de salud
    # ──────────────────────────────────────────────────────────────────────────
    path('enfermeria/',      include(('enfermeria.urls', 'enfermeria'), namespace='enfermeria')),
    path('citas_billingue/', include('citas_billingue.urls')),
    path('citas_colegio/',   include('citas_colegio.urls')),

    # ──────────────────────────────────────────────────────────────────────────
    # 6) Patrocinios y menú principal
    # ──────────────────────────────────────────────────────────────────────────
    path('sponsors/', include('sponsors.urls')),
    path('menu/',     include('menu.urls')),

    # ──────────────────────────────────────────────────────────────────────────
    # 7) Módulo de Seguridad
    # ──────────────────────────────────────────────────────────────────────────
    path('seguridad/', include(('seguridad.urls', 'seguridad'), namespace='seguridad')),

    # ──────────────────────────────────────────────────────────────────────────
    # 8) Notas y Informes
    # ──────────────────────────────────────────────────────────────────────────
    
]
