"""Custom exceptions for the multi-agent system."""


class MultiAgentException(Exception):
    """Base exception for multi-agent system."""
    
    def __init__(self, message: str, context: dict = None):
        """Initialize exception.
        
        Args:
            message: Error message
            context: Additional context information
        """
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(MultiAgentException):
    """Configuration-related errors."""
    pass


class ValidationError(MultiAgentException):
    """Validation-related errors."""
    pass


class LLMError(MultiAgentException):
    """LLM provider errors."""
    pass


class WorkflowError(MultiAgentException):
    """Workflow execution errors."""
    pass


class AgentError(MultiAgentException):
    """Agent execution errors."""
    pass


class ContextError(MultiAgentException):
    """Context management errors."""
    pass
