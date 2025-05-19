import carla
import time
import pygame
import random
import weakref
import numpy as np
import pandas as pd
from datetime import datetime
import threading
import sys
import os

# Charger les hauteurs des véhicules depuis le fichier CSV
csv_path = "CARLA_Vehicles_Available.csv"
df_vehicles = pd.read_csv(csv_path, delimiter=";", dtype=str)
df_vehicles["Height (mm)"] = pd.to_numeric(df_vehicles["Height (mm)"], errors="coerce")
df_vehicles["Height (m)"] = df_vehicles["Height (mm)"] / 1000

# Connexion au serveur CARLA
client = carla.Client('localhost', 2000)
client.set_timeout(80.0)

# Charger le monde (Ville choisie via interface)
if len(sys.argv) >= 2:
    town_name = sys.argv[1]  # Ville sélectionnée envoyée par l'interface
else:
    print("⚠️ Aucune ville spécifiée, utilisation par défaut: Town03")
    town_name = "Town03"

client.load_world(town_name)
world = client.get_world()

# Vérification de l'argument (Blueprint_ID)
if len(sys.argv) < 3:  # ✅ Vérifie si on a au moins 3 arguments (Ville + Véhicule)
    print("⚠️ Aucun véhicule spécifié, utilisation du modèle par défaut: Tesla Model 3")
    vehicle_model = "vehicle.tesla.model3"
else:
    vehicle_model = sys.argv[2]  # ✅ Maintenant, le véhicule est en `sys.argv[2]`

# Récupérer la hauteur du véhicule sélectionné
vehicle_height = df_vehicles.loc[df_vehicles["Blueprint_ID"] == vehicle_model, "Height (m)"].values
if len(vehicle_height) == 0:
    print(f"⚠️ Hauteur non trouvée pour {vehicle_model}, utilisation par défaut: 1.5m")
    vehicle_height = 1.5
else:
    vehicle_height = vehicle_height[0]

# Définir les hauteurs des capteurs
radar_height = vehicle_height + 0.1
lidar_height = vehicle_height + 0.2

# ✅ Vérification des arguments reçus
if len(sys.argv) >= 11:
    town_name = sys.argv[1]  # Ville sélectionnée
    vehicle_model = sys.argv[2]  # Modèle de véhicule sélectionné

    # ✅ Récupération des valeurs météo
    nuages = float(sys.argv[3])
    pluie = float(sys.argv[4])
    flaques = float(sys.argv[5])
    vent = float(sys.argv[6])
    brouillard = float(sys.argv[7])
    distance_brouillard = float(sys.argv[8])
    soleil = float(sys.argv[9])

    # ✅ Récupération du spawn index en **sys.argv[10]**
    spawn_index = int(sys.argv[10])

else:
    print("⚠️ Nombre d'arguments insuffisant, vérifiez l'appel depuis interface.py")
    sys.exit(1)

print(distance_brouillard)

# Appliquer les conditions météo dans CARLA
weather = carla.WeatherParameters(
    cloudiness=nuages,
    precipitation=pluie,
    precipitation_deposits=flaques,
    wind_intensity=vent,
    fog_density=brouillard,  # Gardé en pourcentage
    fog_distance=distance_brouillard,  # Gardé en mètres
    sun_altitude_angle=soleil  # Gardé en degrés
)

print(f"🌡️ Météo appliquée : {weather}")
# ✅ Vérifier la liste des spawn points disponibles
spawn_points = world.get_map().get_spawn_points()

if spawn_index < len(spawn_points):
    spawn_point = spawn_points[spawn_index]
else:
    print(f"⚠️ Spawn index {spawn_index} hors limite ({len(spawn_points)} disponibles), utilisation de l’index 0.")
    spawn_point = spawn_points[1]  # Sécurisation pour éviter un crash

# Obtenir la bibliothèque des plans et choisir un véhicule
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.find(vehicle_model)


# Faire apparaître le véhicule
vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
if vehicle is None:
    print(f"❌ Impossible de faire apparaître le véhicule {vehicle_model}")
    sys.exit(1)

world.set_weather(weather)
time.sleep(1)  # Attendre 1 seconde pour que CARLA applique bien la météo
world.tick()
applied_weather = world.get_weather()
print(f"🌡️ Météo appliquée après world.tick() : {vars(applied_weather)}")


