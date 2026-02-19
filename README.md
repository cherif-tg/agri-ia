# 🌾 Système de Prévision Agricole IA - Togo

Système intelligent de prévision de rendement agricole basé sur l'Intelligence Artificielle, conçu pour les agriculteurs togolais.

## 🎯 Caractéristiques

- **Prévisions de Rendement** : Estimation précise basée sur Random Forest ML
- **Analyse Climatique** : Données météo en temps réel via API Open-Meteo
- **Recommandations Personnalisées** : Adaptées à votre région et vos conditions
- **Historique Complet** : Base de données SQLite persistante
- **Rapport Détaillés** : Analyses et statistiques complètes
- **Exports Multiples** : CSV, TXT, données brutes

## 🚀 Installation Rapide

### Prérequis
- Python 3.10+
- pip ou conda

### 1. Cloner/Télécharger le projet

```bash
cd prevision
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Placer le modèle ML

Copier le fichier `modele_rendement_agricole.pkl` dans le dossier `models/`:

```
prevision/
├── models/
│   └── modele_rendement_agricole.pkl  ← À placer ici
├── utils/
├── components/
└── ...
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira à `http://localhost:8501`

## 📖 Guide d'Utilisation

### Page Accueil
- Présentation générale du système
- Régions et cultures supportées
- Navigation vers les différentes sections

### Page Prévision
1. **Remplir le formulaire** avec vos données :
   - Région agricole
   - Culture (Maïs, Sorgho, Mil)
   - Superficie
   - Date de semis
   - Type de sol
   - **OU** utiliser les données météo en temps réel

2. **Générer la prévision** :
   - Le système analyse vos données
   - Génère un rendement estimé
   - Évalue le niveau de risque
   - Fournit une date de récolte optimale

3. **Télécharger les résultats** :
   - Exporter en CSV
   - Générer un rapport texte
   - Nouvelle prévision

### Page Historique
- Voir toutes vos prévisions passées
- Statistiques globales
- Graphiques d'évolution
- Exporter l'historique complet

### Page Rapports
- Analyse régionale
- Analyse par culture
- Statistiques détaillées
- Télécharger les rapports

### Page Visualisations
- Tendances régionales
- Impact climatique
- Calendrier cultural

## 🏗️ Structure du Projet

```
prevision/
├── app.py                    # Point d'entrée principal
├── config.py                 # Configuration centralisée
├── requirements.txt          # Dépendances Python
├── README.md                 # Cette documentation
│
├── models/
│   ├── __init__.py
│   ├── predictor.py         # Moteur de prédiction ML
│   └── modele_rendement_agricole.pkl  # Modèle Random Forest
│
├── utils/
│   ├── __init__.py
│   ├── weather.py           # API météorologiques
│   ├── database.py          # Gestion SQLite
│   ├── validators.py        # Validation des données
│   └── export.py            # Export CSV/TXT/Rapports
│
├── components/
│   ├── __init__.py
│   ├── home.py              # Page d'accueil
│   ├── prediction.py        # Page prévision
│   ├── visualizations.py    # Page visualisations
│   ├── history.py           # Page historique
│   ├── report.py            # Page rapports
│   └── about.py             # Page à propos
│
├── data/
│   ├── predictions.db       # Base de données (créée auto)
│   └── app.log              # Logs (créés auto)
│
├── assets/                  # Images, logos
│
└── .streamlit/
    └── config.toml          # Configuration Streamlit
```

## 💾 Base de Données

Les prévisions sont sauvegardées automatiquement dans SQLite (`data/predictions.db`) avec :
- Date de création
- Région et culture
- Données climatiques
- Résultats de prévision
- Niveau de risque
- Date de récolte

### Exemple de requête

```python
from utils.database import DatabaseManager

db = DatabaseManager()
df = db.get_all_predictions()
print(df)
```

## 🤖 Modèle Machine Learning

### Algorithm
- **Type** : Random Forest
- **Framework** : Scikit-learn
- **Entrées** : région, culture, type_sol, superficie, pluviométrie, température
- **Sortie** : rendement estimé (t/ha)

### Facteurs d'ajustement
- Pluviométrie : 0.7x à 1.2x
- Température : 0.85x si hors optimum
- Irrigation : 1.0x à 1.25x selon système
- Fertilisation : 0.8x à 1.2x selon type

### Performance
- Précision : R² > 0.85
- Erreur moyenne : ~0.3 t/ha
- Temps prédiction : < 200ms

## 🌡️ Intégrations Externes

### API Météo
- **Service** : Open-Meteo (gratuit)
- **Mise à jour** : Cache 10 minutes
- **Données** : Température, pluviométrie, humidité, vent
- **7 jours** de prévisions

### Pas d'authentification requise !

## 📊 Régions Supportées

| Région | Latitude | Longitude |
|--------|----------|-----------|
| Maritime | 6.1256 | 1.2256 |
| Plateaux | 6.9000 | 0.8500 |
| Centrale | 8.9711 | 1.1056 |
| Kara | 9.5511 | 1.1856 |
| Savanes | 10.5700 | 0.2200 |

## 🌾 Cultures Supportées

1. **Maïs**
   - Durée : 85-95 jours
   - Optimum : 25-30°C, 800-1000mm pluie

2. **Sorgho**
   - Durée : 115-130 jours
   - Optimum : 22-28°C, 600mm pluie

3. **Mil**
   - Durée : 95-110 jours
   - Optimum : 20-27°C, 500mm pluie

## 🔧 Développement

### Ajouter une culture
1. Ajouter dans `config.py` : `CULTURES`
2. Ajouter durée dans `CULTURE_DUREE_JOURS`
3. Ajouter optimums dans `OPTIMUMS_CLIMATIQUES`
4. Entraîner le modèle ML avec nouvelles données

### Ajouter une région
1. Ajouter dans `config.py` : `REGIONS_COORDINATES`
2. Les données météo seront automatiquement disponibles

### Modifier les facteurs d'ajustement
Éditer dans `config.py` :
- `FACTEURS_IRRIGATION`
- `FACTEURS_FERTILISATION`

## 📝 Logs

Les logs sont sauvegardés dans `data/app.log` avec rotation automatique.

#### Niveaux de log
- `DEBUG` : Informations détaillées
- `INFO` : Événements généraux (par défaut)
- `WARNING` : Avertissements
- `ERROR` : Erreurs

## 🐛 Dépannage

### Erreur : "Le modèle n'existe pas"
```
Le modèle 'models/modele_rendement_agricole.pkl' n'existe pas
```
**Solution** : Copier le fichier modèle dans le dossier `models/`

### Erreur : "Connexion Internet"
```
Erreur de connexion API météo
```
**Solution** : Vérifier votre connexion Internet

### Application lente
**Solutions** :
- Vérifier la charge du système
- Actualiser la page Streamlit
- Redémarrer l'application

## 📈 Améliorations Futures

- [ ] Export PDF avec mise en forme
- [ ] Prédictions à long terme
- [ ] Interface multilingue (Français/Anglais)
- [ ] Application mobile
- [ ] Alertes SMS/Email
- [ ] Intégration avec services SIG
- [ ] Calendrier agricole interactif
- [ ] Comparaison de scénarios

## 📞 Support

**Email** : tengacherif@gmail.com  
**Téléphone** : +228 71518061  
**Site** : www.agri-ia-togo.org

## 📄 Licence

Projet conçu pour l'aide à la décision agricole au Togo.

## 👨‍💻 Auteurs

Développé pour l'agriculture durable du Togo.

---

**Version** : 1.0.0  
**Date** : 2026  
**🇹🇬 Fait avec ❤️ pour le Togo**
