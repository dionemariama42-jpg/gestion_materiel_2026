from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, Seance, FichierSeance


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