print(f"🌥️ Météo appliquée : Nuages {nuages}%, Pluie {pluie}%, flaques {flaques},Vent {vent}%, Brouillard {brouillard}%, Distance Brouillard {distance_brouillard}m, Soleil {soleil}°")
# Debug pour vérifier la bonne récupération
print(f"🌍 Chargement de la ville : {town_name}")
print(f"🚗 Modèle de véhicule sélectionné : {vehicle_model}")


# Initialiser pygame
pygame.init()

# Définir la taille de la fenêtre
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("CARLA Autonomous Vehicle with Advanced HUD")

# Classe HUD pour afficher des informations avancées
class HUD:
    def __init__(self, width, height):
        self.dim = (width, height)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)
        self._font_mono = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.notification = ""
        self.notification_end = 0
        self.surface = pygame.Surface(self.dim, pygame.SRCALPHA)

    def set_notification(self, text, seconds=4.0):
        self.notification = text
        self.notification_end = time.time() + seconds

    def tick(self):
        current_time = time.time()
        if current_time > self.notification_end:
            self.notification = ""

    def render(self, display):
        self.surface.fill((0, 0, 0, 0))  # Utiliser la transparence pour éviter le clignotement
        if self.notification:
            notification_surface = self._font_mono.render(self.notification, True, (255, 255, 255))
            self.surface.blit(notification_surface, (10, 10))
        display.blit(self.surface, (0, 0))

    def render_weather_and_metrics(self, display, weather, speed, distance, ttc, stopping_distance):
        # Créer une surface pour le cadre à gauche
        info_surface = pygame.Surface((350, 450), pygame.SRCALPHA)  # Surface plus grande
        info_surface.fill((0, 0, 0, 200))  # Fond semi-transparent

        # Titre "Météo"
        title_meteo = self.font.render("Météo", True, (255, 255, 255))  # Texte blanc
        info_surface.blit(title_meteo, (10, 10))

        # Afficher les informations météo
        y_offset = 50  # Commencer après le titre
        weather_lines = [
            f"Vitesse: {speed:.2f} km/h",
            f"Nuages: {weather.cloudiness:.1f}%",
            f"Précipitation: {weather.precipitation:.1f}%",
            f"Précipitation Déposée: {weather.precipitation_deposits:.1f}%",
            f"Vent: {weather.wind_intensity:.1f}%",
            f"Altitude Soleil: {weather.sun_altitude_angle:.1f}",
            f"Densité Brouillard: {weather.fog_density:.1f}%",
            f"Distance Brouillard: {max(0, (1.0 - weather.fog_distance) * 100):.1f} m"
        ]
        for i, line in enumerate(weather_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))  # Blanc
            info_surface.blit(text_surface, (10, y_offset + i * 30))

        # Titre "Métriques"
        title_metriques = self.font.render("Métriques", True, (255, 255, 255))  # Texte blanc
        info_surface.blit(title_metriques, (10, y_offset + len(weather_lines) * 30 + 20))

        # Afficher les informations de distance, TTC et distance d'arrêt
        metrics_lines = [
            f"Distance: {distance:.2f} m",
            f"TTC: {ttc:.2f} s",
            f"Distance d'arrêt: {stopping_distance:.2f} m"
        ]
        for i, line in enumerate(metrics_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))  # Blanc
            info_surface.blit(text_surface, (10, y_offset + len(weather_lines) * 30 + 50 + i * 30))

        # Positionner la surface à gauche
        display.blit(info_surface, (10, 20))

# Fonction de callback pour recevoir et afficher l'image de la caméra
def process_image(image, screen):
    image.convert(carla.ColorConverter.Raw)
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = array.reshape((image.height, image.width, 4))  # Inclut l'alpha channel
    array = array[:, :, :3]  # Supprimer l'alpha channel
    surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    screen.blit(surface, (0, 0))

# Créer des DataFrames pour les données LiDAR, radar et météo
lidar_data_df = pd.DataFrame(columns=['x', 'y', 'z', 'intensity', 'timestamp'])
radar_data_df = pd.DataFrame(columns=['depth', 'velocity', 'azimuth', 'altitude', 'timestamp'])
meteo_data_df = pd.DataFrame(columns=['cloudiness', 'precipitation', 'wind_intensity', 'sun_azimuth', 'sun_altitude', 'speed', 'timestamp'])
lock = threading.Lock()


hud = HUD(width, height)

