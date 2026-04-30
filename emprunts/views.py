from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Demande, LigneDemande, Emplacement, Restitution, PositionTempsReel
from materiel.models import Materiel
import json
import math
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Demande, LigneDemande, Emplacement, Restitution
from materiel.models import Materiel


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
    materiels = Materiel.objects.filter(etat='disponible')
    if request.method == 'POST':
        date_debut = request.POST['date_debut']
        date_fin = request.POST['date_fin']
        motif = request.POST.get('motif', '')
        materiel_ids = request.POST.getlist('materiels')
        libelle = request.POST.get('libelle', '')
        latitude = request.POST.get('latitude-hidden') or request.POST.get('latitude', 0)
        longitude = request.POST.get('longitude-hidden') or request.POST.get('longitude', 0)

        demande = Demande.objects.create(
            utilisateur=request.user,
            date_debut=date_debut,
            date_fin=date_fin,
            motif=motif,
            statut='en_attente'
        )
        for mid in materiel_ids:
            mat = Materiel.objects.get(id=mid)
            LigneDemande.objects.create(demande=demande, materiel=mat, quantite=1)

        Emplacement.objects.create(
            demande=demande,
            libelle=libelle,
            latitude=float(latitude) if latitude else 0,
            longitude=float(longitude) if longitude else 0,
        )

        # Notifier l'admin
        from django.contrib.auth import get_user_model
        from clubs.models import Notification
        User = get_user_model()
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                destinataire=admin,
                message=f'Nouvelle demande #{demande.id} de {request.user} en attente.',
                lien=f'/emprunts/{demande.id}/'
            )
        Notification.objects.create(
            destinataire=request.user,
            message=f'Votre demande #{demande.id} a été soumise avec succès.',
            lien=f'/emprunts/{demande.id}/'
        )
        messages.success(request, 'Demande envoyée avec succès !')
        return redirect('liste_demandes')
    return render(request, 'emprunts/nouvelle_demande.html', {'materiels': materiels})

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
        Restitution.objects.create(
            demande=demande,
            etat_materiel=etat_materiel,
            observations=observations,
        )
        demande.statut = 'restituee'
        demande.save()
        for ligne in demande.lignes.all():
            ligne.materiel.etat = 'disponible'
            ligne.materiel.save()
        messages.success(request, 'Restitution enregistrée avec succès !')
        return redirect('liste_demandes')
    return render(request, 'emprunts/restituer.html', {'demande': demande})

@login_required
def suivi_gps(request, pk):
    demande = get_object_or_404(Demande, pk=pk)
    return render(request, 'emprunts/suivi_gps.html', {
        'demande': demande,
        'api_key': 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImUxODE1YzlkNzQ3MDRhZDlhMWVlNTc1ODBhNmE2NjMzIiwiaCI6Im11cm11cjY0In0='
    })

import math

def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371  # rayon terre en km
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

        # Enregistrer position
        PositionTempsReel.objects.create(
            demande=demande,
            latitude=lat,
            longitude=lng
        )

        # Vérifier géofencing
        from clubs.models import Notification
        try:
            zone = demande.zone_autorisee
            distance = calculer_distance(
                lat, lng,
                zone.latitude_centre,
                zone.longitude_centre
            )
            if distance > zone.rayon_km:
                # Alerter l'admin
                from django.contrib.auth import get_user_model
                User = get_user_model()
                admins = User.objects.filter(role='admin')
                for admin in admins:
                    # Vérifier pas déjà notifié récemment
                    from django.utils import timezone
                    recente = Notification.objects.filter(
                        destinataire=admin,
                        message__contains=f'demande #{demande.id}',
                        date__gte=timezone.now() - timezone.timedelta(minutes=30)
                    ).exists()
                    if not recente:
                        Notification.objects.create(
                            destinataire=admin,
                            message=f'ALERTE : Le matériel de la demande #{demande.id} '
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