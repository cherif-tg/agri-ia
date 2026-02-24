# 📖 Guide Utilisateur – AgroPredict Togo v2.0

> Plateforme d'intelligence artificielle pour l'agriculture togolaise  
> Prévisions de rendement · Analyse de données · Chatbot agricole

---

## Table des matières

1. [Présentation](#présentation)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Lancement de l'application](#lancement)
5. [Pages et fonctionnalités](#pages)
   - [🏠 Accueil](#accueil)
   - [🌾 Prévision](#prévision)
   - [📊 Visualisations](#visualisations)
   - [📂 Analyse de fichiers (RAG)](#rag)
   - [🤖 AgroBot](#agrobot)
   - [📋 Historique](#historique)
   - [📈 Rapports](#rapports)
6. [Formats de fichiers supportés](#formats)
7. [Modèle Machine Learning](#modele-ml)
8. [FAQ](#faq)
9. [Architecture technique](#architecture)

---

## 1. Présentation {#présentation}

**AgroPredict Togo** est une application web de data science agricole qui permet de :

- **Prédire le rendement** (t/ha) de vos cultures (Maïs, Sorgho, Mil) à partir de données agronomiques
- **Visualiser** des tendances régionales, l'impact climatique et le calendrier cultural
- **Analyser vos propres fichiers** CSV, Excel ou PDF et générer des prévisions en masse
- **Poser des questions** à un assistant IA agricole (AgroBot) basé sur LLaMA 3.3-70B
- **Consulter des rapports** et exporter vos données

**Couverture géographique** : Les 5 régions du Togo (Maritime, Plateaux, Centrale, Kara, Savanes)

---

## 2. Installation {#installation}

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

```bash
# 1. Clonez ou téléchargez le projet
cd c:\Users\Ce PC\OneDrive - Le Gret\Documents\prevision

# 2. Créez un environnement virtuel (recommandé)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / Mac

# 3. Installez les dépendances
pip install -r requirements.txt
```

> **Note** : L'installation peut prendre quelques minutes (XGBoost, LightGBM, etc.).

---

## 3. Configuration {#configuration}

### Clé API Groq (pour le chatbot et l'analyse PDF)

1. Créez un compte gratuit sur [console.groq.com](https://console.groq.com)
2. Générez une clé API (commençant par `gsk_`)
3. Copiez le fichier modèle :
   ```bash
   copy .env.example .env       # Windows
   cp .env.example .env         # Linux / Mac
   ```
4. Ouvrez `.env` et remplacez `gsk_VOTRE_CLE_ICI` par votre clé :
   ```
   GROQ_API_KEY=gsk_abc123...
   ```

> **Sans clé Groq**, le chatbot affiche des exemples statiques et l'analyse PDF est désactivée.  
> Les prévisions de rendement et les visualisations fonctionnent sans clé.

---

## 4. Lancement {#lancement}

```bash
# Depuis le dossier du projet
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :  
`http://localhost:8501`

> **Premier lancement** : Le modèle ML est entraîné automatiquement (environ 2-5 minutes).  
> Les lancements suivants sont immédiats (modèle chargé depuis le disque).

---

## 5. Pages et fonctionnalités {#pages}

### 🏠 Accueil {#accueil}

Tableau de bord avec :
- Indicateurs clés (régions, cultures, précision du modèle)
- Description des fonctionnalités
- Guide de démarrage rapide
- Carte des régions couvertes

---

### 🌾 Prévision {#prévision}

#### Formulaire de prévision

Renseignez les informations suivantes :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Région** | Votre région agricole | Kara |
| **Culture** | Type de culture | Maïs |
| **Type de sol** | Nature du sol | Argileux |
| **Surface (ha)** | Superficie cultivée | 5.0 |
| **Irrigation** | Système utilisé | Goutte à goutte |
| **Fertilisation** | Mode de fertilisation | Chimique |
| **Date de semis** | Date de plantation | 01/03/2026 |
| **Météo temps réel** | Récupération auto de la météo | ✓ Activée |

#### Résultats affichés

- **Rendement estimé** (t/ha) avec intervalle de confiance ±8%
- **Production totale** (tonnes) = rendement × surface
- **Niveau de risque** (Faible / Modéré / Élevé)
- **Date de récolte optimale** estimée
- **Graphiques** : scénarios de rendement + jauge de risque
- **Recommandations** personnalisées selon les conditions

#### Export

Cliquez sur **⬇ Exporter en CSV** pour télécharger les résultats.

---

### 📊 Visualisations {#visualisations}

4 onglets d'analyse :

1. **Tendances régionales** : Rendements moyens par région et culture (barres groupées + boîtes à moustaches)
2. **Impact climatique** : Nuages de points pluviométrie/température vs rendement, heatmap
3. **Calendrier cultural** : Périodes de semis/récolte par culture + diagramme de Gantt
4. **Carte des rendements** : Carte interactive du Togo avec rendements par région

---

### 📂 Analyse de fichiers (RAG) {#rag}

#### Formats acceptés

| Format | Extension | Traitement |
|--------|-----------|------------|
| **CSV** | `.csv` | Détection auto colonnes + prévisions |
| **Excel** | `.xlsx`, `.xls` | Détection auto colonnes + prévisions |
| **PDF** | `.pdf` | Extraction texte + analyse IA |

#### Workflow CSV / Excel

1. **Glissez-déposez** votre fichier dans la zone d'upload
2. **Vérifiez le mapping** des colonnes détectées automatiquement
3. **Corrigez** si nécessaire via les menus déroulants
4. Cliquez sur **✅ Valider et analyser**
5. Consultez les statistiques, graphiques et prévisions batch
6. **Téléchargez** les prévisions en CSV

#### Colonnes attendues pour les prévisions

```
region | culture | type_sol | surface_ha | pluviometrie_mm | temperature_moyenne_c
```

> Le système détecte automatiquement les synonymes courants :  
> `region` → `zone`, `localite` ; `pluviometrie_mm` → `pluie`, `rain`, `precip`

#### Workflow PDF

1. Uploadez votre document PDF
2. Le texte est extrait automatiquement
3. Cliquez sur **🤖 Analyser avec l'IA** (nécessite la clé Groq)
4. Obtenez une synthèse structurée du document

---

### 🤖 AgroBot {#agrobot}

Assistant IA agricole propulsé par **LLaMA 3.3-70B** via l'API Groq.

#### Utilisation

1. Tapez votre question dans le champ en bas de page
2. AgroBot répond en français avec des informations agronomiques précises
3. Utilisez les **suggestions rapides** pour des questions fréquentes

#### Exemples de questions

- « Quels sont les besoins en eau du maïs au Togo ? »
- « Comment améliorer la fertilité des sols sableux de la région Savanes ? »
- « Quand semer le sorgho dans la région Kara ? »
- « Comment lutter contre les ravageurs du mil ? »
- « Expliquez-moi ce que signifie un rendement de 2.5 t/ha »

#### Historique

La conversation est conservée pendant toute votre session.  
Cliquez sur **🗑 Effacer** pour réinitialiser.

> **Prérequis** : Clé GROQ_API_KEY configurée dans `.env`

---

### 📋 Historique {#historique}

Toutes vos prévisions sont automatiquement sauvegardées dans la session.

- **Filtres** : par culture, région, niveau de risque
- **Graphique** : évolution des rendements dans le temps
- **Export CSV** de l'historique complet
- **Effacer** : réinitialise l'historique

> L'historique est conservé pendant la session Streamlit uniquement.  
> Exportez en CSV pour un stockage permanent.

---

### 📈 Rapports {#rapports}

3 onglets :

1. **Synthèse des prévisions** : KPI globaux, graphiques camembert/barres, distribution des risques
2. **Rapport mensuel** : Sélectionnez un mois pour voir les prévisions correspondantes
3. **Performance du modèle** : R², MAE, RMSE, MAPE, validation croisée, importance des features

---

## 6. Formats de fichiers supportés {#formats}

### CSV

```csv
region,culture,type_sol,surface_ha,pluviometrie_mm,temperature_moyenne_c
Kara,Maïs,Argileux,5.0,900,27.5
Maritime,Sorgho,Sableux,3.2,750,28.0
```

**Encodages** supportés : UTF-8, Latin-1, CP1252 (détection automatique)

### Excel (.xlsx / .xls)

Même structure que le CSV.  
La première feuille est utilisée par défaut.

### PDF

N'importe quel PDF lisible avec du texte extractible.  
Les PDF scannés (images) ne sont pas supportés.

---

## 7. Modèle Machine Learning {#modele-ml}

### Architecture

| Composant | Détail |
|-----------|--------|
| **Modèle principal** | XGBoost Regressor |
| **Modèle secondaire** | LightGBM Regressor |
| **Ensemble** | Moyenne pondérée (60% XGBoost + 40% LightGBM) |
| **Optimisation** | Optuna (30 trials, KFold 3-fold) |
| **Validation** | KFold 5-fold cross-validation |

### Features utilisées

| Feature | Source | Description |
|---------|--------|-------------|
| `region` | Saisie | Région du Togo |
| `culture` | Saisie | Type de culture |
| `type_sol` | Saisie | Nature du sol |
| `surface_ha` | Saisie | Surface cultivée |
| `pluviometrie_mm` | Saisie / Météo | Pluviométrie cumulée |
| `temperature_moyenne_c` | Saisie / Météo | Température moyenne |
| `indice_hydrique` | Calculé | Ratio pluie / optimal par culture |
| `stress_thermique` | Calculé | Écart à la température optimale |
| `surface_log` | Calculé | log(surface) |
| `pluvio_temp_inter` | Calculé | Interaction pluie × température |
| `score_region` | Calculé | Encodage ordinal des régions |

### Métriques typiques (données Togo)

| Métrique | Valeur |
|----------|--------|
| R² | > 0.88 |
| MAE | < 0.30 t/ha |
| RMSE | < 0.40 t/ha |
| MAPE | < 12% |

---

## 8. FAQ {#faq}

**Q : Le modèle met longtemps au premier lancement.**  
R : Normal — le modèle est entraîné et optimisé au premier lancement (~2-5 min). Ensuite, il se charge instantanément.

**Q : La météo ne s'affiche pas.**  
R : Vérifiez votre connexion internet. L'API Open-Meteo est gratuite mais nécessite internet. Les valeurs par défaut sont utilisées en l'absence de connexion.

**Q : AgroBot ne répond pas.**  
R : Vérifiez que votre clé Groq est correctement configurée dans le fichier `.env`.

**Q : Mon fichier CSV n'est pas reconnu.**  
R : Vérifiez l'encodage (UTF-8 recommandé). Si les colonnes ne sont pas détectées, utilisez le mapping manuel.

**Q : Comment améliorer la précision du modèle ?**  
R : Ajoutez plus de données dans `data_togo/donnees_agricoles_togo.csv` et supprimez le fichier `models/agro_predict_model.pkl` pour forcer un ré-entraînement.

**Q : Les données sont-elles sauvegardées en permanence ?**  
R : Non — l'historique de session est perdu à la fermeture. Exportez-le en CSV pour le conserver.

---

## 9. Architecture technique {#architecture}

```
prevision/
├── app.py                    # Point d'entrée Streamlit
├── config.py                 # Configuration centralisée
├── requirements.txt          # Dépendances Python
├── .env                      # Clés API (à créer)
├── .env.example              # Modèle de configuration
├── USER_GUIDE.md             # Ce document
│
├── core/                     # Logique métier
│   ├── ml_model.py           # Modèle ML (XGBoost + LightGBM + Optuna)
│   ├── weather.py            # API météo (Open-Meteo)
│   └── data_processor.py     # Traitement de données
│
├── modules/                  # Pages de l'interface
│   ├── styles.py             # CSS global
│   ├── home.py               # Page d'accueil
│   ├── prediction.py         # Page de prévision
│   ├── visualizations.py     # Visualisations
│   ├── history.py            # Historique
│   ├── rag.py                # Module RAG (upload fichiers)
│   ├── chatbot.py            # AgroBot (Groq)
│   └── report.py             # Rapports
│
├── data_togo/                # Données d'entraînement
│   └── donnees_agricoles_togo.csv
│
├── models/                   # Modèles sauvegardés (auto-généré)
│   └── agro_predict_model.pkl
│
├── tests/                    # Suite de tests pytest
│   ├── test_model.py
│   ├── test_weather.py
│   ├── test_data_processor.py
│   └── test_chatbot.py
│
└── temp/                     # Fichiers temporaires (auto-géré)
```

### Flux de données

```
Utilisateur
    ↓
app.py (routing)
    ↓
modules/prediction.py
    ↓ input            ↓ météo
core/ml_model.py    core/weather.py
    ↓                  ↓
Prédiction XGBoost+LGB  Open-Meteo API
    ↓
Résultats → UI Streamlit
```

---

## Contributeurs

- **Développement** : Équipe Le Gret
- **Contact** : tengacherif@gmail.com
- **Version** : 2.0 – Février 2026
- **Licence** : Usage interne Le Gret

---

*AgroPredict Togo – L'IA au service de l'agriculture durable* 🌾
