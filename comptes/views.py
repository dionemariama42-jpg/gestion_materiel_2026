from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur


def accueil(request):
    return render(request, 'comptes/accueil.html')


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} !')
            return redirect('tableau_de_bord')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'comptes/connexion.html')


def deconnexion(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('accueil')


def inscription(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        telephone = request.POST['telephone']
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        else:
            user = Utilisateur.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                telephone=telephone,
                role='etudiant'
            )
            login(request, user)
            messages.success(request, 'Compte créé avec succès !')
            return redirect('tableau_de_bord')
    return render(request, 'comptes/inscription.html')


@login_required
def tableau_de_bord(request):
    from emprunts.models import Demande
    demandes = Demande.objects.filter(utilisateur=request.user).order_by('-date_demande')
    contexte = {
        'demandes': demandes,
        'total_emprunts': demandes.count(),
        'en_cours': demandes.filter(statut='en_cours').count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
        'score': request.user.get_score_fiabilite(),
    }
    return render(request, 'comptes/tableau_de_bord.html', contexte)

@login_required
def parametres(request):
    return render(request, 'comptes/parametres.html')


@login_required
def modifier_profil(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.telephone = request.POST.get('telephone', '')
        request.user.save()
        messages.success(request, 'Profil mis à jour avec succès !')
    return redirect('parametres')


@login_required
def changer_mdp(request):
    if request.method == 'POST':
        mdp_actuel = request.POST.get('mdp_actuel')
        nouveau_mdp = request.POST.get('nouveau_mdp')
        confirmer_mdp = request.POST.get('confirmer_mdp')
        if not request.user.check_password(mdp_actuel):
            messages.error(request, 'Mot de passe actuel incorrect.')
        elif nouveau_mdp != confirmer_mdp:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        else:
            request.user.set_password(nouveau_mdp)
            request.user.save()
            messages.success(request, 'Mot de passe changé avec succès !')
    return redirect('parametres')