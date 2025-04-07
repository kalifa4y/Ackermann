# cabinet_management/models.py

from django.db import models
from django.contrib.auth.models import User # Le modèle utilisateur intégré de Django
from django.utils import timezone # Pour gérer les dates et heures

# Modèle pour les Avocats
# Chaque avocat est lié à un compte Utilisateur pour la connexion future (si nécessaire)
# ou simplement pour stocker email/nom/prénom.
class Lawyer(models.Model):
    # Relation un-à-un avec le modèle User. Si l'utilisateur est supprimé, le profil Avocat l'est aussi.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawyer_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True) # Numéro de téléphone (optionnel ici)
    specialization = models.CharField(max_length=100, blank=True, null=True) # Spécialisation (exemple)
    is_archived = models.BooleanField(default=False) # Pour la fonctionnalité d'archivage

    # Méthode pour afficher lisiblement l'objet Avocat (utile dans l'admin Django)
    def __str__(self):
        # Tente d'afficher le nom complet, sinon le nom d'utilisateur
        name = self.user.get_full_name()
        return f"Avocat: {name if name else self.user.username}"

# Modèle pour les Clients
# Chaque client est lié à un compte Utilisateur pour la connexion.
class Client(models.Model):
    # Relation un-à-un avec le modèle User.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    # Numéro de téléphone requis lors de l'inscription client
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        name = self.user.get_full_name()
        return f"Client: {name if name else self.user.username}"

# Modèle pour les Dossiers juridiques
class Case(models.Model):
    # Choix possibles pour le statut du dossier
    STATUS_CHOICES = [
        ('OP', 'Ouvert'),      # Open
        ('IP', 'En cours'),    # In Progress
        ('CL', 'Clôturé'),     # Closed
    ]

    title = models.CharField(max_length=200, verbose_name="Titre du dossier") # Nom du champ en français pour l'admin
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='OP', verbose_name="Statut")
    # Relation plusieurs-à-un : un client peut avoir plusieurs dossiers. Si le client est supprimé, ses dossiers aussi.
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases', verbose_name="Client Associé")
    # Relation plusieurs-à-un : un avocat peut gérer plusieurs dossiers.
    # Si l'avocat est supprimé (ou archivé), on ne supprime pas le dossier, on met juste ce champ à NULL.
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases', verbose_name="Avocat Assigné")
    creation_date = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    last_updated_date = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    is_archived = models.BooleanField(default=False, verbose_name="Archivé")

    def __str__(self):
        # Utilise __str__ de l'objet client pour plus de clarté
        client_repr = str(self.client) if self.client else 'Client non défini'
        return f"Dossier: {self.title} ({client_repr})"

# Modèle pour les Rendez-vous
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PEND', 'En attente'),  # Pending
        ('CONF', 'Confirmé'),    # Confirmed
        ('CANC', 'Annulé'),      # Cancelled
        ('COMP', 'Terminé'),     # Completed
    ]

    # Le client qui prend le RDV. Si le client est supprimé, ses RDV le sont aussi.
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments', verbose_name="Client")
    # L'avocat concerné par le RDV. Si l'avocat est supprimé, met le champ à NULL.
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name="Avocat")
    appointment_datetime = models.DateTimeField(verbose_name="Date et Heure du RDV")
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='PEND', verbose_name="Statut")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes") # Notes du client ou de l'avocat
    creation_date = models.DateTimeField(default=timezone.now, verbose_name="Date de demande")

    def __str__(self):
        # Formatage de la date pour une meilleure lisibilité
        datetime_str = self.appointment_datetime.strftime('%d/%m/%Y %H:%M') if self.appointment_datetime else 'Non défini'
        # Utilise __str__ des objets client et lawyer
        client_repr = str(self.client) if self.client else 'Client non défini'
        lawyer_repr = str(self.lawyer) if self.lawyer else 'Non assigné'
        return f"RDV {client_repr} avec {lawyer_repr} le {datetime_str}"

# Modèle pour les Factures
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRFT', 'Brouillon'),  # Draft
        ('SENT', 'Envoyée'),    # Sent
        ('PAID', 'Payée'),      # Paid
        ('CANC', 'Annulée'),    # Cancelled
    ]

    # La facture est liée à un dossier spécifique. Si le dossier est supprimé, la facture aussi.
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='invoices', verbose_name="Dossier Concerné")
    # Numéro unique pour chaque facture (il faudra une logique pour le générer)
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant") # 10 chiffres au total, 2 après la virgule
    issue_date = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    due_date = models.DateField(blank=True, null=True, verbose_name="Date d'échéance")
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='DRFT', verbose_name="Statut")
    # Pour savoir quand la facture a été envoyée par email
    emailed_date = models.DateTimeField(blank=True, null=True, verbose_name="Date d'envoi par email")
    # Pour plus de détails (lignes de facture), on pourrait créer un autre modèle `InvoiceItem` lié à celui-ci.

    def __str__(self):
        # Utilise __str__ de l'objet case
        case_repr = str(self.case) if self.case else 'Dossier non défini'
        return f"Facture {self.invoice_number} pour {case_repr}"