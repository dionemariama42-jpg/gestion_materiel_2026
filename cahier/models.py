from django.db import models
from comptes.models import Utilisateur


class Cours(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    niveau = models.CharField(max_length=50, blank=True)
    volume_horaire = models.IntegerField(default=0, verbose_name='Volume horaire prévu (h)')
    enseignant = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cours_assignes',
        limit_choices_to={'role': 'enseignant'}
    )

    def __str__(self):
        return self.nom

    def heures_effectuees(self):
        total = sum([s.duree for s in self.seances.filter(valide=True)])
        return round(total, 1)

    def heures_restantes(self):
        return max(0, self.volume_horaire - self.heures_effectuees())

    def taux_avancement(self):
        if self.volume_horaire == 0:
            return 0
        return min(100, round(self.heures_effectuees() / self.volume_horaire * 100))


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
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    duree = models.FloatField(default=0, verbose_name='Durée (heures)')
    contenu = models.TextField(blank=True)
    valide = models.BooleanField(default=False, verbose_name='Validée par le chef')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    demande = models.ForeignKey(
        'emprunts.Demande',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='seances'
    )

    class Meta:
        ordering = ['-date', '-heure_debut']

    def __str__(self):
        return f"{self.cours} — {self.date}"


class Absence(models.Model):
    seance = models.ForeignKey(
        Seance,
        on_delete=models.CASCADE,
        related_name='absences'
    )
    etudiant = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='absences'
    )
    justifie = models.BooleanField(default=False)
    motif = models.TextField(blank=True)

    class Meta:
        unique_together = ('seance', 'etudiant')

    def __str__(self):
        return f"Absence {self.etudiant} — {self.seance}"


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