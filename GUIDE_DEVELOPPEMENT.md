# 📚 Guide de Développement

## Architecture du Projet

Le projet suit une architecture modulaire et scalable pour faciliter la maintenance et les ajouts de fonctionnalités.

```
config.py        ← Configuration centralisée (lire en premier !)
app.py           ← Point d'entrée, routing des pages
├── models/      ← Machine Learning et prédictions
├── utils/       ← Fonctions utilitaires (BD, météo, validation)
└── components/  ← Pages Streamlit
```

## 🔄 Flux de Données

```
Utilisateur remplit formulaire (prediction.py)
        ↓
Validation (validators.py)
        ↓
Appel API météo (weather.py)
        ↓
Prédiction ML (predictor.py)
        ↓
Sauvegarde BD (database.py)
        ↓
Export (export.py)
        ↓
Affichage résultats
```

## 🛠️ Ajouter une Nouvelle Fonctionnalité

### Exemple : Ajouter la culture "Arachide"

#### 1. Mettre à jour `config.py`

```python
CULTURES = ["Maïs", "Sorgho", "Mil", "Arachide"]  # ← Ajouter

CULTURE_DUREE_JOURS = {
    # ...
    "Arachide": {"min": 110, "max": 130}  # ← Ajouter
}

OPTIMUMS_CLIMATIQUES = {
    # ...
    "Arachide": {
        "temperature_min": 18,
        "temperature_max": 27,
        "pluviometrie_min": 400,
        "pluviometrie_optimal": 700,
        "pluviometrie_max": 1000
    }
}
```

#### 2. Entraîner le modèle ML

Ajouter des données d'entraînement pour l'arachide, puis :

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Charger données
# Encoder les variables catégoriques
# Diviser train/test
# Entraîner
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Évaluer
score = model.score(X_test, y_test)
print(f"R² Score: {score}")

# Sauvegarder
joblib.dump(model, "models/modele_rendement_agricole.pkl")
```

#### 3. Aucun changement dans les autres fichiers !

La culture s'ajoute automatiquement via `config.py`.

## 🔧 Modifier les Facteurs d'Ajustement

### Exemple : Modifier facteur irrigation

#### Avant (config.py)
```python
FACTEURS_IRRIGATION = {
    "Aucun": 1.0,
    "Traditionnel": 1.1,
    "Goutte à goutte": 1.25,
    "Aspersion": 1.15
}
```

#### Après (augmenter efficacité goutte-à-goutte)
```python
FACTEURS_IRRIGATION = {
    "Aucun": 1.0,
    "Traditionnel": 1.1,
    "Goutte à goutte": 1.35,  # ← Augmenté de 1.25 à 1.35
    "Aspersion": 1.15
}
```

Les prédictions utiliseront automatiquement le nouveau facteur.

## 📊 Ajouter une Nouvelle Région

#### `config.py`

```python
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes", "Nouvelle"]

REGIONS_COORDINATES = {
    # ...
    "Nouvelle": {"lat": 7.5, "lon": 0.5}
}
```

Les données météo seront automatiquement disponibles via l'API.

## 📝 Créer une Nouvelle Page

#### 1. Créer `components/mypage.py`

```python
import streamlit as st

def show_mypage():
    """Description de ma page"""
    st.markdown("## Ma Page")
    st.write("Contenu de ma page")
```

#### 2. Ajouter au routeur `app.py`

```python
from components import show_mypage

# Dans le router des pages
elif page == "Ma Page":
    show_mypage()
```

#### 3. Ajouter à la navigation `app.py`

```python
page = st.radio(
    "Sélectionnez une section",
    ["Accueil", "Prévision", ..., "Ma Page", "À propos"]  # ← Ajouter
)
```

## 🗄️ Requêtes Base de Données

### Récupérer toutes les prévisions

```python
from utils.database import DatabaseManager

