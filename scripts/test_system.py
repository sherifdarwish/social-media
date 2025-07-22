#!/usr/bin/env python3
"""
Comprehensive system test script for Social Media Agent.

This script performs end-to-end testing of the Social Media Agent system
to ensure all components work together correctly.
"""

import asyncio
import os
import sys
import tempfile
import yaml
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.config.config_manager import ConfigManager
    from src.config.api_key_manager import APIKeyManager
    from src.content_generation.content_generator import ContentGenerator
    from src.metrics.metrics_collector import MetricsCollector
    from src.agents.team_leader.team_leader import TeamLeader
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)


class SystemTester:
    """Comprehensive system tester."""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.config_path = None
    
    def setup_test_environment(self):
        """Set up test environment with temporary configuration."""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="social_media_agent_test_")
        
        # Create test configuration
        test_config = {
            "general": {
                "app_name": "Social Media Agent Test",
                "environment": "testing",
                "debug": True,
                "timezone": "UTC"
            },
            "llm_providers": {
                "openai": {
                    "api_key": "test_key_openai",
                    "api_base": "https://api.openai.com/v1",
                    "models": {
                        "text": "gpt-3.5-turbo",
                        "image": "dall-e-3"
                    },
                    "rate_limits": {
                        "requests_per_minute": 60
                    }
                },
                "mock": {
                    "api_key": "test_key_mock",
                    "enabled": True
                }
            },
            "platforms": {
                "facebook": {
                    "enabled": True,
                    "api_credentials": {
                        "access_token": "test_facebook_token",
                        "app_id": "test_app_id",
                        "app_secret": "test_app_secret"
                    },
                    "posting_schedule": {
                        "frequency": "daily",
                        "times": ["09:00", "15:00"]
                    }
                },
                "twitter": {
                    "enabled": True,
                    "api_credentials": {
                        "api_key": "test_twitter_key",
                        "api_secret": "test_twitter_secret",
                        "access_token": "test_access_token",
                        "access_token_secret": "test_access_secret"
                    }
                },
                "linkedin": {
                    "enabled": False,  # Disable for testing
                    "api_credentials": {
                        "client_id": "test_linkedin_id",
                        "client_secret": "test_linkedin_secret"
                    }
                }
            },
            "content_generation": {
                "brand_voice": {
                    "tone": "professional",
                    "personality": "helpful"
                },
                "content_types": {
                    "text": {
                        "enabled": True,
                        "max_length": 2000
                    },
                    "image": {
                        "enabled": True,
                        "dimensions": "1080x1080"
                    }
                }
            },
            "team_leader": {
                "report_schedule": "weekly",
                "report_formats": ["html", "json"]
            },
            "database": {
                "url": f"sqlite:///{self.temp_dir}/test.db"
            },
            "logging": {
                "level": "DEBUG",
                "file": f"{self.temp_dir}/test.log"
            }
        }
        
        # Save test configuration
        self.config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(self.config_path, "w") as f:
            yaml.dump(test_config, f, default_flow_style=False)
        
        # Create data directory
        os.makedirs(os.path.join(self.temp_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "logs"), exist_ok=True)
        
        print(f"✅ Test environment created: {self.temp_dir}")
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        
        try:
            result = test_func()
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            
            if result:
                print(f"✅ {test_name}: PASSED")
                self.test_results.append((test_name, "PASSED", None))
            else:
                print(f"❌ {test_name}: FAILED")
                self.test_results.append((test_name, "FAILED", "Test returned False"))
        
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            self.test_results.append((test_name, "ERROR", str(e)))
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        try:
            config_manager = ConfigManager(self.config_path)
            config = config_manager.get_config()
            
            # Validate required sections
            required_sections = ["general", "llm_providers", "platforms", "content_generation"]
            for section in required_sections:
                if section not in config:
                    return False
            
            # Validate configuration
            errors = config_manager.validate_config()
            return len(errors) == 0
        
        except Exception:
            return False
    
    def test_api_key_management(self):
        """Test API key management functionality."""
        try:
            config_manager = ConfigManager(self.config_path)
            api_key_manager = APIKeyManager(config_manager)
            
            # Test getting API keys
            openai_key = api_key_manager.get_api_key("openai")
            mock_key = api_key_manager.get_api_key("mock")
            
            return openai_key is not None and mock_key is not None
        
        except Exception:
            return False
    
    async def test_content_generator(self):
        """Test content generation functionality."""
        try:
            config_manager = ConfigManager(self.config_path)
            api_key_manager = APIKeyManager(config_manager)
            content_generator = ContentGenerator(config_manager, api_key_manager)
            
            # Test text content generation (mock)
            content = await content_generator.generate_text_content(
                prompt="Test content generation",
                platform="facebook",
                content_type="text"
            )
            
            return content is not None and "content" in content
        
        except Exception:
            return False
    
    async def test_metrics_collector(self):
        """Test metrics collection functionality."""
        try:
            config_manager = ConfigManager(self.config_path)
            metrics_collector = MetricsCollector(config_manager)
            
            # Test storing metrics
            test_metrics = {
                "posts_created": 5,
                "engagement_rate": 3.2,
                "success_rate": 95.0
            }
            
            await metrics_collector.store_metrics(
                agent_name="test_agent",
                platform="facebook",
                metrics=test_metrics
            )
            
            return True
        
        except Exception:
            return False
    
    async def test_team_leader(self):
        """Test team leader functionality."""
        try:
            config_manager = ConfigManager(self.config_path)
            api_key_manager = APIKeyManager(config_manager)
            content_generator = ContentGenerator(config_manager, api_key_manager)
            metrics_collector = MetricsCollector(config_manager)
            
            team_leader = TeamLeader(
                config_manager=config_manager,
                content_generator=content_generator,
                metrics_collector=metrics_collector
            )
            
            # Test team leader initialization
            status = team_leader.get_status()
            return status is not None
        
        except Exception:
            return False
    
    async def test_agent_coordination(self):
        """Test agent coordination functionality."""
        try:
            config_manager = ConfigManager(self.config_path)
            api_key_manager = APIKeyManager(config_manager)
            content_generator = ContentGenerator(config_manager, api_key_manager)
            metrics_collector = MetricsCollector(config_manager)
            
            team_leader = TeamLeader(
                config_manager=config_manager,
                content_generator=content_generator,
                metrics_collector=metrics_collector
            )
            
            # Test coordination system
            coordination_system = team_leader.coordination_system
            return coordination_system is not None
        
        except Exception:
            return False
    
    def test_database_operations(self):
        """Test database operations."""
        try:
            # Initialize test database
            from scripts.init_database import create_sqlite_database
            
            db_path = os.path.join(self.temp_dir, "test.db")
            create_sqlite_database(db_path)
            
            # Verify database was created
            return os.path.exists(db_path)
        
        except Exception:
            return False
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        try:
            config_manager = ConfigManager(self.config_path)
            errors = config_manager.validate_config()
            
            # Should have no errors for valid config
            return len(errors) == 0
        
        except Exception:
            return False
    
    def test_logging_setup(self):
        """Test logging setup."""
        try:
            from src.utils.logger import setup_logging
            
            log_file = os.path.join(self.temp_dir, "test.log")
            setup_logging("DEBUG", log_file)
            
            import logging
            logger = logging.getLogger("test")
            logger.info("Test log message")
            
            # Check if log file was created
            return os.path.exists(log_file)
        
        except Exception:
            return False
    
    def test_import_structure(self):
        """Test that all modules can be imported correctly."""
        try:
            # Test core imports
            from src.config.config_manager import ConfigManager
            from src.config.api_key_manager import APIKeyManager
            from src.content_generation.content_generator import ContentGenerator
            from src.metrics.metrics_collector import MetricsCollector
            from src.agents.team_leader.team_leader import TeamLeader
            
            # Test platform agent imports
            from src.agents.platform_agents.facebook_agent import FacebookAgent
            from src.agents.platform_agents.twitter_agent import TwitterAgent
            from src.agents.platform_agents.instagram_agent import InstagramAgent
            from src.agents.platform_agents.linkedin_agent import LinkedInAgent
            from src.agents.platform_agents.tiktok_agent import TikTokAgent
            
            return True
        
        except ImportError:
            return False
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        print(f"\n🧹 Cleaning up test environment: {self.temp_dir}")
        
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            print("✅ Test environment cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up test environment: {e}")
    
    def print_test_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("🧪 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAILED")
        errors = sum(1 for _, status, _ in self.test_results if status == "ERROR")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "N/A")
        
        print("\nDetailed Results:")
        for test_name, status, error in self.test_results:
            emoji = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "🔥"
            print(f"  {emoji} {test_name}: {status}")
            if error:
                print(f"      Error: {error}")
        
        print("\n" + "="*60)
        
        # Return overall success
        return failed == 0 and errors == 0
    
    def run_all_tests(self):
        """Run all system tests."""
        print("🚀 Starting comprehensive system tests...")
        print(f"⏰ Test started at: {datetime.now()}")
        
        # Set up test environment
        self.setup_test_environment()
        
        try:
            # Run all tests
            self.run_test("Import Structure", self.test_import_structure)
            self.run_test("Configuration Loading", self.test_configuration_loading)
            self.run_test("Configuration Validation", self.test_configuration_validation)
            self.run_test("API Key Management", self.test_api_key_management)
            self.run_test("Database Operations", self.test_database_operations)
            self.run_test("Logging Setup", self.test_logging_setup)
            self.run_test("Content Generator", self.test_content_generator)
            self.run_test("Metrics Collector", self.test_metrics_collector)
            self.run_test("Team Leader", self.test_team_leader)
            self.run_test("Agent Coordination", self.test_agent_coordination)
            
            # Print summary
            success = self.print_test_summary()
            
            if success:
                print("\n🎉 All tests passed! The system is ready for use.")
                return True
            else:
                print("\n⚠️  Some tests failed. Please check the errors above.")
                return False
        
        finally:
            # Clean up
            self.cleanup_test_environment()


def main():
    """Main function."""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

