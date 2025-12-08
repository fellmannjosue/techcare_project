from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Login principal (unificado)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('maestro_logout/', views.maestro_logout, name='maestro_logout'),
    path('register/', views.register_maestro, name='register_maestro'),
    path('menu/', views.menu_view, name='menu'),

    # Notificaciones para dashboard
  

    # Recuperación de contraseña (vistas estándar de Django)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
