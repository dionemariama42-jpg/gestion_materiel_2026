from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('technicien', 'Technicien'),
        ('admin', 'Administrateur'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)
    filiere = models.CharField(max_length=100, blank=True)
    niveau = models.CharField(max_length=20, blank=True)
    penalite = models.IntegerField(default=0)
    bloque = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    def get_score_fiabilite(self):
        return max(0, 100 - (self.penalite * 10))


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