db = DatabaseManager()
df = db.get_all_predictions()
print(df.head())
```

### Récupérer par région

```python
df_maritime = db.get_predictions_by_region("Maritime")
```

### Récupérer par culture

```python
df_mais = db.get_predictions_by_culture("Maïs")
```

### Obtenir statistiques

```python
stats = db.get_statistics()
print(stats['average_yield'])  # Rendement moyen
print(stats['total_production'])  # Production totale
```

### Ajouter une prévision manually

```python
prediction = {
    'date': '2026-02-19 10:30',
    'region': 'Maritime',
    'culture': 'Maïs',
    'superficie': 5.0,
    'type_sol': 'Argileux',
    'temperature_moyenne': 27.5,
    'pluviometrie': 800,
    'irrigation': 'Goutte à goutte',
    'fertilisation': 'Chimique',
    'rendement': 3.5,
    'production': 17.5,
    'risque': 'Faible',
    'niveau_risque': 20,
    'date_recolte': '2026-05-20'
}

db.save_prediction(prediction)
```

## 🤖 Modifier le Modèle ML

### Méthode simple (ajuster facteurs)

Éditer `config.py` directement, aucun ML requis.

### Méthode avancée (réentraîner)

```python
from models.predictor import load_model, generate_prediction
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib

# 1. Charger vos données
df_train = pd.read_csv("donnees_entrainement.csv")

# 2. Préparer les features
X = df_train[['region', 'culture', 'type_sol', 'surface_ha', 
               'pluviometrie_mm', 'temperature_moyenne_c']]
y = df_train['rendement']

# 3. Encoder variables catégoriques
from sklearn.preprocessing import LabelEncoder
encoders = {}
for col in ['region', 'culture', 'type_sol']:
    enc = LabelEncoder()
    X[col] = enc.fit_transform(X[col])
    encoders[col] = enc

# 4. Diviser données
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 5. Entraîner
model = RandomForestRegressor(
    n_estimators=150,  # Nombre d'arbres
    max_depth=15,      # Profondeur max
    random_state=42
)
model.fit(X_train, y_train)

# 6. Évaluer
from sklearn.metrics import r2_score, mean_absolute_error
r2 = r2_score(y_test, model.predict(X_test))
mae = mean_absolute_error(y_test, model.predict(X_test))

print(f"R² Score: {r2:.3f}")
print(f"Erreur moyenne: {mae:.3f} t/ha")

# 7. Sauvegarder si bon
if r2 > 0.85:
    joblib.dump(model, "models/modele_rendement_agricole.pkl")
    print("✓ Modèle sauvegardé")
```

## 🧪 Tests

### Créer `tests/test_validators.py`

```python
import pytest
from utils.validators import validate_region

def test_validate_region_valid():
    is_valid, error = validate_region("Maritime")
    assert is_valid == True
    assert error is None

def test_validate_region_invalid():
    is_valid, error = validate_region("Atlantique")
    assert is_valid == False
    assert error is not None

# Lancer tests
# pytest tests/
```

## 🚀 Déploiement

### Local
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Pousser code sur GitHub
2. Aller sur https://share.streamlit.io
3. Connecter repo et lancer

### Serveur Auto-hébergé
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📈 Performance

### Profiler le code

```python
import cProfile
import pstats
from io import StringIO

pr = cProfile.Profile()
pr.enable()

# Code à profiler
result = generate_prediction(...)

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(10)
print(s.getvalue())
```

### Cacher les résultats coûteux

```python
@st.cache_data(ttl=600)  # Cache 10 minutes
def expensive_operation():
    # Code lent
    return result
```

## 🐛 Debugging

### Logs
Vérifier `data/app.log` pour les erreurs et infos.

### Streamlit Logger
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Information")
logger.warning("Attention")
logger.error("Erreur")
```

### Breakpoints (développement local)
```python
import pdb; pdb.set_trace()
```

## 📋 Checklist Avant Publication

- [ ] Tous les tests passent
- [ ] Aucune dépendance manquante
- [ ] `requirements.txt` à jour
- [ ] README.md complet
- [ ] Logs désactivés en production
- [ ] Pas de données sensibles exposées
- [ ] Modèle ML entraîné et testé
- [ ] Base de données initiale créée

## 📞 Support Développement

Pour questions techniques, faire un issue ou consulter les logs détaillés.

---

**Bonne programmation! 🚀**
