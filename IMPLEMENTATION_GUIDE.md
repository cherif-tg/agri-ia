# 🚀 PLAN DE MISE EN PLACE - Guide Pratique

**Comment implémenter les 3 améliorations étape par étape**

---

## 📋 SOMMAIRE DES 3 PHASES

| Phase | Amélioration | Durée | Fichiers | Priorité |
|-------|-------------|-------|----------|----------|
| 1 | ML Optimization | 2-3h | `train_ml_advanced.py` + data_preparator.py | ⭐ HAUTE |
| 2 | RAG Architecture | 4-5h | 5 modules RAG + page | ⭐ MOYENNE |
| 3 | Chatbot Assistant | 2-3h | 5 modules chatbot + page | ⭐ MOYENNE |

**Total: 10-12 heures de travail** (5-6 heures si parallèle)

---

## 🟢 PHASE 1: ML IMPROVEMENT (Commencer Par Ici!)

### ✅ Vous avez déjà:
- `IMPROVING_ML.md` - Guide ML complet
- 2 scripts prêts à utiliser:
  - `data_preparator.py` - Charge FAOSTAT
  - `train_ml_advanced.py` - XGBoost + GridSearch

### 📝 ÉTAPES:

#### Step 1: Créer dossier structure
```bash
prevision/
├── training/          ← Nouveau dossier
│   ├── __init__.py
│   ├── data_preparator.py       # Copier du IMPROVING_ML.md
│   ├── train_ml_advanced.py     # Copier du IMPROVING_ML.md
│   └── evaluate_model.py         # Optionnel
│
├── data/
│   └── augmented_data.csv       # Sera créé
│
└── models/
    ├── modele_rendement_agricole.pkl          # Ancien
    └── modele_rendement_agricole_v2_xgb.pkl  # Nouveau (sera créé)
```

#### Step 2: Installer dépendances
```bash
pip install xgboost==2.0.0 optuna==3.14.0 scikit-learn>=1.3.0
```

#### Step 3: Préparer données
```bash
cd prevision/training
python data_preparator.py
# Output: ../data/augmented_data.csv (5000+ lignes)
```

#### Step 4: Entraîner modèle
```bash
python train_ml_advanced.py
# Output: ../models/modele_rendement_agricole_v2_xgb.pkl
# + rapport avec R² et MAE
```

#### Step 5: Tester le nouveau modèle
```python
# Dans Python
import joblib
model = joblib.load("models/modele_rendement_agricole_v2_xgb.pkl")
predictions = model.predict([[25, 800, 5, 1, 0.8]])  # Test
```

#### Step 6: Basculer en production
```python
# Dans models/predictor.py, ligne ~30
# Changer:
self.model_path = Path("models/modele_rendement_agricole.pkl")
# En:
self.model_path = Path("models/modele_rendement_agricole_v2_xgb.pkl")
```

### ⏱️ Temps:
- Setup: 5 min
- Préparation données: 10 min
- Entraînement: 30-60 min (GridSearch)
- Tests: 5 min
- **Total: 1-2 heures**

### 🎯 Résultats attendus:
- ✅ Ancien modèle: R² = 0.72, MAE = 0.45
- ✅ Nouveau modèle: R² = 0.76-0.78, MAE = 0.35-0.38
- ✅ **Amélioration: +5-7% précision**

---

## 🟠 PHASE 2: RAG ARCHITECTURE

### ✅ Vous avez déjà:
- `RAG_ARCHITECTURE.md` - Guide complet RAG
- 5 fichiers prêts à copier:
  - `rag/loader.py` - Charger CSV/PDF
  - `rag/extractor.py` - Extraire données
  - `rag/processor.py` - Nettoyer données
  - `rag/batch_predictor.py` - Prédictions batch
  - `rag/visualizer.py` - Graphiques auto
  - `components/rag_analysis.py` - Page Streamlit

### 📝 ÉTAPES:

