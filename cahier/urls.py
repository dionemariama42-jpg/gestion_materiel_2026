from django.urls import path
from . import views

urlpatterns = [
    path('calendrier/', views.calendrier, name='calendrier'),
    path('calendrier/evenement/nouveau/', views.nouvel_evenement, name='nouvel_evenement'),
    path('calendrier/evenement/<int:pk>/', views.detail_evenement, name='detail_evenement'),
    path('calendrier/evenement/<int:pk>/supprimer/', views.supprimer_evenement, name='supprimer_evenement'),
    path('calendrier/api/', views.api_evenements, name='api_evenements'),
]