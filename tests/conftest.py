"""
Pytest configuration and shared fixtures for the social media agent test suite.
"""

import asyncio
import os
import tempfile
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Generator, AsyncGenerator

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Test database

# Import after setting environment
from src.config.config_manager import ConfigManager
from src.config.api_key_manager import APIKeyManager
from src.config.environment_config import EnvironmentConfigManager
from src.agents.base_agent import BaseAgent
from src.content_generation.content_generator import ContentGenerator
from src.metrics.metrics_collector import MetricsCollector
from src.metrics.report_generator import ReportGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config_data():
    """Sample configuration data for testing."""
    return {
        "general": {
            "app_name": "Test Social Media Agent",
            "environment": "testing",
            "debug": True
        },
        "llm_providers": {
            "openai": {
                "api_key": "test-openai-key",
                "models": {
                    "text": "gpt-3.5-turbo",
                    "image": "dall-e-2"
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
                    "access_token": "test-facebook-token"
                }
            },
            "twitter": {
                "enabled": True,
                "api_credentials": {
                    "api_key": "test-twitter-key",
                    "api_secret": "test-twitter-secret"
                }
            }
        },
        "content_generation": {
            "brand_voice": {
                "tone": "professional",
                "personality": "helpful"
            }
        }
    }


@pytest.fixture
def mock_config_manager(test_config_data, temp_dir):
    """Mock configuration manager for testing."""
    config_file = temp_dir / "test_config.yaml"
    
    # Create mock config manager
    config_manager = Mock(spec=ConfigManager)
    config_manager.config_path = config_file
    config_manager.config_data = test_config_data
    
    # Mock methods
    config_manager.get_config.return_value = test_config_data
    config_manager.get_llm_config.return_value = test_config_data["llm_providers"]
    config_manager.get_platform_config.side_effect = lambda platform: test_config_data["platforms"].get(platform, {})
    config_manager.get_content_config.return_value = test_config_data["content_generation"]
    config_manager.get_api_key.side_effect = lambda provider: test_config_data["llm_providers"].get(provider, {}).get("api_key")
    config_manager.validate_config.return_value = []
    
    return config_manager


@pytest.fixture
def mock_api_key_manager(temp_dir):
    """Mock API key manager for testing."""
    api_key_manager = Mock(spec=APIKeyManager)
    
    # Mock API keys
    test_keys = {
        "openai": "test-openai-key",
        "anthropic": "test-anthropic-key",
        "stability": "test-stability-key"
    }
    
    api_key_manager.get_api_key.side_effect = lambda provider: test_keys.get(provider)
    api_key_manager.get_api_base.return_value = None
    api_key_manager.validate_key_access.return_value = True
    api_key_manager.list_keys.return_value = []
    
    return api_key_manager


@pytest.fixture
def mock_environment_config():
    """Mock environment configuration manager."""
    env_config = Mock(spec=EnvironmentConfigManager)
    env_config.is_testing.return_value = True
    env_config.is_development.return_value = False
    env_config.is_production.return_value = False
    env_config.get_database_config.return_value = None
    env_config.get_redis_config.return_value = None
    env_config.validate_configuration.return_value = []
    
    return env_config


