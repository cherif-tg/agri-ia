"""
OpenAI API ChatBot
Fast but costs money
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
        "gpt-3.5-turbo": "Fast & cheap",
        "gpt-4-turbo": "Powerful & expensive",
        "gpt-4": "Best (most expensive)"
    }
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        super().__init__(model_name)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.is_ready = False
    
    def initialize(self):
        """Init OpenAI client"""
        
        if not self.api_key:
            logger.error("❌ OPENAI_API_KEY not set")
            logger.error("Create .env with: OPENAI_API_KEY=sk-...")
            return False
        
        try:
            from openai import OpenAI
            
            self.client = OpenAI(api_key=self.api_key)
            
            # Test connection
            self.client.models.list()
            
            self.is_ready = True
            logger.info(f"✓ OpenAI {self.model_name} connected")
            return True
        
        except ImportError:
            logger.error("❌ openai package not installed: pip install openai")
            return False
        except Exception as e:
            logger.error(f"OpenAI init error: {e}")
            return False
    
    def chat(self, user_message: str, temperature: float = 0.7) -> ChatResponse:
        """Chat with OpenAI API"""
        
        if not self.is_ready:
            raise RuntimeError("OpenAI not initialized")
        
        self.add_message("user", user_message)
        
        try:
            logger.info(f"Calling OpenAI {self.model_name}...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.get_history(),
                temperature=temperature,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            self.add_message("assistant", assistant_message)
            
            tokens_used = response.usage.total_tokens
            logger.info(f"Tokens used: {tokens_used}")
            
            return ChatResponse(
                text=assistant_message,
                model=self.model_name,
                tokens_used=tokens_used
            )
        
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text"""
        
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
            logger.error(f"Generate error: {e}")
            raise
