from django.contrib import admin
from .models import Categorie, Materiel, Maintenance

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'description']
    search_fields = ['libelle']

@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ['nom', 'numero_serie', 'categorie', 'etat']
    list_filter = ['etat', 'categorie']
    search_fields = ['nom', 'numero_serie']

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['materiel', 'type', 'statut', 'date_signalement']
    list_filter = ['statut', 'type']