@pytest.fixture
def mock_content_generator():
    """Mock content generator for testing."""
    content_generator = Mock(spec=ContentGenerator)
    
    # Mock content generation methods
    async def mock_generate_text_content(*args, **kwargs):
        return {
            "content": "This is test generated content.",
            "hashtags": ["#test", "#socialmedia"],
            "metadata": {"model": "test-model", "tokens": 50}
        }
    
    async def mock_generate_image_content(*args, **kwargs):
        return {
            "image_path": "/tmp/test_image.jpg",
            "description": "Test generated image",
            "metadata": {"model": "test-image-model"}
        }
    
    content_generator.generate_text_content = AsyncMock(side_effect=mock_generate_text_content)
    content_generator.generate_image_content = AsyncMock(side_effect=mock_generate_image_content)
    content_generator.optimize_for_platform = AsyncMock(return_value="Optimized content for platform")
    
    return content_generator


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector for testing."""
    metrics_collector = Mock(spec=MetricsCollector)
    
    # Mock metrics methods
    async def mock_store_metrics(*args, **kwargs):
        return True
    
    async def mock_get_agent_metrics(*args, **kwargs):
        return []
    
    async def mock_get_platform_summary(*args, **kwargs):
        return {
            "platform": "test",
            "total_posts": 10,
            "successful_posts": 9,
            "success_rate": 90.0
        }
    
    metrics_collector.store_metrics = AsyncMock(side_effect=mock_store_metrics)
    metrics_collector.get_agent_metrics = AsyncMock(side_effect=mock_get_agent_metrics)
    metrics_collector.get_platform_summary = AsyncMock(side_effect=mock_get_platform_summary)
    
    return metrics_collector


@pytest.fixture
def mock_platform_client():
    """Mock platform API client for testing."""
    client = Mock()
    
    # Mock API methods
    async def mock_post_content(*args, **kwargs):
        return {
            "success": True,
            "post_id": "test_post_123",
            "url": "https://platform.com/post/123"
        }
    
    async def mock_get_metrics(*args, **kwargs):
        return {
            "likes": 100,
            "comments": 20,
            "shares": 15,
            "views": 1000
        }
    
    client.post_content = AsyncMock(side_effect=mock_post_content)
    client.get_metrics = AsyncMock(side_effect=mock_get_metrics)
    client.get_account_info = AsyncMock(return_value={"followers": 5000, "following": 1000})
    
    return client


@pytest.fixture
def sample_agent_metrics():
    """Sample agent metrics for testing."""
    from src.metrics.metrics_collector import MetricSnapshot
    
    base_time = datetime.utcnow() - timedelta(days=7)
    metrics = []
    
    for i in range(7):
        timestamp = base_time + timedelta(days=i)
        metric = MetricSnapshot(
            agent_name="test_agent",
            platform="test_platform",
            timestamp=timestamp,
            engagement_rate=2.5 + (i * 0.1),
            reach=1000 + (i * 100),
            impressions=5000 + (i * 500),
            clicks=50 + (i * 5),
            shares=10 + i,
            comments=20 + (i * 2),
            likes=100 + (i * 10),
            followers=5000 + (i * 50),
            posts_count=1,
            success_rate=95.0
        )
        metrics.append(metric)
    
    return metrics


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "agent_name": "test_agent",
        "platform": "test_platform",
        "post_id": "test_post_123",
        "content_type": "text",
        "content_preview": "This is a test post content...",
        "hashtags": ["#test", "#socialmedia"],
        "success": True,
        "timestamp": datetime.utcnow(),
        "engagement_metrics": {
            "likes": 100,
            "comments": 20,
            "shares": 15
        }
    }


@pytest.fixture
def mock_database_session():
    """Mock database session for testing."""
    from unittest.mock import MagicMock
    
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.query = MagicMock()
    
    return session


@pytest.fixture
async def mock_base_agent(mock_config_manager, mock_content_generator, mock_metrics_collector):
    """Mock base agent for testing."""
    agent = Mock(spec=BaseAgent)
    agent.name = "test_agent"
    agent.platform = "test_platform"
    agent.config_manager = mock_config_manager
    agent.content_generator = mock_content_generator
    agent.metrics_collector = mock_metrics_collector
    agent.is_running = False
    
    # Mock agent methods
    async def mock_start():
        agent.is_running = True
        return True
    
    async def mock_stop():
        agent.is_running = False
        return True
    
    async def mock_create_post(*args, **kwargs):
        return {
            "success": True,
            "post_id": "test_post_123",
            "content": "Test post content"
        }
    
    agent.start = AsyncMock(side_effect=mock_start)
    agent.stop = AsyncMock(side_effect=mock_stop)
    agent.create_post = AsyncMock(side_effect=mock_create_post)
    agent.get_status = Mock(return_value={"status": "active", "last_post": datetime.utcnow()})
    
    return agent


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    client = Mock()
    
    async def mock_generate_text(*args, **kwargs):
        return "This is mock generated text content."
    
    async def mock_generate_image(*args, **kwargs):
        return "/tmp/mock_generated_image.jpg"
    
    client.generate_text = AsyncMock(side_effect=mock_generate_text)
    client.generate_image = AsyncMock(side_effect=mock_generate_image)
    client.validate_api_key = AsyncMock(return_value=True)
    
    return client


@pytest.fixture
def test_content_templates():
    """Test content templates for different platforms."""
    return {
        "facebook": {
            "text_post": "Check out this amazing content! {content} #facebook #socialmedia",
            "image_post": "{content} 📸 #visual #facebook",
            "max_length": 2000
        },
        "twitter": {
            "text_post": "{content} #twitter #socialmedia",
            "image_post": "{content} 📸",
            "max_length": 280
        },
        "instagram": {
            "text_post": "{content} ✨ #instagram #socialmedia #lifestyle",
            "image_post": "{content} 📷 #insta #photo",
            "max_length": 2200
        },
        "linkedin": {
            "text_post": "{content}\n\n#linkedin #professional #business",
            "image_post": "{content}\n\n#professional #business",
            "max_length": 3000
        },
        "tiktok": {
            "text_post": "{content} #tiktok #viral #trending",
            "video_post": "{content} 🎵 #tiktok #video",
            "max_length": 150
        }
    }


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    redis_client = Mock()
    
    # Mock Redis operations
    redis_client.get = AsyncMock(return_value=None)
    redis_client.set = AsyncMock(return_value=True)
    redis_client.delete = AsyncMock(return_value=1)
    redis_client.exists = AsyncMock(return_value=False)
    redis_client.expire = AsyncMock(return_value=True)
    redis_client.keys = AsyncMock(return_value=[])
    redis_client.flushdb = AsyncMock(return_value=True)
    
    return redis_client


@pytest.fixture
def test_api_responses():
    """Sample API responses for testing."""
    return {
        "facebook": {
            "post_success": {
                "id": "123456789_987654321",
                "created_time": "2024-01-01T12:00:00+0000"
            },
            "metrics": {
                "data": [
                    {
                        "name": "post_impressions",
                        "values": [{"value": 1000}]
                    },
                    {
                        "name": "post_engaged_users",
                        "values": [{"value": 50}]
                    }
                ]
            }
        },
        "twitter": {
            "post_success": {
                "data": {
                    "id": "1234567890123456789",
                    "text": "Test tweet content"
                }
            },
            "metrics": {
                "data": {
                    "public_metrics": {
                        "retweet_count": 10,
                        "like_count": 50,
                        "reply_count": 5,
                        "quote_count": 2
                    }
                }
            }
        },
        "instagram": {
            "post_success": {
                "id": "17841400455970028"
            },
            "metrics": {
                "data": [
                    {
                        "name": "impressions",
                        "values": [{"value": 800}]
                    },
                    {
                        "name": "reach",
                        "values": [{"value": 600}]
                    }
                ]
            }
        }
    }


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "api_rate_limit": {
            "status_code": 429,
            "message": "Rate limit exceeded",
            "retry_after": 3600
        },
        "invalid_credentials": {
            "status_code": 401,
            "message": "Invalid or expired credentials"
        },
        "network_error": {
            "error": "ConnectionError",
            "message": "Failed to connect to API endpoint"
        },
        "invalid_content": {
            "status_code": 400,
            "message": "Content violates platform guidelines"
        },
        "server_error": {
            "status_code": 500,
            "message": "Internal server error"
        }
    }


# Async fixtures
@pytest.fixture
async def async_mock_agent(mock_base_agent):
    """Async version of mock base agent."""
    return mock_base_agent


@pytest.fixture
async def running_agent(mock_base_agent):
    """Mock agent in running state."""
    await mock_base_agent.start()
    yield mock_base_agent
    await mock_base_agent.stop()


# Parametrized fixtures
@pytest.fixture(params=["facebook", "twitter", "instagram", "linkedin", "tiktok"])
def platform_name(request):
    """Parametrized fixture for platform names."""
    return request.param


@pytest.fixture(params=["text", "image", "video"])
def content_type(request):
    """Parametrized fixture for content types."""
    return request.param


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup temporary files after each test."""
    yield
    # Cleanup logic would go here
    pass


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Markers for test categorization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: Tests requiring API access")
    config.addinivalue_line("markers", "database: Tests requiring database")
    config.addinivalue_line("markers", "redis: Tests requiring Redis")
    config.addinivalue_line("markers", "mock: Tests using mocks")
    config.addinivalue_line("markers", "real_api: Tests using real API calls")


