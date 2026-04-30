from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_clubs, name='liste_clubs'),
    path('<int:pk>/', views.detail_club, name='detail_club'),
    path('<int:pk>/rejoindre/', views.rejoindre_club, name='rejoindre_club'),
    path('<int:pk>/cotisation/', views.payer_cotisation, name='payer_cotisation'),
    path('activite/nouvelle/', views.nouvelle_activite, name='nouvelle_activite'),
    path('activite/<int:pk>/', views.detail_activite, name='detail_activite'),
    path('activite/<int:pk>/photos/', views.ajouter_photos, name='ajouter_photos'),
    path('notifications/', views.mes_notifications, name='mes_notifications'),
    path('notifications/count/', views.count_notifications, name='count_notifications'),
    path('classement/', views.classement_clubs, name='classement_clubs'),
]