#### Step 1: Structure dossiers
```bash
prevision/
├── rag/
│   ├── __init__.py
│   ├── loader.py            # Copier du RAG_ARCHITECTURE.md
│   ├── processor.py         # Copier du RAG_ARCHITECTURE.md
│   ├── batch_predictor.py   # Copier du RAG_ARCHITECTURE.md
│   └── visualizer.py        # Copier du RAG_ARCHITECTURE.md
│
├── components/
│   ├── rag_analysis.py      # Copier du RAG_ARCHITECTURE.md (nouveau)
│   └── ...
│
└── temp/                    # Dossier temporaire
```

#### Step 2: Installer dépendances
```bash
pip install langchain==0.1.0 chromadb==0.4.0 pdf2image==1.16.0 pdfplumber==0.10.0
```

#### Step 3: Tester chaque module
```python
# Test 1: Charger CSV
from rag.loader import FileLoader
df = FileLoader.load_csv("data_togo/donnees_agricoles_togo.csv")

# Test 2: Identifier colonnes
from rag.processor import DataProcessor
col_mapping = DataProcessor.identify_columns(df)

# Test 3: Prédictions batch
from rag.batch_predictor import BatchPredictor
predictor = BatchPredictor()
df_results = predictor.predict_batch(df, col_mapping)

# Test 4: Visualisations
from rag.visualizer import RAGVisualizer
plots = RAGVisualizer.generate_all_visualizations(df_results, col_mapping)
```

#### Step 4: Ajouter page Streamlit
- Copier `components/rag_analysis.py` du guide

#### Step 5: Intégrer dans app.py
```python
# Dans imports (top du file)
from components.rag_analysis import show_rag_analysis_page

# Dans la section "elif page == ..." ajouter:
elif page == "📊 Analyse Batch (RAG)":
    show_rag_analysis_page()

# Dans le st.radio add:
pages = [
    "Accueil",
    "Prévision",
    "📊 Analyse Batch (RAG)",    # ← Nouveau
    "Visualisations",
    "Historique",
    "À Propos"
]
```

### ⏱️ Temps:
- Setup: 10 min
- Installation modules: 5 min
- Copier 5 fichiers: 5 min
- Tests unitaires: 15 min
- Intégration Streamlit: 10 min
- **Total: 45 minutes - 1 heure**

### 🎯 Fonctionnalités:
- ✅ Upload CSV/PDF
- ✅ Auto-identification colonnes
- ✅ Prédictions batch (100+ lignes)
- ✅ Graphiques auto-générés:
  - Distribution rendements
  - Risques par zone
  - Production par culture
  - Relation pluviométrie-rendement

---

## 🔵 PHASE 3: CHATBOT ASSISTANT

### ✅ Vous avez déjà:
- `CHATBOT_GUIDE.md` - Guide complet chatbot
- 5 fichiers prêts:
  - `chatbot/base.py` - Interface abstraite
  - `chatbot/local_llm.py` - Ollama (gratuit)
  - `chatbot/api_llm.py` - OpenAI (API)
  - `chatbot/prompts.py` - System prompts
  - `components/chatbot_ui.py` - Page Streamlit

### 📝 ÉTAPES:

#### Step 1: Choisir option (A ou B):

**Option A: LOCAL (Recommandé)**
```bash
# 1. Installer Ollama
# https://ollama.ai
# Windows/Mac/Linux

# 2. Démarrer
ollama serve

# 3. Pull modèle
ollama pull mistral

# 4. Vérifier
curl http://localhost:11434/api/tags
# Doit afficher mistral
```

**Option B: OPENAI API**
```bash
# 1. Compte OpenAI
# https://platform.openai.com

# 2. API key
# https://platform.openai.com/api-keys

# 3. .env file
echo "OPENAI_API_KEY=sk-..." > .env

# 4. pip install
pip install openai
```

#### Step 2: Structure dossiers
```bash
prevision/
├── chatbot/
│   ├── __init__.py
│   ├── base.py              # Copier du CHATBOT_GUIDE.md
│   ├── local_llm.py         # Copier du CHATBOT_GUIDE.md (pour Ollama)
│   ├── api_llm.py           # Copier du CHATBOT_GUIDE.md (pour OpenAI)
│   └── prompts.py           # Copier du CHATBOT_GUIDE.md
│
├── components/
│   ├── chatbot_ui.py        # Copier du CHATBOT_GUIDE.md (nouveau)
│   └── ...
│
└── .env                     # Si OpenAI
```

