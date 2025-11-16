"""Error handling for the multi-agent system."""

import time
from typing import Any, Callable, Optional

from multi_agent.core.exceptions import (
    ConfigurationError,
    LLMError,
    ValidationError,
    WorkflowError,
)


class ErrorHandler:
    """Handles errors and implements retry/rollback logic."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize error handler.
        
        Args:
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def handle_error(self, error: Exception, context: dict) -> dict:
        """Handle error with appropriate strategy.
        
        Args:
            error: Exception to handle
            context: Error context
            
        Returns:
            Resolution information
        """
        if isinstance(error, ConfigurationError):
            return self._handle_configuration_error(error, context)
        elif isinstance(error, ValidationError):
            return self._handle_validation_error(error, context)
        elif isinstance(error, LLMError):
            return self._handle_llm_error(error, context)
        elif isinstance(error, WorkflowError):
            return self._handle_workflow_error(error, context)
        else:
            return self._handle_unknown_error(error, context)
    
    def _handle_configuration_error(
        self,
        error: ConfigurationError,
        context: dict,
    ) -> dict:
        """Handle configuration errors."""
        return {
            "strategy": "fail_fast",
            "message": f"Configuration error: {str(error)}",
            "recoverable": False,
            "context": context,
        }
    
    def _handle_validation_error(
        self,
        error: ValidationError,
        context: dict,
    ) -> dict:
        """Handle validation errors."""
        return {
            "strategy": "rollback",
            "message": f"Validation failed: {str(error)}",
            "recoverable": True,
            "context": context,
        }
    
    def _handle_llm_error(self, error: LLMError, context: dict) -> dict:
        """Handle LLM errors."""
        return {
            "strategy": "retry",
            "message": f"LLM error: {str(error)}",
            "recoverable": True,
            "max_retries": self.max_retries,
            "context": context,
        }
    
    def _handle_workflow_error(
        self,
        error: WorkflowError,
        context: dict,
    ) -> dict:
        """Handle workflow errors."""
        return {
            "strategy": "rollback",
            "message": f"Workflow error: {str(error)}",
            "recoverable": True,
            "context": context,
        }
    
    def _handle_unknown_error(self, error: Exception, context: dict) -> dict:
        """Handle unknown errors."""
        return {
            "strategy": "escalate",
            "message": f"Unknown error: {str(error)}",
            "recoverable": False,
            "context": context,
        }
    
    def with_retry(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except LLMError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
            except Exception as e:
                raise
        
        if last_error:
            raise last_error
