from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur
import os


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
        role = request.POST.get('role', 'etudiant')
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validations de base
        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'comptes/inscription.html')

        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'comptes/inscription.html')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'comptes/inscription.html')

        # Créer l'utilisateur
        user = Utilisateur(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)

        # Champs selon le rôle
        if role == 'etudiant':
            user.filiere = request.POST.get('filiere', '').strip()
            user.niveau = request.POST.get('niveau', '')
            # Photo carte étudiant
            if 'carte_etudiant' in request.FILES:
                user.carte_etudiant = request.FILES['carte_etudiant']

        elif role == 'enseignant':
            user.departement = request.POST.get('departement', '').strip()
            user.fonction = request.POST.get('fonction', '')

        # Photo de profil (optionnelle pour tous)
        if 'photo_profil' in request.FILES:
            user.photo_profil = request.FILES['photo_profil']

        user.save()
        login(request, user)
        messages.success(request, f'Bienvenue {first_name} ! Votre compte a été créé avec succès.')
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

        # Champs étudiant
        if request.user.role == 'etudiant':
            request.user.filiere = request.POST.get('filiere', '')
            request.user.niveau = request.POST.get('niveau', '')

        # Champs enseignant
        if request.user.role == 'enseignant':
            request.user.departement = request.POST.get('departement', '')
            request.user.fonction = request.POST.get('fonction', '')

        # Photo de profil
        if 'photo_profil' in request.FILES:
            # Supprimer l'ancienne photo si elle existe
            if request.user.photo_profil:
                if os.path.isfile(request.user.photo_profil.path):
                    os.remove(request.user.photo_profil.path)
            request.user.photo_profil = request.FILES['photo_profil']

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
        elif len(nouveau_mdp) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        else:
            request.user.set_password(nouveau_mdp)
            request.user.save()
            messages.success(request, 'Mot de passe changé avec succès !')
    return redirect('parametres')