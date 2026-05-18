from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Materiel, Categorie


def liste_materiels(request):
    materiels = Materiel.objects.all()
    categories = Categorie.objects.all()

    # Filtrer par domaine selon le rôle
    if request.user.is_authenticated:
        if request.user.role == 'admin_terrain':
            materiels = materiels.filter(domaine='terrain')
            categories = categories.filter(materiels__domaine='terrain').distinct()
        elif request.user.role == 'admin_bureau':
            materiels = materiels.filter(domaine='bureau')
            categories = categories.filter(materiels__domaine='bureau').distinct()

    # Filtres supplémentaires
    categorie_id = request.GET.get('categorie')
    etat = request.GET.get('etat')
    domaine = request.GET.get('domaine')

    if categorie_id:
        materiels = materiels.filter(categorie_id=categorie_id)
    if etat:
        materiels = materiels.filter(etat=etat)
    if domaine and request.user.is_authenticated and request.user.role == 'admin':
        materiels = materiels.filter(domaine=domaine)

    contexte = {
        'materiels': materiels,
        'categories': categories,
        'etat_filtre': etat,
        'domaine_filtre': domaine,
    }
    return render(request, 'materiel/liste_materiels.html', contexte)


def detail_materiel(request, pk):
    materiel = get_object_or_404(Materiel, pk=pk)

    # Vérifier que l'admin accède uniquement à son domaine
    if request.user.is_authenticated:
        if request.user.role == 'admin_terrain' and materiel.domaine != 'terrain':
            messages.error(request, "Vous n'avez pas accès à ce matériel.")
            return redirect('liste_materiels')
        elif request.user.role == 'admin_bureau' and materiel.domaine != 'bureau':
            messages.error(request, "Vous n'avez pas accès à ce matériel.")
            return redirect('liste_materiels')

    return render(request, 'materiel/detail_materiel.html', {'materiel': materiel})