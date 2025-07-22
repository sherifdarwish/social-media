"""
Instagram Agent

This module implements the Instagram-specific social media agent.
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


class InstagramAgent(BaseAgent):
    """
    Instagram-specific social media agent.
    
    Handles content creation, posting, and engagement for Instagram business accounts.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the Instagram agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="Instagram Content Agent",
            platform="instagram",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("InstagramAgent", "instagram")
        
        # Instagram-specific configuration
        self.access_token = self.platform_config.get("access_token")
        self.business_account_id = self.platform_config.get("business_account_id")
        
        # Instagram API endpoints
        self.base_url = "https://graph.facebook.com/v18.0"
        
        # Content settings
        self.max_caption_length = 2200
        self.optimal_caption_length = 500
        self.max_hashtags = 30
        self.optimal_hashtags = 15
        
        self.agent_logger.info("Instagram agent initialized")
    
    async def _initialize_platform_connection(self):
        """Initialize connection to Instagram API."""
        try:
            # Verify access token and business account
            await self._verify_access_token()
            await self._verify_business_account()
            
            self.agent_logger.info("Instagram API connection verified")
            
        except Exception as e:
            self.agent_logger.error(f"Failed to initialize Instagram connection: {e}")
            raise
    
    async def _verify_access_token(self):
        """Verify the Instagram access token is valid."""
        url = f"{self.base_url}/me"
        params = {"access_token": self.access_token}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Invalid Instagram access token: {error_data}")
                
                data = await response.json()
                self.agent_logger.debug(f"Access token verified for user: {data.get('name')}")
    
    async def _verify_business_account(self):
        """Verify the Instagram business account."""
        url = f"{self.base_url}/{self.business_account_id}"
        params = {
            "access_token": self.access_token,
            "fields": "name,username,account_type"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Cannot access Instagram business account: {error_data}")
                
                data = await response.json()
                self.agent_logger.debug(f"Business account verified: @{data.get('username')}")
    
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to Instagram."""
        try:
            if content.content_type == ContentType.IMAGE:
                return await self._post_image_content(content)
            elif content.content_type == ContentType.VIDEO:
                return await self._post_video_content(content)
            elif content.content_type == ContentType.MIXED:
                return await self._post_mixed_content(content)
            else:
                raise ValueError(f"Unsupported content type for Instagram: {content.content_type}")
                
        except Exception as e:
            self.agent_logger.error(f"Error posting to Instagram: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_image_content(self, content: ContentItem) -> PostResult:
        """Post image content to Instagram."""
        try:
            # Step 1: Create media container
            container_id = await self._create_media_container(
                image_url=content.image_url,
                caption=content.text
            )
            
            # Step 2: Publish the media
            post_id = await self._publish_media(container_id)
            
            self.agent_logger.log_post_activity(post_id, "create", True, content_type="image")
            
            return PostResult(
                success=True,
                post_id=post_id,
                platform_response={"container_id": container_id}
            )
            
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_video_content(self, content: ContentItem) -> PostResult:
        """Post video content (Reel) to Instagram."""
        try:
            # Step 1: Create video container
            container_id = await self._create_media_container(
                video_url=content.video_url,
                caption=content.text,
                media_type="REELS"
            )
            
            # Step 2: Publish the media
            post_id = await self._publish_media(container_id)
            
            self.agent_logger.log_post_activity(post_id, "create", True, content_type="video")
            
            return PostResult(
                success=True,
                post_id=post_id,
                platform_response={"container_id": container_id}
            )
            
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_mixed_content(self, content: ContentItem) -> PostResult:
        """Post mixed content to Instagram."""
        # For Instagram, mixed content is posted as an image with caption
        return await self._post_image_content(content)
    
    async def _create_media_container(
        self,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        caption: Optional[str] = None,
        media_type: str = "IMAGE"
    ) -> str:
        """Create a media container for Instagram posting."""
        url = f"{self.base_url}/{self.business_account_id}/media"
        
        data = {
            "access_token": self.access_token,
            "media_type": media_type
        }
        
        if image_url:
            data["image_url"] = image_url
        elif video_url:
            data["video_url"] = video_url
        
        if caption:
            data["caption"] = caption
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return response_data.get("id")
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise Exception(f"Failed to create media container: {error_msg}")
    
    async def _publish_media(self, container_id: str) -> str:
        """Publish a media container to Instagram."""
        url = f"{self.base_url}/{self.business_account_id}/media_publish"
        
        data = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return response_data.get("id")
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise Exception(f"Failed to publish media: {error_msg}")
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from Instagram API."""
        try:
            # Get account insights
            account_insights = await self._get_account_insights()
            
            # Get media insights
            media_insights = await self._get_media_insights()
            
            # Combine metrics
            metrics = {
                **account_insights,
                **media_insights
            }
            
            return metrics
            
        except Exception as e:
            self.agent_logger.error(f"Error getting Instagram metrics: {e}")
            return {}
    
    async def _get_account_insights(self) -> Dict[str, Any]:
        """Get Instagram account insights."""
        url = f"{self.base_url}/{self.business_account_id}/insights"
        
        # Metrics to retrieve
        metrics = [
            "follower_count",
            "reach",
            "impressions",
            "profile_views"
        ]
        
        params = {
            "metric": ",".join(metrics),
            "period": "day",
            "since": (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "until": datetime.utcnow().strftime("%Y-%m-%d"),
            "access_token": self.access_token
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
                    self.agent_logger.warning(f"Failed to get account insights: {response.status}")
                    return {}
    
    async def _get_media_insights(self) -> Dict[str, Any]:
        """Get insights for recent media."""
        # First, get recent media
        media_url = f"{self.base_url}/{self.business_account_id}/media"
        media_params = {
            "fields": "id,media_type,timestamp",
            "limit": 10,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(media_url, params=media_params) as response:
                if response.status != 200:
                    return {}
                
                media_data = await response.json()
                media_items = media_data.get("data", [])
                
                total_likes = 0
                total_comments = 0
                total_shares = 0
                total_reach = 0
                total_impressions = 0
                
                # Get insights for each media item
                for media in media_items:
                    media_id = media.get("id")
                    insights = await self._get_single_media_insights(media_id)
                    
                    total_likes += insights.get("likes", 0)
                    total_comments += insights.get("comments", 0)
                    total_shares += insights.get("shares", 0)
                    total_reach += insights.get("reach", 0)
                    total_impressions += insights.get("impressions", 0)
                
                return {
                    "recent_media_likes": total_likes,
                    "recent_media_comments": total_comments,
                    "recent_media_shares": total_shares,
                    "recent_media_reach": total_reach,
                    "recent_media_impressions": total_impressions,
                    "recent_media_count": len(media_items)
                }
    
    async def _get_single_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Get insights for a single media item."""
        url = f"{self.base_url}/{media_id}/insights"
        
        metrics = ["likes", "comments", "shares", "reach", "impressions"]
        
        params = {
            "metric": ",".join(metrics),
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    insights = {}
                    
                    for metric_data in data.get("data", []):
                        metric_name = metric_data.get("name")
                        value = metric_data.get("values", [{}])[0].get("value", 0)
                        insights[metric_name] = value
                    
                    return insights
                else:
                    return {}
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get Instagram-specific content requirements."""
        base_requirements = {
            "max_caption_length": self.max_caption_length,
            "optimal_caption_length": self.optimal_caption_length,
            "max_hashtags": self.max_hashtags,
            "optimal_hashtags": self.optimal_hashtags,
            "platform_style": "visually appealing and lifestyle-focused",
            "audience": "visual content enthusiasts",
            "tone": "inspiring and authentic"
        }
        
        if content_type == ContentType.IMAGE:
            return {
                **base_requirements,
                "image_style": "high-quality, aesthetic, square format preferred",
                "focus": "visual storytelling",
                "emoji_usage": "heavy"
            }
        elif content_type == ContentType.VIDEO:
            return {
                **base_requirements,
                "video_style": "vertical format (9:16), engaging first 3 seconds",
                "video_length": "15-90 seconds",
                "focus": "entertainment and education"
            }
        else:
            return base_requirements
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply Instagram-specific content optimizations."""
        # Optimize caption length
        if content.text and len(content.text) > self.optimal_caption_length:
            content.text = content.text[:self.optimal_caption_length - 3] + "..."
        
        # Optimize hashtags
        if len(content.hashtags) > self.optimal_hashtags:
            content.hashtags = content.hashtags[:self.optimal_hashtags]
        
        # Add hashtags to caption
        if content.text and content.hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in content.hashtags])
            content.text = f"{content.text}\n\n{hashtag_text}"
        
        # Add metadata
        content.metadata.update({
            "optimized_for": "instagram",
            "optimization_timestamp": datetime.utcnow().isoformat()
        })
        
        return content
    
    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """Instagram-specific content validation."""
        # Check caption length
        if content.text and len(content.text) > self.max_caption_length:
            self.agent_logger.warning(f"Caption too long: {len(content.text)} > {self.max_caption_length}")
            return False
        
        # Check hashtag count
        if len(content.hashtags) > self.max_hashtags:
            self.agent_logger.warning(f"Too many hashtags: {len(content.hashtags)} > {self.max_hashtags}")
            return False
        
        # Check for required access token
        if not self.access_token:
            self.agent_logger.error("Instagram access token not configured")
            return False
        
        # Check for business account ID
        if not self.business_account_id:
            self.agent_logger.error("Instagram business account ID not configured")
            return False
        
        return True
    
    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on Instagram posts."""
        media_id = post.get("id")
        if not media_id:
            return
        
        try:
            # Get comments that need responses
            comments = await self._get_media_comments(media_id)
            
            for comment in comments:
                if await self._should_respond_to_comment(comment):
                    response = await self._generate_comment_response(comment)
                    await self._reply_to_comment(comment["id"], response)
            
        except Exception as e:
            self.agent_logger.error(f"Error handling Instagram engagement: {e}")
    
    async def _get_media_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """Get comments for an Instagram media item."""
        url = f"{self.base_url}/{media_id}/comments"
        
        params = {
            "fields": "id,text,username,timestamp",
            "access_token": self.access_token
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
        text = comment.get("text", "").lower()
        
        # Respond to questions and specific keywords
        if "?" in text or any(word in text for word in ["love", "amazing", "beautiful", "how", "where"]):
            return True
        
        return False
    
    async def _generate_comment_response(self, comment: Dict[str, Any]) -> str:
        """Generate a response to a comment."""
        comment_text = comment.get("text", "")
        
        response_content = await self.content_generator.generate_content(
            platform="instagram",
            content_type=ContentType.TEXT,
            topic=f"Response to comment: {comment_text}",
            requirements={
                "max_text_length": 200,
                "tone": "friendly and engaging",
                "emoji_usage": "moderate"
            }
        )
        
        return response_content.text
    
    async def _reply_to_comment(self, comment_id: str, response: str):
        """Reply to an Instagram comment."""
        url = f"{self.base_url}/{comment_id}/replies"
        
        data = {
            "message": response,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    self.agent_logger.info("Successfully replied to comment")
                else:
                    self.agent_logger.warning(f"Failed to reply to comment: {response.status}")
    
    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent Instagram media for engagement checking."""
        url = f"{self.base_url}/{self.business_account_id}/media"
        
        params = {
            "fields": "id,media_type,timestamp,caption",
            "limit": 5,
            "access_token": self.access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    return []

