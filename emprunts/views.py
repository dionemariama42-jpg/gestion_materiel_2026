from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Demande, LigneDemande, Emplacement, Restitution, PositionTempsReel
from materiel.models import Materiel, Categorie
import json
import math


@login_required
def liste_demandes(request):
    if request.user.role == 'admin':
        demandes = Demande.objects.all().order_by('-date_demande')
    else:
        demandes = Demande.objects.filter(
            utilisateur=request.user
        ).order_by('-date_demande')
    return render(request, 'emprunts/liste_demandes.html', {'demandes': demandes})


@login_required
def nouvelle_demande(request):
    from clubs.models import MembreClub, Club

    # Vérifier si demande pour un club
    club_id = request.GET.get('club') or request.POST.get('club_id')
    club = None
    est_president = False

    if club_id:
        club = Club.objects.filter(id=club_id).first()
        if club:
            est_president = MembreClub.objects.filter(
                club=club,
                utilisateur=request.user,
                role='president'
            ).exists()
            if not est_president:
                messages.error(request, 'Seul le président du club peut faire une demande.')
                return redirect('detail_club', pk=club_id)

    materiels = Materiel.objects.filter(
        quantite_disponible__gt=0
    ).select_related('categorie').order_by('categorie__libelle', 'nom')

    categories = Categorie.objects.all().order_by('libelle')

    if request.method == 'POST':
        date_debut = request.POST['date_debut']
        date_fin = request.POST['date_fin']
        motif = request.POST.get('motif', '')
        materiel_ids = request.POST.getlist('materiels')
        libelle = request.POST.get('libelle', '')
        latitude = request.POST.get('latitude-hidden') or request.POST.get('latitude', 0)
        longitude = request.POST.get('longitude-hidden') or request.POST.get('longitude', 0)
        club_id_post = request.POST.get('club_id', '')

        if not materiel_ids:
            messages.error(request, 'Veuillez sélectionner au moins un matériel.')
            return render(request, 'emprunts/nouvelle_demande.html', {
                'materiels': materiels,
                'categories': categories,
                'club': club,
            })

        # Vérifier stocks
        erreurs = []
        for mid in materiel_ids:
            quantite = int(request.POST.get(f'quantite_{mid}', 1))
            mat = Materiel.objects.get(id=mid)
            if mat.quantite_disponible < quantite:
                erreurs.append(
                    f'❌ Stock insuffisant pour "{mat.nom}" — '
                    f'Disponible : {mat.quantite_disponible}, '
                    f'Demandé : {quantite}'
                )

        if erreurs:
            for erreur in erreurs:
                messages.error(request, erreur)
            return render(request, 'emprunts/nouvelle_demande.html', {
                'materiels': materiels,
                'categories': categories,
                'club': club,
            })

        # Créer la demande
        demande = Demande.objects.create(
            utilisateur=request.user,
            date_debut=date_debut,
            date_fin=date_fin,
            motif=motif,
            statut='en_attente'
        )

        for mid in materiel_ids:
            mat = Materiel.objects.get(id=mid)
            quantite = int(request.POST.get(f'quantite_{mid}', 1))
            LigneDemande.objects.create(
                demande=demande,
                materiel=mat,
                quantite=quantite
            )
            # Réduire stock disponible
            mat.quantite_disponible -= quantite
            if mat.quantite_disponible <= 0:
                mat.etat = 'emprunte'
            mat.save()

        Emplacement.objects.create(
            demande=demande,
            libelle=libelle,
            latitude=float(latitude) if latitude else 0,
            longitude=float(longitude) if longitude else 0,
        )

        # Notifications
        from clubs.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admins = User.objects.filter(role='admin')
        club_nom = f' pour le club {club.nom}' if club_id_post else ''
        for admin in admins:
            Notification.objects.create(
                destinataire=admin,
                message=f'📋 Nouvelle demande #{demande.id} de '
                       f'{request.user.get_full_name() or request.user.username}'
                       f'{club_nom} en attente de validation.',
                lien=f'/emprunts/{demande.id}/'
            )
        Notification.objects.create(
            destinataire=request.user,
            message=f'✅ Votre demande #{demande.id}{club_nom} a été soumise avec succès.',
            lien=f'/emprunts/{demande.id}/'
        )

        messages.success(request, 'Demande envoyée avec succès !')
        return redirect('liste_demandes')

    return render(request, 'emprunts/nouvelle_demande.html', {
        'materiels': materiels,
        'categories': categories,
        'club': club,
        'est_president': est_president,
    })


