"""
Local LLM using Ollama
Free, no API key, works offline
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
    
    DEFAULT_MODEL = "mistral"
    OLLAMA_URL = "http://localhost:11434/api"
    
    AVAILABLE_MODELS = {
        "mistral": "Fast & good (7B)",
        "neural-chat": "Chat optimized (7B)",
        "dolphin-mixtral": "Powerful (8x7B)",
        "llama2": "Large & robust (7B/13B/70B)"
    }
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        super().__init__(model_name)
        self.model_name = model_name
        self.is_ready = False
    
    def initialize(self):
        """Check Ollama available"""
        
        try:
            response = requests.get(f"{self.OLLAMA_URL}/tags", timeout=2)
            
            if response.status_code == 200:
                self.is_ready = True
                logger.info("✓ Ollama connected")
                
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                
                if self.model_name not in model_names:
                    logger.warning(f"Model {self.model_name} not installed")
                    return False
                
                return True
            else:
                logger.error("Ollama not accessible")
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ollama not found. Install: https://ollama.ai")
            return False
        except Exception as e:
            logger.error(f"Ollama init error: {e}")
            return False
    
    def chat(self, user_message: str, temperature: float = 0.7) -> ChatResponse:
        """Chat with local LLM"""
        
        if not self.is_ready:
            raise RuntimeError("Ollama not initialized")
        
        self.add_message("user", user_message)
        
        try:
            payload = {
                "model": self.model_name,
                "messages": self.get_history(),
                "temperature": temperature,
                "stream": False
            }
            
            logger.info(f"Sending to {self.model_name}...")
            start = time.time()
            
            response = requests.post(
                f"{self.OLLAMA_URL}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise ValueError(f"API error: {response.status_code}")
            
            data = response.json()
            assistant_message = data.get('message', {}).get('content', '')
            
            self.add_message("assistant", assistant_message)
            
            elapsed = time.time() - start
            logger.info(f"Response in {elapsed:.2f}s")
            
            return ChatResponse(
                text=assistant_message,
                model=self.model_name,
                tokens_used=0
            )
        
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate via prompt"""
        
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
            logger.error(f"Generate error: {e}")
            raise
    
    @staticmethod
    def is_installed() -> bool:
        """Check if Ollama installed"""
        try:
            response = requests.get(
                f"{OllamaChat.OLLAMA_URL}/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
