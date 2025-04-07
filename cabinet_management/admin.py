# cabinet_management/admin.py
from django.contrib import admin
from .models import Lawyer, Client, Case, Appointment, Invoice # Importez vos modèles

# Enregistrez vos modèles ici pour les rendre visibles dans l'interface d'admin
# Des configurations plus avancées sont possibles pour personnaliser l'affichage

@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'phone_number', 'specialization', 'is_archived')
    list_filter = ('is_archived', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'specialization')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'phone_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'lawyer', 'status', 'creation_date', 'is_archived')
    list_filter = ('status', 'is_archived', 'lawyer')
    search_fields = ('title', 'client__user__username', 'lawyer__user__username')
    date_hierarchy = 'creation_date' # Ajoute une navigation par date

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'lawyer', 'appointment_datetime', 'status')
    list_filter = ('status', 'lawyer')
    search_fields = ('client__user__username', 'lawyer__user__username', 'notes')
    date_hierarchy = 'appointment_datetime'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'case', 'amount', 'status', 'issue_date', 'emailed_date')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'case__title')
    date_hierarchy = 'issue_date'

# Ou plus simplement si vous ne voulez pas de personnalisation au début:
# admin.site.register(Lawyer)
# admin.site.register(Client)
# admin.site.register(Case)
# admin.site.register(Appointment)
# admin.site.register(Invoice)