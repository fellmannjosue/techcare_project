from django.urls import path
from . import views

urlpatterns = [
    # Login principal
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('maestro_logout/', views.maestro_logout, name='maestro_logout'),
    path('register/', views.register_maestro, name='register_maestro'),
    path('menu/', views.menu_view, name='menu'),

    # NUEVO Login duplicado para "user_login"
    path('user_login/', views.user_login_view, name='user_login'),
    # Ruta para chequear notificaciones:
    path('check-new-notifications/', views.check_new_notifications, name='check_new_notifications'),

]
