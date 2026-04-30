from django.contrib import admin
from .models import Club, MembreClub, Activite, PhotoActivite, Notification

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nombre_membres', 'cotisation_montant', 'date_creation']
    search_fields = ['nom']

@admin.register(MembreClub)
class MembreClubAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'club', 'role', 'cotisation_payee', 'date_adhesion']
    list_filter = ['role', 'cotisation_payee', 'club']

@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'club', 'type', 'date', 'statut']
    list_filter = ['type', 'statut', 'club']

@admin.register(PhotoActivite)
class PhotoActiviteAdmin(admin.ModelAdmin):
    list_display = ['activite', 'legende', 'date_ajout']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['destinataire', 'message', 'lu', 'date']
    list_filter = ['lu']