#### Step 3: Tests
```python
# Test Ollama (si choisi)
from chatbot.local_llm import OllamaChat
chat = OllamaChat()
chat.initialize()
response = chat.chat("Comment utiliser?")
print(response.text)

# Test OpenAI (si choisi)
from chatbot.api_llm import OpenAIChat
chat = OpenAIChat(api_key="sk-...")
chat.initialize()
response = chat.chat("Comment utiliser?")
```

#### Step 4: Ajouter page Streamlit
- Copier `components/chatbot_ui.py`

#### Step 5: Intégrer dans app.py
```python
# Dans imports
from components.chatbot_ui import show_chatbot_page

# Ajouter page
elif page == "💬 Assistant IA":
    show_chatbot_page()

# st.radio
pages = [
    "Accueil",
    "Prévision",
    "💬 Assistant IA",          # ← Nouveau
    "📊 Analyse Batch (RAG)",
    "Visualisations",
    "Historique",
    "À Propos"
]
```

### ⏱️ Temps:
- Setup Ollama/OpenAI: 10 min
- Copier 5 fichiers: 5 min
- Tests: 10 min
- Intégration: 10 min
- **Total: 35-45 minutes**

### 🎯 Fonctionnalités:
- ✅ Chat interactif
- ✅ 2 options (Local + API)
- ✅ 3 niveaux expertise
- ✅ Context awareness
- ✅ Historique conversation

---

## 🎯 CHECKLIST COMPLÈTE

### AVANT De Commencer:
```
☐ Vérifier dossier prevision/ existe
☐ Avoir Python 3.10+
☐ pip à jour (pip install --upgrade pip)
☐ Parcourir IMPROVING_ML.md, RAG_ARCHITECTURE.md, CHATBOT_GUIDE.md
```

### PHASE 1 - ML (2-3h):
```
☐ Créer dossier training/
☐ Copier data_preparator.py
☐ Copier train_ml_advanced.py
☐ pip install xgboost optuna

☐ Lancer data_preparator.py
  ☐ Vérifier data/augmented_data.csv créé
  ☐ Vérifier 5000+ lignes
  
☐ Lancer train_ml_advanced.py
  ☐ Attendre 30-60min (GridSearch)
  ☐ Vérifier models/modele_rendement_agricole_v2_xgb.pkl créé
  ☐ Lire rapport: R² = ?, MAE = ?
  
☐ Tester nouveau modèle
  ☐ Importer modèle en Python
  ☐ Faire prédiction test
  ☐ Comparer avec ancien modèle
  
☐ Changer path dans models/predictor.py
  ☐ 1 lignes à modifier
  ☐ Redémarrer app.py
  ☐ Tester prédiction dans UI
```

### PHASE 2 - RAG (4-5h):
```
☐ pip install langchain chromadb pdf2image pdfplumber

☐ Créer dossier rag/
☐ Copier loader.py
☐ Copier processor.py
☐ Copier batch_predictor.py
☐ Copier visualizer.py

☐ Tests unitaires
  ☐ Test loader (CSV)
  ☐ Test processor (identify columns)
  ☐ Test predictor (batch predictions)
  ☐ Test visualizer (plot generation)

☐ Copier components/rag_analysis.py
☐ Intégrer dans app.py
  ☐ Import show_rag_analysis_page
  ☐ Ajouter elif page == "📊 Analyse Batch (RAG)"
  ☐ Ajouter "📊 Analyse Batch (RAG)" dans st.radio
  
☐ Test en Streamlit
  ☐ Lancer app.py
  ☐ Naviguer vers "Analyse Batch"
  ☐ Upload fichier CSV
  ☐ Vérifier prédictions générées
  ☐ Vérifier graphiques affichés
```

