"""Claude LLM provider implementation."""

import json
import time
from typing import Any, Dict, Optional

try:
    from anthropic import Anthropic, APIError, RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from multi_agent.integrations.llm_provider import LLMProvider, GenerationConfig


class ClaudeProvider(LLMProvider):
    """Claude LLM provider using Anthropic API."""

    def __init__(self, api_key: str, config: Optional[GenerationConfig] = None):
        """Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key
            config: Default generation configuration
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )
        
        super().__init__(api_key, config)
        self.client = Anthropic(api_key=api_key)
        self.max_retries = 3
        self.retry_delay = 1.0

    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """Generate text using Claude.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Returns:
            Generated text
        """
        merged_config = self._merge_config(config)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=merged_config.model,
                    max_tokens=merged_config.max_tokens,
                    temperature=merged_config.temperature,
                    top_p=merged_config.top_p,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    stop_sequences=merged_config.stop_sequences or None,
                )
                
                # Extract text from response
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                return ""
                
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
            except APIError as e:
                if attempt < self.max_retries - 1 and e.status_code >= 500:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
        
        return ""

    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        config: Optional[GenerationConfig] = None,
    ) -> Dict[str, Any]:
        """Generate structured output using Claude.
        
        Args:
            prompt: Input prompt
            schema: JSON schema for output
            config: Generation configuration
            
        Returns:
            Structured output as dictionary
        """
        # Add schema instructions to prompt
        schema_prompt = f"""{prompt}

Please provide your response as a JSON object matching this schema:
{json.dumps(schema, indent=2)}

Respond with ONLY the JSON object, no additional text."""

        response_text = self.generate(schema_prompt, config)
        
        # Try to parse JSON from response
        try:
            # Find JSON in response (handle cases where model adds text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            # If no JSON found, try parsing entire response
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            # Return error structure
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text,
                "parse_error": str(e),
            }
