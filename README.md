# ESME3TD2025CARLA

# Simuler pour Sauver - Analyse de la Sécurité Routière avec CARLA

### Projet réalisé par :

* Sandrine BATISTA
* Clément CRUSSY
* Majeure : Transformation Digitale - ESME 3TD 2025

### Encadrant :

* M. Lamine AMOUR

## 🛠️ Description rapide

Simuler pour Sauver est un projet visant à analyser la sécurité routière des véhicules autonomes à l'aide du simulateur CARLA, en se concentrant sur les impacts des conditions météorologiques sur les capteurs (LIDAR, Radar, Caméra) et les distances de sécurité.

## 📦 Objectif du projet

L'objectif principal de ce projet est de simuler des scénarios de conduite autonome dans des conditions météorologiques variées pour analyser la sécurité routière et la performance des capteurs embarqués (LIDAR, Radar, Caméra). Le simulateur CARLA est utilisé pour recréer des environnements réalistes et collecter des données permettant d'évaluer les distances de sécurité, le temps de collision prévu (TTC) et d'autres métriques critiques.

## 🔍 Contexte

Les véhicules autonomes promettent une réduction des accidents dus aux erreurs humaines, mais leur efficacité dépend des capteurs embarqués et de leur capacité à percevoir l'environnement dans des conditions complexes (pluie, brouillard, faible luminosité). Ce projet explore ces scénarios critiques pour proposer des stratégies d'amélioration des systèmes de conduite autonome.

## 🚀 Fonctionnalités développées

* **Liste des véhicules disponibles :** Extraction des modèles compatibles avec CARLA via `liste_voiture.py`.
* **Cartographie des villes :** Récupération des cartes HD disponibles dans le simulateur à l'aide de `liste_ville.py`.
* **Simulation des conditions météorologiques :** Personnalisation des paramètres météo (pluie, vent, brouillard) et analyse des impacts sur la sécurité.
* **Interface graphique :** Interface développée avec PyQt5 pour sélectionner les scénarios, les véhicules et les paramètres de simulation (`interface_2.py`).
* **Exécution de la simulation :** Script `code_final.py` permettant de lancer des simulations en fonction des paramètres choisis.

## 📂 Structure du dépôt

```
├── liste_ville.py           # Extraction des cartes HD disponibles
├── liste_voiture.py         # Extraction des modèles de véhicules compatibles
├── interface_2.py           # Interface utilisateur (PyQt5)
├── interface.py             # Interface utilisateur (tkinter)
├── code_final.py            # Exécution des scénarios de simulation
├── CARLA_Vehicles1.csv      # Liste des véhicules importés
├── liste_villes.csv         # Liste des villes disponibles
├── README.md                # Présentation du projet
```

## 🛠️ Prérequis

* Python 3.7
* CARLA
* PyQt5
* Pandas
* NumPy
* Unreal Engine pour les cartes personnalisées

## ⚡ Installation

1. Cloner le dépôt :

   ```bash
   git clone <URL_du_dépôt>
   ```

2. Installer les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. Démarrer CARLA :


4. Lancer l'interface utilisateur :

   ```bash
   python interface_2.py
   ```

## 📊 Données générées

* `lidar_data.csv` : Points collectés par le LiDAR
* `radar_data.csv` : Données du Radar (profondeur, vitesse)
* `meteo_data.csv` : Paramètres météorologiques appliqués
* `metrics_data.csv` : Métriques de conduite (distance d'arrêt, TTC, distance de sécurité)

## 🔧 Prochaines améliorations

* Intégration du Machine Learning pour ajuster dynamiquement les distances de sécurité.
* Optimisation des scénarios pour inclure des transitions météorologiques.
* Automatisation de la génération des cartes HD à partir de données OpenStreetMap.

## 📝 Références

* [CARLA Simulator](https://carla.org/)
* [OpenStreetMap](https://www.openstreetmap.org/)
* [PyQt5 Documentation](https://riverbankcomputing.com/software/pyqt/intro)

---

Simuler pour sauver - Exploiter les données de simulation pour renforcer la sécurité routière.
