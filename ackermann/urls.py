# Dans votre fichier urls.py principal (du projet)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('django.contrib.auth.urls')),
    # Inclut toutes les URLs définies dans cabinet_management/urls.py
    path('', include('cabinet_management.urls')),
]