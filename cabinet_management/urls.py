# cabinet_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Authentification/Inscription Client ---
    path('inscription/client/', views.client_registration_view, name='client_registration'),

    # --- Vues Client ---
    path('avocats/', views.lawyer_list_for_clients_view, name='lawyer_list_client'),
    path('avocats/<int:lawyer_id>/prendre-rdv/', views.book_appointment_view, name='book_appointment'),
    # Ajouter ici plus tard : path('mes-rendez-vous/', views.client_appointment_list_view, name='client_appointment_list'),

    # --- Vues Admin - Gestion des Avocats ---
    path('admin/avocats/', views.lawyer_list_view, name='lawyer_list'),
    path('admin/avocats/ajouter/', views.add_lawyer_view, name='add_lawyer'),
    # Ajouter ici plus tard : URLs pour modifier, archiver, voir détails avocat

    # --- Vues Admin - Gestion des Dossiers ---
    path('admin/dossiers/', views.case_list_view, name='case_list'),
    path('admin/dossiers/ajouter/', views.add_case_view, name='add_case'),
    path('admin/dossiers/<int:case_id>/modifier/', views.edit_case_view, name='edit_case'),
    path('admin/dossiers/<int:case_id>/archiver/', views.archive_case_view, name='archive_case'),
    # Ajouter ici plus tard : path('admin/dossiers/<int:case_id>/', views.case_detail_view, name='case_detail'),

    # --- Vues Admin - Gestion des Rendez-vous ---
    path('admin/rendez-vous/demandes/', views.appointment_request_list_view, name='appointment_request_list'),
    path('admin/rendez-vous/<int:appointment_id>/confirmer/', views.confirm_appointment_view, name='confirm_appointment'),
    path('admin/rendez-vous/<int:appointment_id>/annuler/', views.cancel_appointment_view, name='cancel_appointment'),
    # Ajouter ici plus tard : path('admin/rendez-vous/tous/', views.all_appointment_list_view, name='all_appointment_list'),

]