@login_required
def detail_demande(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    return render(request, 'emprunts/detail_demande.html', {'demande': demande})


@login_required
def restituer(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    if request.method == 'POST':
        etat_materiel = request.POST['etat_materiel']
        observations = request.POST['observations']
        photo = request.FILES.get('photo', None)

        restitution = Restitution.objects.create(
            demande=demande,
            etat_materiel=etat_materiel,
            observations=observations,
        )
        if photo:
            restitution.photo = photo
            restitution.save()

        # Statut en attente de vérification admin
        demande.statut = 'en_attente_restitution'
        demande.save()

        from clubs.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Notification étudiant
        Notification.objects.create(
            destinataire=demande.utilisateur,
            message=f'⏳ Votre restitution pour la demande #{demande.id} '
                   f'est en attente de vérification par l\'admin.',
            lien=f'/emprunts/{demande.id}/'
        )

        # Notification admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                destinataire=admin,
                message=f'📦 {demande.utilisateur.get_full_name() or demande.utilisateur.username} '
                       f'a déposé le matériel — Demande #{demande.id} — '
                       f'État déclaré : {etat_materiel}. Veuillez vérifier.',
                lien=f'/emprunts/{demande.id}/'
            )

        messages.success(request, 'Restitution soumise ! En attente de vérification.')
        return redirect('liste_demandes')
    return render(request, 'emprunts/restituer.html', {'demande': demande})


@login_required
def confirmer_restitution(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    if request.user.role != 'admin':
        messages.error(request, 'Accès refusé.')
        return redirect('liste_demandes')

    if request.method == 'POST':
        demande.statut = 'restituee'
        demande.save()

        # Remettre le stock disponible
        for ligne in demande.lignes.all():
            ligne.materiel.quantite_disponible += ligne.quantite
            if ligne.materiel.quantite_disponible > 0:
                ligne.materiel.etat = 'disponible'
            ligne.materiel.save()

        from clubs.models import Notification

        # Notification étudiant
        Notification.objects.create(
            destinataire=demande.utilisateur,
            message=f'✅ Restitution confirmée par l\'admin pour la demande '
                   f'#{demande.id}. Merci !',
            lien=f'/emprunts/{demande.id}/'
        )

        # Notification admin
        Notification.objects.create(
            destinataire=request.user,
            message=f'✅ Vous avez confirmé la restitution de la demande #{demande.id}.',
            lien=f'/emprunts/{demande.id}/'
        )

        messages.success(request, 'Restitution confirmée avec succès !')
        return redirect('liste_demandes')

    return render(request, 'emprunts/confirmer_restitution.html', {
        'demande': demande
    })


@login_required
def suivi_gps(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    return render(request, 'emprunts/suivi_gps.html', {
        'demande': demande,
        'api_key': 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImUxODE1YzlkNzQ3MDRhZDlhMWVlNTc1ODBhNmE2NjMzIiwiaCI6Im11cm11cjY0In0='
    })


def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


@login_required
@csrf_exempt
def envoyer_position(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        lat = data['latitude']
        lng = data['longitude']

        PositionTempsReel.objects.create(
            demande=demande,
            latitude=lat,
            longitude=lng
        )

        from clubs.models import Notification
        try:
            zone = demande.zone_autorisee
            distance = calculer_distance(
                lat, lng,
                zone.latitude_centre,
                zone.longitude_centre
            )
            if distance > zone.rayon_km:
                from django.contrib.auth import get_user_model
                from django.utils import timezone
                User = get_user_model()
                admins = User.objects.filter(role='admin')
                for admin in admins:
                    recente = Notification.objects.filter(
                        destinataire=admin,
                        message__contains=f'demande #{demande.id}',
                        date__gte=timezone.now() - timezone.timedelta(minutes=30)
                    ).exists()
                    if not recente:
                        Notification.objects.create(
                            destinataire=admin,
                            message=f'🚨 ALERTE : Le matériel de la demande #{demande.id} '
                                   f'est sorti de la zone autorisée ! '
                                   f'Distance : {distance:.1f} km',
                            lien=f'/emprunts/carte-admin/'
                        )
        except:
            pass

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})


@login_required
def get_positions(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    positions = demande.positions.all()[:100]
    data = [{
        'lat': p.latitude,
        'lng': p.longitude,
        'date': p.date.strftime('%H:%M:%S')
    } for p in positions]
    return JsonResponse({'positions': data})


@login_required
def carte_admin(request):
    demandes_actives = Demande.objects.filter(
        statut='en_cours'
    ).select_related('utilisateur', 'emplacement')
    return render(request, 'emprunts/carte_admin.html', {
        'demandes': demandes_actives
    })


def suivi_mobile(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    return render(request, 'emprunts/suivi_mobile.html', {
        'demande': demande
    })