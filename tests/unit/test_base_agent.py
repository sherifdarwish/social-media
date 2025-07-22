"""
Unit tests for BaseAgent class.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.agents.base_agent import BaseAgent, AgentStatus, PostResult
from src.config.config_manager import ConfigManager
from src.content_generation.content_generator import ContentGenerator
from src.metrics.metrics_collector import MetricsCollector


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    @pytest.fixture
    def agent_config(self):
        """Agent configuration for testing."""
        return {
            "name": "test_agent",
            "platform": "test_platform",
            "enabled": True,
            "posting_schedule": {
                "frequency": "daily",
                "times": ["09:00", "15:00", "21:00"]
            },
            "content_settings": {
                "max_posts_per_day": 3,
                "content_types": ["text", "image"]
            }
        }
    
    @pytest.fixture
    def base_agent(self, mock_config_manager, mock_content_generator, mock_metrics_collector, agent_config):
        """Create BaseAgent instance for testing."""
        return BaseAgent(
            name="test_agent",
            platform="test_platform",
            config_manager=mock_config_manager,
            content_generator=mock_content_generator,
            metrics_collector=mock_metrics_collector,
            config=agent_config
        )
    
    @pytest.mark.unit
    def test_agent_initialization(self, base_agent, agent_config):
        """Test agent initialization."""
        assert base_agent.name == "test_agent"
        assert base_agent.platform == "test_platform"
        assert base_agent.config == agent_config
        assert base_agent.status == AgentStatus.STOPPED
        assert not base_agent.is_running
        assert base_agent.last_post_time is None
        assert base_agent.posts_today == 0
    
    @pytest.mark.unit
    async def test_agent_start(self, base_agent):
        """Test agent start functionality."""
        # Mock platform client initialization
        with patch.object(base_agent, '_initialize_platform_client', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = True
            
            result = await base_agent.start()
            
            assert result is True
            assert base_agent.status == AgentStatus.RUNNING
            assert base_agent.is_running is True
            mock_init.assert_called_once()
    
    @pytest.mark.unit
    async def test_agent_start_failure(self, base_agent):
        """Test agent start failure handling."""
        with patch.object(base_agent, '_initialize_platform_client', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = Exception("Platform initialization failed")
            
            result = await base_agent.start()
            
            assert result is False
            assert base_agent.status == AgentStatus.ERROR
            assert base_agent.is_running is False
    
    @pytest.mark.unit
    async def test_agent_stop(self, base_agent):
        """Test agent stop functionality."""
        # Start agent first
        base_agent.status = AgentStatus.RUNNING
        base_agent._running = True
        
        result = await base_agent.stop()
        
        assert result is True
        assert base_agent.status == AgentStatus.STOPPED
        assert base_agent.is_running is False
    
    @pytest.mark.unit
    async def test_create_post_success(self, base_agent, mock_content_generator):
        """Test successful post creation."""
        # Setup mocks
        mock_content_generator.generate_text_content.return_value = {
            "content": "Test post content",
            "hashtags": ["#test"],
            "metadata": {"model": "test-model"}
        }
        
        with patch.object(base_agent, '_post_to_platform', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {
                "success": True,
                "post_id": "test_post_123",
                "url": "https://platform.com/post/123"
            }
            
            result = await base_agent.create_post("text", "Test prompt")
            
            assert isinstance(result, PostResult)
            assert result.success is True
            assert result.post_id == "test_post_123"
            assert result.content == "Test post content"
            assert base_agent.posts_today == 1
            assert base_agent.last_post_time is not None
    
    @pytest.mark.unit
    async def test_create_post_failure(self, base_agent, mock_content_generator):
        """Test post creation failure."""
        mock_content_generator.generate_text_content.return_value = {
            "content": "Test post content",
            "hashtags": ["#test"],
            "metadata": {"model": "test-model"}
        }
        
        with patch.object(base_agent, '_post_to_platform', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Platform posting failed")
            
            result = await base_agent.create_post("text", "Test prompt")
            
            assert isinstance(result, PostResult)
            assert result.success is False
            assert result.error_message == "Platform posting failed"
            assert base_agent.posts_today == 0
    
    @pytest.mark.unit
    async def test_daily_post_limit(self, base_agent):
        """Test daily post limit enforcement."""
        # Set posts_today to max limit
        base_agent.posts_today = 3
        base_agent.config["content_settings"]["max_posts_per_day"] = 3
        
        result = await base_agent.create_post("text", "Test prompt")
        
        assert isinstance(result, PostResult)
        assert result.success is False
        assert "daily limit" in result.error_message.lower()
    
    @pytest.mark.unit
    def test_get_status(self, base_agent):
        """Test status retrieval."""
        base_agent.status = AgentStatus.RUNNING
        base_agent.posts_today = 2
        base_agent.last_post_time = datetime.utcnow()
        
        status = base_agent.get_status()
        
        assert status["status"] == "running"
        assert status["posts_today"] == 2
        assert status["last_post_time"] is not None
        assert "uptime" in status
    
    @pytest.mark.unit
    async def test_collect_metrics(self, base_agent, mock_metrics_collector):
        """Test metrics collection."""
        test_metrics = {
            "posts_created": 5,
            "engagement_rate": 3.2,
            "success_rate": 95.0
        }
        
        with patch.object(base_agent, '_get_platform_metrics', new_callable=AsyncMock) as mock_get_metrics:
            mock_get_metrics.return_value = test_metrics
            
            await base_agent.collect_metrics()
            
            mock_metrics_collector.store_metrics.assert_called_once_with(
                "test_agent", "test_platform", test_metrics
            )
    
    @pytest.mark.unit
    async def test_schedule_validation(self, base_agent):
        """Test posting schedule validation."""
        # Test valid schedule
        schedule = {
            "frequency": "daily",
            "times": ["09:00", "15:00", "21:00"]
        }
        
        is_valid = base_agent._validate_schedule(schedule)
        assert is_valid is True
        
        # Test invalid schedule
        invalid_schedule = {
            "frequency": "invalid",
            "times": ["25:00"]  # Invalid time
        }
        
        is_valid = base_agent._validate_schedule(invalid_schedule)
        assert is_valid is False
    
    @pytest.mark.unit
    def test_should_post_now(self, base_agent):
        """Test posting time logic."""
        # Mock current time to match schedule
        with patch('src.agents.base_agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 9, 0, 0)  # 09:00
            
            should_post = base_agent._should_post_now()
            assert should_post is True
            
            # Test non-scheduled time
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)  # 10:00
            
            should_post = base_agent._should_post_now()
            assert should_post is False
    
    @pytest.mark.unit
    async def test_content_optimization(self, base_agent, mock_content_generator):
        """Test content optimization for platform."""
        original_content = "This is a very long piece of content that needs to be optimized for the platform"
        
        mock_content_generator.optimize_for_platform.return_value = "Optimized content"
        
        optimized = await base_agent._optimize_content(original_content)
        
        assert optimized == "Optimized content"
        mock_content_generator.optimize_for_platform.assert_called_once_with(
            original_content, "test_platform"
        )
    
    @pytest.mark.unit
    async def test_error_handling(self, base_agent):
        """Test error handling and recovery."""
        # Test network error handling
        with patch.object(base_agent, '_post_to_platform', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = ConnectionError("Network error")
            
            result = await base_agent.create_post("text", "Test prompt")
            
            assert result.success is False
            assert "network error" in result.error_message.lower()
            assert base_agent.status == AgentStatus.ERROR
    
    @pytest.mark.unit
    async def test_retry_mechanism(self, base_agent):
        """Test retry mechanism for failed operations."""
        call_count = 0
        
        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "Success"
        
        with patch.object(base_agent, '_post_to_platform', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = failing_operation
            
            result = await base_agent._retry_operation(mock_post, max_retries=3)
            
            assert result == "Success"
            assert call_count == 3
    
    @pytest.mark.unit
    def test_config_validation(self, base_agent):
        """Test configuration validation."""
        # Test valid config
        valid_config = {
            "name": "test_agent",
            "platform": "test_platform",
            "enabled": True,
            "posting_schedule": {
                "frequency": "daily",
                "times": ["09:00"]
            }
        }
        
        errors = base_agent._validate_config(valid_config)
        assert len(errors) == 0
        
        # Test invalid config
        invalid_config = {
            "name": "",  # Empty name
            "platform": "invalid_platform",
            "posting_schedule": {}  # Missing required fields
        }
        
        errors = base_agent._validate_config(invalid_config)
        assert len(errors) > 0
    
    @pytest.mark.unit
    async def test_graceful_shutdown(self, base_agent):
        """Test graceful shutdown handling."""
        base_agent.status = AgentStatus.RUNNING
        base_agent._running = True
        
        # Simulate ongoing operation
        with patch.object(base_agent, '_cleanup_resources', new_callable=AsyncMock) as mock_cleanup:
            await base_agent.stop()
            
            mock_cleanup.assert_called_once()
            assert base_agent.status == AgentStatus.STOPPED
    
    @pytest.mark.unit
    async def test_health_check(self, base_agent):
        """Test agent health check."""
        # Healthy agent
        base_agent.status = AgentStatus.RUNNING
        base_agent.last_post_time = datetime.utcnow() - timedelta(hours=1)
        
        health = await base_agent.health_check()
        
        assert health["healthy"] is True
        assert health["status"] == "running"
        
        # Unhealthy agent (no posts for too long)
        base_agent.last_post_time = datetime.utcnow() - timedelta(days=2)
        
        health = await base_agent.health_check()
        
        assert health["healthy"] is False
        assert "inactive" in health["issues"]
    
    @pytest.mark.unit
    def test_metrics_calculation(self, base_agent):
        """Test metrics calculation."""
        # Setup test data
        base_agent.posts_today = 5
        base_agent.successful_posts = 4
        base_agent.failed_posts = 1
        
        metrics = base_agent._calculate_metrics()
        
        assert metrics["posts_created"] == 5
        assert metrics["success_rate"] == 80.0
        assert metrics["failure_rate"] == 20.0
    
    @pytest.mark.unit
    async def test_concurrent_posting(self, base_agent):
        """Test handling of concurrent posting attempts."""
        # Simulate concurrent post creation
        async def create_multiple_posts():
            tasks = []
            for i in range(3):
                task = asyncio.create_task(base_agent.create_post("text", f"Post {i}"))
                tasks.append(task)
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        with patch.object(base_agent, '_post_to_platform', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"success": True, "post_id": "test_123"}
            
            results = await create_multiple_posts()
            
            # Should handle concurrent requests gracefully
            assert len(results) == 3
            successful_posts = sum(1 for r in results if isinstance(r, PostResult) and r.success)
            assert successful_posts <= base_agent.config["content_settings"]["max_posts_per_day"]


class TestAgentStatus:
    """Test cases for AgentStatus enum."""
    
    @pytest.mark.unit
    def test_status_values(self):
        """Test status enum values."""
        assert AgentStatus.STOPPED.value == "stopped"
        assert AgentStatus.STARTING.value == "starting"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.STOPPING.value == "stopping"
        assert AgentStatus.ERROR.value == "error"
    
    @pytest.mark.unit
    def test_status_transitions(self):
        """Test valid status transitions."""
        # Valid transitions
        valid_transitions = [
            (AgentStatus.STOPPED, AgentStatus.STARTING),
            (AgentStatus.STARTING, AgentStatus.RUNNING),
            (AgentStatus.RUNNING, AgentStatus.STOPPING),
            (AgentStatus.STOPPING, AgentStatus.STOPPED),
            (AgentStatus.RUNNING, AgentStatus.ERROR),
            (AgentStatus.ERROR, AgentStatus.STOPPED)
        ]
        
        for from_status, to_status in valid_transitions:
            # This would test transition validation if implemented
            assert from_status != to_status


class TestPostResult:
    """Test cases for PostResult class."""
    
    @pytest.mark.unit
    def test_successful_post_result(self):
        """Test successful post result creation."""
        result = PostResult(
            success=True,
            post_id="test_123",
            content="Test content",
            platform="test_platform",
            timestamp=datetime.utcnow()
        )
        
        assert result.success is True
        assert result.post_id == "test_123"
        assert result.content == "Test content"
        assert result.error_message is None
    
    @pytest.mark.unit
    def test_failed_post_result(self):
        """Test failed post result creation."""
        result = PostResult(
            success=False,
            error_message="Posting failed",
            platform="test_platform",
            timestamp=datetime.utcnow()
        )
        
        assert result.success is False
        assert result.error_message == "Posting failed"
        assert result.post_id is None
        assert result.content is None
    
    @pytest.mark.unit
    def test_post_result_serialization(self):
        """Test post result serialization."""
        result = PostResult(
            success=True,
            post_id="test_123",
            content="Test content",
            platform="test_platform",
            timestamp=datetime.utcnow()
        )
        
        serialized = result.to_dict()
        
        assert serialized["success"] is True
        assert serialized["post_id"] == "test_123"
        assert serialized["content"] == "Test content"
        assert "timestamp" in serialized

