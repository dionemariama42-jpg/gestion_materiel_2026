from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_demandes, name='liste_demandes'),
    path('nouvelle/', views.nouvelle_demande, name='nouvelle_demande'),
    path('<int:pk>/', views.detail_demande, name='detail_demande'),
    path('<int:pk>/restituer/', views.restituer, name='restituer'),
    path('<int:pk>/confirmer-restitution/', views.confirmer_restitution, name='confirmer_restitution'),
    path('<int:pk>/suivi/', views.suivi_gps, name='suivi_gps'),
    path('<int:pk>/position/', views.envoyer_position, name='envoyer_position'),
    path('<int:pk>/positions/', views.get_positions, name='get_positions'),
    path('carte-admin/', views.carte_admin, name='carte_admin'),
    path('suivi-mobile/<int:pk>/', views.suivi_mobile, name='suivi_mobile'),
]