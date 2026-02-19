# 🤖 CHATBOT ASSISTANT - Guide Complet

**Chatbot AI simple pour aider les utilisateurs**

---

## 🎯 CAPACITÉS

- 💬 Répondre questions sur le système
- 📖 Guide d'utilisation auto-généré
- 🌾 Conseils agricoles basiques
- 🔧 Aide fonctionnalités
- 📊 Explications prédictions

---

## 🔀 2 OPTIONS

### Option 1️⃣ : LOCAL (Ollama) ⭐ RECOMMANDÉ

✅ Gratuit  
✅ Rien à configurer  
✅ Fonctionne offline  
✅ Pas d'API key

❌ Plus lent (3-5 sec réponse)
❌ Besoin 4GB RAM minimum

---

### Option 2️⃣ : API (OpenAI/Gemini)

✅ Super rapide (1-2 sec)  
✅ Réponses excellentes  

❌ Coûte argent  
❌ Besoin API key  
❌ Dépend internet

**Choice: Faire les DEUX = utilisateur choisit!**

---

## 📦 DÉPENDANCES A AJOUTER

```
# Chat & LLM
ollama==0.1.0
openai==1.6.0

# Tokenization
tiktoken==0.5.0
```

---

## 🏗️ ARCHITECTURE CHATBOT

```
prevision/
├── chatbot/
│   ├── __init__.py
│   ├── base.py        ← Interface abstraite
│   ├── local_llm.py   ← Ollama local
│   ├── api_llm.py     ← OpenAI/Gemini
│   ├── context.py     ← Context manager
│   └── prompts.py     ← System prompts
│
└── components/
    └── chatbot_ui.py  ← Page Streamlit
```

---

## 💻 FICHIER 1 : BASE ABSTRAITE

Créer `chatbot/base.py`:

```python
"""
Interface abstraite pour LLM
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Un message de chat"""
    role: str  # 'user', 'assistant', 'system'
    content: str


@dataclass
class ChatResponse:
    """Réponse du modèle"""
    text: str
    model: str
    tokens_used: int = 0


class BaseLLM(ABC):
    """Interface LLM abstraite"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.conversation_history: List[Message] = []
    
    @abstractmethod
    def initialize(self):
        """Initialize le modèle"""
        pass
    
    @abstractmethod
    def chat(self, user_message: str) -> ChatResponse:
        """Répondre à message"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Générer texte libre"""
        pass
    
    def add_message(self, role: str, content: str):
        """Ajouter message à historique"""
        self.conversation_history.append(Message(role, content))
    
    def get_history(self) -> List[Dict]:
        """Obtenir historique formaté"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
    
    def clear_history(self):
        """Effacer historique"""
        self.conversation_history = []
        logger.info("Historique chat effacé")
    
    def set_context(self, system_prompt: str):
        """Set system context"""
        self.conversation_history = [
            Message("system", system_prompt)
        ]
```

---

## 🏠 FICHIER 2 : OLLAMA LOCAL

Créer `chatbot/local_llm.py`:

