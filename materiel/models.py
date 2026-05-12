from django.db import models
import qrcode
import os
from io import BytesIO
from django.core.files import File


class Categorie(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.libelle


class Materiel(models.Model):
    ETATS = [
        ('disponible', 'Disponible'),
        ('emprunte', 'Emprunté'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
    ]
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name='materiels'
    )
    numero_serie = models.CharField(max_length=100, unique=True)
    etat = models.CharField(max_length=20, choices=ETATS, default='disponible')
    photo = models.ImageField(upload_to='materiels/photos/', blank=True)
    description = models.TextField(blank=True)
    date_acquisition = models.DateField(null=True, blank=True)
    code_qr = models.ImageField(upload_to='materiels/qrcodes/', blank=True)

    def __str__(self):
        return f"{self.nom} ({self.numero_serie})"

    def est_disponible(self):
        return self.etat == 'disponible'

    def generer_qr(self):
        qr = qrcode.make(f"http://127.0.0.1:8000/materiel/{self.id}/")
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        nom_fichier = f'qr_materiel_{self.id}.png'
        self.code_qr.save(nom_fichier, File(buffer), save=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.code_qr:
            self.generer_qr()
            super().save(update_fields=['code_qr'])


class Maintenance(models.Model):
    TYPES = [
        ('panne', 'Panne'),
        ('entretien', 'Entretien'),
        ('reparation', 'Réparation'),
    ]
    STATUTS = [
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('en_attente', 'En attente'),
    ]
    materiel = models.ForeignKey(
        Materiel,
        on_delete=models.CASCADE,
        related_name='maintenances'
    )
    type = models.CharField(max_length=20, choices=TYPES)
    date_signalement = models.DateField(auto_now_add=True)
    date_resolution = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.materiel} - {self.type} - {self.statut}"