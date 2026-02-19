"""
Abstract base class for LLM
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Chat message"""
    role: str  # 'user', 'assistant', 'system'
    content: str


@dataclass
class ChatResponse:
    """Model response"""
    text: str
    model: str
    tokens_used: int = 0


class BaseLLM(ABC):
    """Abstract LLM interface"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.conversation_history: List[Message] = []
    
    @abstractmethod
    def initialize(self):
        """Initialize model"""
        pass
    
    @abstractmethod
    def chat(self, user_message: str) -> ChatResponse:
        """Chat with model"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text"""
        pass
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.conversation_history.append(Message(role, content))
    
    def get_history(self) -> List[Dict]:
        """Get formatted history"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
    
    def clear_history(self):
        """Clear history"""
        self.conversation_history = []
        logger.info("Chat history cleared")
    
    def set_context(self, system_prompt: str):
        """Set system context"""
        self.conversation_history = [
            Message("system", system_prompt)
        ]
