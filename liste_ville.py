import os
import csv

# Chemin du répertoire contenant les cartes HD
hdmaps_directory = r"C:\Program Files\CARLA_0.9.9.4\WindowsNoEditor\HDMaps"

# Vérifier si le répertoire existe
if not os.path.exists(hdmaps_directory):
    print(f"❌ Le répertoire {hdmaps_directory} n'existe pas.")
    exit()

# Lister les fichiers dans le répertoire
try:
    hdmaps_files = [f for f in os.listdir(hdmaps_directory) if f.endswith('.pcd')]
except Exception as e:
    print(f"❌ Erreur lors de la lecture du répertoire : {e}")
    exit()

# Vérifier si des fichiers ont été trouvés
if not hdmaps_files:
    print(f"❌ Aucun fichier .bin trouvé dans {hdmaps_directory}.")
    exit()

# Enregistrer les noms des fichiers dans un fichier CSV
csv_filename = "liste_villes.csv"

try:
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Nom Ville"])  # En-tête du fichier CSV
        for hdmap_file in hdmaps_files:
            writer.writerow([hdmap_file])
    print(f"✅ Liste des fichiers HDMap enregistrée dans {csv_filename}.")
except Exception as e:
    print(f"❌ Erreur lors de l'écriture du fichier CSV : {e}")