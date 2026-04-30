from django.db import models
from comptes.models import Utilisateur
from emprunts.models import Demande


class Cours(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    niveau = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nom


class Seance(models.Model):
    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name='seances'
    )
    enseignant = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seances'
    )
    date = models.DateField()
    contenu = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    demande = models.ForeignKey(
        Demande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seances'
    )

    def __str__(self):
        return f"{self.cours} - {self.date}"


class FichierSeance(models.Model):
    seance = models.ForeignKey(
        Seance,
        on_delete=models.CASCADE,
        related_name='fichiers'
    )
    nom_fichier = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    fichier = models.FileField(upload_to='cahier/fichiers/')

    def __str__(self):
        return self.nom_fichier
