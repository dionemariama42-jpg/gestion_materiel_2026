from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Log

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'bloque']
    list_filter = ['role', 'bloque']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations UFR', {
            'fields': ('role', 'telephone', 'filiere', 'niveau', 'penalite', 'bloque')
        }),
    )

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'action', 'date']