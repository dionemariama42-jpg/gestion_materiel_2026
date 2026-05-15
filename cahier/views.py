from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import calendar
import datetime
from .models import Cours, Seance, FichierSeance, Evenement


def liste_cours(request):
    cours = Cours.objects.all()
    return render(request, 'cahier/liste_cours.html', {'cours': cours})


def detail_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    seances = cours.seances.all().order_by('-date')
    return render(request, 'cahier/detail_cours.html', {
        'cours': cours,
        'seances': seances
    })


@login_required
def nouvelle_seance(request):
    cours_list = Cours.objects.all()
    if request.method == 'POST':
        cours_id = request.POST['cours']
        date = request.POST['date']
        contenu = request.POST['contenu']
        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        cours = Cours.objects.get(id=cours_id)
        seance = Seance.objects.create(
            cours=cours,
            enseignant=request.user,
            date=date,
            contenu=contenu,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
        )
        fichiers = request.FILES.getlist('fichiers')
        for fichier in fichiers:
            FichierSeance.objects.create(
                seance=seance,
                nom_fichier=fichier.name,
                type=fichier.content_type,
                fichier=fichier,
            )
        messages.success(request, 'Séance ajoutée avec succès !')
        return redirect('detail_cours', pk=cours.id)
    return render(request, 'cahier/nouvelle_seance.html', {'cours_list': cours_list})


# ============================================================
# CALENDRIER
# ============================================================

def calendrier(request):
    aujourd_hui = timezone.now().date()
    annee = int(request.GET.get('annee', aujourd_hui.year))
    mois = int(request.GET.get('mois', aujourd_hui.month))

    if mois == 1:
        mois_precedent, annee_precedente = 12, annee - 1
    else:
        mois_precedent, annee_precedente = mois - 1, annee

    if mois == 12:
        mois_suivant, annee_suivante = 1, annee + 1
    else:
        mois_suivant, annee_suivante = mois + 1, annee

    debut_mois = datetime.date(annee, mois, 1)
    fin_mois = datetime.date(annee, mois, calendar.monthrange(annee, mois)[1])

    evenements_mois = Evenement.objects.filter(
        date_debut__lte=fin_mois,
        date_fin__gte=debut_mois
    ).select_related('organisateur', 'demande').order_by('date_debut', 'heure_debut')

    evenements_par_jour = {}
    for evt in evenements_mois:
        date_courante = evt.date_debut
        while date_courante <= evt.date_fin and date_courante <= fin_mois:
            if date_courante >= debut_mois:
                jour = date_courante.day
                if jour not in evenements_par_jour:
                    evenements_par_jour[jour] = []
                evenements_par_jour[jour].append(evt)
            date_courante += datetime.timedelta(days=1)

    cal_brut = calendar.monthcalendar(annee, mois)
    grille = []
    for semaine in cal_brut:
        semaine_data = []
        for jour in semaine:
            if jour == 0:
                semaine_data.append({'jour': 0, 'evenements': [], 'est_aujourd_hui': False, 'date_str': ''})
            else:
                semaine_data.append({
                    'jour': jour,
                    'evenements': evenements_par_jour.get(jour, []),
                    'est_aujourd_hui': (jour == aujourd_hui.day and mois == aujourd_hui.month and annee == aujourd_hui.year),
                    'date_str': f"{annee}-{mois:02d}-{jour:02d}",
                })
        grille.append(semaine_data)

    debut_semaine = aujourd_hui - datetime.timedelta(days=aujourd_hui.weekday())
    fin_semaine = debut_semaine + datetime.timedelta(days=6)
    evenements_semaine = Evenement.objects.filter(
        date_debut__lte=fin_semaine,
        date_fin__gte=debut_semaine
    ).select_related('organisateur', 'demande').order_by('date_debut', 'heure_debut')

    prochains = Evenement.objects.filter(
        date_debut__gte=aujourd_hui,
        date_debut__lte=aujourd_hui + datetime.timedelta(days=30),
        statut__in=['planifie', 'confirme']
    ).select_related('organisateur', 'demande')[:8]

    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

    contexte = {
        'grille': grille,
        'annee': annee,
        'mois': mois,
        'mois_nom': mois_noms[mois],
        'mois_precedent': mois_precedent,
        'annee_precedente': annee_precedente,
        'mois_suivant': mois_suivant,
        'annee_suivante': annee_suivante,
        'evenements_semaine': evenements_semaine,
        'prochains': prochains,
        'aujourd_hui': aujourd_hui,
        'jours_semaine': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        'peut_creer': request.user.is_authenticated and request.user.role in ['enseignant', 'admin'],
    }
    return render(request, 'cahier/calendrier.html', contexte)

