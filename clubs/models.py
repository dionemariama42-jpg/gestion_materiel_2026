from django.db import models
from comptes.models import Utilisateur


class Club(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='clubs/logos/', blank=True)
    date_creation = models.DateField(auto_now_add=True)
    materiel_propre = models.ManyToManyField(
        'materiel.Materiel',
        related_name='clubs_proprietaires',
        blank=True,
        verbose_name='Matériel propre au club'
    )
    cotisation_montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Montant cotisation (FCFA)'
    )

    def __str__(self):
        return self.nom

    def nombre_membres(self):
        return self.membres.count()

    def president(self):
        membre = self.membres.filter(role='president').first()
        return membre.utilisateur if membre else None

    def score_activite(self):
        return self.activites.filter(statut='terminee').count()


class MembreClub(models.Model):
    ROLES = [
        ('president', 'Président'),
        ('vice_president', 'Vice-Président'),
        ('secretaire', 'Secrétaire'),
        ('membre', 'Membre'),
    ]
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='membres'
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='appartenances_clubs'
    )
    role = models.CharField(max_length=20, choices=ROLES, default='membre')
    date_adhesion = models.DateField(auto_now_add=True)
    cotisation_payee = models.BooleanField(default=False)
    date_paiement = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('club', 'utilisateur')

    def __str__(self):
        return f"{self.utilisateur} — {self.club} ({self.role})"


class Activite(models.Model):
    TYPES = [
        ('conference', 'Conférence'),
        ('sortie', 'Sortie pédagogique'),
        ('jpo', 'Journée portes ouvertes'),
        ('atelier', 'Atelier'),
        ('cours', 'Cours / Formation'),
        ('competition', 'Compétition'),
        ('autre', 'Autre'),
    ]
    STATUTS = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='activites'
    )
    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField(blank=True)
    date = models.DateField()
    lieu = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifiee')
    demande = models.ForeignKey(
        'emprunts.Demande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activites'
    )
    seance = models.ForeignKey(
        'cahier.Seance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activites_clubs'
    )
    photo_principale = models.ImageField(
        upload_to='clubs/activites/',
        blank=True
    )
    programme = models.FileField(
        upload_to='clubs/programmes/',
        blank=True
    )

    def __str__(self):
        return f"{self.titre} — {self.club.nom}"


class PhotoActivite(models.Model):
    activite = models.ForeignKey(
        Activite,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo = models.ImageField(upload_to='clubs/galerie/')
    legende = models.CharField(max_length=200, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo — {self.activite.titre}"


class Notification(models.Model):
    destinataire = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    lu = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    lien = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Notif → {self.destinataire} — {self.message[:50]}"