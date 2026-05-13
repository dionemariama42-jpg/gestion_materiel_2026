from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):
    ROLES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('technicien', 'Technicien'),
        ('admin', 'Administrateur'),
    ]

    NIVEAUX = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('D', 'Doctorat'),
    ]

    FONCTIONS = [
        ('professeur', 'Professeur'),
        ('maitre_assistant', 'Maître Assistant'),
        ('maitre_conference', 'Maître de Conférences'),
        ('vacataire', 'Vacataire'),
        ('chef_departement', 'Chef de Département'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)

    # Photo de profil (tous les utilisateurs)
    photo_profil = models.ImageField(
        upload_to='profils/', blank=True, null=True
    )

    # Champs étudiant
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=10, choices=NIVEAUX, blank=True)
    carte_etudiant = models.ImageField(
        upload_to='cartes_etudiants/', blank=True, null=True
    )

    # Champs enseignant
    departement = models.CharField(max_length=100, blank=True)
    fonction = models.CharField(max_length=30, choices=FONCTIONS, blank=True)

    # Pénalités
    penalite = models.IntegerField(default=0)
    bloque = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    def get_score_fiabilite(self):
        return max(0, 100 - (self.penalite * 10))

    def get_photo_profil_url(self):
        if self.photo_profil:
            return self.photo_profil.url
        return None


class Log(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.action} - {self.date}"