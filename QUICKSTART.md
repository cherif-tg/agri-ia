# ⚡ Démarrage Rapide (5 minutes)

## 1️⃣ Prérequis (1 min)

```bash
# Vérifier Python 3.10+
python --version

# Windows : Ouvrir PowerShell dans prevision/
# Mac/Linux : Ouvrir Terminal
cd prevision
```

## 2️⃣ Installation (2 min)

```bash
# Installer les dépendances
pip install -r requirements.txt
```

**⏱️ Attendre la fin (+- 1 minute)**

## 3️⃣ Copier le Modèle (30 sec)

Placer `modele_rendement_agricole.pkl` dans:
```
prevision/models/modele_rendement_agricole.pkl
```

❌ **Sans ce fichier** : L'app ne fonctionne pas  
✅ **Avec ce fichier** : Prêt à démarrer

## 4️⃣ Lancer l'App (30 sec)

```bash
streamlit run app.py
```

Vous verrez dans le terminal:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Cliquez sur le lien** → L'app s'ouvre ! 🎉

## 5️⃣ Premier Test

1. **Aller à "Prévision"** (Navigation gauche)
2. **Remplir le formulaire** :
   - Région : Maritime
   - Culture : Maïs
   - Superficie : 5 ha
   - Autres : valeurs par défaut
3. **Cliquer "Générer la Prévision"** ✓
4. **Voir les résultats** 📊

## 🎯 C'EST TOUT !

Votre application fonctionne ! 🚀

---

## ❓ Dépannage Rapide

### ❌ Erreur "Modèle n'existe pas"
```
✅ Solution : Copier modele_rendement_agricole.pkl dans models/
```

### ❌ Erreur "ModuleNotFoundError"
```bash
✅ Solution : pip install -r requirements.txt
```

### ❌ L'app ne s'ouvre pas dans le navigateur
```
✅ Solution : Aller manuellement à http://localhost:8501
```

### ❌ "Connexion Internet" dans prévisions
```
✅ Solution : Vérifier votre connexion WiFi/Ethernet
```

---

## 📚 Prochaines Étapes

- 📖 Lire `README.md` pour documentation complète
- 🔧 Lire `GUIDE_DEVELOPPEMENT.md` pour personnaliser
- 🔄 Lire `MIGRATION.md` si vous veniez de l'ancienne version

---

## 🎓 Comprendre la Structure (2 min)

```
prevision/
├── app.py          ← Lance ici avec streamlit run app.py
├── config.py       ← Modifier constantes ICI
├── models/         ← Le modèle ML
├── utils/          ← Outils (BD, météo, validation)
├── components/     ← Les pages de l'app
└── data/           ← BD et logs (créés automatiquement)
```

---

## 🚀 Vous Êtes Prêt!

Explorez l'application et amusez-vous ! 🌾

**Questions ?** Voir `README.md` section "Support"
