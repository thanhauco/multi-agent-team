"""Tests for Claude provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from multi_agent.integrations.claude_provider import ClaudeProvider, ANTHROPIC_AVAILABLE
from multi_agent.integrations.llm_provider import GenerationConfig


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_provider_initialization():
    """Test Claude provider initialization."""
    with patch('multi_agent.integrations.claude_provider.Anthropic'):
        provider = ClaudeProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.max_retries == 3


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_generate():
    """Test Claude text generation."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        # Mock the response
        mock_content = Mock()
        mock_content.text = "Generated response"
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
        result = provider.generate("Test prompt")
        
        assert result == "Generated response"
        mock_client.messages.create.assert_called_once()


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_generate_with_config():
    """Test Claude generation with custom config."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        mock_content = Mock()
        mock_content.text = "Response"
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
        config = GenerationConfig(temperature=0.9, max_tokens=2048)
        
        result = provider.generate("Test", config)
        
        # Verify config was used
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs['temperature'] == 0.9
        assert call_args.kwargs['max_tokens'] == 2048


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_generate_structured():
    """Test Claude structured generation."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        mock_content = Mock()
        mock_content.text = '{"name": "test", "value": 42}'
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
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


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_generate_structured_with_extra_text():
    """Test structured generation when response has extra text."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        mock_content = Mock()
        mock_content.text = 'Here is the JSON: {"result": "success"} Hope this helps!'
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
        schema = {"type": "object"}
        
        result = provider.generate_structured("Test", schema)
        
        assert isinstance(result, dict)
        assert result["result"] == "success"


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_generate_structured_invalid_json():
    """Test structured generation with invalid JSON."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        mock_content = Mock()
        mock_content.text = 'This is not valid JSON'
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
        schema = {"type": "object"}
        
        result = provider.generate_structured("Test", schema)
        
        assert "error" in result
        assert "raw_response" in result


@pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic package not installed")
def test_claude_retry_on_rate_limit():
    """Test retry logic on rate limit error."""
    with patch('multi_agent.integrations.claude_provider.Anthropic') as mock_anthropic:
        from anthropic import RateLimitError
        
        mock_content = Mock()
        mock_content.text = "Success after retry"
        
        mock_response = Mock()
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        # Fail twice, then succeed
        mock_client.messages.create.side_effect = [
            RateLimitError("Rate limit"),
            RateLimitError("Rate limit"),
            mock_response,
        ]
        mock_anthropic.return_value = mock_client
        
        provider = ClaudeProvider(api_key="test-key")
        provider.retry_delay = 0.01  # Speed up test
        
        result = provider.generate("Test")
        
        assert result == "Success after retry"
        assert mock_client.messages.create.call_count == 3
