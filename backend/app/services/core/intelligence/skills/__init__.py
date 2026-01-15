"""
Base Skill Interface.

All skills must inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSkill(ABC):
    """
    Abstract base class for AI Skills.
    Skills are modular logic units that process context and return prompt injections.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute the skill logic.
        
        Args:
            context: Dictionary containing available data (resume, job_role, etc.)
            
        Returns:
            str: Text to be injected into the system prompt.
                 Return empty string if no relevant output.
        """
        pass
