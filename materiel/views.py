from django.shortcuts import render, get_object_or_404
from .models import Materiel, Categorie


def liste_materiels(request):
    materiels = Materiel.objects.all()
    categories = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    etat = request.GET.get('etat')
    if categorie_id:
        materiels = materiels.filter(categorie_id=categorie_id)
    if etat:
        materiels = materiels.filter(etat=etat)
    contexte = {
        'materiels': materiels,
        'categories': categories,
        'etat_filtre': etat,
    }
    return render(request, 'materiel/liste_materiels.html', contexte)


def detail_materiel(request, pk):
    materiel = get_object_or_404(Materiel, pk=pk)
    return render(request, 'materiel/detail_materiel.html', {'materiel': materiel})