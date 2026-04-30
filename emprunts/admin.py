from django.contrib import admin
from .models import Demande, LigneDemande, Emplacement, Restitution
from clubs.models import Notification


@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'statut', 'date_demande', 'date_fin']
    list_filter = ['statut']
    search_fields = ['utilisateur__username']
    actions = ['approuver_demandes', 'refuser_demandes']

    def approuver_demandes(self, request, queryset):
        for demande in queryset:
            if demande.statut == 'en_attente':
                demande.statut = 'en_cours'
                demande.save()
                # Mettre le matériel en emprunté
                for ligne in demande.lignes.all():
                    ligne.materiel.etat = 'emprunte'
                    ligne.materiel.save()
                # Notifier l'étudiant
                Notification.objects.create(
                    destinataire=demande.utilisateur,
                    message=f'Votre demande #{demande.id} a été approuvée !',
                    lien=f'/emprunts/{demande.id}/'
                )
        self.message_user(request, 'Demandes approuvées avec succès !')
    approuver_demandes.short_description = 'Approuver les demandes sélectionnées'

    def refuser_demandes(self, request, queryset):
        for demande in queryset:
            if demande.statut == 'en_attente':
                demande.statut = 'refusee'
                demande.save()
                Notification.objects.create(
                    destinataire=demande.utilisateur,
                    message=f'Votre demande #{demande.id} a été refusée.',
                    lien=f'/emprunts/{demande.id}/'
                )
        self.message_user(request, 'Demandes refusées avec succès !')
    refuser_demandes.short_description = 'Refuser les demandes sélectionnées'


@admin.register(LigneDemande)
class LigneDemandeAdmin(admin.ModelAdmin):
    list_display = ['demande', 'materiel', 'quantite']


@admin.register(Emplacement)
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'latitude', 'longitude']


@admin.register(Restitution)
class RestitutionAdmin(admin.ModelAdmin):
    list_display = ['demande', 'date_retour', 'etat_materiel']
    list_filter = ['etat_materiel']