@login_required
def nouvel_evenement(request):
    from emprunts.models import Demande
    from materiel.models import Materiel

    cours_list = Cours.objects.all()
    materiels = Materiel.objects.filter(disponible=True)
    date_selectionnee = request.GET.get('date', '')

    if request.method == 'POST':
        # Vérifier les droits
        if request.user.role not in ['enseignant', 'admin']:
            messages.error(request, 'Vous n\'avez pas les droits pour créer un événement.')
            return redirect('calendrier')

        titre = request.POST.get('titre', '').strip()
        type_evt = request.POST.get('type', 'autre')
        description = request.POST.get('description', '')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin', date_debut)
        heure_debut = request.POST.get('heure_debut') or None
        heure_fin = request.POST.get('heure_fin') or None
        lieu = request.POST.get('lieu', '')
        cours_id = request.POST.get('cours') or None

        if not titre or not date_debut:
            messages.error(request, 'Le titre et la date sont obligatoires.')
            return render(request, 'cahier/nouvel_evenement.html', {
                'cours_list': cours_list,
                'materiels': materiels,
                'date_selectionnee': date_selectionnee,
            })

        # Créer l'événement
        evt = Evenement(
            titre=titre,
            type=type_evt,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            lieu=lieu,
            organisateur=request.user,
            cours_id=cours_id,
        )

        # Demande de matériel associée
        materiels_ids = request.POST.getlist('materiels')
        if materiels_ids:
            demande = Demande.objects.create(
                utilisateur=request.user,
                date_debut=datetime.datetime.strptime(date_debut, '%Y-%m-%d'),
                date_fin=datetime.datetime.strptime(date_fin, '%Y-%m-%d'),
                motif=f"Matériel pour : {titre}",
                statut='en_attente',
            )
            from emprunts.models import LigneDemande
            for mat_id in materiels_ids:
                quantite = int(request.POST.get(f'quantite_{mat_id}', 1))
                LigneDemande.objects.create(
                    demande=demande,
                    materiel_id=mat_id,
                    quantite=quantite,
                )
            evt.demande = demande
            messages.info(request, 'Une demande de matériel a été créée et est en attente d\'approbation.')

        evt.save()
        messages.success(request, f'Événement "{titre}" créé avec succès !')
        return redirect('calendrier')

    return render(request, 'cahier/nouvel_evenement.html', {
        'cours_list': cours_list,
        'materiels': materiels,
        'date_selectionnee': date_selectionnee,
    })


def detail_evenement(request, pk):
    evt = get_object_or_404(Evenement, pk=pk)
    return render(request, 'cahier/detail_evenement.html', {'evt': evt})


@login_required
def supprimer_evenement(request, pk):
    evt = get_object_or_404(Evenement, pk=pk)
    if request.user == evt.organisateur or request.user.role == 'admin':
        evt.delete()
        messages.success(request, 'Événement supprimé.')
    else:
        messages.error(request, 'Vous ne pouvez pas supprimer cet événement.')
    return redirect('calendrier')


# API JSON pour le calendrier (utilisé par JavaScript)
def api_evenements(request):
    annee = int(request.GET.get('annee', timezone.now().year))
    mois = int(request.GET.get('mois', timezone.now().month))
    debut_mois = datetime.date(annee, mois, 1)
    fin_mois = datetime.date(annee, mois, calendar.monthrange(annee, mois)[1])

    evenements = Evenement.objects.filter(
        date_debut__lte=fin_mois,
        date_fin__gte=debut_mois
    ).select_related('organisateur', 'demande')

    data = []
    for evt in evenements:
        data.append({
            'id': evt.id,
            'titre': evt.titre,
            'type': evt.type,
            'statut': evt.statut,
            'date_debut': str(evt.date_debut),
            'date_fin': str(evt.date_fin),
            'heure_debut': str(evt.heure_debut) if evt.heure_debut else '',
            'lieu': evt.lieu,
            'couleur': evt.couleur(),
            'organisateur': evt.organisateur.get_full_name(),
            'a_materiel': evt.demande is not None,
        })
    return JsonResponse({'evenements': data})