# agents/base_agent.py
"""
Base Agent - Abstract base class for all agents
Provides common functionality and lazy LLM initialization
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from llm.llm_client import get_llm_client

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    
    Provides:
    - Lazy LLM client initialization
    - Logging setup
    - Error handling pattern
    """

    def __init__(self):
        """Initialize the Base Agent."""
        self.llm_client = None
        self._initialized = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def _ensure_initialized(self):
        """Lazy initialization of LLM client."""
        if not self._initialized:
            try:
                self.llm_client = get_llm_client()
                self.logger.info(f"{self.__class__.__name__} initialized with LLM client")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM client: {e}")
                self.llm_client = None
            finally:
                self._initialized = True

    @abstractmethod
    def process(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Process method to be implemented by subclasses.
        
        Returns:
            Result dictionary with status and data
        """
        pass

    def _handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Common error handling for all agents.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Standardized error response
        """
        error_msg = f"Error in {self.__class__.__name__}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        self.logger.error(error_msg)
        return {
            "success": False,
            "error": str(error),
            "context": context
        }

    def _log_step(self, step_num: int, action: str, status: str = "executing"):
        """Log a step execution for debugging."""
        self.logger.info(f"Step {step_num}: {action} ({status})")