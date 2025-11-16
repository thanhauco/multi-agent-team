"""Configuration loader for system settings."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigurationLoader:
    """Loads and manages system configuration."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration loader.
        
        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = config_dir or Path("config")
        self.configs: Dict[str, Dict[str, Any]] = {}

    def load_system_config(self) -> Dict[str, Any]:
        """Load system configuration.
        
        Returns:
            System configuration
        """
        config_file = self.config_dir / "system_config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.configs["system"] = yaml.safe_load(f)
        else:
            self.configs["system"] = self._get_default_system_config()
        
        return self.configs["system"]

    def load_llm_config(self) -> Dict[str, Any]:
        """Load LLM configuration.
        
        Returns:
            LLM configuration
        """
        config_file = self.config_dir / "llm_config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.configs["llm"] = yaml.safe_load(f)
        else:
            self.configs["llm"] = self._get_default_llm_config()
        
        return self.configs["llm"]

    def load_logging_config(self) -> Dict[str, Any]:
        """Load logging configuration.
        
        Returns:
            Logging configuration
        """
        config_file = self.config_dir / "logging_config.yaml"
        if config_file.exists():
            with open(config_file, "r") as f:
                self.configs["logging"] = yaml.safe_load(f)
        else:
            self.configs["logging"] = self._get_default_logging_config()
        
        return self.configs["logging"]

    def validate_config(self, config_name: str) -> list[str]:
        """Validate configuration.
        
        Args:
            config_name: Name of configuration to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if config_name not in self.configs:
            errors.append(f"Configuration '{config_name}' not loaded")
            return errors
        
        config = self.configs[config_name]
        
        # Validate based on config type
        if config_name == "llm":
            if "providers" not in config:
                errors.append("LLM config missing 'providers' section")
        
        return errors

    def _get_default_system_config(self) -> Dict[str, Any]:
        """Get default system configuration."""
        return {
            "system": {
                "agent_templates_dir": "agents/templates",
                "custom_templates_dir": "agents/custom",
                "context_store_path": ".multi_agent/context",
                "log_dir": ".multi_agent/logs",
            },
            "workflow": {
                "default_workflow": "workflows/default_workflow.yaml",
                "max_rollback_attempts": 3,
                "validation_timeout": 300,
            },
            "agents": {
                "max_retry_attempts": 3,
                "timeout": 600,
            },
        }

    def _get_default_llm_config(self) -> Dict[str, Any]:
        """Get default LLM configuration."""
        return {
            "providers": {
                "claude": {
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                },
                "openai": {
                    "api_key_env": "OPENAI_API_KEY",
                    "model": "gpt-4-turbo-preview",
                    "max_tokens": 4096,
                    "temperature": 0.7",
                },
            },
            "default_provider": "claude",
        }

    def _get_default_logging_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            "level": "INFO",
            "format": "json",
            "rotation": {
                "enabled": True,
                "max_size_mb": 100,
                "backup_count": 5,
            },
        }
