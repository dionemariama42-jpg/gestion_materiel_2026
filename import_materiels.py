import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from materiel.models import Materiel, Categorie

# Reset complet
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM emprunts_positiontempsreel")
    cursor.execute("DELETE FROM emprunts_restitution")
    cursor.execute("DELETE FROM emprunts_emplacement")
    cursor.execute("DELETE FROM emprunts_lignedemande")
    cursor.execute("DELETE FROM emprunts_demande")
    cursor.execute("DELETE FROM materiel_materiel")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='materiel_materiel'")

print("Suppression terminee.")

cat_gps, _ = Categorie.objects.get_or_create(libelle='GPS et GNSS', defaults={'description': 'Recepteurs GPS et GNSS'})
cat_station, _ = Categorie.objects.get_or_create(libelle='Stations totales', defaults={'description': 'Stations totales topographiques'})
cat_niveau, _ = Categorie.objects.get_or_create(libelle='Niveaux', defaults={'description': 'Niveaux optiques et numeriques'})
cat_accessoire, _ = Categorie.objects.get_or_create(libelle='Accessoires topo', defaults={'description': 'Accessoires topographiques'})
cat_communication, _ = Categorie.objects.get_or_create(libelle='Communication', defaults={'description': 'Materiel de communication'})
cat_informatique, _ = Categorie.objects.get_or_create(libelle='Informatique', defaults={'description': 'Materiel informatique'})
cat_geophysique, _ = Categorie.objects.get_or_create(libelle='Geophysique', defaults={'description': 'Materiel geophysique'})
cat_mobilier, _ = Categorie.objects.get_or_create(libelle='Mobilier', defaults={'description': 'Mobilier et equipement salle'})

materiels = [
    ('GPS differentiel i50', 'GPS-i50-001', cat_gps, 4, 'GPS differentiel i50 de precision avec batteries et accessoires complets'),
    ('GPS differentiel i73', 'GPS-i73-001', cat_gps, 5, 'GPS Differentiel i73 avec accessoires'),
    ('GPS de poche Garmin MAP 65S', 'GPS-G65-001', cat_gps, 40, 'Garmin MAPS 65S GPS en poche'),
    ('Station totale Leica', 'ST-LCA-001', cat_station, 8, 'Station totale non robotisee avec batteries et accessoires'),
    ('Station totale CTS-112 R4', 'ST-CTS-001', cat_station, 7, 'Station Total CTS-112 R4'),
    ('Station totale Geomesure', 'ST-GEO-001', cat_station, 1, 'Station totale laboratoire Geomesure'),
    ('Niveau electronique numerique', 'NIV-ELC-001', cat_niveau, 1, 'Niveau electronique avec trepied et mire code barre 4m'),
    ('Niveau optique de precision', 'NIV-OPT-001', cat_niveau, 9, 'Niveau optique de precision avec mire et trepied'),
    ('Mire telescopique aluminium 4m', 'MIRE-001', cat_accessoire, 9, 'Mire telescopique en aluminium de 4m'),
    ('Trepied aluminium', 'TREP-001', cat_accessoire, 42, 'Trepied en aluminium pour instruments topographiques'),
    ('Prisme Leica avec reflecteur', 'PRISME-001', cat_accessoire, 22, 'Prisme avec reflecteur pour station totale Leica'),
    ('Canne porte prisme Leica GLS11', 'CANNE-001', cat_accessoire, 2, 'Canne porte prisme Leica GLS 11'),
    ('Embase adaptateur antenne GS14', 'EMBASE-001', cat_accessoire, 15, 'Embase et adaptateur pour antenne GS14'),
    ('Batterie interne station totale', 'BAT-ST-001', cat_accessoire, 2, 'Batterie interne pour station totale Leica'),
    ('Batterie externe recepteur GS14', 'BAT-GPS-001', cat_accessoire, 9, 'Batterie externe pour recepteur GS14'),
    ('Chargeur batterie Leica GKL221', 'CHARG-001', cat_accessoire, 10, 'Chargeur de batterie Leica GKL221'),
    ('Talkie-Walkie', 'TW-001', cat_communication, 6, 'Paires de Talkie-Walkie pour communications terrain'),
    ('Videoprojecteur Epson', 'VP-001', cat_communication, 4, 'Videoprojecteur Epson CO W-01'),
    ('Microphone Logitech', 'MICRO-001', cat_communication, 2, 'Logitech GROUP camera de visioconference'),
    ('Resistivimetre ADEM TERRAMETER', 'RES-001', cat_geophysique, 1, 'Resistivimetre ADEM TERRAMETER LS'),
    ('Radar UNITI ESCAM', 'RADAR-001', cat_geophysique, 1, 'Radar UNITI ESCAM avec accessoires'),
    ('Conductivimetre EM31 MK2', 'COND-001', cat_geophysique, 1, 'Conductivimetre EM31 MK2 avec PC'),
    ('Magnetometre MN1', 'MAG-001', cat_geophysique, 1, 'Magnetometre MN1'),
    ('Sismographe 24 canaux', 'SISMO-001', cat_geophysique, 1, 'Sismographe a 24 canaux'),
    ('Tablette Galaxy', 'TAB-001', cat_informatique, 50, 'Tablettes Galaxy avec accessoires'),
    ('Ordinateur fixe Lenovo', 'PC-LEN-001', cat_informatique, 48, 'Ordinateur fixe Lenovo'),
    ('Ordinateur portable HP Core i5', 'PC-HP-001', cat_informatique, 4, 'Ordinateur Portable HP Core i5'),
    ('Chaise visiteur', 'CHR-001', cat_mobilier, 45, 'Chaise visiteur sans accoudoirs'),
    ('Chaise avec table rabat', 'CHR-TR-001', cat_mobilier, 10, 'Chaise bourree avec table rabat'),
    ('Table de reunion', 'TBL-001', cat_mobilier, 4, 'Table de reunion'),
]

total = 0
for nom, numero_serie, categorie, quantite, description in materiels:
    Materiel.objects.create(
        nom=nom,
        numero_serie=numero_serie,
        categorie=categorie,
        etat='disponible',
        description=description,
        quantite_stock=quantite,
        quantite_disponible=quantite
    )
    total += 1

print(f"Import termine ! {total} types de materiels ajoutes.")
print(f"Total en base : {Materiel.objects.count()}")