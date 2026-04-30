from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('tableau-de-bord/', views.tableau_de_bord, name='tableau_de_bord'),
    path('parametres/', views.parametres, name='parametres'),
    path('parametres/profil/', views.modifier_profil, name='modifier_profil'),
    path('parametres/mdp/', views.changer_mdp, name='changer_mdp'),
]