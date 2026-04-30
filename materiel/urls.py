from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_materiels, name='liste_materiels'),
    path('<int:pk>/', views.detail_materiel, name='detail_materiel'),
]