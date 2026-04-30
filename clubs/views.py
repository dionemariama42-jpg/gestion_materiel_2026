from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Club, MembreClub, Activite, PhotoActivite, Notification


def envoyer_notification(utilisateur, message, lien=''):
    Notification.objects.create(
        destinataire=utilisateur,
        message=message,
        lien=lien
    )


def liste_clubs(request):
    clubs = Club.objects.all()
    classement = sorted(clubs, key=lambda c: c.score_activite(), reverse=True)
    return render(request, 'clubs/liste_clubs.html', {
        'clubs': clubs,
        'classement': classement[:3],
    })


def detail_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    activites = club.activites.all().order_by('-date')
    membres = club.membres.all()
    activites_a_venir = club.activites.filter(
        date__gte=timezone.now().date(),
        statut='planifiee'
    ).order_by('date')
    activites_terminees = club.activites.filter(statut='terminee')
    est_membre = False
    mon_role = None
    est_president = False
    if request.user.is_authenticated:
        appartenance = club.membres.filter(utilisateur=request.user).first()
        if appartenance:
            est_membre = True
            mon_role = appartenance.role
            est_president = appartenance.role == 'president'
    return render(request, 'clubs/detail_club.html', {
        'club': club,
        'activites': activites,
        'activites_a_venir': activites_a_venir,
        'activites_terminees': activites_terminees,
        'membres': membres,
        'est_membre': est_membre,
        'mon_role': mon_role,
        'est_president': est_president,
        'total_membres': club.nombre_membres(),
        'total_activites': activites_terminees.count(),
    })


@login_required
def rejoindre_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    appartenance = club.membres.filter(utilisateur=request.user).first()
    if appartenance:
        appartenance.delete()
        messages.success(request, f'Vous avez quitté le club {club.nom}.')
    else:
        MembreClub.objects.create(
            club=club,
            utilisateur=request.user,
            role='membre'
        )
        messages.success(request, f'Bienvenue dans le club {club.nom} !')
        president = club.president()
        if president:
            envoyer_notification(
                president,
                f'{request.user} a rejoint votre club {club.nom}.',
                f'/clubs/{club.id}/'
            )
    return redirect('detail_club', pk=pk)


@login_required
def nouvelle_activite(request):
    mes_clubs = MembreClub.objects.filter(
        utilisateur=request.user,
        role='president'
    )
    if not mes_clubs.exists():
        messages.error(request, 'Seul un président de club peut créer une activité.')
        return redirect('liste_clubs')
    clubs = [mc.club for mc in mes_clubs]
    if request.method == 'POST':
        club_id = request.POST['club']
        titre = request.POST['titre']
        type_activite = request.POST['type']
        description = request.POST['description']
        date = request.POST['date']
        lieu = request.POST['lieu']
        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        photo = request.FILES.get('photo_principale', None)
        programme = request.FILES.get('programme', None)
        club = Club.objects.get(id=club_id)
        membre = club.membres.filter(
            utilisateur=request.user,
            role='president'
        ).first()
        if not membre:
            messages.error(request, 'Vous n\'êtes pas président de ce club.')
            return redirect('liste_clubs')
        activite = Activite.objects.create(
            club=club,
            titre=titre,
            type=type_activite,
            description=description,
            date=date,
            lieu=lieu,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
        )
        if photo:
            activite.photo_principale = photo
        if programme:
            activite.programme = programme
        activite.save()
        from cahier.models import Cours, Seance
        cours, _ = Cours.objects.get_or_create(
            nom=f"Activités — {club.nom}",
            defaults={'description': f'Toutes les activités du {club.nom}'}
        )
        seance = Seance.objects.create(
            cours=cours,
            enseignant=request.user,
            date=date,
            contenu=f"[{activite.get_type_display()}] {titre}\n\n{description}",
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
        )
        activite.seance = seance
        activite.save()
        for membre in club.membres.all():
            envoyer_notification(
                membre.utilisateur,
                f'Nouvelle activité dans {club.nom} : {titre} le {date}',
                f'/clubs/activite/{activite.id}/'
            )
        messages.success(request, 'Activité créée et membres notifiés !')
        return redirect('detail_club', pk=club_id)
    return render(request, 'clubs/nouvelle_activite.html', {'clubs': clubs})


def detail_activite(request, pk):
    activite = get_object_or_404(Activite, pk=pk)
    photos = activite.photos.all()
    return render(request, 'clubs/detail_activite.html', {
        'activite': activite,
        'photos': photos,
    })


@login_required
def ajouter_photos(request, pk):
    activite = get_object_or_404(Activite, pk=pk)
    if request.method == 'POST':
        photos = request.FILES.getlist('photos')
        for photo in photos:
            legende = request.POST.get('legende', '')
            PhotoActivite.objects.create(
                activite=activite,
                photo=photo,
                legende=legende
            )
        messages.success(request, 'Photos ajoutées à la galerie !')
        return redirect('detail_activite', pk=pk)
    return render(request, 'clubs/ajouter_photos.html', {'activite': activite})


@login_required
def payer_cotisation(request, pk):
    club = get_object_or_404(Club, pk=pk)
    appartenance = get_object_or_404(
        MembreClub,
        club=club,
        utilisateur=request.user
    )
    if not appartenance.cotisation_payee:
        appartenance.cotisation_payee = True
        appartenance.date_paiement = timezone.now().date()
        appartenance.save()
        messages.success(request, f'Cotisation payée pour {club.nom} !')
        president = club.president()
        if president:
            envoyer_notification(
                president,
                f'{request.user} a payé sa cotisation pour {club.nom}.',
                f'/clubs/{club.id}/'
            )
    return redirect('detail_club', pk=pk)


@login_required
def mes_notifications(request):
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-date')
    notifications.filter(lu=False).update(lu=True)
    return render(request, 'clubs/notifications.html', {
        'notifications': notifications
    })


def classement_clubs(request):
    clubs = Club.objects.all()
    classement = sorted(
        clubs,
        key=lambda c: c.score_activite(),
        reverse=True
    )
    return render(request, 'clubs/classement.html', {'classement': classement})

def count_notifications(request):
    from django.http import JsonResponse
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(
            destinataire=request.user,
            lu=False
        ).order_by('-date')
        count = notifs.count()
        derniere = None
        if notifs.exists():
            n = notifs.first()
            derniere = {
                'id': n.id,
                'message': n.message,
                'lien': n.lien
            }
        return JsonResponse({'count': count, 'derniere': derniere})
    return JsonResponse({'count': 0, 'derniere': None})