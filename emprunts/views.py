from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Demande, LigneDemande, Emplacement, Restitution, PositionTempsReel
from materiel.models import Materiel, Categorie
from django.utils import timezone
import json
import math


@login_required
def liste_demandes(request):
    if request.user.role in ['admin', 'admin_terrain', 'admin_bureau']:
        demandes = Demande.objects.all().order_by('-date_demande')
        if request.user.role == 'admin_terrain':
            demandes = demandes.filter(
                lignes__materiel__domaine='terrain'
            ).distinct()
        elif request.user.role == 'admin_bureau':
            demandes = demandes.filter(
                lignes__materiel__domaine='bureau'
            ).distinct()
    else:
        demandes = Demande.objects.filter(
            utilisateur=request.user
        ).order_by('-date_demande')
    return render(request, 'emprunts/liste_demandes.html', {'demandes': demandes})


@login_required
def nouvelle_demande(request):
    from clubs.models import MembreClub, Club

    aujourd_hui = timezone.now().date()

    # ===== 1. COMPTE BLOQUÉ =====
    if request.user.bloque:
        messages.error(
            request,
            f'⛔ Votre compte est bloqué suite à {request.user.penalite} pénalité(s). '
            f'Contactez l\'administration pour le déblocage.'
        )
        return redirect('tableau_de_bord')

    # ===== 2. EMPRUNT EN RETARD (date dépassée et non restitué) =====
    emprunt_en_retard = Demande.objects.filter(
        utilisateur=request.user,
        statut__in=['approuvee', 'en_cours'],
        date_fin__date__lt=aujourd_hui
    ).first()

    if emprunt_en_retard:
        messages.error(
            request,
            f'🚫 Vous avez un emprunt en retard (Demande #{emprunt_en_retard.id} — '
            f'date limite dépassée le {emprunt_en_retard.date_fin.strftime("%d/%m/%Y")}). '
            f'Restituez le matériel avant de faire une nouvelle demande.'
        )
        return redirect('detail_demande', pk=emprunt_en_retard.id)

    # ===== 3. AVERTISSEMENT PÉNALITÉS =====
    if request.user.penalite == 1:
        messages.warning(
            request,
            '⚠️ Attention : vous avez 1 pénalité sur 3. '
            'Encore 2 pénalités et votre compte sera bloqué.'
        )
    elif request.user.penalite == 2:
        messages.warning(
            request,
            '⚠️ Dernier avertissement : vous avez 2 pénalités sur 3. '
            'Une nouvelle pénalité bloquera votre compte définitivement.'
        )

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

    materiels = Materiel.objects.filter(quantite_disponible__gt=0).select_related('categorie').order_by('categorie__libelle', 'nom')

    if request.user.role == 'admin_terrain':
        materiels = materiels.filter(domaine='terrain')
    elif request.user.role == 'admin_bureau':
        materiels = materiels.filter(domaine='bureau')

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

        from clubs.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()

        domaines = set()
        for mid in materiel_ids:
            mat = Materiel.objects.get(id=mid)
            domaines.add(getattr(mat, 'domaine', 'autre'))

        roles_a_notifier = ['admin']
        if 'terrain' in domaines:
            roles_a_notifier.append('admin_terrain')
        if 'bureau' in domaines:
            roles_a_notifier.append('admin_bureau')

        admins = User.objects.filter(role__in=roles_a_notifier)
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

        demande.statut = 'en_attente_restitution'
        demande.save()

        from clubs.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()

        Notification.objects.create(
            destinataire=demande.utilisateur,
            message=f'⏳ Votre restitution pour la demande #{demande.id} '
                   f'est en attente de vérification par l\'admin.',
            lien=f'/emprunts/{demande.id}/'
        )

        domaines = set()
        for ligne in demande.lignes.all():
            domaines.add(getattr(ligne.materiel, 'domaine', 'autre'))

        roles_a_notifier = ['admin']
        if 'terrain' in domaines:
            roles_a_notifier.append('admin_terrain')
        if 'bureau' in domaines:
            roles_a_notifier.append('admin_bureau')

        admins = User.objects.filter(role__in=roles_a_notifier)
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
    if request.user.role not in ['admin', 'admin_terrain', 'admin_bureau']:
        messages.error(request, 'Accès refusé.')
        return redirect('liste_demandes')

    if request.user.role == 'admin_terrain':
        if not demande.lignes.filter(materiel__domaine='terrain').exists():
            messages.error(request, 'Vous ne pouvez confirmer que les matériels terrain.')
            return redirect('liste_demandes')
    elif request.user.role == 'admin_bureau':
        if not demande.lignes.filter(materiel__domaine='bureau').exists():
            messages.error(request, 'Vous ne pouvez confirmer que les matériels bureau.')
            return redirect('liste_demandes')

    if request.method == 'POST':
        etat = request.POST.get('etat_materiel', 'bon')
        aujourd_hui = timezone.now().date()

        demande.statut = 'restituee'
        demande.save()

        for ligne in demande.lignes.all():
            ligne.materiel.quantite_disponible += ligne.quantite
            if ligne.materiel.quantite_disponible > 0:
                ligne.materiel.etat = 'disponible'
            ligne.materiel.save()

        utilisateur = demande.utilisateur
        from clubs.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # ===== PÉNALITÉ : RETARD OU MATÉRIEL ABÎMÉ/PERDU =====
        rendu_en_retard = demande.date_fin.date() < aujourd_hui
        penalite_ajoutee = False

        if rendu_en_retard or etat in ['abime', 'perdu']:
            utilisateur.penalite += 1
            penalite_ajoutee = True

            raisons = []
            if rendu_en_retard:
                jours_retard = (aujourd_hui - demande.date_fin.date()).days
                raisons.append(f'retard de {jours_retard} jour(s)')
            if etat in ['abime', 'perdu']:
                raisons.append(f'matériel {etat}')

            raison_texte = ' + '.join(raisons)

            # ===== BLOCAGE APRÈS 3 PÉNALITÉS =====
            if utilisateur.penalite >= 3:
                utilisateur.bloque = True
                utilisateur.save()

                Notification.objects.create(
                    destinataire=utilisateur,
                    message=f'⛔ Votre compte a été bloqué automatiquement après '
                           f'{utilisateur.penalite} pénalité(s) ({raison_texte}). '
                           f'Contactez l\'administration pour le déblocage.',
                    lien='/comptes/parametres/'
                )

                admins = User.objects.filter(role='admin')
                for admin in admins:
                    Notification.objects.create(
                        destinataire=admin,
                        message=f'🔒 Le compte de {utilisateur.get_full_name()} '
                               f'a été automatiquement bloqué après '
                               f'{utilisateur.penalite} pénalité(s) ({raison_texte}).',
                        lien=f'/admin/comptes/utilisateur/{utilisateur.id}/change/'
                    )

                messages.warning(
                    request,
                    f'⚠️ {utilisateur.get_full_name()} a été bloqué '
                    f'automatiquement ({utilisateur.penalite} pénalités — {raison_texte}).'
                )

            else:
                utilisateur.save()
                restantes = 3 - utilisateur.penalite

                Notification.objects.create(
                    destinataire=utilisateur,
                    message=f'⚠️ Une pénalité a été ajoutée ({raison_texte}). '
                           f'Total : {utilisateur.penalite}/3. '
                           f'Encore {restantes} avant blocage de votre compte.',
                    lien=f'/emprunts/{demande.id}/'
                )

                messages.info(
                    request,
                    f'ℹ️ Une pénalité a été appliquée à {utilisateur.get_full_name()} '
                    f'({raison_texte}). Total : {utilisateur.penalite}/3.'
                )

        # Notification de confirmation restitution
        Notification.objects.create(
            destinataire=utilisateur,
            message=f'✅ Restitution confirmée par l\'admin pour la demande #{demande.id}.'
                   f'{" Une pénalité a été appliquée." if penalite_ajoutee else " Merci !"}',
            lien=f'/emprunts/{demande.id}/'
        )

        messages.success(request, 'Restitution confirmée avec succès !')
        return redirect('liste_demandes')

    return render(request, 'emprunts/confirmer_restitution.html', {
        'demande': demande
    })


# ===== DÉBLOQUER UN UTILISATEUR =====
@login_required
def debloquer_utilisateur(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Accès refusé.')
        return redirect('liste_demandes')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    utilisateur = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        utilisateur.bloque = False
        utilisateur.penalite = 0
        utilisateur.save()

        from clubs.models import Notification
        Notification.objects.create(
            destinataire=utilisateur,
            message='✅ Votre compte a été débloqué par l\'administrateur. '
                   'Vos pénalités ont été réinitialisées.',
            lien='/emprunts/'
        )

        messages.success(
            request,
            f'✅ Le compte de {utilisateur.get_full_name()} a été débloqué.'
        )

    return redirect('liste_demandes')


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
                User = get_user_model()
                admins = User.objects.filter(role__in=['admin', 'admin_terrain'])
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
    if request.user.role not in ['admin', 'admin_terrain']:
        messages.error(request, 'Accès refusé.')
        return redirect('tableau_de_bord')
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