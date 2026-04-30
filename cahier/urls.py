from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_cours, name='liste_cours'),
    path('<int:pk>/', views.detail_cours, name='detail_cours'),
    path('seance/nouvelle/', views.nouvelle_seance, name='nouvelle_seance'),
]