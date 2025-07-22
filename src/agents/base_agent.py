"""
Base Agent Class

This module defines the base agent class that all platform-specific agents inherit from.
It provides common functionality for content generation, posting, metrics collection,
and coordination with other agents.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import schedule
from pydantic import BaseModel, Field

from ..config.config_manager import ConfigManager
from ..content_generation.content_generator import ContentGenerator
from ..metrics.metrics_collector import MetricsCollector
from ..utils.logger import get_logger


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"


@dataclass
class ContentItem:
    """Represents a piece of content to be posted."""
    content_type: ContentType
    text: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    scheduled_time: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PostResult:
    """Result of a posting operation."""
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    platform_response: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    posts_created: int = 0
    posts_successful: int = 0
    posts_failed: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    followers_gained: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Base class for all social media agents.
    
    This class provides the common interface and functionality that all
    platform-specific agents inherit from.
    """

    def __init__(
        self,
        agent_name: str,
        platform: str,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            platform: Platform this agent manages
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        self.agent_name = agent_name
        self.platform = platform
        self.config_manager = config_manager
        self.content_generator = content_generator
        self.metrics_collector = metrics_collector
        
        self.logger = get_logger(f"agent.{platform}")
        self.status = AgentStatus.IDLE
        self.last_activity = datetime.utcnow()
        self.metrics = AgentMetrics()
        
        # Get agent-specific configuration
        self.agent_config = self.config_manager.get_agent_config(platform)
        self.platform_config = self.config_manager.get_platform_config(platform)
        
        # Initialize scheduling
        self._setup_schedule()
        
        self.logger.info(f"Initialized {agent_name} for {platform}")

    def _setup_schedule(self):
        """Set up the posting and activity schedule for this agent."""
        if not self.agent_config.get("enabled", True):
            self.logger.info(f"Agent {self.agent_name} is disabled")
            self.status = AgentStatus.DISABLED
            return
            
        # Set up posting schedule
        posting_schedule = self.agent_config.get("schedule", {}).get("posting")
        if posting_schedule:
            schedule.every().day.at(posting_schedule).do(self._scheduled_post)
            
        # Set up engagement check schedule
        engagement_schedule = self.agent_config.get("schedule", {}).get("engagement_check")
        if engagement_schedule:
            schedule.every().hour.do(self._check_engagement)
            
        self.logger.info(f"Schedule configured for {self.agent_name}")

    async def start(self):
        """Start the agent and begin its activities."""
        if self.status == AgentStatus.DISABLED:
            self.logger.warning(f"Cannot start disabled agent {self.agent_name}")
            return
            
        self.status = AgentStatus.ACTIVE
        self.logger.info(f"Starting agent {self.agent_name}")
        
        # Run initial setup
        await self._initialize_platform_connection()
        
        # Start the main agent loop
        await self._run_agent_loop()

    async def stop(self):
        """Stop the agent and clean up resources."""
        self.status = AgentStatus.IDLE
        self.logger.info(f"Stopping agent {self.agent_name}")
        
        # Clean up any resources
        await self._cleanup()

    async def _run_agent_loop(self):
        """Main agent loop that handles scheduled tasks and monitoring."""
        while self.status == AgentStatus.ACTIVE:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Update metrics
                await self._update_metrics()
                
                # Check for coordination messages
                await self._check_coordination_messages()
                
                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in agent loop: {e}")
                self.status = AgentStatus.ERROR
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def create_content(
        self,
        content_type: ContentType,
        topic: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> ContentItem:
        """
        Create content for this platform.
        
        Args:
            content_type: Type of content to create
            topic: Optional topic for the content
            style: Optional style specification
            **kwargs: Additional parameters for content generation
            
        Returns:
            Generated content item
        """
        try:
            self.logger.info(f"Creating {content_type.value} content for {self.platform}")
            
            # Get platform-specific content requirements
            content_requirements = self._get_content_requirements(content_type)
            
            # Generate content using the content generator
            content = await self.content_generator.generate_content(
                platform=self.platform,
                content_type=content_type,
                topic=topic,
                style=style,
                requirements=content_requirements,
                **kwargs
            )
            
            # Apply platform-specific optimizations
            optimized_content = await self._optimize_content(content)
            
            self.metrics.posts_created += 1
            return optimized_content
            
        except Exception as e:
            self.logger.error(f"Error creating content: {e}")
            raise

    async def post_content(self, content: ContentItem) -> PostResult:
        """
        Post content to the platform.
        
        Args:
            content: Content item to post
            
        Returns:
            Result of the posting operation
        """
        try:
            self.logger.info(f"Posting content to {self.platform}")
            
            # Validate content before posting
            if not await self._validate_content(content):
                return PostResult(
                    success=False,
                    error_message="Content validation failed"
                )
            
            # Post to platform
            result = await self._post_to_platform(content)
            
            # Update metrics
            if result.success:
                self.metrics.posts_successful += 1
            else:
                self.metrics.posts_failed += 1
                
            # Store post for tracking
            await self._store_post_record(content, result)
            
            self.last_activity = datetime.utcnow()
            return result
            
        except Exception as e:
            self.logger.error(f"Error posting content: {e}")
            self.metrics.posts_failed += 1
            return PostResult(
                success=False,
                error_message=str(e)
            )

    async def get_metrics(self) -> AgentMetrics:
        """Get current agent metrics."""
        # Update metrics from platform
        await self._update_metrics()
        return self.metrics

    async def handle_coordination_message(self, message: Dict[str, Any]):
        """
        Handle coordination messages from the team leader.
        
        Args:
            message: Coordination message to handle
        """
        message_type = message.get("type")
        
        if message_type == "status_request":
            await self._send_status_response()
        elif message_type == "content_request":
            await self._handle_content_request(message)
        elif message_type == "schedule_update":
            await self._handle_schedule_update(message)
        elif message_type == "emergency_stop":
            await self.stop()
        else:
            self.logger.warning(f"Unknown coordination message type: {message_type}")

    # Abstract methods that must be implemented by platform-specific agents

    @abstractmethod
    async def _initialize_platform_connection(self):
        """Initialize connection to the platform API."""
        pass

    @abstractmethod
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to the specific platform."""
        pass

    @abstractmethod
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from the platform API."""
        pass

    @abstractmethod
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get platform-specific content requirements."""
        pass

    @abstractmethod
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply platform-specific content optimizations."""
        pass

    # Helper methods

    async def _validate_content(self, content: ContentItem) -> bool:
        """Validate content before posting."""
        # Basic validation
        if content.content_type == ContentType.TEXT and not content.text:
            return False
        if content.content_type == ContentType.IMAGE and not content.image_url:
            return False
        if content.content_type == ContentType.VIDEO and not content.video_url:
            return False
            
        # Platform-specific validation
        return await self._platform_specific_validation(content)

    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """Platform-specific content validation."""
        return True  # Override in subclasses

    async def _update_metrics(self):
        """Update agent metrics from platform data."""
        try:
            platform_metrics = await self._get_platform_metrics()
            
            # Update metrics object
            self.metrics.engagement_rate = platform_metrics.get("engagement_rate", 0.0)
            self.metrics.reach = platform_metrics.get("reach", 0)
            self.metrics.impressions = platform_metrics.get("impressions", 0)
            self.metrics.clicks = platform_metrics.get("clicks", 0)
            self.metrics.shares = platform_metrics.get("shares", 0)
            self.metrics.comments = platform_metrics.get("comments", 0)
            self.metrics.likes = platform_metrics.get("likes", 0)
            self.metrics.followers_gained = platform_metrics.get("followers_gained", 0)
            self.metrics.last_updated = datetime.utcnow()
            
            # Store metrics
            await self.metrics_collector.store_metrics(
                agent_name=self.agent_name,
                platform=self.platform,
                metrics=self.metrics.dict()
            )
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    async def _store_post_record(self, content: ContentItem, result: PostResult):
        """Store post record for tracking and analytics."""
        post_record = {
            "agent_name": self.agent_name,
            "platform": self.platform,
            "content_type": content.content_type.value,
            "post_id": result.post_id,
            "success": result.success,
            "timestamp": result.timestamp,
            "content_preview": content.text[:100] if content.text else None,
            "hashtags": content.hashtags,
            "error_message": result.error_message
        }
        
        await self.metrics_collector.store_post_record(post_record)

    async def _scheduled_post(self):
        """Handle scheduled posting."""
        try:
            # Create content for scheduled post
            content = await self.create_content(ContentType.TEXT)
            
            # Post the content
            result = await self.post_content(content)
            
            if result.success:
                self.logger.info(f"Scheduled post successful: {result.post_id}")
            else:
                self.logger.error(f"Scheduled post failed: {result.error_message}")
                
        except Exception as e:
            self.logger.error(f"Error in scheduled post: {e}")

    async def _check_engagement(self):
        """Check and respond to engagement on recent posts."""
        try:
            # Get recent posts that need engagement checking
            recent_posts = await self._get_recent_posts()
            
            for post in recent_posts:
                await self._handle_post_engagement(post)
                
        except Exception as e:
            self.logger.error(f"Error checking engagement: {e}")

    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent posts for engagement checking."""
        # This would typically query the database or platform API
        return []

    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on a specific post."""
        # Override in platform-specific agents
        pass

    async def _check_coordination_messages(self):
        """Check for coordination messages from team leader."""
        # This would typically check a message queue or database
        pass

    async def _send_status_response(self):
        """Send status response to team leader."""
        status_data = {
            "agent_name": self.agent_name,
            "platform": self.platform,
            "status": self.status.value,
            "last_activity": self.last_activity.isoformat(),
            "metrics": self.metrics.dict()
        }
        
        # Send to coordination system
        await self._send_coordination_message("status_response", status_data)

    async def _handle_content_request(self, message: Dict[str, Any]):
        """Handle content creation request from team leader."""
        content_type = ContentType(message.get("content_type", "text"))
        topic = message.get("topic")
        
        content = await self.create_content(content_type, topic=topic)
        
        response = {
            "request_id": message.get("request_id"),
            "content": content.__dict__
        }
        
        await self._send_coordination_message("content_response", response)

    async def _handle_schedule_update(self, message: Dict[str, Any]):
        """Handle schedule update from team leader."""
        new_schedule = message.get("schedule")
        if new_schedule:
            # Update agent configuration
            self.agent_config["schedule"] = new_schedule
            self._setup_schedule()
            self.logger.info("Schedule updated")

    async def _send_coordination_message(self, message_type: str, data: Dict[str, Any]):
        """Send coordination message to team leader."""
        # This would typically send to a message queue or coordination service
        pass

    async def _cleanup(self):
        """Clean up resources when stopping the agent."""
        pass

