# cabinet_management/views.py

# Imports Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

# Imports Locaux (de cette application)
from .models import Client, Lawyer, Appointment, Case
from .forms import (
    ClientRegistrationForm,
    LawyerAddForm,
    AppointmentForm,
    CaseForm
)

# --- Fonctions d'Aide / Tests ---

def is_staff_user(user):
    """Vérifie si l'utilisateur est membre du staff."""
    return user.is_authenticated and user.is_staff

def is_client_user(user):
    """Vérifie si l'utilisateur est un client authentifié (non-staff avec profil client)."""
    # hasattr vérifie si la relation inversée 'client_profile' existe
    return user.is_authenticated and not user.is_staff and hasattr(user, 'client_profile')

# --- Vues Générales ---

def home_view(request):
    """Affiche la page d'accueil du site."""
    return render(request, 'cabinet_management/home.html')


# --- Vues d'Authentification / Inscription ---

def client_registration_view(request):
    """Gère l'inscription d'un nouveau client."""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            try:
                # Utilise l'email comme nom d'utilisateur
                new_user = User.objects.create_user(username=email, email=email, password=password)
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()

                Client.objects.create(user=new_user, phone_number=phone_number)
                login(request, new_user) # Connecte l'utilisateur
                messages.success(request, "Inscription réussie ! Vous êtes maintenant connecté.")
                return redirect('home')

            except Exception as e:
                # Logguer l'erreur ici serait préférable en production
                messages.error(request, f"Une erreur est survenue lors de l'inscription : {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientRegistrationForm()

    return render(request, 'cabinet_management/client_registration.html', {'form': form})

# --- Vues Avocats ---

@login_required
@user_passes_test(is_staff_user)
def lawyer_list_view(request):
    """Liste les avocats actifs pour l'administrateur."""
    lawyers = Lawyer.objects.filter(is_archived=False).select_related('user')
    context = {'lawyers': lawyers}
    return render(request, 'cabinet_management/lawyer_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def add_lawyer_view(request):
    """Ajoute un nouvel avocat (par l'administrateur)."""
    if request.method == 'POST':
        form = LawyerAddForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            specialization = form.cleaned_data['specialization']
            password = form.cleaned_data['password']

            try:
                # Crée le User (non staff par défaut)
                lawyer_user = User.objects.create_user(username=email, email=email, password=password)
                lawyer_user.first_name = first_name
                lawyer_user.last_name = last_name
                lawyer_user.save()

                # Crée le profil Lawyer lié
                Lawyer.objects.create(
                    user=lawyer_user,
                    phone_number=phone_number,
                    specialization=specialization
                )
                messages.success(request, f"L'avocat '{first_name} {last_name}' a été ajouté avec succès.")
                return redirect('lawyer_list')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'avocat : {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = LawyerAddForm()

    return render(request, 'cabinet_management/add_lawyer.html', {'form': form})

@login_required
def lawyer_list_for_clients_view(request):
    """Liste les avocats actifs pour les clients connectés."""
    lawyers = Lawyer.objects.filter(is_archived=False).select_related('user')
    context = {'lawyers': lawyers}
    return render(request, 'cabinet_management/lawyer_list_client.html', context)

# --- Vues Rendez-vous ---

@login_required
@user_passes_test(is_client_user, login_url='/comptes/login/') # Assure que seul un client peut réserver
def book_appointment_view(request, lawyer_id):
    """Permet à un client de demander un RDV avec un avocat spécifique."""
    lawyer = get_object_or_404(Lawyer, id=lawyer_id, is_archived=False)
    client_profile = request.user.client_profile # Le décorateur devrait garantir l'existence

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_datetime = form.cleaned_data['appointment_datetime']
            notes = form.cleaned_data['notes']

            try:
                Appointment.objects.create(
                    client=client_profile,
                    lawyer=lawyer,
                    appointment_datetime=appointment_datetime,
                    notes=notes,
                )
                # Formatage correct de la date pour le message
                dt_str = appointment_datetime.strftime('%d/%m/%Y à %H:%M')
                messages.success(request, f"Votre demande de rendez-vous avec {lawyer.user.get_full_name()} pour le {dt_str} a été envoyée.")
                return redirect('lawyer_list_client') # Ou vers 'mes_rdv' plus tard
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {e}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = AppointmentForm()

    context = {'form': form, 'lawyer': lawyer}
    return render(request, 'cabinet_management/appointment.html', context)

@login_required
@user_passes_test(is_staff_user)
def appointment_request_list_view(request):
    """Liste les demandes de RDV en attente pour l'admin."""
    pending_appointments = Appointment.objects.filter(status='PEND').select_related(
        'client__user',
        'lawyer__user'
    ).order_by('appointment_datetime')
    context = {'pending_appointments': pending_appointments}
    return render(request, 'cabinet_management/appointment_request_list.html', context)

@require_POST
@login_required
@user_passes_test(is_staff_user)
def confirm_appointment_view(request, appointment_id):
    """Confirme une demande de RDV (par l'admin)."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.status == 'PEND':
        appointment.status = 'CONF'
        appointment.save()
        # Formatage correct de la date pour le message
        dt_str = appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')
        messages.success(request, f"Le rendez-vous du {dt_str} a été confirmé.")
        # TODO: Envoyer notification au client
    else:
        messages.warning(request, "Ce rendez-vous n'était pas en attente.")
    return redirect('appointment_request_list')

@require_POST
@login_required
@user_passes_test(is_staff_user)
def cancel_appointment_view(request, appointment_id):
    """Annule une demande de RDV (par l'admin)."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.status in ['PEND', 'CONF']: # On peut annuler si en attente ou confirmé
        appointment.status = 'CANC'
        appointment.save()
         # Formatage correct de la date pour le message
        dt_str = appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')
        messages.success(request, f"Le rendez-vous du {dt_str} a été annulé.")
        # TODO: Envoyer notification au client
    else:
        messages.warning(request, "Ce rendez-vous ne pouvait pas être annulé.")
    return redirect('appointment_request_list')

# --- Vues Dossiers ---

@login_required
@user_passes_test(is_staff_user)
def case_list_view(request):
    """Liste les dossiers actifs pour l'admin."""
    cases = Case.objects.filter(is_archived=False).select_related(
        'client__user',
        'lawyer__user'
    ).order_by('-last_updated_date')
    context = {'cases': cases}
    return render(request, 'cabinet_management/case_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def add_case_view(request):
    """Ajoute un nouveau dossier (par l'admin)."""
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save() # ModelForm.save() crée l'instance
            messages.success(request, f"Le dossier '{case.title}' a été créé avec succès.")
            return redirect('case_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CaseForm()

    context = {
        'form': form,
        'form_title': "Ajouter un Nouveau Dossier"
    }
    return render(request, 'cabinet_management/case_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def edit_case_view(request, case_id):
    """Modifie un dossier existant (par l'admin)."""
    case_instance = get_object_or_404(Case, id=case_id, is_archived=False) # Ne modifie que les non-archivés
    if request.method == 'POST':
        form = CaseForm(request.POST, instance=case_instance) # Passe l'instance pour mise à jour
        if form.is_valid():
            form.save()
            messages.success(request, f"Le dossier '{case_instance.title}' a été mis à jour.")
            return redirect('case_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = CaseForm(instance=case_instance) # Pré-remplit le formulaire

    context = {
        'form': form,
        'form_title': f"Modifier le Dossier : {case_instance.title}",
        'case': case_instance
    }
    return render(request, 'cabinet_management/case_form.html', context)

@require_POST
@login_required
@user_passes_test(is_staff_user)
def archive_case_view(request, case_id):
    """Archive un dossier (par l'admin)."""
    case_to_archive = get_object_or_404(Case, id=case_id)
    if not case_to_archive.is_archived:
        case_to_archive.is_archived = True
        case_to_archive.save()
        messages.success(request, f"Le dossier '{case_to_archive.title}' a été archivé.")
    else:
        messages.warning(request, f"Le dossier '{case_to_archive.title}' est déjà archivé.")
    return redirect('case_list')