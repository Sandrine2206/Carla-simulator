from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGroupBox, QVBoxLayout, QComboBox, QPushButton, QHBoxLayout, QRadioButton, QSlider, QLineEdit, QSizePolicy, QWidget, QGridLayout
import sys
import pandas as pd
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import subprocess
import sys

style_qgroupbox = """
    QGroupBox {
        background-color: rgba(255, 255, 255, 180);
        font-weight: bold;
        font-size: 18px;
        color: black;
        text-align: center;
        border: 2px solid gray;
        border-radius: 10px;
        padding-top: 20px;
    }
"""

class CarlaInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        # 🖥️ Titre de la fenêtre
        self.setWindowTitle("ESME3TD2025CARLA - SIPOSA - Interface de lancement")

        # 🖼️ Ajouter une image de fond
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap("image.png")  # Assurez-vous que l'image est bien dans le dossier
        self.background_label.setPixmap(self.background_pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatioByExpanding
        ))
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # Ajouter l'image ESME.png en bas à droite
        self.esme_label = QLabel(self)  # Créer un QLabel pour l'image
        self.esme_pixmap = QPixmap("ESME.png")  # Charger l'image ESME.png
        self.esme_label.setPixmap(self.esme_pixmap)  # Afficher l'image sans redimensionnement initial
        self.esme_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)  # Positionner en bas à droite

        # Ajouter un QLabel pour les informations en bas à gauche
        self.info_label = QLabel(self)
        self.info_label.setText(
            "Sandrine Batista\n"
            "Clément Crussy\n"
            "Année: 2024/2025\n"
            "Majeure: 3TD"
        )
        self.info_label.setStyleSheet("color: white; font-weight: bold;")  # Style du texte (taille dynamique)
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)  # Aligner en bas à gauche

        # ✅ Supprimer setGeometry() et passer en plein écran
        self.showMaximized()  # Ouvre directement en plein écran

        # 🔹 Définir un widget central pour la mise en page
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 🔹 Créer un layout principal HORIZONTAL pour aligner tout sur une seule ligne
        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)

        # 🌦️ Scénarios météo
        self.scenarios = {
            "Scénario 1": {"Nuages": 10, "Pluie": 0, "Flaques d'eau": 0, "Vent": 5, "Brouillard": 0,
                           "Distance brouillard": 100, "Soleil": 60},
            "Scénario 2": {"Nuages": 90, "Pluie": 80, "Flaques d'eau": 70, "Vent": 40, "Brouillard": 80,
                           "Distance brouillard": 60, "Soleil": 10},
            "Scénario personnalisé": None  # Curseurs actifs
        }

        # 🚗 Charger la liste des véhicules
        self.vehicles = self.load_vehicles()

        # 🏙️ Charger la liste des villes
        self.villes = self.load_villes()

        # 🔹 Ajouter les cadres
        self.create_scenario_box()
        self.create_voiture_box()
        self.create_meteo_box()
        self.create_ville_box()
        self.create_spawn_box()
        self.create_button_box()

        # Forcer la mise à jour de la géométrie
        QApplication.processEvents()

        # 📌 Créer des layouts verticaux pour forcer l'alignement en haut
        self.scenario_layout = QVBoxLayout()
        self.scenario_layout.addWidget(self.scenario_box)
        self.scenario_layout.setAlignment(Qt.AlignTop)

        self.voiture_layout = QVBoxLayout()
        self.voiture_layout.addWidget(self.voiture_box)
        self.voiture_layout.setAlignment(Qt.AlignTop)

        self.meteo_layout = QVBoxLayout()
        self.meteo_layout.addWidget(self.meteo_box)
        self.meteo_layout.setAlignment(Qt.AlignTop)

        # 📌 Créer un layout vertical pour empiler "Ville" au-dessus de "Spawn"
        self.ville_spawn_layout = QVBoxLayout()
        self.ville_spawn_layout.addWidget(self.ville_box)
        self.ville_spawn_layout.addWidget(self.spawn_box)
        self.ville_spawn_layout.addStretch(1)  # Ajouter un espace dynamique avant la box du bouton
        self.ville_spawn_layout.addWidget(self.button_box)  # Ajouter la box du bouton ici
        self.ville_spawn_layout.addStretch(2)  # Ajouter un espace dynamique après la box du bouton
        self.ville_spawn_layout.setAlignment(Qt.AlignTop)  # Tout aligner en haut

        # Ajouter la nouvelle box pour le bouton
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.button_box)
        self.button_layout.setAlignment(Qt.AlignTop)


        # 📌 Ajouter les layouts au layout horizontal
        self.main_layout.addLayout(self.scenario_layout)
        self.main_layout.addLayout(self.voiture_layout)
        self.main_layout.addLayout(self.meteo_layout)
        self.main_layout.addLayout(self.ville_spawn_layout)

        # 📌 Ajuster la largeur relative des éléments
        self.main_layout.setStretchFactor(self.scenario_layout, 1)  # Scénarios normal
        self.main_layout.setStretchFactor(self.voiture_layout, 1)  # Voiture normal
        self.main_layout.setStretchFactor(self.meteo_layout, 2)  # Météo DEUX FOIS plus large
        self.main_layout.setStretchFactor(self.ville_spawn_layout, 1)  # Ville + Spawn normal

        # ✅ Empêcher certaines sections de s’étirer trop
        self.scenario_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.voiture_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.meteo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Seule Météo peut s'agrandir
        self.ville_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.spawn_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Bouton s'étire horizontalement

    def resizeEvent(self, event):
        """Ajuste l'image de fond lorsque la fenêtre est redimensionnée"""
        self.background_label.setPixmap(self.background_pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatioByExpanding))
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # Redimensionner l'image ESME.png en fonction de la taille de la fenêtre
        esme_width = int(self.width() * 0.1)  # 10% de la largeur de la fenêtre
        esme_height = int(self.height() * 0.1)  # 10% de la hauteur de la fenêtre
        self.esme_label.setPixmap(self.esme_pixmap.scaled(
            esme_width, esme_height, Qt.KeepAspectRatio))  # Redimensionner l'image

        # Positionner l'image ESME.png en bas à droite
        self.esme_label.setGeometry(
            self.width() - esme_width - 10,  # 10 pixels de marge à droite
            self.height() - esme_height - 10,  # 10 pixels de marge en bas
            esme_width, esme_height)

        # Ajuster la taille du texte et la position du QLabel des informations en bas à gauche
        font_size = max(10, int(self.height() * 0.02))  # Taille de police proportionnelle à la hauteur de la fenêtre
        self.info_label.setStyleSheet(
            f"font-size: {font_size}px; color: white; font-weight: bold;")  # Appliquer la taille dynamique

        # Positionner le QLabel des informations en bas à gauche
        info_width = int(self.width() * 0.5)  # 30% de la largeur de la fenêtre
        info_height = int(self.height() * 0.5)  # 10% de la hauteur de la fenêtre
        self.info_label.setGeometry(
            10,  # Marge de 10 pixels à gauche
            self.height() - info_height - 10,  # Marge de 10 pixels en bas
            info_width, info_height)
        event.accept()





    def launch_simulation(self):
        """Lance `code_final.py` avec les paramètres sélectionnés"""

        # Récupérer le véhicule sélectionné
        selected_vehicle = self.voiture_dropdown.currentText()
        blueprint_id = next((bp for model, bp in self.vehicles if model == selected_vehicle), self.vehicles[0][1])

        # Récupérer la ville sélectionnée
        selected_map = self.ville_dropdown.currentText()

        # Récupérer le Spawn Point (après validation)
        spawn_index = self.spawn_input.text()
        if not spawn_index.isdigit() or not (0 <= int(spawn_index) <= 100):
            spawn_index = "0"  # Valeur par défaut si la saisie est incorrecte

        # Appliquer les paramètres météo du scénario sélectionné
        self.update_weather_scenario()

        # Récupérer les valeurs météo des sliders
        meteo_values = {param: self.meteo_sliders[param].value() for param in self.meteo_sliders}

        # Convertir les valeurs météo en arguments pour `code_final.py`
        meteo_args = [str(meteo_values[param]) for param in meteo_values]

        # Debug : Vérifier les valeurs envoyées
        print(
            f"🚀 Lancement de `code_final.py` avec ville '{selected_map}', véhicule '{selected_vehicle}', météo : {meteo_values}, spawn {spawn_index}")

        # Construire la commande pour exécuter `code_final.py`
        python_exec = sys.executable  # Utilise l'interpréteur Python actuel
        command = [python_exec, "code_final.py", selected_map, blueprint_id] + meteo_args + [spawn_index]

        print(f"Commande exécutée : {' '.join(command)}")  # Debug

        # Exécuter `code_final.py` avec les paramètres
        self.simulation_process = subprocess.Popen(command, shell=True)  # Stocker le processus

    def stop_simulation(self):
        """Arrête la simulation en cours"""
        try:
            # Vérifier si un processus de simulation est en cours
            if hasattr(self, 'simulation_process') and self.simulation_process:
                print("🛑 Arrêt de la simulation en cours...")

                # Créer un fichier pour signaler l'arrêt
                with open("stop_simulation.txt", "w") as f:
                    f.write("stop")  # Écrire un message quelconque

                self.simulation_process.terminate()  # Arrêter le processus
                self.simulation_process = None  # Réinitialiser la référence
                print("✅ Simulation arrêtée avec succès.")
            else:
                print("⚠️ Aucune simulation en cours à arrêter.")
        except Exception as e:
            print(f"❌ Erreur lors de l'arrêt de la simulation : {e}")

    def load_vehicles(self):
        """Charge la liste des véhicules depuis un fichier CSV"""
        csv_path = "CARLA_Vehicles_Available.csv"
        try:
            df = pd.read_csv(csv_path, delimiter=";", dtype=str)
            df = df[df["Type"] == "Car"]  # Filtrer uniquement les voitures
            df = df.dropna(subset=["Blueprint_ID"])  # Supprimer les entrées vides
            df["Model"] = df["Brand"] + " " + df["Model"]  # Fusionner Marque + Modèle
            return df[["Model", "Blueprint_ID"]].drop_duplicates().values.tolist()
        except FileNotFoundError:
            print("⚠️ Le fichier 'CARLA_Vehicles_Available.csv' est introuvable. Vérifiez son emplacement.")
            return [["Tesla Model 3", "vehicle.tesla.model3"],
                    ["Audi e-Tron", "vehicle.audi.etron"]]  # Valeurs par défaut

    def create_scenario_box(self):

        """Cadre Scénarios"""
        self.scenario_box = QGroupBox(self)
        self.scenario_box.setTitle("Scénarios")
        self.scenario_box.setGeometry(20, 20, 250, 150)
        self.scenario_box.setAlignment(Qt.AlignCenter)  # Centrer le titre
        self.scenario_box.setStyleSheet(style_qgroupbox)

        # Layout vertical pour organiser les boutons radio
        layout = QVBoxLayout()

        # Boutons radio pour sélectionner un scénario
        self.scenario1 = QRadioButton("Beau temps")
        self.scenario2 = QRadioButton("Mauvais temps")
        self.scenario_custom = QRadioButton("Scénario personnalisé")
        self.scenario_custom.setChecked(True)  # Par défaut, le mode personnalisé est sélectionné

        # Connecter les boutons radio à la mise à jour météo
        self.scenario1.toggled.connect(self.update_weather_scenario)
        self.scenario2.toggled.connect(self.update_weather_scenario)
        self.scenario_custom.toggled.connect(self.update_weather_scenario)

        # Ajouter les boutons radio au layout
        layout.addWidget(self.scenario1)
        layout.addWidget(self.scenario2)
        layout.addWidget(self.scenario_custom)

        # Appliquer le layout au cadre
        self.scenario_box.setLayout(layout)


    def update_weather_scenario(self):
        """Met à jour l'interface en fonction du scénario sélectionné"""
        if self.scenario1.isChecked():
            scenario_name = "Scénario 1"
        elif self.scenario2.isChecked():
            scenario_name = "Scénario 2"
        else:
            scenario_name = "Scénario personnalisé"

        if scenario_name in self.scenarios and self.scenarios[scenario_name] is not None:
            for condition, value in self.scenarios[scenario_name].items():
                self.meteo_sliders[condition].setValue(value)
                self.meteo_sliders[condition].setEnabled(False)  # Désactiver les sliders
        else:
            for condition in self.meteo_sliders:
                self.meteo_sliders[condition].setEnabled(True)  # Réactiver les sliders

    def create_voiture_box(self):
        """Cadre Voiture avec liste des véhicules dynamiques"""
        self.voiture_box = QGroupBox(self)
        self.voiture_box.setTitle("Voitures")
        self.voiture_box.setGeometry(290, 20, 300, 150)
        self.voiture_box.setAlignment(Qt.AlignCenter)  # Centrer le titre
        self.voiture_box.setStyleSheet(style_qgroupbox)

        # Layout vertical pour organiser les éléments
        layout = QVBoxLayout()

        # Liste déroulante pour choisir un véhicule
        self.voiture_dropdown = QComboBox()
        self.voiture_dropdown.addItems([v[0] for v in self.vehicles])  # Ajouter les noms des véhicules
        layout.addWidget(self.voiture_dropdown)


        # Appliquer le layout au cadre
        self.voiture_box.setLayout(layout)

    def get_curseur_color(self, param, value):
        """Retourne la couleur du curseur en fonction du paramètre météo et de sa valeur."""
        seuils = {
            "Nuages": [(50, "#00FF00"), (70, "#FFFF00"), (90, "#FFA500"), (100, "#FF0000")],
            "Pluie": [(30, "#00FF00"), (60, "#FFFF00"), (80, "#FFA500"), (100, "#FF0000")],
            "Flaques d'eau": [(20, "#00FF00"), (50, "#FFFF00"), (80, "#FFA500"), (100, "#FF0000")],
            "Vent": [(40, "#00FF00"), (70, "#FFFF00"), (90, "#FFA500"), (100, "#FF0000")],
            "Brouillard": [(20, "#00FF00"), (50, "#FFFF00"), (80, "#FFA500"), (100, "#FF0000")],
            "Distance brouillard": [(20, "#FF0000"), (40, "#FFA500"), (70, "#FFFF00"), (100, "#00FF00")],
            "Soleil": [(-70, "#FF0000"), (-50, "#FFA500"), (-30, "#FFFF00"), (30, "#00FF00"), (60, "#FFFF00"), (70, "#FFA500"), (100, "#FF0000")]
        }

        for seuil, couleur in seuils[param]:
            if value <= seuil:
                return couleur
        return "#FFFFFF"  # Blanc par défaut

    def create_meteo_box(self):
        """Cadre Météo avec sliders"""
        self.meteo_box = QGroupBox(self)
        self.meteo_box.setTitle("Météo")
        self.meteo_box.setGeometry(600, 20, 400, 400)
        self.meteo_box.setAlignment(Qt.AlignCenter)
        self.meteo_box.setStyleSheet(style_qgroupbox)

        # ✅ Ajouter un layout vertical à la box
        layout = QVBoxLayout()

        # Liste des paramètres météo
        self.meteo_sliders = {}
        self.meteo_labels = {}

        meteo_params = {
            "Nuages": (0, 100),
            "Pluie": (0, 100),
            "Flaques d'eau": (0, 100),
            "Vent": (0, 100),
            "Brouillard": (0, 100),
            "Distance brouillard": (1, 100),
            "Soleil": (-90, 90)
        }

        for param, (min_val, max_val) in meteo_params.items():
            condition_frame = QVBoxLayout()

            # Nom du paramètre météo au-dessus du slider
            label = QLabel(f"{param}: {min_val}", self)
            condition_frame.addWidget(label)

            # Slider pour modifier la valeur
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(min_val)

            # Mise à jour du texte et couleur du slider en temps réel
            slider.valueChanged.connect(lambda value, lbl=label, p=param: lbl.setText(f"{p}: {value}"))
            slider.valueChanged.connect(lambda: self.update_curseur_colors())  # ✅ Appel avec self

            condition_frame.addWidget(slider)

            # Ajouter au dictionnaire pour un accès facile
            self.meteo_sliders[param] = slider
            self.meteo_labels[param] = label

            layout.addLayout(condition_frame)  # ✅ Ajout au layout local

        # ✅ Appliquer le layout final à la box météo
        self.meteo_box.setLayout(layout)

        # ✅ Mise à jour immédiate des couleurs au démarrage
        self.update_curseur_colors()

    def update_curseur_colors(self):
        """Met à jour la couleur de chaque curseur en fonction des conditions météo."""
        for param, slider in self.meteo_sliders.items():
            value = slider.value()
            color = self.get_curseur_color(param, value)  # ✅ Correction ici
            slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background: {color};
                    height: 8px;
                }}
                QSlider::handle:horizontal {{
                    background: white;
                    border: 1px solid black;
                    width: 14px;
                    margin: -4px 0;
                    border-radius: 7px;
                }}
            """)

    def load_villes(self):
        """Charge la liste des villes depuis un fichier CSV"""
        csv_villes_path = "liste_villes.csv"
        try:
            df_villes = pd.read_csv(csv_villes_path, delimiter=";", dtype=str)

            # Supprimer l'extension .pcd des noms de villes
            df_villes["Nom Ville"] = df_villes["Nom Ville"].str.replace(".pcd", "", regex=False)

            return df_villes["Nom Ville"].tolist()  # Extrait uniquement les noms des villes
        except FileNotFoundError:
            print("⚠️ Le fichier 'liste_villes.csv' est introuvable. Vérifiez son emplacement.")
            return ["Town01", "Town02", "Town03", "Town04"]  # Valeurs par défaut si le fichier est absent

    def create_ville_box(self):
        """Cadre Ville avec liste déroulante"""
        self.ville_box = QGroupBox(self)
        self.ville_box.setTitle("Ville")
        self.ville_box.setGeometry(1020, 20, 240, 100)
        self.ville_box.setAlignment(Qt.AlignCenter)  # Centrer le titre
        self.ville_box.setStyleSheet(style_qgroupbox)


        # Layout vertical
        layout = QVBoxLayout()

        # Liste déroulante pour la sélection des villes
        self.ville_dropdown = QComboBox()
        self.ville_dropdown.addItems(self.villes)  # Ajouter dynamiquement les villes du CSV
        layout.addWidget(self.ville_dropdown)

        # Appliquer le layout au cadre
        self.ville_box.setLayout(layout)

    def create_spawn_box(self):
        """Cadre Spawn Point avec champ de saisie"""
        self.spawn_box = QGroupBox(self)
        self.spawn_box.setTitle("Spawn Point (0-100)")
        self.spawn_box.setGeometry(1020, 140, 240, 100)
        self.spawn_box.setAlignment(Qt.AlignCenter)  # Centrer le titre
        self.spawn_box.setStyleSheet(style_qgroupbox)


        # Layout vertical
        layout = QVBoxLayout()

        # Champ de saisie pour entrer le Spawn Point
        self.spawn_input = QLineEdit()
        self.spawn_input.setPlaceholderText("Entrez une valeur entre 0 et 100")
        self.spawn_input.textChanged.connect(self.validate_spawn)  # Ajout de la validation dynamique

        layout.addWidget(self.spawn_input)

        # Appliquer le layout au cadre
        self.spawn_box.setLayout(layout)

    def create_button_box(self):
        """Cadre pour les boutons Lancer et Arrêter Simulation"""
        self.button_box = QGroupBox(self)  # Crée une nouvelle box
        self.button_box.setTitle("Actions")  # Titre optionnel
        self.button_box.setAlignment(Qt.AlignCenter)  # Centrer le titre
        self.button_box.setStyleSheet(style_qgroupbox)  # Appliquer le style
        self.button_box.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Fixed)  # Permet à la box de s'étirer horizontalement

        # Layout horizontal pour organiser les boutons
        layout = QHBoxLayout()

        # Créer le bouton "Lancer Simulation"
        self.btn_lancer = QPushButton("Lancer Simulation")
        self.btn_lancer.setStyleSheet("background-color: #06ad0b; color: white; font-weight: bold;")
        self.btn_lancer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Bouton s'étire horizontalement
        self.btn_lancer.clicked.connect(self.launch_simulation)

        # Créer le bouton "Arrêter Simulation"
        self.btn_stop = QPushButton("Arrêter Simulation")
        self.btn_stop.setStyleSheet(
            "background-color: #ad0606; color: white; font-weight: bold;")  # Rouge pour indiquer l'arrêt
        self.btn_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Bouton s'étire horizontalement
        self.btn_stop.clicked.connect(self.stop_simulation)  # Connecter à la méthode stop_simulation

        # Ajouter les boutons au layout
        layout.addWidget(self.btn_lancer)
        layout.addWidget(self.btn_stop)

        # Appliquer le layout à la box
        self.button_box.setLayout(layout)

    def validate_spawn(self):
        """Validation de l'entrée du Spawn Point"""
        try:
            value = int(self.spawn_input.text())
            if 0 <= value <= 100:
                self.spawn_input.setStyleSheet("color: black;")  # Texte normal
            else:
                self.spawn_input.setStyleSheet("color: red;")  # Met le texte en rouge si hors limite
                self.spawn_input.setText("0")  # Réinitialise à 0 si invalide
        except ValueError:
            self.spawn_input.setStyleSheet("color: red;")  # Rouge si saisie invalide
            self.spawn_input.setText("0")  # Réinitialise à 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CarlaInterface()
    window.show()
    sys.exit(app.exec_())
