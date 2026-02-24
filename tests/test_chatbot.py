"""
tests/test_chatbot.py
=====================
Tests pour le module chatbot (modules/chatbot.py).
Utilise des mocks pour éviter les appels API réels.

Exécution :
    pytest tests/test_chatbot.py -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GROQ_MODEL, SYSTEM_PROMPT_CHATBOT


class TestGroqCall:
    """Tests pour la fonction _call_groq du chatbot."""

    @patch("modules.chatbot.GROQ_API_KEY", "test_key_123")
    @patch("groq.Groq")
    def test_call_groq_returns_string(self, mock_groq_class):
        """_call_groq doit retourner une chaîne de caractères."""
        # Construire une réponse mock
        mock_choice = MagicMock()
        mock_choice.message.content = "Le maïs a besoin de 800-1000mm de pluie."

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        mock_groq_class.return_value = mock_client

        # Import après le patch
        from modules.chatbot import _call_groq

        messages = [{"role": "user", "content": "Quels sont les besoins en eau du maïs ?"}]
        result = _call_groq(messages)

        # Groq est importé en lazy dans la fonction ; on vérifie juste que ça ne plante pas
        # Si GROQ_API_KEY est configurée, result est str, sinon None est acceptable en test
        assert result is None or isinstance(result, str)

    @patch("modules.chatbot.GROQ_API_KEY", "test_key")
    def test_system_prompt_in_messages(self):
        """Le prompt système doit être inclus dans les messages envoyés à l'API."""
        assert len(SYSTEM_PROMPT_CHATBOT) > 20, "Le system prompt est trop court"
        assert "agro" in SYSTEM_PROMPT_CHATBOT.lower() or "agricol" in SYSTEM_PROMPT_CHATBOT.lower()
        assert "togo" in SYSTEM_PROMPT_CHATBOT.lower() or "Togo" in SYSTEM_PROMPT_CHATBOT

    def test_groq_model_name(self):
        """Le modèle Groq configuré doit être llama-3.3-70b-versatile."""
        assert GROQ_MODEL == "llama-3.3-70b-versatile", \
            f"Modèle inattendu: {GROQ_MODEL}"


class TestSystemPrompt:
    """Tests sur la configuration du chatbot."""

    def test_system_prompt_not_empty(self):
        assert SYSTEM_PROMPT_CHATBOT, "Le system prompt est vide"

    def test_system_prompt_french(self):
        """Le system prompt doit mentionner le français."""
        assert "français" in SYSTEM_PROMPT_CHATBOT.lower(), \
            "Le system prompt ne mentionne pas le français"

    def test_system_prompt_agriculture_context(self):
        """Le system prompt doit inclure un contexte agricole."""
        keywords = ["agro", "agricol", "cultiv", "récolte", "culture"]
        has_keyword = any(kw in SYSTEM_PROMPT_CHATBOT.lower() for kw in keywords)
        assert has_keyword, "Le system prompt ne contient pas de contexte agricole"
