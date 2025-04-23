# system_proyect/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('',      lambda request: redirect('/accounts/login/')),
    path('admin/', admin.site.urls),

    path('accounts/',       include('accounts.urls')),
    path('tickets/',        include('tickets.urls')),
    path('inventario/',     include('inventario.urls')),

    # Registro con namespace para mantenimiento:
    path(
        'mantenimiento/',
        include(
            ('mantenimiento.urls', 'mantenimiento'),
            namespace='mantenimiento'
        )
    ),

    path('citas_billingue/', include('citas_billingue.urls')),
    path('citas_colegio/',   include('citas_colegio.urls')),
    path('sponsors/',        include('sponsors.urls')),
    path('menu/',            include('menu.urls')),
    path(
  'enfermeria/',
  include(
    ('enfermeria.urls','enfermeria'),
    namespace='enfermeria'
  )
),

]