```python
"""
Chatbot local utilisant Ollama
Gratuit, pas d'API key, fonctionne offline
"""

import requests
import json
import logging
import time
from typing import Optional
from .base import BaseLLM, ChatResponse

logger = logging.getLogger(__name__)


class OllamaChat(BaseLLM):
    """Local LLM via Ollama"""
    
    DEFAULT_MODEL = "mistral"  # Léger & rapide
    OLLAMA_URL = "http://localhost:11434/api"
    
    AVAILABLE_MODELS = {
        "mistral": "Fast & good (7B)",
        "neural-chat": "Optimisé chat (7B)",
        "dolphin-mixtral": "Puissant (8x7B)",
        "llama2": "Large & robuste (7B/13B/70B)"
    }
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        super().__init__(model_name)
        self.model_name = model_name
        self.is_ready = False
    
    def initialize(self):
        """Check Ollama disponible"""
        
        try:
            response = requests.get(f"{self.OLLAMA_URL}/tags", timeout=2)
            
            if response.status_code == 200:
                self.is_ready = True
                logger.info("✓ Ollama connecté")
                
                # Check model
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                
                if self.model_name not in model_names:
                    logger.warning(f"Model {self.model_name} not installed")
                    return False
                
                return True
            else:
                logger.error("Ollama pas accessible")
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ollama non trouvé. Installer: https://ollama.ai")
            return False
        except Exception as e:
            logger.error(f"Erreur init Ollama: {e}")
            return False
    
    def chat(self, user_message: str, temperature: float = 0.7) -> ChatResponse:
        """Chat avec local LLM"""
        
        if not self.is_ready:
            raise RuntimeError("Ollama not initialized")
        
        # Ajouter message utilisateur
        self.add_message("user", user_message)
        
        try:
            # Préparer payload
            payload = {
                "model": self.model_name,
                "messages": self.get_history(),
                "temperature": temperature,
                "stream": False
            }
            
            logger.info(f"Envoi à {self.model_name}...")
            start = time.time()
            
            # Appel API
            response = requests.post(
                f"{self.OLLAMA_URL}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise ValueError(f"API error: {response.status_code}")
            
            data = response.json()
            
            # Extraire réponse
            assistant_message = data.get('message', {}).get('content', '')
            
            # Ajouter à historique
            self.add_message("assistant", assistant_message)
            
            elapsed = time.time() - start
            logger.info(f"Réponse en {elapsed:.2f}s")
            
            return ChatResponse(
                text=assistant_message,
                model=self.model_name,
                tokens_used=0  # Ollama ne fournit pas
            )
        
        except Exception as e:
            logger.error(f"Erreur chat: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Générer via prompt simple"""
        
        if not self.is_ready:
            raise RuntimeError("Ollama not initialized")
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.OLLAMA_URL}/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise ValueError(f"API error: {response.status_code}")
            
            data = response.json()
            return data.get('response', '')
        
        except Exception as e:
            logger.error(f"Erreur generate: {e}")
            raise
    
    @staticmethod
    def is_installed() -> bool:
        """Check si Ollama installé"""
        try:
            response = requests.get(
                f"{OllamaChat.OLLAMA_URL}/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
```

---

## 🌐 FICHIER 3 : OPENAI API

Créer `chatbot/api_llm.py`:

```python
"""
Chatbot API OpenAI
Rapide mais coûte de l'argent
"""

import os
from typing import Optional
import logging
import json
from .base import BaseLLM, ChatResponse

logger = logging.getLogger(__name__)


class OpenAIChat(BaseLLM):
    """Chat via OpenAI API"""
    
    AVAILABLE_MODELS = {
        "gpt-3.5-turbo": "Rapide & économique",
        "gpt-4-turbo": "Puissant & cher",
        "gpt-4": "Le meilleur (le plus cher)"
    }
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        super().__init__(model_name)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.is_ready = False
    
    def initialize(self):
        """Init OpenAI client"""
        
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY non configurée")
            logger.error("Créer .env avec: OPENAI_API_KEY=sk-...")
            return False
        
        try:
            from openai import OpenAI
            
            self.client = OpenAI(api_key=self.api_key)
            
            # Test connection
            self.client.models.list()
            
            self.is_ready = True
            logger.info(f"✓ OpenAI {self.model_name} connecté")
            return True
        
        except ImportError:
            logger.error("❌ openai package pas installé: pip install openai")
            return False
        except Exception as e:
            logger.error(f"Erreur OpenAI init: {e}")
            return False
    
    def chat(self, user_message: str, temperature: float = 0.7) -> ChatResponse:
        """Chat avec API OpenAI"""
        
        if not self.is_ready:
            raise RuntimeError("OpenAI not initialized")
        
        # Ajouter message
        self.add_message("user", user_message)
        
        try:
            logger.info(f"Appel OpenAI {self.model_name}...")
            
            # Appel API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.get_history(),
                temperature=temperature,
                max_tokens=1000
            )
            
            # Extraire réponse
            assistant_message = response.choices[0].message.content
            
            # Ajouter à historique
            self.add_message("assistant", assistant_message)
            
            tokens_used = response.usage.total_tokens
            logger.info(f"Tokens utilisés: {tokens_used}")
            
            return ChatResponse(
                text=assistant_message,
                model=self.model_name,
                tokens_used=tokens_used
            )
        
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Générer texte via prompt simple"""
        
        if not self.is_ready:
            raise RuntimeError("OpenAI not initialized")
        
        try:
            response = self.client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].text
        
        except Exception as e:
            logger.error(f"Erreur generate: {e}")
            raise
```

