from django.contrib import admin
from .models import Cours, Seance, FichierSeance

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau']
    search_fields = ['nom']

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ['cours', 'enseignant', 'date']
    list_filter = ['cours']
    search_fields = ['cours__nom']

@admin.register(FichierSeance)
class FichierSeanceAdmin(admin.ModelAdmin):
    list_display = ['nom_fichier', 'type', 'seance']
