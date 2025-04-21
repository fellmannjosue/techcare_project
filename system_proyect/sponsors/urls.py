from django.urls import path
from . import views
from accounts.views import menu_view  # Importa correctamente la vista de `accounts`

app_name = "sponsors"

urlpatterns = [
    path('dashboard/', views.sponsors_dashboard, name='sponsors_dashboard'),
    path('add/', views.add_sponsor, name='add_sponsor'),
    path('get-sponsor-data/', views.get_sponsor_data, name='get_sponsor_data'),
    path('edit/<int:sponsor_id>/', views.edit_sponsor, name='edit_sponsor'),
    path('delete/<int:sponsor_id>/', views.delete_sponsor, name='delete_sponsor'),
    path('list/', views.sponsor_list, name='sponsor_list'),
    

    # Formularios adicionales
    path('add-city/', views.add_city, name='add_city'),
    path('add-country/', views.add_country, name='add_country'),
    path('add-directed/', views.add_directed, name='add_directed'),
    path('add-title/', views.add_title, name='add_title'),
    path('add-correspondence/', views.add_correspondence, name='add_correspondence'),
    path('add-descr-godfather/', views.add_descr_godfather, name='add_descr_godfather'),
    path('add-godfather/', views.add_godfather, name='add_godfather'),
    path('add-income/', views.add_income, name='add_income'),
    path('add-sponsored/', views.add_sponsored, name='add_sponsored'),

    path('search-name/', views.search_name, name='search_name'),
    path('search-lastname/', views.search_lastname, name='search_lastname'),
    path('search-id/', views.search_id, name='search_id'),

    path('menu/', menu_view, name='menu'),  # Usa `menu_view` como callable
]
