from django.db import models
from comptes.models import Utilisateur
from materiel.models import Materiel


class Demande(models.Model):
    STATUTS = [
    ('en_attente', 'En attente'),
    ('approuvee', 'Approuvée'),
    ('refusee', 'Refusée'),
    ('en_cours', 'En cours'),
    ('en_attente_restitution', 'En attente de vérification'),
    ('restituee', 'Restituée'),
]
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='demandes'
    )
    date_demande = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    statut = models.CharField(max_length=30, choices=STATUTS, default='en_attente')
    motif = models.TextField(blank=True)

    def __str__(self):
        return f"Demande {self.id} - {self.utilisateur} - {self.statut}"

    def est_en_retard(self):
        from django.utils import timezone
        return self.date_fin < timezone.now().date() and self.statut == 'en_cours'

    def duree_emprunt(self):
        return (self.date_fin - self.date_debut).days


class LigneDemande(models.Model):
    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    materiel = models.ForeignKey(
        Materiel,
        on_delete=models.CASCADE,
        related_name='lignes_demande'
    )
    quantite = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.materiel} x{self.quantite}"


class Emplacement(models.Model):
    demande = models.OneToOneField(
        Demande,
        on_delete=models.CASCADE,
        related_name='emplacement'
    )
    libelle = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    adresse = models.TextField(blank=True)

    def __str__(self):
        return f"{self.libelle} ({self.latitude}, {self.longitude})"


class Restitution(models.Model):
    ETATS = [
        ('bon', 'Bon état'),
        ('abime', 'Abîmé'),
        ('perdu', 'Perdu'),
    ]
    demande = models.OneToOneField(
        Demande,
        on_delete=models.CASCADE,
        related_name='restitution'
    )
    date_retour = models.DateTimeField(auto_now_add=True)
    etat_materiel = models.CharField(max_length=20, choices=ETATS, default='bon')
    observations = models.TextField(blank=True)
    photo = models.ImageField(upload_to='restitutions/photos/', blank=True)

    def __str__(self):
        return f"Restitution demande {self.demande.id} - {self.etat_materiel}"
    
class ZoneAutorisee(models.Model):
    demande = models.OneToOneField(
        Demande,
        on_delete=models.CASCADE,
        related_name='zone_autorisee'
    )
    latitude_centre = models.FloatField()
    longitude_centre = models.FloatField()
    rayon_km = models.FloatField(default=50)  # rayon en km

    def __str__(self):
        return f"Zone demande #{self.demande.id} — rayon {self.rayon_km}km"    
    
class PositionTempsReel(models.Model):
    demande = models.ForeignKey(
        Demande,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Position {self.demande.id} — {self.date}"


class ZoneAutorisee(models.Model):
    demande = models.OneToOneField(
        Demande,
        on_delete=models.CASCADE,
        related_name='zone_autorisee'
    )
    latitude_centre = models.FloatField()
    longitude_centre = models.FloatField()
    rayon_km = models.FloatField(default=50)

    def __str__(self):
        return f"Zone demande #{self.demande.id} — rayon {self.rayon_km}km"