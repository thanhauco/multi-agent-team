"""LLM provider abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class GenerationConfig:
    """Configuration for LLM generation."""

    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    stop_sequences: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, config: Optional[GenerationConfig] = None):
        """Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            config: Default generation configuration
        """
        self.api_key = api_key
        self.config = config or GenerationConfig()

    @abstractmethod
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate text from prompt.
        
        Args:
            prompt: Input prompt
            config: Generation configuration (overrides default)
            
        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        config: Optional[GenerationConfig] = None,
    ) -> Dict[str, Any]:
        """Generate structured output matching a schema.
        
        Args:
            prompt: Input prompt
            schema: JSON schema for output structure
            config: Generation configuration
            
        Returns:
            Structured output as dictionary
        """
        pass

    def _merge_config(
        self,
        override_config: Optional[GenerationConfig],
    ) -> GenerationConfig:
        """Merge override config with default config.
        
        Args:
            override_config: Configuration to override defaults
            
        Returns:
            Merged configuration
        """
        if not override_config:
            return self.config
        
        return GenerationConfig(
            model=override_config.model or self.config.model,
            max_tokens=override_config.max_tokens or self.config.max_tokens,
            temperature=override_config.temperature if override_config.temperature is not None else self.config.temperature,
            top_p=override_config.top_p if override_config.top_p is not None else self.config.top_p,
            stop_sequences=override_config.stop_sequences or self.config.stop_sequences,
            metadata={**self.config.metadata, **override_config.metadata},
        )
