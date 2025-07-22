"""
Configuration Manager

This module handles loading, validation, and management of all configuration settings.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from cryptography.fernet import Fernet
import base64

from ..utils.logger import get_logger


class ConfigManager:
    """
    Manages configuration loading, validation, and secure storage of sensitive data.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = get_logger("config_manager")
        
        # Determine config path
        if config_path is None:
            config_path = self._find_config_file()
        
        self.config_path = config_path
        self.config_data = {}
        
        # Initialize encryption for sensitive data
        self._init_encryption()
        
        # Load configuration
        self._load_config()
        
        self.logger.info(f"Configuration loaded from {config_path}")
    
    def _find_config_file(self) -> str:
        """Find the configuration file in standard locations."""
        possible_paths = [
            "config/config.yaml",
            "config.yaml",
            "../config/config.yaml",
            os.path.expanduser("~/.social-media-agent/config.yaml"),
            "/etc/social-media-agent/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, use example config
        example_path = "examples/config.example.yaml"
        if os.path.exists(example_path):
            self.logger.warning(f"No config file found, using example config: {example_path}")
            return example_path
        
        raise FileNotFoundError("No configuration file found")
    
    def _init_encryption(self):
        """Initialize encryption for sensitive data."""
        # Get or generate encryption key
        key_file = os.path.expanduser("~/.social-media-agent/encryption.key")
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
        
        self.cipher = Fernet(key)
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            with open(self.config_path, "r") as f:
                self.config_data = yaml.safe_load(f)
            
            # Decrypt sensitive data
            self._decrypt_sensitive_data()
            
            # Load environment variable overrides
            self._load_env_overrides()
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _decrypt_sensitive_data(self):
        """Decrypt sensitive configuration data."""
        # This would decrypt API keys and other sensitive data
        # For now, we'll just load them as-is
        pass
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # Override database URL if set
        if "DATABASE_URL" in os.environ:
            if "database" not in self.config_data:
                self.config_data["database"] = {}
            self.config_data["database"]["url"] = os.environ["DATABASE_URL"]
        
        # Override Redis URL if set
        if "REDIS_URL" in os.environ:
            if "redis" not in self.config_data:
                self.config_data["redis"] = {}
            self.config_data["redis"]["url"] = os.environ["REDIS_URL"]
        
        # Override LLM API keys
        llm_env_mappings = {
            "OPENAI_API_KEY": ["llm_providers", "openai", "api_key"],
            "ANTHROPIC_API_KEY": ["llm_providers", "anthropic", "api_key"],
            "STABILITY_API_KEY": ["llm_providers", "stability", "api_key"],
        }
        
        for env_var, config_path in llm_env_mappings.items():
            if env_var in os.environ:
                self._set_nested_config(config_path, os.environ[env_var])
        
        # Override platform API keys
        platform_env_mappings = {
            "FACEBOOK_ACCESS_TOKEN": ["platforms", "facebook", "access_token"],
            "TWITTER_API_KEY": ["platforms", "twitter", "api_key"],
            "INSTAGRAM_ACCESS_TOKEN": ["platforms", "instagram", "access_token"],
            "LINKEDIN_ACCESS_TOKEN": ["platforms", "linkedin", "access_token"],
            "TIKTOK_ACCESS_TOKEN": ["platforms", "tiktok", "access_token"],
        }
        
        for env_var, config_path in platform_env_mappings.items():
            if env_var in os.environ:
                self._set_nested_config(config_path, os.environ[env_var])
    
    def _set_nested_config(self, path: List[str], value: Any):
        """Set a nested configuration value."""
        current = self.config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration."""
        return self.config_data.copy()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM provider configuration."""
        return self.config_data.get("llm_providers", {})
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get configuration for a specific platform."""
        platforms = self.config_data.get("platforms", {})
        return platforms.get(platform, {})
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        agents = self.config_data.get("agents", {})
        return agents.get(agent_name, {})
    
    def get_content_config(self) -> Dict[str, Any]:
        """Get content generation configuration."""
        return self.config_data.get("content", {})
    
    def get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics collection configuration."""
        return self.config_data.get("metrics", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.config_data.get("database", {})
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return self.config_data.get("redis", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config_data.get("logging", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.config_data.get("security", {})
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags."""
        return self.config_data.get("features", {})
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        features = self.get_feature_flags()
        return features.get(feature_name, False)
    
    def get_development_config(self) -> Dict[str, Any]:
        """Get development configuration."""
        return self.config_data.get("development", {})
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        dev_config = self.get_development_config()
        return dev_config.get("debug", False)
    
    def is_test_mode(self) -> bool:
        """Check if test mode is enabled."""
        dev_config = self.get_development_config()
        return dev_config.get("test_mode", False)
    
    def should_mock_api_calls(self) -> bool:
        """Check if API calls should be mocked."""
        dev_config = self.get_development_config()
        return dev_config.get("mock_api_calls", False)
    
    def is_dry_run(self) -> bool:
        """Check if dry run mode is enabled."""
        dev_config = self.get_development_config()
        return dev_config.get("dry_run", False)
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        self._deep_update(self.config_data, updates)
        self.logger.info("Configuration updated")
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Recursively update nested dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self, output_path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            output_path: Path to save configuration (default: current config path)
        """
        if output_path is None:
            output_path = self.config_path
        
        try:
            # Create a copy for saving (encrypt sensitive data)
            save_data = self.config_data.copy()
            self._encrypt_sensitive_data(save_data)
            
            with open(output_path, "w") as f:
                yaml.dump(save_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def _encrypt_sensitive_data(self, data: Dict[str, Any]):
        """Encrypt sensitive data before saving."""
        # This would encrypt API keys and other sensitive data
        # For now, we'll just save them as-is
        pass
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required sections
        required_sections = ["llm_providers", "platforms", "agents", "content"]
        for section in required_sections:
            if section not in self.config_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate LLM providers
        llm_providers = self.config_data.get("llm_providers", {})
        if not llm_providers:
            errors.append("No LLM providers configured")
        
        for provider_name, provider_config in llm_providers.items():
            if "api_key" not in provider_config:
                errors.append(f"Missing API key for LLM provider: {provider_name}")
        
        # Validate platforms
        platforms = self.config_data.get("platforms", {})
        if not platforms:
            errors.append("No platforms configured")
        
        # Validate agents
        agents = self.config_data.get("agents", {})
        if not agents:
            errors.append("No agents configured")
        
        # Check that enabled agents have corresponding platform configs
        for agent_name, agent_config in agents.items():
            if agent_config.get("enabled", True):
                if agent_name not in platforms and agent_name != "team_leader":
                    errors.append(f"Enabled agent {agent_name} has no platform configuration")
        
        return errors
    
    def get_agent_platforms(self) -> List[str]:
        """Get list of platforms that have enabled agents."""
        platforms = []
        agents = self.config_data.get("agents", {})
        
        for agent_name, agent_config in agents.items():
            if agent_config.get("enabled", True) and agent_name != "team_leader":
                platforms.append(agent_name)
        
        return platforms
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features."""
        features = self.get_feature_flags()
        return [name for name, enabled in features.items() if enabled]
    
    def reload_config(self):
        """Reload configuration from file."""
        self.logger.info("Reloading configuration")
        self._load_config()
    
    def create_agent_config(self, agent_name: str, platform: str, **kwargs) -> Dict[str, Any]:
        """
        Create configuration for a new agent.
        
        Args:
            agent_name: Name of the agent
            platform: Platform the agent manages
            **kwargs: Additional configuration options
            
        Returns:
            Agent configuration dictionary
        """
        default_config = {
            "name": agent_name,
            "enabled": True,
            "schedule": {
                "posting": "0 10,14,18 * * *",  # 10 AM, 2 PM, 6 PM daily
                "engagement_check": "0 */2 * * *"  # Every 2 hours
            },
            "content_types": ["text_posts", "image_posts"],
            "target_audience": "general_public"
        }
        
        # Update with provided kwargs
        default_config.update(kwargs)
        
        return default_config