---

## 📝 FICHIER 4 : SYSTEM PROMPTS

Créer `chatbot/prompts.py`:

```python
"""
System prompts pour chatbot agricole
"""

SYSTEM_PROMPTS = {
    "default": """Tu es un assisant IA pour un système de prévision agricole au Togo.
Tu aides les agriculteurs à:
- Comprendre le système de prévision
- Interpréter les prédictions de rendement
- Donner conseils agricoles basiques
- Utiliser l'interface

Réponds en FRANÇAIS avec:
- Explications simples et clairs
- Exemples concrets
- Conseils pratiques
- Pas de jargon technique inutile

Si question pas sur agriculture ou système - redirection polite.
""",
    
    "expert": """Tu es expert agricole IA pour un système de prédiction.
Tu aides sur:
- Analyse détaillée rendement
- Facteurs agricoles complexes
- Optimisation production
- Tendances climatiques

Tu peux utiliser termes techniques mais toujours explique.
Références, données quand possible.
""",
    
    "simple": """Tu es assistant sympa pour agriculteurs débutants.
Langage très simple, pas de jargon.
Réponds courtes (2-3 phrases max).
Encourage l'utilisation du système.
Peut utiliser emojis!
"""
}


def get_system_prompt(mode: str = "default") -> str:
    """Obtenir prompt système"""
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])


def get_context_injection(history_stats: dict = None) -> str:
    """Contexte additionnelle pour chatbot"""
    
    if not history_stats:
        return ""
    
    return f"""
CONTEXTE UTILISATEUR:
- Prédictions faites: {history_stats.get('total_predictions', 0)}
- Dernière région: {history_stats.get('last_region', 'Non spécifiée')}
- Dernière culture: {history_stats.get('last_culture', 'Non spécifiée')}
- Rendement moyen historique: {history_stats.get('avg_rendement', 'N/A')} t/ha
"""
```

---

## 🎨 FICHIER 5 : PAGE STREAMLIT

Créer `components/chatbot_ui.py`:

