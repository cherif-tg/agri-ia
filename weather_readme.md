# 🌦️ Guide d'Intégration des Données Météo en Temps Réel

## Vue d'ensemble

Ce système intègre des données météorologiques en temps réel pour améliorer les prévisions agricoles au Togo. Il utilise principalement **Open-Meteo** (gratuit, sans clé API) et supporte également **OpenWeatherMap** en option.

---

## 🎯 Fonctionnalités

- ✅ **Données météo en temps réel** pour les 5 régions du Togo
- ✅ **Température actuelle et moyenne** (°C)
- ✅ **Pluviométrie cumulée** (mm)
- ✅ **Humidité et vent**
- ✅ **Historique météo** (jusqu'à 80 ans avec Open-Meteo)
- ✅ **Prévisions sur 7 jours**
- ✅ **Cache intelligent** (mise à jour toutes les 10 minutes)

---

## 📦 Installation

### 1. Dépendances requises

```bash
pip install streamlit pandas numpy plotly requests joblib scikit-learn
```

### 2. Structure des fichiers

```
projet/
├── app.py                              # Interface Streamlit (mise à jour)
├── weather_api.py                       # Module API météo
├── config_weather.py                    # Configuration
├── predict_with_realtime_weather.py     # Prédiction avec météo
├── modele_rendement_agricole.pkl        # Modèle entraîné
└── .env                                 # Variables d'environnement (optionnel)
```

---

## 🚀 Démarrage Rapide

### Option 1: Open-Meteo (Recommandé - GRATUIT)

**Aucune configuration nécessaire !** Open-Meteo fonctionne sans clé API.

```python
from weather_api import WeatherAPI

# Initialisation
api = WeatherAPI(provider="open-meteo")

# Récupération météo
meteo = api.get_weather("Maritime")
print(f"Température: {meteo['temperature_actuelle']}°C")
print(f"Pluie (7j): {meteo['precipitation_cumul_7j']} mm")
```

### Option 2: OpenWeatherMap (Optionnel)

1. **Créer un compte** sur [OpenWeatherMap](https://openweathermap.org/api)
2. **Récupérer votre clé API** depuis votre profil
3. **Configurer la clé**:

```bash
# Méthode 1: Variable d'environnement
export OPENWEATHERMAP_API_KEY="votre_cle_ici"

# Méthode 2: Fichier .env
echo "OPENWEATHERMAP_API_KEY=votre_cle_ici" > .env
```

4. **Utiliser l'API**:

```python
from weather_api import WeatherAPI

api = WeatherAPI(api_key="votre_cle", provider="openweathermap")
meteo = api.get_weather("Maritime")
```

---

## 💻 Utilisation

### 1. Interface Streamlit

Lancez l'application web:

```bash
streamlit run app.py
```

L'interface permet de:
- ✅ Cocher "Utiliser les données météo en temps réel"
- ✅ Les données sont automatiquement récupérées pour la région sélectionnée
- ✅ Possibilité de modifier manuellement les valeurs

### 2. Module Python

#### Récupérer la météo actuelle

```python
from weather_api import obtenir_meteo_region

# Simple et direct
meteo = obtenir_meteo_region("Plateaux")

if meteo["success"]:
    print(f"Température: {meteo['temperature_moyenne']}°C")
    print(f"Pluviométrie: {meteo['precipitation_cumul_7j']} mm")
```

#### Prédiction avec météo temps réel

```python
from predict_with_realtime_weather import AgriPredictorWithWeather

# Initialisation
predictor = AgriPredictorWithWeather("modele_rendement_agricole.pkl")

# Prédiction automatique avec météo temps réel
result = predictor.predict_rendement(
    region="Maritime",
    culture="Maïs",
    type_sol="Argilo-sableux",
    surface_ha=10.0,
    use_real_weather=True  # Météo temps réel
)

print(f"Rendement prévu: {result['rendement_t_ha']} t/ha")
print(f"Température utilisée: {result['donnees_meteo']['temperature_c']}°C")
print(f"Pluviométrie: {result['donnees_meteo']['pluviometrie_mm']} mm")
```

#### Comparer toutes les régions

```python
# Obtenir prédictions pour toutes les régions
df_regions = predictor.predict_batch_regions(
    culture="Maïs",
    type_sol="Argilo-sableux",
    surface_ha=5.0
)

print(df_regions)
```

---

## 🌍 Régions Couvertes

| Région     | Ville principale | Coordonnées        | Climat              |
|------------|------------------|--------------------|---------------------|
| Maritime   | Lomé             | 6.13°N, 1.23°E     | Tropical            |
| Plateaux   | Kpalimé          | 6.90°N, 0.85°E     | Sub-équatorial      |
| Centrale   | Sokodé           | 8.97°N, 1.11°E     | Tropical transition |
| Kara       | Kara             | 9.55°N, 1.19°E     | Soudanien           |
| Savanes    | Dapaong          | 10.57°N, 0.22°E    | Sahélien            |

---

## 📊 Données Disponibles

### Données actuelles (Open-Meteo)
- ✅ Température actuelle (°C)
- ✅ Précipitations horaires (mm)
- ✅ Humidité relative (%)
- ✅ Vitesse du vent (km/h)
- ✅ Code météo (conditions)

### Prévisions
- ✅ 7 jours (Open-Meteo gratuit)
- ✅ 16 jours (OpenWeatherMap payant)
- ✅ Températures min/max
- ✅ Précipitations cumulées

### Historique
- ✅ Jusqu'à 80 ans (Open-Meteo)
- ✅ Données journalières
- ✅ Températures et précipitations
- ✅ Statistiques agrégées

---

## ⚙️ Configuration Avancée

### Modifier la durée du cache

Dans `app.py`:

```python
@st.cache_data(ttl=600)  # 600 secondes = 10 minutes
def get_real_time_weather(region: str) -> Dict:
    # ...
```

### Changer le nombre de jours d'historique

```python
# Pour 60 jours au lieu de 30
temp, pluie = api.get_weather_for_prediction("Maritime", jours_historique=60)
```

### Valeurs par défaut en cas d'erreur

Dans `config_weather.py`:

```python
DEFAULT_VALUES = {
    "temperature_moyenne": 27.0,  # °C
    "pluviometrie_annuelle": 800.0,  # mm
    "humidite": 70,  # %
    "vitesse_vent": 10  # km/h
}
```

---

## 🔧 Résolution de problèmes

### Erreur: "Région inconnue"

**Cause**: Nom de région incorrect

**Solution**: Utilisez exactement: `"Maritime"`, `"Plateaux"`, `"Centrale"`, `"Kara"`, ou `"Savanes"`

### Erreur de connexion API

**Cause**: Problème réseau ou API indisponible

**Solution**: Le système utilise automatiquement des valeurs par défaut

```python
if not meteo["success"]:
    print(f"Erreur: {meteo['error']}")
    # Valeurs par défaut utilisées automatiquement
```

### Données météo semblent incorrectes

**Cause**: Cache périmé ou problème de géolocalisation

**Solution**:
1. Vérifier les coordonnées dans `config_weather.py`
2. Effacer le cache Streamlit: `streamlit cache clear`
3. Attendre 10 minutes pour mise à jour automatique

---

## 📈 Limites et Quotas

### Open-Meteo (Gratuit)
- ✅ **10,000+ requêtes/jour**
- ✅ Données actuelles
- ✅ Prévisions 7 jours
- ✅ Historique 80 ans
- ✅ Aucune clé API nécessaire
- ⚠️ Pas d'alertes météo

### OpenWeatherMap (Gratuit)
- ✅ **1,000 appels/jour**
- ✅ Données actuelles
- ✅ Prévisions 5 jours
- ⚠️ Historique payant
- ⚠️ Nécessite inscription

---

## 🎓 Exemples Complets

### Exemple 1: Script de monitoring quotidien

```python
# monitoring_meteo.py
from weather_api import WeatherAPI
from datetime import datetime

api = WeatherAPI(provider="open-meteo")

print(f"=== Rapport Météo Togo - {datetime.now().strftime('%d/%m/%Y')} ===\n")

for region in ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]:
    meteo = api.get_weather(region)
    
    if meteo["success"]:
        print(f"📍 {region}:")
        print(f"   Température: {meteo['temperature_actuelle']}°C")
        print(f"   Pluie (7j): {meteo['precipitation_cumul_7j']} mm")
        print(f"   Humidité: {meteo['humidite']}%\n")
```

### Exemple 2: Comparaison météo entre régions

```python
# comparaison_regions.py
import pandas as pd
from weather_api import WeatherAPI

api = WeatherAPI(provider="open-meteo")
data = []

for region in api.regions_coordinates.keys():
    meteo = api.get_weather(region)
    if meteo["success"]:
        data.append({
            "Région": region,
            "Temp (°C)": meteo["temperature_moyenne"],
            "Pluie (mm)": meteo["precipitation_cumul_7j"],
            "Humidité (%)": meteo["humidite"]
        })

df = pd.DataFrame(data)
print(df)

# Exporter en CSV
df.to_csv("meteo_togo.csv", index=False)
```

### Exemple 3: Intégration avec le modèle existant

```python
# integration_modele.py
import joblib
import pandas as pd
from weather_api import WeatherAPI

# Charger le modèle
model = joblib.load("modele_rendement_agricole.pkl")

# Récupérer météo temps réel
api = WeatherAPI(provider="open-meteo")
temp, pluie = api.get_weather_for_prediction("Maritime")

# Préparer données
data = pd.DataFrame([{
    "region": "Maritime",
    "culture": "Maïs",
    "type_sol": "Argilo-sableux",
    "surface_ha": 10.0,
    "pluviometrie_mm": pluie,
    "temperature_moyenne_c": temp
}])

# Prédiction
rendement = model.predict(data)[0]
print(f"Rendement prévu: {rendement:.2f} t/ha")
```

---

## 🔒 Sécurité et Bonnes Pratiques

1. **Ne jamais commiter les clés API** dans Git
2. **Utiliser des variables d'environnement**
3. **Limiter les requêtes API** (utiliser le cache)
4. **Gérer les erreurs** gracieusement
5. **Logger les échecs** pour debugging

```python
# .gitignore
.env
*.pkl
__pycache__/
```

---

## 📞 Support

### Problèmes avec Open-Meteo
- Documentation: [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs)
- GitHub: [https://github.com/open-meteo/open-meteo](https://github.com/open-meteo/open-meteo)

### Problèmes avec OpenWeatherMap
- Documentation: [https://openweathermap.org/api](https://openweathermap.org/api)
- Support: [https://openweathermap.org/faq](https://openweathermap.org/faq)

---

## 📝 Changelog

### Version 1.0 (2026-01)
- ✅ Intégration Open-Meteo (gratuit)
- ✅ Support OpenWeatherMap
- ✅ Interface Streamlit mise à jour
- ✅ Cache intelligent
- ✅ Gestion erreurs robuste
- ✅ Données historiques

---

## 🎯 Prochaines Étapes

- [ ] Alertes météo automatiques
- [ ] Notifications push pour conditions critiques
- [ ] Export automatique des données
- [ ] Dashboard de monitoring
- [ ] API REST pour intégration externe
- [ ] Support multi-langues (Français, Éwé, Kabyè)

---

## 📄 Licence

Ce projet est sous licence MIT. Libre d'utilisation pour des projets agricoles au Togo.

---

**Développé pour l'agriculture togolaise 🇹🇬**
