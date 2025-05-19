import carla
import pandas as pd

# Connexion au serveur CARLA
client = carla.Client('localhost', 2000)
client.set_timeout(80.0)

# Obtenir la bibliothèque des blueprints de véhicules
world = client.get_world()
blueprint_library = world.get_blueprint_library()

# Récupérer tous les blueprint_id disponibles dans CARLA
available_blueprints = {blueprint.id for blueprint in blueprint_library.filter("vehicle.*")}

# Charger ton fichier CSV avec les véhicules
csv_path = "CARLA_Vehicles1.csv"
df = pd.read_csv(csv_path, delimiter=";", dtype=str)

# Filtrer les véhicules dont le blueprint_id est disponible dans CARLA
df_filtered = df[df["Blueprint_ID"].isin(available_blueprints)]

# Enregistrer le nouveau fichier CSV avec les véhicules disponibles dans CARLA
output_path = "CARLA_Vehicles_Available.csv"
df_filtered.to_csv(output_path, index=False, sep=";")

print(f"✅ Fichier filtré enregistré dans '{output_path}'")
