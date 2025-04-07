# cabinet_management/forms.py

# Imports Python Standard Library
import datetime

# Imports Django
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# Imports Locaux (de cette application)
from .models import Case, Client, Lawyer

# --- Formulaires d'Inscription / Ajout ---

class ClientRegistrationForm(forms.Form):
    first_name = forms.CharField(label="Prénom", max_length=100, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", max_length=100, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Adresse Email", required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label="Numéro de téléphone", max_length=20, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    password_confirm = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    # Validation pour vérifier si l'email existe déjà
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Vérifie si l'email ou le username (qui est l'email) existe déjà
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    # Validation pour vérifier si les mots de passe correspondent
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")

        return cleaned_data

class LawyerAddForm(forms.Form):
    first_name = forms.CharField(label="Prénom", max_length=100, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", max_length=100, required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Adresse Email", required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label="Numéro de téléphone (Optionnel)", max_length=20, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    specialization = forms.CharField(label="Spécialisation (Optionnel)", max_length=100, required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe initial", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    password_confirm = forms.CharField(label="Confirmer le mot de passe initial", widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    # Validation pour vérifier si l'email existe déjà
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise ValidationError("Un utilisateur (avocat ou client) avec cet email existe déjà.")
        return email

    # Validation pour vérifier si les mots de passe correspondent
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe initiaux ne correspondent pas.")

        return cleaned_data

# --- Formulaire de Prise de Rendez-vous ---

class AppointmentForm(forms.Form):
    appointment_datetime = forms.DateTimeField(
        label="Date et Heure du Rendez-vous",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )
    notes = forms.CharField(
        label="Notes (Optionnel)",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )

    # Validation : La date doit être dans le futur et pendant les heures ouvrables
    def clean_appointment_datetime(self):
        appointment_time = self.cleaned_data.get('appointment_datetime')
        if appointment_time:
            # Gestion du fuseau horaire
            if timezone.is_naive(appointment_time):
                appointment_time = timezone.make_aware(appointment_time, timezone.get_current_timezone())

            # Vérification si dans le futur
            if appointment_time <= timezone.now():
                raise ValidationError("La date et l'heure du rendez-vous doivent être dans le futur.", code='past_date')

            # Validation heures ouvrables (exemple simple)
            if appointment_time.weekday() >= 5: # Lundi=0, Mardi=1, ..., Samedi=5, Dimanche=6
                raise ValidationError("Les rendez-vous ne sont possibles que du Lundi au Vendredi.", code='weekend')
            if not (datetime.time(9, 0) <= appointment_time.time() <= datetime.time(17, 0)):
                raise ValidationError("Les rendez-vous ne sont possibles qu'entre 9h00 et 17h00.", code='outside_hours')

        return appointment_time

# --- Formulaire pour les Dossiers (Cases) ---

class CaseForm(forms.ModelForm):
    # Champs pour sélectionner Client et Avocat via une liste déroulante
    client = forms.ModelChoiceField(
        queryset=Client.objects.all().select_related('user'), # Pourrait être filtré davantage si nécessaire
        label="Client",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    lawyer = forms.ModelChoiceField(
        queryset=Lawyer.objects.filter(is_archived=False).select_related('user'), # Ne montre que les avocats actifs
        label="Avocat Assigné",
        required=False, # Permet de créer un dossier sans assigner d'avocat immédiatement
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Case
        fields = ['title', 'description', 'status', 'client', 'lawyer']
        # Définition des widgets pour ajouter les classes Bootstrap
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            # Les widgets pour client et lawyer sont définis ci-dessus
        }
        # Définition des labels personnalisés
        labels = {
            'title': 'Titre du dossier',
            'description': 'Description',
            'status': 'Statut',
        }

    # Optionnel: Décommenter pour personnaliser l'affichage des noms dans les listes déroulantes
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['client'].label_from_instance = lambda obj: f"{obj.user.get_full_name()} ({obj.user.email})"
    #     self.fields['lawyer'].label_from_instance = lambda obj: f"{obj.user.get_full_name()}"