```python
"""
Interface Streamlit pour chatbot
"""

import streamlit as st
import logging
from pathlib import Path

from chatbot.local_llm import OllamaChat
from chatbot.api_llm import OpenAIChat
from chatbot.prompts import get_system_prompt, get_context_injection

logger = logging.getLogger(__name__)


def initialize_chat_state():
    """Initialise session state pour chat"""
    
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "ollama"
    
    if "chat_instance" not in st.session_state:
        st.session_state.chat_instance = None
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_ready" not in st.session_state:
        st.session_state.chat_ready = False


def get_chat_instance(mode: str, api_key: str = None):
    """Obtenir instance chat"""
    
    try:
        if mode == "ollama":
            chat = OllamaChat("mistral")
            if chat.initialize():
                return chat
            else:
                raise RuntimeError("Ollama not available")
        
        elif mode == "openai":
            chat = OpenAIChat("gpt-3.5-turbo", api_key)
            if chat.initialize():
                return chat
            else:
                raise RuntimeError("OpenAI API not configured")
        
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    except Exception as e:
        logger.error(f"Erreur init chat: {e}")
        return None


def show_chatbot_page():
    """Page chatbot complète"""
    
    initialize_chat_state()
    
    st.markdown("## 🤖 Assistant Agricole IA")
    
    st.info("""
    Posez vos questions sur:
    - 💭 Comment utiliser le système
    - 📊 Comprendre les prédictions
    - 🌾 Conseils agricoles
    - 📈 Optimiser rendement
    """)
    
    # Sélecteur mode
    col1, col2 = st.columns([1, 3])
    
    with col1:
        mode = st.radio(
            "Mode Chat:",
            ["ollama", "openai"],
            format_func=lambda x: "🏠 Local" if x == "ollama" else "🌐 API",
            key="chat_mode_radio"
        )
    
    with col2:
        if mode == "openai":
            api_key = st.text_input(
                "OpenAI API Key:",
                type="password",
                help="sk-..."
            )
        else:
            api_key = None
    
    # Niveau expertise
    level = st.select_slider(
        "Votre niveau:",
        options=["Débutant", "Intermédiaire", "Expert"],
        value="Intermédiaire"
    )
    
    # Init chat
    if not st.session_state.chat_ready:
        if st.button("🚀 Démarrer Chat", use_container_width=True):
            with st.spinner("⏳ Initialisation..."):
                chat = get_chat_instance(mode, api_key)
                
                if chat:
                    # Set system prompt
                    level_map = {
                        "Débutant": "simple",
                        "Intermédiaire": "default",
                        "Expert": "expert"
                    }
                    system_prompt = get_system_prompt(level_map[level])
                    chat.set_context(system_prompt)
                    
                    st.session_state.chat_instance = chat
                    st.session_state.chat_ready = True
                    st.rerun()
                else:
                    st.error(f"❌ Impossible de démarrer {mode}")
    
    # Chat interface
    if st.session_state.chat_ready:
        chat = st.session_state.chat_instance
        
        st.success(f"✓ Chat prêt ({chat.model_name})")
        
        # Messages display
        messages_container = st.container()
        
        with messages_container:
            for msg in chat.get_history():
                if msg['role'] != 'system':
                    with st.chat_message(msg['role']):
                        st.write(msg['content'])
        
        # Input
        user_input = st.chat_input(
            "Votre question...",
            key="chat_input"
        )
        
        if user_input:
            # Ajouter message user
            with st.chat_message("user"):
                st.write(user_input)
            
            # Générer réponse
            try:
                with st.spinner("🤔 Réflexion..."):
                    response = chat.chat(user_input)
                
                # Afficher réponse
                with st.chat_message("assistant"):
                    st.write(response.text)
                    
                    if response.tokens_used > 0:
                        st.caption(f"Tokens: {response.tokens_used}")
            
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Chat error: {e}", exc_info=True)
        
        # Contrôles
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Effacer historique", use_container_width=True):
                chat.clear_history()
                chat.set_context(get_system_prompt())
                st.rerun()
        
        with col2:
            if st.button("🔄 Changer mode", use_container_width=True):
                st.session_state.chat_ready = False
                st.rerun()
```

---

## 🔧 INTÉGRATION DANS APP

Ajouter à `app.py`:

```python
# Dans imports
from components.chatbot_ui import show_chatbot_page

# Ajouter page
elif page == "💬 Assistant IA":
    show_chatbot_page()

# Dans st.radio
pages = [
    "Accueil",
    "Prévision",
    "💬 Assistant IA",        # ← Nouveau
    "📊 Analyse Batch (RAG)",  # ← Nouveau
    "Visualisations",
    "Historique",
    "À Propos"
]
```

---

## 🔴 SETUP GUIDE

### Si vous choisissez OLLAMA (Local):

```bash
# 1. Installer Ollama
# https://ollama.ai

# 2. Démarrer service
ollama serve

# 3. Dans autre terminal, pull modèle
ollama pull mistral

# 4. Vérifier
curl http://localhost:11434/api/tags
```

### Si vous choisissez OPENAI (API):

```bash
# 1. Créer compte OpenAI
# https://platform.openai.com

# 2. Générer API key
# https://platform.openai.com/api-keys

# 3. Créer .env
OPENAI_API_KEY=sk-your-key-here

# 4. pip install openai
```

---

## 💰 COÛTS

**Ollama**: 0€ (gratuit)
**OpenAI**: ~$0.001 par message (très bon marché)

---

## ✅ RÉSUMÉ

Vous avez:
- ✅ Chat local (Ollama) = gratuit
- ✅ Chat API (OpenAI) = rapide
- ✅ 3 niveaux expertise
- ✅ Contexte historique
- ✅ Intégration Streamlit

**Chatbot prêt!** 🎉

---

## 🎬 PROCHAIN

Vous avez maintenant:
1. ✅ **ML IMPROVEMENT** (guide + scripts)
2. ✅ **RAG ARCHITECTURE** (5 modules + page)
3. ✅ **CHATBOT** (2 options + page)

**Prochaine étape:**
Déployer le système! 🚀
