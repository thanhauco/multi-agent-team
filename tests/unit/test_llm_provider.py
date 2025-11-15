"""Tests for LLM provider base class."""

import pytest
from multi_agent.integrations.llm_provider import LLMProvider, GenerationConfig


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def generate(self, prompt: str, config: GenerationConfig | None = None) -> str:
        """Mock generate method."""
        return f"Generated: {prompt[:20]}..."

    def generate_structured(
        self,
        prompt: str,
        schema: dict,
        config: GenerationConfig | None = None,
    ) -> dict:
        """Mock structured generation."""
        return {"result": "structured output"}


def test_generation_config_defaults():
    """Test GenerationConfig default values."""
    config = GenerationConfig()
    assert config.model == "claude-3-5-sonnet-20241022"
    assert config.max_tokens == 4096
    assert config.temperature == 0.7
    assert config.top_p == 1.0


def test_generation_config_custom():
    """Test GenerationConfig with custom values."""
    config = GenerationConfig(
        model="gpt-4",
        max_tokens=2048,
        temperature=0.5,
        stop_sequences=["END"],
    )
    assert config.model == "gpt-4"
    assert config.max_tokens == 2048
    assert config.temperature == 0.5
    assert "END" in config.stop_sequences


def test_llm_provider_initialization():
    """Test LLM provider initialization."""
    provider = MockLLMProvider(api_key="test-key")
    assert provider.api_key == "test-key"
    assert provider.config is not None


def test_llm_provider_with_config():
    """Test LLM provider with custom config."""
    config = GenerationConfig(temperature=0.9)
    provider = MockLLMProvider(api_key="test-key", config=config)
    assert provider.config.temperature == 0.9


def test_merge_config():
    """Test config merging."""
    default_config = GenerationConfig(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=4096,
    )
    provider = MockLLMProvider(api_key="test-key", config=default_config)
    
    override_config = GenerationConfig(
        temperature=0.9,
        max_tokens=2048,
    )
    
    merged = provider._merge_config(override_config)
    assert merged.temperature == 0.9
    assert merged.max_tokens == 2048
    assert merged.model == "claude-3-5-sonnet-20241022"  # From default


def test_merge_config_none():
    """Test merging with None config."""
    config = GenerationConfig(temperature=0.8)
    provider = MockLLMProvider(api_key="test-key", config=config)
    
    merged = provider._merge_config(None)
    assert merged.temperature == 0.8


def test_generate_method():
    """Test generate method."""
    provider = MockLLMProvider(api_key="test-key")
    result = provider.generate("Test prompt")
    assert "Generated:" in result


def test_generate_structured_method():
    """Test generate_structured method."""
    provider = MockLLMProvider(api_key="test-key")
    schema = {"type": "object", "properties": {"result": {"type": "string"}}}
    result = provider.generate_structured("Test prompt", schema)
    assert isinstance(result, dict)
    assert "result" in result
