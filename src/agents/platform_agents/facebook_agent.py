"""
Facebook Agent

This module implements the Facebook-specific social media agent.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from ..base_agent import BaseAgent, ContentItem, ContentType, PostResult, AgentMetrics
from ...config.config_manager import ConfigManager
from ...content_generation.content_generator import ContentGenerator
from ...metrics.metrics_collector import MetricsCollector
from ...utils.logger import AgentLogger


class FacebookAgent(BaseAgent):
    """
    Facebook-specific social media agent.
    
    Handles content creation, posting, and engagement for Facebook pages.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the Facebook agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="Facebook Content Agent",
            platform="facebook",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("FacebookAgent", "facebook")
        
        # Facebook-specific configuration
        self.app_id = self.platform_config.get("app_id")
        self.app_secret = self.platform_config.get("app_secret")
        self.access_token = self.platform_config.get("access_token")
        self.page_id = self.platform_config.get("page_id")
        self.api_version = self.platform_config.get("api_version", "v18.0")
        
        # Facebook API endpoints
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # Content settings
        self.max_text_length = 63206  # Facebook's character limit
        self.optimal_text_length = 300  # Optimal for engagement
        self.max_hashtags = 30
        
        self.agent_logger.info("Facebook agent initialized")
    
    async def _initialize_platform_connection(self):
        """Initialize connection to Facebook API."""
        try:
            # Verify access token and page permissions
            await self._verify_access_token()
            await self._verify_page_permissions()
            
            self.agent_logger.info("Facebook API connection verified")
            
        except Exception as e:
            self.agent_logger.error(f"Failed to initialize Facebook connection: {e}")
            raise
    
    async def _verify_access_token(self):
        """Verify the Facebook access token is valid."""
        url = f"{self.base_url}/me"
        params = {"access_token": self.access_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Invalid Facebook access token: {error_data}")
                
                data = await response.json()
                self.agent_logger.debug(f"Access token verified for user: {data.get('name')}")
    
    async def _verify_page_permissions(self):
        """Verify permissions for the Facebook page."""
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "access_token": self.access_token,
            "fields": "name,access_token,permissions"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Cannot access Facebook page: {error_data}")
                
                data = await response.json()
                self.page_access_token = data.get("access_token", self.access_token)
                self.agent_logger.debug(f"Page permissions verified for: {data.get('name')}")
    
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to Facebook."""
        try:
            if content.content_type == ContentType.TEXT:
                return await self._post_text_content(content)
            elif content.content_type == ContentType.IMAGE:
                return await self._post_image_content(content)
            elif content.content_type == ContentType.VIDEO:
                return await self._post_video_content(content)
            elif content.content_type == ContentType.MIXED:
                return await self._post_mixed_content(content)
            else:
                raise ValueError(f"Unsupported content type: {content.content_type}")
                
        except Exception as e:
            self.agent_logger.error(f"Error posting to Facebook: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_text_content(self, content: ContentItem) -> PostResult:
        """Post text content to Facebook."""
        url = f"{self.base_url}/{self.page_id}/feed"
        
        # Prepare post data
        post_data = {
            "message": content.text,
            "access_token": self.page_access_token
        }
        
        # Add scheduled publishing if specified
        if content.scheduled_time:
            scheduled_timestamp = int(content.scheduled_time.timestamp())
            post_data["scheduled_publish_time"] = scheduled_timestamp
            post_data["published"] = False
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=post_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    post_id = response_data.get("id")
                    self.agent_logger.log_post_activity(post_id, "create", True)
                    
                    return PostResult(
                        success=True,
                        post_id=post_id,
                        platform_response=response_data
                    )
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    self.agent_logger.log_post_activity("", "create", False, error=error_msg)
                    
                    return PostResult(
                        success=False,
                        error_message=error_msg,
                        platform_response=response_data
                    )
    
    async def _post_image_content(self, content: ContentItem) -> PostResult:
        """Post image content to Facebook."""
        url = f"{self.base_url}/{self.page_id}/photos"
        
        # Prepare post data
        post_data = {
            "url": content.image_url,
            "caption": content.text or "",
            "access_token": self.page_access_token
        }
        
        # Add scheduled publishing if specified
        if content.scheduled_time:
            scheduled_timestamp = int(content.scheduled_time.timestamp())
            post_data["scheduled_publish_time"] = scheduled_timestamp
            post_data["published"] = False
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=post_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    post_id = response_data.get("id")
                    self.agent_logger.log_post_activity(post_id, "create", True, content_type="image")
                    
                    return PostResult(
                        success=True,
                        post_id=post_id,
                        platform_response=response_data
                    )
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    self.agent_logger.log_post_activity("", "create", False, error=error_msg)
                    
                    return PostResult(
                        success=False,
                        error_message=error_msg,
                        platform_response=response_data
                    )
    
    async def _post_video_content(self, content: ContentItem) -> PostResult:
        """Post video content to Facebook."""
        url = f"{self.base_url}/{self.page_id}/videos"
        
        # Prepare post data
        post_data = {
            "file_url": content.video_url,
            "description": content.text or "",
            "access_token": self.page_access_token
        }
        
        # Add scheduled publishing if specified
        if content.scheduled_time:
            scheduled_timestamp = int(content.scheduled_time.timestamp())
            post_data["scheduled_publish_time"] = scheduled_timestamp
            post_data["published"] = False
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=post_data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    post_id = response_data.get("id")
                    self.agent_logger.log_post_activity(post_id, "create", True, content_type="video")
                    
                    return PostResult(
                        success=True,
                        post_id=post_id,
                        platform_response=response_data
                    )
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    self.agent_logger.log_post_activity("", "create", False, error=error_msg)
                    
                    return PostResult(
                        success=False,
                        error_message=error_msg,
                        platform_response=response_data
                    )
    
    async def _post_mixed_content(self, content: ContentItem) -> PostResult:
        """Post mixed content (text + image) to Facebook."""
        # For Facebook, mixed content is posted as an image with caption
        return await self._post_image_content(content)
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from Facebook API."""
        try:
            # Get page insights
            insights = await self._get_page_insights()
            
            # Get recent posts metrics
            posts_metrics = await self._get_posts_metrics()
            
            # Combine metrics
            metrics = {
                **insights,
                **posts_metrics
            }
            
            return metrics
            
        except Exception as e:
            self.agent_logger.error(f"Error getting Facebook metrics: {e}")
            return {}
    
    async def _get_page_insights(self) -> Dict[str, Any]:
        """Get Facebook page insights."""
        url = f"{self.base_url}/{self.page_id}/insights"
        
        # Metrics to retrieve
        metrics = [
            "page_fans",
            "page_fan_adds",
            "page_impressions",
            "page_reach",
            "page_engaged_users",
            "page_post_engagements"
        ]
        
        params = {
            "metric": ",".join(metrics),
            "period": "day",
            "since": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "until": datetime.utcnow().strftime("%Y-%m-%d"),
            "access_token": self.page_access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    insights = {}
                    
                    for metric_data in data.get("data", []):
                        metric_name = metric_data.get("name")
                        values = metric_data.get("values", [])
                        
                        if values:
                            latest_value = values[-1].get("value", 0)
                            insights[metric_name] = latest_value
                    
                    return insights
                else:
                    self.agent_logger.warning(f"Failed to get page insights: {response.status}")
                    return {}
    
    async def _get_posts_metrics(self) -> Dict[str, Any]:
        """Get metrics for recent posts."""
        url = f"{self.base_url}/{self.page_id}/posts"
        
        params = {
            "fields": "id,created_time,message,likes.summary(true),comments.summary(true),shares",
            "limit": 10,
            "access_token": self.page_access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = data.get("data", [])
                    
                    total_likes = 0
                    total_comments = 0
                    total_shares = 0
                    
                    for post in posts:
                        likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                        comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                        shares = post.get("shares", {}).get("count", 0)
                        
                        total_likes += likes
                        total_comments += comments
                        total_shares += shares
                    
                    return {
                        "recent_posts_likes": total_likes,
                        "recent_posts_comments": total_comments,
                        "recent_posts_shares": total_shares,
                        "recent_posts_count": len(posts)
                    }
                else:
                    self.agent_logger.warning(f"Failed to get posts metrics: {response.status}")
                    return {}
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get Facebook-specific content requirements."""
        base_requirements = {
            "max_text_length": self.max_text_length,
            "optimal_text_length": self.optimal_text_length,
            "max_hashtags": self.max_hashtags,
            "platform_style": "engaging and conversational",
            "audience": "broad demographic",
            "tone": "friendly and approachable"
        }
        
        if content_type == ContentType.TEXT:
            return {
                **base_requirements,
                "focus": "storytelling and engagement",
                "call_to_action": True,
                "emoji_usage": "moderate"
            }
        elif content_type == ContentType.IMAGE:
            return {
                **base_requirements,
                "image_style": "high-quality, eye-catching",
                "caption_length": "50-150 characters",
                "visual_focus": True
            }
        elif content_type == ContentType.VIDEO:
            return {
                **base_requirements,
                "video_length": "15-60 seconds",
                "description_length": "100-300 characters",
                "engaging_thumbnail": True
            }
        else:
            return base_requirements
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply Facebook-specific content optimizations."""
        # Optimize text length
        if content.text and len(content.text) > self.optimal_text_length:
            # Truncate while preserving meaning
            content.text = content.text[:self.optimal_text_length - 3] + "..."
        
        # Optimize hashtags
        if len(content.hashtags) > self.max_hashtags:
            content.hashtags = content.hashtags[:self.max_hashtags]
        
        # Add Facebook-specific formatting
        if content.text:
            # Ensure proper spacing around hashtags
            hashtag_text = " ".join([f"#{tag}" for tag in content.hashtags])
            if hashtag_text:
                content.text = f"{content.text}\n\n{hashtag_text}"
        
        # Add metadata
        content.metadata.update({
            "optimized_for": "facebook",
            "optimization_timestamp": datetime.utcnow().isoformat()
        })
        
        return content
    
    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """Facebook-specific content validation."""
        # Check text length
        if content.text and len(content.text) > self.max_text_length:
            self.agent_logger.warning(f"Content text too long: {len(content.text)} > {self.max_text_length}")
            return False
        
        # Check hashtag count
        if len(content.hashtags) > self.max_hashtags:
            self.agent_logger.warning(f"Too many hashtags: {len(content.hashtags)} > {self.max_hashtags}")
            return False
        
        # Check for required access token
        if not self.access_token:
            self.agent_logger.error("Facebook access token not configured")
            return False
        
        return True
    
    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on Facebook posts."""
        post_id = post.get("id")
        if not post_id:
            return
        
        try:
            # Get comments that need responses
            comments = await self._get_post_comments(post_id)
            
            for comment in comments:
                if await self._should_respond_to_comment(comment):
                    response = await self._generate_comment_response(comment)
                    await self._reply_to_comment(comment["id"], response)
            
        except Exception as e:
            self.agent_logger.error(f"Error handling post engagement: {e}")
    
    async def _get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments for a Facebook post."""
        url = f"{self.base_url}/{post_id}/comments"
        
        params = {
            "fields": "id,message,from,created_time",
            "access_token": self.page_access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []
    
    async def _should_respond_to_comment(self, comment: Dict[str, Any]) -> bool:
        """Determine if we should respond to a comment."""
        # Simple logic - respond to questions and mentions
        message = comment.get("message", "").lower()
        
        # Check for questions
        if "?" in message:
            return True
        
        # Check for mentions or direct engagement
        if any(word in message for word in ["help", "question", "how", "what", "when", "where", "why"]):
            return True
        
        return False
    
    async def _generate_comment_response(self, comment: Dict[str, Any]) -> str:
        """Generate a response to a comment."""
        comment_text = comment.get("message", "")
        
        # Use content generator to create a response
        response_content = await self.content_generator.generate_content(
            platform="facebook",
            content_type=ContentType.TEXT,
            topic=f"Response to comment: {comment_text}",
            requirements={
                "max_text_length": 200,
                "tone": "helpful and friendly",
                "response_type": "comment_reply"
            }
        )
        
        return response_content.text
    
    async def _reply_to_comment(self, comment_id: str, response: str):
        """Reply to a Facebook comment."""
        url = f"{self.base_url}/{comment_id}/comments"
        
        post_data = {
            "message": response,
            "access_token": self.page_access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=post_data) as response:
                if response.status == 200:
                    self.agent_logger.info("Successfully replied to comment")
                else:
                    self.agent_logger.warning(f"Failed to reply to comment: {response.status}")
    
    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent Facebook posts for engagement checking."""
        url = f"{self.base_url}/{self.page_id}/posts"
        
        params = {
            "fields": "id,created_time,message",
            "limit": 5,
            "access_token": self.page_access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []

