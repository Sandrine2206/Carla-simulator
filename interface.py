import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import pandas as pd
import subprocess
import sys

# Charger la liste des villes depuis le fichier CSV
csv_villes_path = "liste_villes.csv"

try:
    df_villes = pd.read_csv(csv_villes_path, delimiter=";", dtype=str)
    villes = df_villes["Nom Ville"].tolist()  # Extrait uniquement les noms courts des villes (ex: Town01, Town02)
except FileNotFoundError:
    print("⚠️ Le fichier 'liste_villes.csv' est introuvable. Vérifiez son emplacement.")
    villes = ["Town01", "Town02", "Town03", "Town04"]  # Valeurs par défaut si le fichier est absent


# Charger la liste des véhicules depuis le fichier CSV
csv_path = "CARLA_Vehicles_Available.csv"
df = pd.read_csv(csv_path, delimiter=";", dtype=str)
df = df[df["Type"] == "Car"]
df = df.dropna(subset=["Blueprint_ID"])
df["Model"] = df["Brand"] + " " + df["Model"]  # Fusionner marque et modèle
vehicles = df[["Model", "Blueprint_ID"]].drop_duplicates().values.tolist()

# Création de la fenêtre principale
root = tk.Tk()
root.title("ESME3TD2025CARLA - SIPOSA - Interface de lancement")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")


# Canvas pour gérer l'image de fond
canvas = tk.Canvas(root, highlightthickness=0, width=1720, height=900)
canvas.place(x=0, y=0)

# **Chargement de l'image de fond (commenté)**

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "image.png")
bg_photo = None
try:
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((1720, 900), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)
except Exception as e:
    print("Erreur lors du chargement de l'image :", e)
    root.configure(bg="gray")

# **Sélection du véhicule**
selected_vehicle = tk.StringVar()
selected_vehicle.set(vehicles[0][0])  # Valeur par défaut


# **Fonction pour lancer la simulation**
def lancer_simulation():
    blueprint_id = next((bp for model, bp in vehicles if model == selected_vehicle.get()), vehicles[0][1])

    # ✅ Récupérer la ville sélectionnée
    selected_map = selected_ville.get()

    spawn_index = validate_spawn()  # Récupérer le spawn sélectionné

    # ✅ Appliquer les valeurs météo du scénario sélectionné
    update_weather_scenario()
    # Récupérer les valeurs météo des curseurs
    meteo_values = {condition: sliders[condition].get() for condition in conditions_meteo}

    # Convertir les valeurs en arguments pour `code_final.py`
    meteo_args = [str(meteo_values[condition]) for condition in conditions_meteo]

    # Debug : Vérifier les valeurs envoyées
    print(f"🚀 Lancement avec ville '{selected_map}', météo : {meteo_values}, spawn {spawn_index}")

    # Utiliser l'interpréteur Python actuel
    python_exec = sys.executable

    print(
        f"🚀 Commande exécutée : {python_exec} code_final.py {selected_map} {blueprint_id} {' '.join(meteo_args)} {spawn_index}")

    # Exécuter `code_final.py` avec les paramètres météo
    subprocess.Popen([python_exec, "code_final.py", selected_map, blueprint_id] + meteo_args + [str(spawn_index)])




# Cadre Voiture
frame_voiture = tk.Frame(root, borderwidth=2, relief="solid", bg="#f5f5f5")
frame_voiture.place(x=300, y=10, width=350, height=150)

# Titre du cadre
title_label = tk.Label(
    frame_voiture,
    text="Voiture",
    font=("Arial", 12, "bold"),
    bg="#f5f5f5",
    fg="#333"
)
title_label.pack(pady=5)

# Liste déroulante des véhicules
voiture_dropdown = ttk.Combobox(
    frame_voiture,
    textvariable=selected_vehicle,
    values=[v[0] for v in vehicles],
    state="readonly",
    font=("Arial", 10)
)
voiture_dropdown.pack(pady=10, padx=10, fill="x")

# Bouton de lancement de la simulation
# Style pour améliorer la visibilité du bouton
style = ttk.Style()
style.configure("Accent.TButton", font=("Arial", 10, "bold"), foreground="black", background="#0078D7", padding=5)

# Bouton de lancement de la simulation avec une meilleure lisibilité
btn_lancement = ttk.Button(
    frame_voiture,
    text="Lancer Simulation",
    command=lancer_simulation,
    style="Accent.TButton"
)
btn_lancement.pack(pady=10, padx=10, fill="x")






# Cadre Scénarios
frame_scenarios = tk.Frame(root, borderwidth=2, relief="solid", bg="#f5f5f5")
frame_scenarios.place(x=10, y=10, width=270, height=150)

# Titre
title_label = tk.Label(
    frame_scenarios,
    text="Scénarios",
    font=("Arial", 12, "bold"),
    bg="#f5f5f5",
    fg="#333"
)
title_label.pack(pady=5)

# Liste des scénarios
scenarios = {
    "Scénario 1": {"Nuages": 10, "Pluie": 0, "Flaque d'eau": 0, "Vent": 5, "Brouillard": 0, "Distance brouillard": 100, "Soleil": 60},
    "Scénario 2": {"Nuages": 90, "Pluie": 80, "Flaque d'eau": 70, "Vent": 40, "Brouillard": 80, "Distance brouillard": 60, "Soleil": 10},
    "Scénario personnalisé": None  # Curseurs actifs
}

selected_scenario = tk.StringVar(value="Scénario personnalisé")


