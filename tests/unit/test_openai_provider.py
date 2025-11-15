"""Tests for OpenAI provider."""

import pytest
from unittest.mock import Mock, patch

from multi_agent.integrations.openai_provider import OpenAIProvider, OPENAI_AVAILABLE
from multi_agent.integrations.llm_provider import GenerationConfig


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    with patch('multi_agent.integrations.openai_provider.OpenAI'):
        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.max_retries == 3


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_generate():
    """Test OpenAI text generation."""
    with patch('multi_agent.integrations.openai_provider.OpenAI') as mock_openai:
        # Mock the response
        mock_message = Mock()
        mock_message.content = "Generated response"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key")
        result = provider.generate("Test prompt")
        
        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_generate_with_config():
    """Test OpenAI generation with custom config."""
    with patch('multi_agent.integrations.openai_provider.OpenAI') as mock_openai:
        mock_message = Mock()
        mock_message.content = "Response"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key")
        config = GenerationConfig(
            model="gpt-4",
            temperature=0.9,
            max_tokens=2048
        )
        
        result = provider.generate("Test", config)
        
        # Verify config was used
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['temperature'] == 0.9
        assert call_args.kwargs['max_tokens'] == 2048
        assert call_args.kwargs['model'] == "gpt-4"


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_generate_structured():
    """Test OpenAI structured generation."""
    with patch('multi_agent.integrations.openai_provider.OpenAI') as mock_openai:
        mock_message = Mock()
        mock_message.content = '{"name": "test", "value": 42}'
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key")
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            }
        }
        
        result = provider.generate_structured("Test prompt", schema)
        
        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 42


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_model_mapping():
    """Test that Claude model names are mapped to OpenAI models."""
    with patch('multi_agent.integrations.openai_provider.OpenAI'):
        config = GenerationConfig(model="claude-3-5-sonnet-20241022")
        provider = OpenAIProvider(api_key="test-key", config=config)
        
        # Should map to GPT-4
        assert provider.config.model == "gpt-4-turbo-preview"


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_retry_on_rate_limit():
    """Test retry logic on rate limit error."""
    with patch('multi_agent.integrations.openai_provider.OpenAI') as mock_openai:
        from openai import RateLimitError
        
        mock_message = Mock()
        mock_message.content = "Success after retry"
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        # Fail twice, then succeed
        mock_client.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=Mock(), body=None),
            RateLimitError("Rate limit", response=Mock(), body=None),
            mock_response,
        ]
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key")
        provider.retry_delay = 0.01  # Speed up test
        
        result = provider.generate("Test")
        
        assert result == "Success after retry"
        assert mock_client.chat.completions.create.call_count == 3


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_openai_empty_response():
    """Test handling of empty response."""
    with patch('multi_agent.integrations.openai_provider.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = []
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key")
        result = provider.generate("Test")
        
        assert result == ""