# Test data generators
def generate_test_metrics(count: int = 10, platform: str = "test"):
    """Generate test metrics data."""
    from src.metrics.metrics_collector import MetricSnapshot
    
    metrics = []
    base_time = datetime.utcnow() - timedelta(days=count)
    
    for i in range(count):
        timestamp = base_time + timedelta(days=i)
        metric = MetricSnapshot(
            agent_name=f"{platform}_agent",
            platform=platform,
            timestamp=timestamp,
            engagement_rate=2.0 + (i * 0.1),
            reach=1000 + (i * 100),
            impressions=5000 + (i * 500),
            clicks=50 + (i * 5),
            shares=10 + i,
            comments=20 + (i * 2),
            likes=100 + (i * 10),
            followers=5000 + (i * 50),
            posts_count=1,
            success_rate=95.0 + (i * 0.5)
        )
        metrics.append(metric)
    
    return metrics


def generate_test_posts(count: int = 5, platform: str = "test"):
    """Generate test post data."""
    posts = []
    base_time = datetime.utcnow() - timedelta(days=count)
    
    for i in range(count):
        timestamp = base_time + timedelta(days=i)
        post = {
            "agent_name": f"{platform}_agent",
            "platform": platform,
            "post_id": f"test_post_{i}",
            "content_type": "text",
            "content_preview": f"Test post content {i}...",
            "hashtags": [f"#test{i}", "#socialmedia"],
            "success": i % 10 != 0,  # 90% success rate
            "timestamp": timestamp,
            "engagement_metrics": {
                "likes": 100 + (i * 10),
                "comments": 20 + (i * 2),
                "shares": 10 + i
            }
        }
        posts.append(post)
    
    return posts

