# techcare_project/django_test/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Cambiamos 'enfermeria.urls' por 'enfermeria2.urls'
    path('enfermeria2/', include('enfermeria2.urls')),
]
