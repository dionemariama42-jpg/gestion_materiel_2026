from django.utils import timezone
from datetime import timedelta
from emprunts.models import Demande
from clubs.models import Notification


def envoyer_notification(utilisateur, message, lien=''):
    Notification.objects.create(
        destinataire=utilisateur,
        message=message,
        lien=lien
    )


def verifier_restitutions():
    maintenant = timezone.now()
    aujourd_hui = maintenant.date()
    demain = aujourd_hui + timedelta(days=1)

    demandes_en_cours = Demande.objects.filter(statut='en_cours')

    for demande in demandes_en_cours:
        try:
            if hasattr(demande.date_fin, 'date'):
                date_fin = demande.date_fin.date()
            else:
                date_fin = demande.date_fin

            materiels = ", ".join([
                l.materiel.nom for l in demande.lignes.all()
            ])

            # J-1
            if date_fin == demain:
                # Vérifier pas déjà notifié aujourd'hui
                deja_notifie = Notification.objects.filter(
                    destinataire=demande.utilisateur,
                    message__contains='restituer demain',
                    date__date=aujourd_hui
                ).exists()
                if not deja_notifie:
                    envoyer_notification(
                        demande.utilisateur,
                        f'⏰ Rappel J-1 : Vous devez restituer demain — {materiels}',
                        f'/emprunts/{demande.id}/'
                    )

            # Jour J
            elif date_fin == aujourd_hui:
                deja_notifie = Notification.objects.filter(
                    destinataire=demande.utilisateur,
                    message__contains='dernier jour',
                    date__date=aujourd_hui
                ).exists()
                if not deja_notifie:
                    envoyer_notification(
                        demande.utilisateur,
                        f'🔔 Jour J : C\'est le dernier jour pour restituer — {materiels}',
                        f'/emprunts/{demande.id}/'
                    )

            # Retard
            elif date_fin < aujourd_hui:
                deja_notifie_aujourd_hui = Notification.objects.filter(
                    destinataire=demande.utilisateur,
                    message__contains='RETARD',
                    date__date=aujourd_hui
                ).exists()
                if not deja_notifie_aujourd_hui:
                    demande.utilisateur.penalite += 1
                    demande.utilisateur.save()
                    envoyer_notification(
                        demande.utilisateur,
                        f'❌ RETARD : Vous n\'avez pas restitué — {materiels}. '
                        f'Pénalité appliquée. Score : {demande.utilisateur.get_score_fiabilite()}/100',
                        f'/emprunts/{demande.id}/'
                    )

        except Exception as e:
            print(f"Erreur demande {demande.id}: {e}")
            continue