### PHASE 3 - CHATBOT (2-3h):
```
☐ CHOISIR: Ollama XOR OpenAI

Si OLLAMA:
  ☐ Installer Ollama (https://ollama.ai)
  ☐ ollama serve (laisser tourner)
  ☐ ollama pull mistral
  ☐ Vérifier: curl http://localhost:11434/api/tags

Si OPENAI:
  ☐ Créer compte et API key
  ☐ Créer .env avec OPENAI_API_KEY=sk-...
  ☐ pip install openai

☐ pip install (si pas déjà fatto)

☐ Créer dossier chatbot/
☐ Copier base.py
☐ Copier local_llm.py OU api_llm.py
☐ Copier prompts.py

☐ Tests unitaires
  ☐ Initialiser chat instance
  ☐ Faire test message
  ☐ Vérifier réponse

☐ Copier components/chatbot_ui.py
☐ Intégrer dans app.py
  ☐ Import show_chatbot_page
  ☐ Ajouter elif page == "💬 Assistant IA"
  ☐ Ajouter "💬 Assistant IA" dans st.radio
  
☐ Test en Streamlit
  ☐ Lancer app.py
  ☐ Naviguer vers "Assistant IA"
  ☐ Choisir mode (Ollama/OpenAI)
  ☐ Envoyer message test
  ☐ Vérifier réponse
```

---

## 📊 DÉPENDANCES FINALES

Ajouter à `requirements.txt`:

```
# ML Amélioré
xgboost==2.0.0
optuna==3.14.0
scikit-learn>=1.3.0
joblib>=1.3.0

# RAG
langchain==0.1.0
chromadb==0.4.0
pdf2image==1.16.0
pdfplumber==0.10.0

# Chatbot
ollama==0.1.0          # Pour Ollama local
openai==1.6.0          # Pour OpenAI API (optionnel)
tiktoken==0.5.0        # Pour tokenization
```

---

## ⚠️ TROUBLESHOOTING

**Problème: Ollama pas connecté**
```
Solution: 
- Vérifier: ollama serve tourne
- Vérifier port 11434
- Vérifier modèle installé: ollama pull mistral
```

**Problème: OpenAI API key invalide**
```
Solution:
- Vérifier .env created correctly
- Vérifier OPENAI_API_KEY=sk-...
- Vérifier key valide sur https://platform.openai.com/api-keys
```

**Problème: Modèle ML pas trouvé**
```
Solution:
- Vérifier dossier models/ existe
- Vérifier path dans predictor.py correct
- Lancer train_ml_advanced.py de nouveau
```

**Problème: RAG fichier trop gros**
```
Solution:
- Limiter nombre lignes (dans processor.py)
- Utiliser format CSV au lieu de PDF
- Découper en plusieurs fichiers
```

---

## 🚀 APRÈS LES 3 PHASES

Une fois tout complété:

1. ✅ **ML**: Prédictions +7% plus précises
2. ✅ **RAG**: Peut analyser batch de 100+ prédictions
3. ✅ **Chatbot**: Utilisateurs ont support 24/7

**Prêt pour déployer!** 🎉

Voir: [DEPLOYMENT.md](DEPLOYMENT.md) pour options.

---

## 💡 TIPS & TRICKS

- **Paralélliser**: Faire Phase 2 et 3 en même temps (RAG + Chatbot indépendants)
- **Tester d'abord**: Run chaque module indépendamment avant intégration
- **Logging**: Vérifier logs (`data/app.log`) si problmes
- **Version control**: `git add`, `git commit` avant/après chaque phase
- **Backup**: Garder ancien modèle (modele_rendement_agricole.pkl) en cas rollback

---

## 📞 SUPPORT

Questions?
- Lire le guide correspondant:
  - ML → IMPROVING_ML.md
  - RAG → RAG_ARCHITECTURE.md
  - Chat → CHATBOT_GUIDE.md
- Vérifier logs: `tail data/app.log`
- Tester modules indépendamment en Python

---

Bon luck! 🍀 Vous pouvez tout faire! 💪