if vehicle is not None:
    # Activer l'autopilote
    traffic_manager = client.get_trafficmanager(8000)
    traffic_manager.set_global_distance_to_leading_vehicle(1.5)  # Réduire la distance entre les véhicules pour plus d'animation
    vehicle.set_autopilot(True, traffic_manager.get_port())
    traffic_manager.auto_lane_change(vehicle, True)  # Permettre le dépassement
    traffic_manager.vehicle_percentage_speed_difference(vehicle, random.uniform(0, 5))


    # Faire apparaître d'autres véhicules pour la circulation
    spawn_points_for_npc = world.get_map().get_spawn_points()
    for _ in range(10):  # Réduire le nombre de véhicules pour éviter les problèmes de performance
        npc_vehicle_bp = random.choice(blueprint_library.filter('vehicle.*'))
        npc_spawn_point = random.choice([point for point in spawn_points_for_npc if point.location.distance(spawn_point.location) < 100])
        npc_vehicle = world.try_spawn_actor(npc_vehicle_bp, npc_spawn_point)
        if npc_vehicle:
            npc_vehicle.set_autopilot(True, traffic_manager.get_port())
            traffic_manager.vehicle_percentage_speed_difference(npc_vehicle, random.uniform(0, 5))
            npc_vehicle.set_light_state(carla.VehicleLightState(carla.VehicleLightState.All))  # Activer les feux des véhicules
            traffic_manager.set_global_distance_to_leading_vehicle(1.5)  # Réduire la distance entre les véhicules pour plus d'animation
            traffic_manager.ignore_lights_percentage(npc_vehicle, 0)  # Respecter les feux
            traffic_manager.auto_lane_change(vehicle, True)  # Permettre le dépassement
            traffic_manager.ignore_signs_percentage(npc_vehicle, 0)  # Respecter les panneaux
            traffic_manager.ignore_walkers_percentage(npc_vehicle, 0)  # Éviter les piétons
            traffic_manager.ignore_vehicles_percentage(npc_vehicle, 0)  # Prendre en compte les autres véhicule

    # Ajouter un capteur LiDAR au véhicule
    lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
    lidar_bp.set_attribute('range', '50')
    lidar_bp.set_attribute('rotation_frequency', '10')
    lidar_bp.set_attribute('channels', '32')
    lidar_bp.set_attribute('points_per_second', '56000')

    lidar_transform = carla.Transform(carla.Location(x=0, z=lidar_height))
    lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

    # Ajouter un capteur Radar au véhicule
    radar_bp = blueprint_library.find('sensor.other.radar')
    radar_bp.set_attribute('horizontal_fov', '30')
    radar_bp.set_attribute('vertical_fov', '10')
    radar_bp.set_attribute('range', '20')
    radar_transform = carla.Transform(carla.Location(x=0, z=radar_height))
    radar = world.spawn_actor(radar_bp, radar_transform, attach_to=vehicle)

    # Fonction pour traiter et enregistrer les données LiDAR
    def process_lidar(lidar_data):
        points = np.frombuffer(lidar_data.raw_data, dtype=np.float32)

        # ✅ Vérifier que la taille est bien un multiple de 4
        if points.size % 4 != 0:
            points = points[:-(points.size % 4)]  # Ajuster pour éviter les erreurs de reshape

        points = points.reshape((-1, 4))  # x, y, z, intensity
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        # ✅ Filtrage correct
        filtered_points = points[(points[:, 2] + lidar_height >= -1) & (points[:, 2] <= 1.5)]

        with lock:
            with open('lidar_data.csv', 'a') as f:
                if f.tell() == 0:
                    f.write('x,y,z,intensity,timestamp\n')
                for point in filtered_points:
                    f.write(f"{point[0]:.2f},{point[1]:.2f},{point[2]:.2f},{point[3]:.2f},{current_time}\n")


    # Fonction pour traiter et enregistrer les données Radar
    # Fonction pour traiter et enregistrer les données Radar
    def process_radar(radar_data):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with lock:
            with open('radar_data.csv', 'a') as f:
                if f.tell() == 0:
                    f.write('depth,velocity,azimuth,altitude,timestamp\n')
                for detection in radar_data:
                    f.write(f"{detection.depth},{detection.velocity},{detection.azimuth},{detection.altitude},{current_time}\n")


    # Fonction pour enregistrer les données météo
    def log_weather():
        world.set_weather(weather)
        current_weather = world.get_weather()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        vehicle_speed = vehicle.get_velocity()
        # Convertir la vitesse en km/h
        speed = 3.6 * np.linalg.norm([vehicle_speed.x, vehicle_speed.y, vehicle_speed.z])

        # ✅ Stocker directement la valeur envoyée à `set_weather()`
        if current_weather.fog_distance is not None:
            recorded_fog_distance = (1.0 - current_weather.fog_distance) * 100  # Conversion en mètres
            recorded_fog_distance = max(0, recorded_fog_distance)  # Éviter les valeurs négatives
        else:
            recorded_fog_distance = 0  # Valeur par défaut si non définie
        print(f"🌡️ Météo actuelle : {current_weather}")
        print(f"📡 Enregistrement fog_distance : {recorded_fog_distance} mètres (valeur réellement envoyée)")


        # Vérifier que toutes les valeurs existent
        weather_data = [
            current_weather.cloudiness if current_weather.cloudiness is not None else 0,
            current_weather.precipitation if current_weather.precipitation is not None else 0,
            current_weather.precipitation_deposits if current_weather.precipitation_deposits is not None else 0,
            current_weather.wind_intensity if current_weather.wind_intensity is not None else 0,
            current_weather.sun_azimuth_angle if current_weather.sun_azimuth_angle is not None else 0,
            current_weather.sun_altitude_angle if current_weather.sun_altitude_angle is not None else 0,
            current_weather.fog_density if current_weather.fog_density is not None else 0,
            recorded_fog_distance,
            speed if not np.isnan(speed) else 0,  # Gérer le cas où la vitesse est NaN
            current_time
        ]

        # Vérifier si le fichier existe et ajouter l'entête si besoin
        with lock:
            with open('meteo_data.csv', 'a') as f:
                if f.tell() == 0:
                    f.write(
                        'cloudiness,precipitation,precipitation_deposits,wind_intensity,sun_azimuth,sun_altitude,fog_density,fog_distance,speed,timestamp\n')
                f.write(','.join(map(str, weather_data)) + '\n')

        print(f"📡 Données météo enregistrées : {weather_data}")


    # Attacher les capteurs et enregistrer les données
    lidar.listen(lambda lidar_data: process_lidar(lidar_data))
    radar.listen(lambda radar_data: process_radar(radar_data))

    # Ajouter une caméra au véhicule
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', f'{width}')
    camera_bp.set_attribute('image_size_y', f'{height}')
    camera_bp.set_attribute('fov', '110')
    camera_transform = carla.Transform(carla.Location(x=-10, y=0, z=5), carla.Rotation(pitch=-15))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    last_weather_log_time = 0


    def detect_vehicle_ahead():
        vehicles = world.get_actors().filter('vehicle.*')  # Récupérer tous les véhicules

        min_distance = float('inf')
        found_vehicle = None
        found_vehicle_speed = None
        ttc = float('inf')  # Initialiser le TTC à l'infini

        # Récupérer la vitesse de votre véhicule
        my_velocity = vehicle.get_velocity()
        my_speed = 3.6 * np.linalg.norm([my_velocity.x, my_velocity.y, my_velocity.z])  # Convertir en km/h

        for v in vehicles:
            if v.id == vehicle.id:  # Ignorer notre propre véhicule
                continue

            # Calculer la distance entre notre véhicule et l'autre
            distance = vehicle.get_location().distance(v.get_location())

            if 0 < distance < 20:  # Garder uniquement les véhicules entre 3m et 20m
                # Vérifier que le véhicule va dans le même sens
                my_forward_vector = vehicle.get_transform().get_forward_vector()
                other_forward_vector = v.get_transform().get_forward_vector()

                # Produit scalaire entre les vecteurs de direction
                dot_product = my_forward_vector.x * other_forward_vector.x + my_forward_vector.y * other_forward_vector.y

                if dot_product > 0.5:  # Si le produit scalaire est positif, les véhicules vont dans le même sens
                    if distance < min_distance:
                        min_distance = distance
                        found_vehicle = v
                        # Récupérer la vitesse du véhicule détecté
                        found_vehicle_velocity = v.get_velocity()
                        # Convertir la vitesse en km/h (1 m/s = 3.6 km/h)
                        found_vehicle_speed = 3.6 * np.linalg.norm(
                            [found_vehicle_velocity.x, found_vehicle_velocity.y, found_vehicle_velocity.z])

                        # Calculer la vitesse relative (en m/s)
                        relative_speed = (my_speed - found_vehicle_speed) / 3.6  # Convertir en m/s

                        # Calculer le TTC (en secondes)
                        if relative_speed > 0:  # Éviter la division par zéro ou les valeurs négatives
                            ttc = distance / relative_speed
                        else:
                            ttc = float(
                                'inf')  # Pas de risque de collision si la vitesse relative est nulle ou négative

        if found_vehicle:
            print(
                f"🚗 Véhicule détecté DEVANT à {min_distance:.2f}m (même direction), vitesse: {found_vehicle_speed:.2f} km/h")
            print(f"⏱️ Time to Collision (TTC): {ttc:.2f} secondes")
        else:
            print("✅ Aucun véhicule devant dans le même sens.")

        return found_vehicle is not None, found_vehicle_speed, ttc, found_vehicle  # Retourner également le véhicule détecté


    if camera is not None:
        try:
            weak_self = weakref.ref(screen)
            camera.listen(lambda image: process_image(image, weak_self()))

            # Supprimer le fichier d'arrêt s'il existe
            if os.path.exists("stop_simulation.txt"):
                os.remove("stop_simulation.txt")


            # Lancer la boucle principale
            clock = pygame.time.Clock()
            while True:

                # Détecter les véhicules devant
                vehicle_detected, vehicle_speed, ttc, found_vehicle = detect_vehicle_ahead()
                if vehicle_detected:
                    print("⚠️ Véhicule détecté dans la même direction !")
                    distance = vehicle.get_location().distance(found_vehicle.get_location())  # Distance avec le véhicule détecté
                else:
                    print("✅ Aucun véhicule détecté.")
                    distance = float('inf')  # Aucun véhicule détecté, distance infinie
                    ttc = float('inf')  # Aucun véhicule détecté, TTC infini



                if detect_vehicle_ahead():
                    print("⚠️ Véhicule détecté dans la même direction !")

                # Vérifier si un signal d'arrêt a été envoyé
                if os.path.exists("stop_simulation.txt"):
                    print("🛑 Signal d'arrêt détecté, arrêt de la simulation...")
                    break  # Quitter la boucle principale
                # Gérer les événements pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            # Modifier la météo au hasard lorsque 'w' est pressé
                            weather_presets = [
                                carla.WeatherParameters.ClearNoon,
                                carla.WeatherParameters.CloudyNoon,
                                carla.WeatherParameters.WetNoon,
                                carla.WeatherParameters.WetCloudyNoon,
                                carla.WeatherParameters.MidRainyNoon,
                                carla.WeatherParameters.HardRainNoon,
                                carla.WeatherParameters.SoftRainNoon
                            ]
                            new_weather = random.choice(weather_presets)
                            world.set_weather(new_weather)
                            hud.set_notification(f"Météo définie sur: {new_weather}")

                # Enregistrer les données météo toutes les 5 secondes
                current_time = time.time()
                if current_time - last_weather_log_time >= 2:
                    log_weather()
                    last_weather_log_time = current_time

                # Obtenir la vitesse actuelle et les paramètres météo
                vehicle_speed = vehicle.get_velocity()
                speed = 3.6 * np.linalg.norm([vehicle_speed.x, vehicle_speed.y, vehicle_speed.z])
                current_weather = world.get_weather()

                # Convertir la vitesse en m/s pour le calcul de la distance d'arrêt
                speed_mps = speed / 3.6

                # Temps de réaction (1 seconde par défaut)
                reaction_time = 1.0  # en secondes

                # Décélération (6 m/s² pour un freinage normal)
                deceleration = 6.0  # en m/s²

                # Calculer la distance d'arrêt
                reaction_distance = speed_mps * reaction_time
                braking_distance = (speed_mps ** 2) / (2 * deceleration)
                stopping_distance = reaction_distance + braking_distance

                # Dans la boucle principale
                hud.render_weather_and_metrics(screen, current_weather, speed, distance, ttc, stopping_distance)

                # Mettre à jour l'affichage du HUD
                hud.tick()
                hud.render(screen)
                pygame.display.update()

                clock.tick(30)
        except KeyboardInterrupt:
            print("Arrêt de la simulation...")
        finally:
            # Nettoyer et détruire les acteurs
            print("Nettoyage en cours...")
            if lidar is not None and lidar.is_alive:
                lidar.destroy()
            if radar is not None and radar.is_alive:
                radar.destroy()
            if camera is not None and camera.is_alive:
                camera.destroy()
            if vehicle is not None and vehicle.is_alive:
                vehicle.destroy()
else:
    print("Échec de l'apparition du véhicule.")

pygame.quit()