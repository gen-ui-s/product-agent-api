from abc import ABC, abstractmethod
from typing import List, Dict

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def completion(self, messages: List[Dict[str, str]]) -> str:
        """Generate completion from messages"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is properly configured"""
        pass

