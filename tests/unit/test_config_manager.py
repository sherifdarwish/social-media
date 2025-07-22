"""
Unit tests for ConfigManager class.
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.config.config_manager import ConfigManager, ConfigValidationError


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration data."""
        return {
            "general": {
                "app_name": "Social Media Agent",
                "environment": "testing",
                "debug": True,
                "log_level": "INFO"
            },
            "llm_providers": {
                "openai": {
                    "api_key": "test-openai-key",
                    "api_base": "https://api.openai.com/v1",
                    "models": {
                        "text": "gpt-3.5-turbo",
                        "image": "dall-e-2"
                    },
                    "rate_limits": {
                        "requests_per_minute": 60,
                        "tokens_per_minute": 90000
                    }
                },
                "anthropic": {
                    "api_key": "test-anthropic-key",
                    "models": {
                        "text": "claude-3-haiku-20240307"
                    }
                }
            },
            "platforms": {
                "facebook": {
                    "enabled": True,
                    "api_credentials": {
                        "access_token": "test-facebook-token",
                        "app_id": "test-app-id",
                        "app_secret": "test-app-secret"
                    },
                    "posting_schedule": {
                        "frequency": "daily",
                        "times": ["09:00", "15:00", "21:00"]
                    }
                },
                "twitter": {
                    "enabled": True,
                    "api_credentials": {
                        "api_key": "test-twitter-key",
                        "api_secret": "test-twitter-secret",
                        "access_token": "test-access-token",
                        "access_token_secret": "test-access-secret"
                    }
                }
            },
            "content_generation": {
                "brand_voice": {
                    "tone": "professional",
                    "personality": "helpful",
                    "style_guidelines": ["Be concise", "Use active voice"]
                },
                "content_types": {
                    "text": {"enabled": True, "max_length": 2000},
                    "image": {"enabled": True, "dimensions": "1080x1080"},
                    "video": {"enabled": False}
                }
            },
            "metrics": {
                "collection_interval": 3600,
                "retention_period": 365,
                "database": {
                    "url": "sqlite:///metrics.db",
                    "pool_size": 10
                }
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config, temp_dir):
        """Create temporary config file."""
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
        return config_file
    
    @pytest.mark.unit
    def test_config_manager_initialization(self, temp_config_file):
        """Test ConfigManager initialization."""
        config_manager = ConfigManager(str(temp_config_file))
        
        assert config_manager.config_path == str(temp_config_file)
        assert config_manager.config_data is not None
        assert "general" in config_manager.config_data
    
    @pytest.mark.unit
    def test_load_config_yaml(self, temp_config_file, sample_config):
        """Test loading YAML configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        assert config_manager.config_data == sample_config
    
    @pytest.mark.unit
    def test_load_config_json(self, sample_config, temp_dir):
        """Test loading JSON configuration."""
        config_file = temp_dir / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(sample_config, f)
        
        config_manager = ConfigManager(str(config_file))
        
        assert config_manager.config_data == sample_config
    
    @pytest.mark.unit
    def test_load_config_file_not_found(self):
        """Test handling of missing config file."""
        with pytest.raises(FileNotFoundError):
            ConfigManager("/nonexistent/config.yaml")
    
    @pytest.mark.unit
    def test_load_config_invalid_yaml(self, temp_dir):
        """Test handling of invalid YAML."""
        config_file = temp_dir / "invalid_config.yaml"
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(yaml.YAMLError):
            ConfigManager(str(config_file))
    
    @pytest.mark.unit
    def test_get_config(self, temp_config_file, sample_config):
        """Test getting full configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        config = config_manager.get_config()
        assert config == sample_config
    
    @pytest.mark.unit
    def test_get_section(self, temp_config_file, sample_config):
        """Test getting configuration section."""
        config_manager = ConfigManager(str(temp_config_file))
        
        general_config = config_manager.get_section("general")
        assert general_config == sample_config["general"]
        
        # Test non-existent section
        non_existent = config_manager.get_section("non_existent")
        assert non_existent == {}
    
    @pytest.mark.unit
    def test_get_llm_config(self, temp_config_file, sample_config):
        """Test getting LLM provider configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        llm_config = config_manager.get_llm_config()
        assert llm_config == sample_config["llm_providers"]
        
        # Test specific provider
        openai_config = config_manager.get_llm_config("openai")
        assert openai_config == sample_config["llm_providers"]["openai"]
        
        # Test non-existent provider
        non_existent = config_manager.get_llm_config("non_existent")
        assert non_existent == {}
    
    @pytest.mark.unit
    def test_get_platform_config(self, temp_config_file, sample_config):
        """Test getting platform configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        facebook_config = config_manager.get_platform_config("facebook")
        assert facebook_config == sample_config["platforms"]["facebook"]
        
        # Test non-existent platform
        non_existent = config_manager.get_platform_config("non_existent")
        assert non_existent == {}
    
    @pytest.mark.unit
    def test_get_content_config(self, temp_config_file, sample_config):
        """Test getting content generation configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        content_config = config_manager.get_content_config()
        assert content_config == sample_config["content_generation"]
    
    @pytest.mark.unit
    def test_get_metrics_config(self, temp_config_file, sample_config):
        """Test getting metrics configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        metrics_config = config_manager.get_metrics_config()
        assert metrics_config == sample_config["metrics"]
    
    @pytest.mark.unit
    def test_get_database_config(self, temp_config_file):
        """Test getting database configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        db_config = config_manager.get_database_config()
        assert "url" in db_config
        assert db_config["url"] == "sqlite:///metrics.db"
    
    @pytest.mark.unit
    def test_get_api_key(self, temp_config_file):
        """Test getting API keys."""
        config_manager = ConfigManager(str(temp_config_file))
        
        openai_key = config_manager.get_api_key("openai")
        assert openai_key == "test-openai-key"
        
        # Test non-existent provider
        non_existent_key = config_manager.get_api_key("non_existent")
        assert non_existent_key is None
    
    @pytest.mark.unit
    def test_set_config_value(self, temp_config_file):
        """Test setting configuration values."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Set new value
        config_manager.set_config_value("general.app_name", "New App Name")
        assert config_manager.get_section("general")["app_name"] == "New App Name"
        
        # Set nested value
        config_manager.set_config_value("platforms.facebook.enabled", False)
        assert config_manager.get_platform_config("facebook")["enabled"] is False
    
    @pytest.mark.unit
    def test_update_config(self, temp_config_file):
        """Test updating configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        updates = {
            "general": {
                "debug": False,
                "new_setting": "test_value"
            },
            "new_section": {
                "setting": "value"
            }
        }
        
        config_manager.update_config(updates)
        
        # Check updates
        assert config_manager.get_section("general")["debug"] is False
        assert config_manager.get_section("general")["new_setting"] == "test_value"
        assert config_manager.get_section("new_section")["setting"] == "value"
    
    @pytest.mark.unit
    def test_save_config(self, temp_config_file):
        """Test saving configuration to file."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Modify config
        config_manager.set_config_value("general.app_name", "Modified App")
        
        # Save config
        config_manager.save_config()
        
        # Reload and verify
        new_config_manager = ConfigManager(str(temp_config_file))
        assert new_config_manager.get_section("general")["app_name"] == "Modified App"
    
    @pytest.mark.unit
    def test_backup_config(self, temp_config_file):
        """Test configuration backup."""
        config_manager = ConfigManager(str(temp_config_file))
        
        backup_path = config_manager.backup_config()
        
        assert Path(backup_path).exists()
        assert backup_path.endswith(".backup")
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = yaml.safe_load(f)
        
        assert backup_data == config_manager.config_data
    
    @pytest.mark.unit
    def test_restore_config(self, temp_config_file):
        """Test configuration restoration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Create backup
        backup_path = config_manager.backup_config()
        
        # Modify config
        config_manager.set_config_value("general.app_name", "Modified")
        
        # Restore from backup
        config_manager.restore_config(backup_path)
        
        # Verify restoration
        assert config_manager.get_section("general")["app_name"] == "Social Media Agent"
    
    @pytest.mark.unit
    def test_validate_config_valid(self, temp_config_file):
        """Test validation of valid configuration."""
        config_manager = ConfigManager(str(temp_config_file))
        
        errors = config_manager.validate_config()
        assert len(errors) == 0
    
    @pytest.mark.unit
    def test_validate_config_missing_required(self, temp_dir):
        """Test validation with missing required fields."""
        invalid_config = {
            "general": {
                # Missing required fields
            },
            "llm_providers": {},
            "platforms": {}
        }
        
        config_file = temp_dir / "invalid_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        config_manager = ConfigManager(str(config_file))
        errors = config_manager.validate_config()
        
        assert len(errors) > 0
        assert any("app_name" in error for error in errors)
    
    @pytest.mark.unit
    def test_validate_config_invalid_values(self, temp_dir):
        """Test validation with invalid values."""
        invalid_config = {
            "general": {
                "app_name": "",  # Empty string
                "environment": "invalid_env",  # Invalid environment
                "debug": "not_boolean"  # Invalid type
            },
            "llm_providers": {
                "openai": {
                    "api_key": "",  # Empty API key
                    "models": {}  # Empty models
                }
            }
        }
        
        config_file = temp_dir / "invalid_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        config_manager = ConfigManager(str(config_file))
        errors = config_manager.validate_config()
        
        assert len(errors) > 0
    
    @pytest.mark.unit
    def test_get_nested_value(self, temp_config_file):
        """Test getting nested configuration values."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Test existing nested value
        value = config_manager.get_nested_value("llm_providers.openai.models.text")
        assert value == "gpt-3.5-turbo"
        
        # Test non-existent nested value
        value = config_manager.get_nested_value("non.existent.path")
        assert value is None
        
        # Test with default value
        value = config_manager.get_nested_value("non.existent.path", "default")
        assert value == "default"
    
    @pytest.mark.unit
    def test_environment_specific_config(self, temp_dir):
        """Test environment-specific configuration loading."""
        base_config = {
            "general": {
                "app_name": "Social Media Agent",
                "debug": False
            }
        }
        
        env_config = {
            "general": {
                "debug": True,
                "log_level": "DEBUG"
            }
        }
        
        # Create base config
        base_file = temp_dir / "config.yaml"
        with open(base_file, 'w') as f:
            yaml.dump(base_config, f)
        
        # Create environment config
        env_file = temp_dir / "config.testing.yaml"
        with open(env_file, 'w') as f:
            yaml.dump(env_config, f)
        
        with patch.dict('os.environ', {'ENVIRONMENT': 'testing'}):
            config_manager = ConfigManager(str(base_file))
            
            # Should merge environment-specific config
            assert config_manager.get_section("general")["debug"] is True
            assert config_manager.get_section("general")["log_level"] == "DEBUG"
            assert config_manager.get_section("general")["app_name"] == "Social Media Agent"
    
    @pytest.mark.unit
    def test_config_encryption(self, temp_config_file):
        """Test configuration encryption/decryption."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Test encrypting sensitive values
        encrypted_key = config_manager.encrypt_value("sensitive_api_key")
        assert encrypted_key != "sensitive_api_key"
        assert encrypted_key.startswith("encrypted:")
        
        # Test decrypting values
        decrypted_key = config_manager.decrypt_value(encrypted_key)
        assert decrypted_key == "sensitive_api_key"
    
    @pytest.mark.unit
    def test_config_templating(self, temp_dir):
        """Test configuration templating with variables."""
        template_config = {
            "general": {
                "app_name": "${APP_NAME}",
                "environment": "${ENVIRONMENT:development}"
            },
            "database": {
                "url": "postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}/${DB_NAME}"
            }
        }
        
        config_file = temp_dir / "template_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(template_config, f)
        
        with patch.dict('os.environ', {
            'APP_NAME': 'Test App',
            'DB_USER': 'testuser',
            'DB_PASS': 'testpass',
            'DB_HOST': 'localhost',
            'DB_NAME': 'testdb'
        }):
            config_manager = ConfigManager(str(config_file))
            
            assert config_manager.get_section("general")["app_name"] == "Test App"
            assert config_manager.get_section("general")["environment"] == "development"
            assert "testuser:testpass@localhost" in config_manager.get_section("database")["url"]
    
    @pytest.mark.unit
    def test_config_schema_validation(self, temp_config_file):
        """Test configuration schema validation."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Test with valid schema
        schema = {
            "type": "object",
            "properties": {
                "general": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "debug": {"type": "boolean"}
                    },
                    "required": ["app_name"]
                }
            },
            "required": ["general"]
        }
        
        is_valid = config_manager.validate_schema(schema)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_config_hot_reload(self, temp_config_file):
        """Test configuration hot reloading."""
        config_manager = ConfigManager(str(temp_config_file))
        
        original_name = config_manager.get_section("general")["app_name"]
        
        # Modify config file
        config_data = config_manager.config_data.copy()
        config_data["general"]["app_name"] = "Hot Reloaded App"
        
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Reload config
        config_manager.reload_config()
        
        assert config_manager.get_section("general")["app_name"] == "Hot Reloaded App"
    
    @pytest.mark.unit
    def test_config_merge_strategies(self, temp_dir):
        """Test different configuration merge strategies."""
        base_config = {
            "platforms": {
                "facebook": {"enabled": True, "setting1": "value1"},
                "twitter": {"enabled": False}
            }
        }
        
        override_config = {
            "platforms": {
                "facebook": {"enabled": False, "setting2": "value2"},
                "instagram": {"enabled": True}
            }
        }
        
        config_manager = ConfigManager()
        
        # Test deep merge
        merged = config_manager.merge_configs(base_config, override_config, strategy="deep")
        
        assert merged["platforms"]["facebook"]["enabled"] is False  # Overridden
        assert merged["platforms"]["facebook"]["setting1"] == "value1"  # Preserved
        assert merged["platforms"]["facebook"]["setting2"] == "value2"  # Added
        assert merged["platforms"]["twitter"]["enabled"] is False  # Preserved
        assert merged["platforms"]["instagram"]["enabled"] is True  # Added
    
    @pytest.mark.unit
    def test_config_export_import(self, temp_config_file, temp_dir):
        """Test configuration export and import."""
        config_manager = ConfigManager(str(temp_config_file))
        
        # Export to different formats
        json_export = temp_dir / "exported_config.json"
        config_manager.export_config(str(json_export), format="json")
        
        assert json_export.exists()
        
        # Import and verify
        imported_manager = ConfigManager()
        imported_manager.import_config(str(json_export), format="json")
        
        assert imported_manager.config_data == config_manager.config_data