def update_weather_scenario():
    scenario_name = selected_scenario.get()

    if scenario_name in scenarios and scenarios[scenario_name] is not None:
        # ✅ Appliquer les valeurs fixes et bloquer toute interaction
        for condition, value in scenarios[scenario_name].items():
            sliders[condition].set(value)  # Déplacer le curseur
            root.update_idletasks()  # ✅ Forcer la mise à jour graphique
            slider_values[condition].config(text=f"{value} {get_unit(condition)}")

            # ✅ Désactiver l'interaction en annulant le comportement du slider
            def block_event(event):
                return "break"  # Empêche Tkinter de traiter l'événement

            sliders[condition].bind("<Button-1>", block_event)  # Empêche le clic
            sliders[condition].bind("<B1-Motion>", block_event)  # Empêche le déplacement
            sliders[condition].bind("<ButtonRelease-1>", block_event)  # Empêche relâchement

    else:
        # ✅ Mode personnalisé : Réactiver les sliders
        for condition in sliders:
            sliders[condition].unbind("<Button-1>")  # Permet le clic
            sliders[condition].unbind("<B1-Motion>")  # Permet le déplacement
            sliders[condition].unbind("<ButtonRelease-1>")  # Permet relâchement



# Ajouter les boutons radio avec un bon espacement
for scenario in scenarios.keys():
    radio = ttk.Radiobutton(
        frame_scenarios,
        text=scenario,
        variable=selected_scenario,
        value=scenario,
        command=update_weather_scenario
    )
    radio.pack(anchor="w", padx=10, pady=2)  # Ajout d'un padding pour plus d'espace



# Cadre Météo
frame_meteo = tk.Frame(root, borderwidth=2, relief="solid", bg="#f5f5f5")
frame_meteo.place(x=680, y=10, width=500, height=700)  # Augmenté de 500 -> 600

# Titre du cadre
title_label = tk.Label(
    frame_meteo,
    text="Météo",
    font=("Arial", 12, "bold"),
    bg="#f5f5f5",
    fg="#333"
)
title_label.pack(pady=5)

# Définition des unités et des plages des curseurs météo
def get_unit(condition):
    return "m" if condition == "Distance brouillard" else "°" if condition == "Soleil" else "%"

conditions_meteo = {
    "Nuages": (0, 100),
    "Pluie": (0, 100),
    "Flaque d'eau": (0, 100),
    "Vent": (0, 100),
    "Brouillard": (0, 100),
    "Distance brouillard": (1, 100),
    "Soleil": (-90, 90)
}

sliders = {}
slider_values = {}

# Ajout des sliders avec une meilleure disposition
for condition, (min_val, max_val) in conditions_meteo.items():
    condition_frame = tk.Frame(frame_meteo, bg="#f5f5f5")
    condition_frame.pack(fill="x", pady=8)  # Augmenté de 5 -> 8

    # Nom du paramètre météo au-dessus du slider
    label = tk.Label(condition_frame, text=condition, font=("Arial", 10, "bold"), bg="#f5f5f5")
    label.pack()

    # Slider pour modifier la valeur
    slider = ttk.Scale(
        condition_frame,
        from_=min_val,
        to=max_val,
        orient="horizontal",
        length=300
    )
    slider.pack(expand=True, fill="x", padx=10)

    # Valeur affichée en dessous du slider
    value_label = tk.Label(condition_frame, text=f"{min_val} {get_unit(condition)}", font=("Arial", 10), bg="#f5f5f5")
    value_label.pack(pady=2)

    sliders[condition] = slider
    slider_values[condition] = value_label

    # Mise à jour dynamique de la valeur affichée
    def update_value(val, condition=condition):
        value = float(val)
        slider_values[condition].config(text=f"{value:.1f} {get_unit(condition)}")

    slider.config(command=update_value)

# Initialiser le soleil à 0° par défaut
sliders["Soleil"].set(0)


# Cadre Ville (plus grand et mieux espacé)
frame_ville = tk.Frame(root, borderwidth=2, relief="solid", bg="#f5f5f5")
frame_ville.place(x=1200, y=10, width=300, height=120)  # Augmenté de 100 -> 120

# Titre du cadre
title_label = tk.Label(
    frame_ville,
    text="Ville",
    font=("Arial", 12, "bold"),
    bg="#f5f5f5",
    fg="#333"
)
title_label.pack(pady=5)

# Liste déroulante pour la sélection des villes
selected_ville = tk.StringVar()
ville_dropdown = ttk.Combobox(
    frame_ville,
    textvariable=selected_ville,
    values=villes,
    state="readonly",
    font=("Arial", 10)
)
ville_dropdown.pack(pady=10, padx=10, fill="x")

# Sélection par défaut
selected_ville.set(villes[0] if villes else "Town01")


# Cadre Spawn Point
frame_spawn = tk.Frame(root, borderwidth=2, relief="solid", bg="#f5f5f5")
frame_spawn.place(x=1200, y=140, width=300, height=100)  # Hauteur augmentée pour plus de lisibilité

# Titre du cadre
title_label = tk.Label(
    frame_spawn,
    text="Spawn Point (0-100)",
    font=("Arial", 12, "bold"),
    bg="#f5f5f5",
    fg="#333"
)
title_label.pack(pady=5)

# Champ de saisie pour le spawn point
spawn_var = tk.StringVar(value="0")
entry_spawn = ttk.Entry(
    frame_spawn,
    textvariable=spawn_var,
    width=10,
    justify="center",
    font=("Arial", 10)
)
entry_spawn.pack(pady=10)

# Fonction pour valider l’entrée et éviter les erreurs
def validate_spawn():
    try:
        value = int(spawn_var.get())
        if 0 <= value <= 100:
            return value
        else:
            spawn_var.set("0")  # Réinitialisation en cas de valeur hors limite
            return 0
    except ValueError:
        spawn_var.set("0")  # Réinitialisation si la saisie n'est pas un nombre
        return 0



try:
    root.mainloop()
except KeyboardInterrupt:
    print("Interface fermée proprement.")