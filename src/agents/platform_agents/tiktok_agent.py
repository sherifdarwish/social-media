"""
TikTok Agent

This module implements the TikTok-specific social media agent focused on
short-form video content and trending topics.
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


class TikTokAgent(BaseAgent):
    """
    TikTok-specific social media agent.
    
    Handles short-form video content creation, posting, and trend analysis
    for TikTok business accounts.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the TikTok agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="TikTok Content Agent",
            platform="tiktok",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("TikTokAgent", "tiktok")
        
        # TikTok-specific configuration
        self.app_id = self.platform_config.get("app_id")
        self.app_secret = self.platform_config.get("app_secret")
        self.access_token = self.platform_config.get("access_token")
        
        # TikTok API endpoints
        self.base_url = "https://open-api.tiktok.com"
        
        # Content settings
        self.max_caption_length = 2200
        self.optimal_caption_length = 150
        self.max_hashtags = 10
        self.optimal_hashtags = 5
        self.video_min_duration = 15  # seconds
        self.video_max_duration = 180  # seconds
        
        # Trending topics cache
        self.trending_topics = []
        self.trending_hashtags = []
        self.trending_sounds = []
        
        self.agent_logger.info("TikTok agent initialized")
    
    async def _initialize_platform_connection(self):
        """Initialize connection to TikTok API."""
        try:
            # Verify access token
            await self._verify_access_token()
            
            # Load trending topics
            await self._load_trending_data()
            
            self.agent_logger.info("TikTok API connection verified")
            
        except Exception as e:
            self.agent_logger.error(f"Failed to initialize TikTok connection: {e}")
            raise
    
    async def _verify_access_token(self):
        """Verify the TikTok access token is valid."""
        url = f"{self.base_url}/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Invalid TikTok access token: {error_data}")
                
                data = await response.json()
                user_data = data.get("data", {}).get("user", {})
                self.agent_logger.debug(f"Access token verified for user: {user_data.get('display_name')}")
    
    async def _load_trending_data(self):
        """Load trending topics, hashtags, and sounds."""
        try:
            # Load trending hashtags
            await self._load_trending_hashtags()
            
            # Load trending sounds (if available)
            await self._load_trending_sounds()
            
            self.agent_logger.info("Trending data loaded successfully")
            
        except Exception as e:
            self.agent_logger.warning(f"Failed to load trending data: {e}")
    
    async def _load_trending_hashtags(self):
        """Load trending hashtags from TikTok."""
        # This is a simplified implementation
        # In practice, you'd use TikTok's research API or third-party services
        self.trending_hashtags = [
            "fyp", "foryou", "viral", "trending", "tiktok",
            "dance", "comedy", "lifestyle", "diy", "tutorial"
        ]
    
    async def _load_trending_sounds(self):
        """Load trending sounds from TikTok."""
        # This would require access to TikTok's music/sound API
        self.trending_sounds = []
    
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to TikTok."""
        try:
            if content.content_type == ContentType.VIDEO:
                return await self._post_video_content(content)
            else:
                raise ValueError(f"TikTok only supports video content, got: {content.content_type}")
                
        except Exception as e:
            self.agent_logger.error(f"Error posting to TikTok: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_video_content(self, content: ContentItem) -> PostResult:
        """Post video content to TikTok."""
        try:
            # Step 1: Initialize video upload
            upload_url, video_id = await self._initialize_video_upload()
            
            # Step 2: Upload video file
            await self._upload_video_file(upload_url, content.video_url)
            
            # Step 3: Publish the video
            post_id = await self._publish_video(video_id, content)
            
            self.agent_logger.log_post_activity(post_id, "create", True, content_type="video")
            
            return PostResult(
                success=True,
                post_id=post_id,
                platform_response={"video_id": video_id}
            )
            
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _initialize_video_upload(self) -> tuple[str, str]:
        """Initialize video upload to TikTok."""
        url = f"{self.base_url}/v2/post/publish/video/init/"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "post_info": {
                "title": "Video Upload",
                "privacy_level": "SELF_ONLY",  # Will be updated when publishing
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": 10485760,  # 10MB default
                "chunk_size": 10485760,
                "total_chunk_count": 1
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    data = response_data.get("data", {})
                    upload_url = data.get("upload_url")
                    video_id = data.get("publish_id")
                    return upload_url, video_id
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to initialize video upload: {error_data}")
    
    async def _upload_video_file(self, upload_url: str, video_url: str):
        """Upload video file to TikTok."""
        # Download video data
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                video_data = await resp.read()
        
        # Upload to TikTok
        async with aiohttp.ClientSession() as session:
            async with session.put(upload_url, data=video_data) as response:
                if response.status not in [200, 201]:
                    raise Exception(f"Failed to upload video: {response.status}")
    
    async def _publish_video(self, video_id: str, content: ContentItem) -> str:
        """Publish the uploaded video."""
        url = f"{self.base_url}/v2/post/publish/status/fetch/"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Wait for video processing
        await asyncio.sleep(10)
        
        # Check upload status and publish
        data = {
            "publish_id": video_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("data", {}).get("publish_id", video_id)
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to publish video: {error_data}")
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from TikTok API."""
        try:
            # Get user metrics
            user_metrics = await self._get_user_metrics()
            
            # Get video metrics
            video_metrics = await self._get_video_metrics()
            
            # Combine metrics
            metrics = {
                **user_metrics,
                **video_metrics
            }
            
            return metrics
            
        except Exception as e:
            self.agent_logger.error(f"Error getting TikTok metrics: {e}")
            return {}
    
    async def _get_user_metrics(self) -> Dict[str, Any]:
        """Get TikTok user metrics."""
        url = f"{self.base_url}/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get("data", {}).get("user", {})
                    
                    return {
                        "follower_count": user_data.get("follower_count", 0),
                        "following_count": user_data.get("following_count", 0),
                        "likes_count": user_data.get("likes_count", 0),
                        "video_count": user_data.get("video_count", 0)
                    }
                else:
                    return {}
    
    async def _get_video_metrics(self) -> Dict[str, Any]:
        """Get metrics for recent videos."""
        url = f"{self.base_url}/v2/video/list/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "max_count": 20
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    videos = response_data.get("data", {}).get("videos", [])
                    
                    total_views = 0
                    total_likes = 0
                    total_comments = 0
                    total_shares = 0
                    
                    for video in videos:
                        total_views += video.get("view_count", 0)
                        total_likes += video.get("like_count", 0)
                        total_comments += video.get("comment_count", 0)
                        total_shares += video.get("share_count", 0)
                    
                    return {
                        "recent_videos_views": total_views,
                        "recent_videos_likes": total_likes,
                        "recent_videos_comments": total_comments,
                        "recent_videos_shares": total_shares,
                        "recent_videos_count": len(videos)
                    }
                else:
                    return {}
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get TikTok-specific content requirements."""
        base_requirements = {
            "max_caption_length": self.max_caption_length,
            "optimal_caption_length": self.optimal_caption_length,
            "max_hashtags": self.max_hashtags,
            "optimal_hashtags": self.optimal_hashtags,
            "platform_style": "entertaining, authentic, and trend-aware",
            "audience": "Gen Z and millennials",
            "tone": "casual, fun, and engaging"
        }
        
        if content_type == ContentType.VIDEO:
            return {
                **base_requirements,
                "video_format": "vertical (9:16 aspect ratio)",
                "video_duration": f"{self.video_min_duration}-{self.video_max_duration} seconds",
                "focus": "hook in first 3 seconds, entertainment value",
                "trending_elements": True,
                "music_integration": True
            }
        else:
            return base_requirements
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply TikTok-specific content optimizations."""
        # Optimize caption length
        if content.text and len(content.text) > self.optimal_caption_length:
            content.text = content.text[:self.optimal_caption_length - 3] + "..."
        
        # Add trending hashtags
        content.hashtags = await self._optimize_hashtags(content.hashtags)
        
        # Add TikTok-specific formatting
        if content.text and content.hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in content.hashtags])
            content.text = f"{content.text}\n\n{hashtag_text}"
        
        # Add trending elements to metadata
        content.metadata.update({
            "optimized_for": "tiktok",
            "optimization_timestamp": datetime.utcnow().isoformat(),
            "trending_hashtags_used": [tag for tag in content.hashtags if tag in self.trending_hashtags],
            "video_optimized": content.content_type == ContentType.VIDEO
        })
        
        return content
    
    async def _optimize_hashtags(self, hashtags: List[str]) -> List[str]:
        """Optimize hashtags for TikTok by including trending ones."""
        optimized_hashtags = hashtags.copy()
        
        # Add trending hashtags if not already present
        for trending_tag in self.trending_hashtags[:3]:  # Add top 3 trending
            if trending_tag not in optimized_hashtags and len(optimized_hashtags) < self.optimal_hashtags:
                optimized_hashtags.append(trending_tag)
        
        # Ensure we don't exceed the limit
        return optimized_hashtags[:self.max_hashtags]
    
    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """TikTok-specific content validation."""
        # Check if content is video
        if content.content_type != ContentType.VIDEO:
            self.agent_logger.error("TikTok only supports video content")
            return False
        
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
            self.agent_logger.error("TikTok access token not configured")
            return False
        
        # Check video URL
        if not content.video_url:
            self.agent_logger.error("Video URL is required for TikTok posts")
            return False
        
        return True
    
    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on TikTok videos."""
        video_id = post.get("id")
        if not video_id:
            return
        
        try:
            # Get comments that need responses
            comments = await self._get_video_comments(video_id)
            
            for comment in comments:
                if await self._should_respond_to_comment(comment):
                    response = await self._generate_comment_response(comment)
                    await self._reply_to_comment(comment["id"], response)
            
        except Exception as e:
            self.agent_logger.error(f"Error handling TikTok engagement: {e}")
    
    async def _get_video_comments(self, video_id: str) -> List[Dict[str, Any]]:
        """Get comments for a TikTok video."""
        url = f"{self.base_url}/v2/video/comment/list/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "video_id": video_id,
            "max_count": 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("data", {}).get("comments", [])
                else:
                    return []
    
    async def _should_respond_to_comment(self, comment: Dict[str, Any]) -> bool:
        """Determine if we should respond to a comment."""
        text = comment.get("text", "").lower()
        
        # Respond to questions and positive engagement
        if "?" in text or any(word in text for word in ["love", "amazing", "how", "tutorial", "more"]):
            return True
        
        return False
    
    async def _generate_comment_response(self, comment: Dict[str, Any]) -> str:
        """Generate a response to a comment."""
        comment_text = comment.get("text", "")
        
        response_content = await self.content_generator.generate_content(
            platform="tiktok",
            content_type=ContentType.TEXT,
            topic=f"Response to comment: {comment_text}",
            requirements={
                "max_text_length": 150,
                "tone": "casual and friendly",
                "emoji_usage": "moderate"
            }
        )
        
        return response_content.text
    
    async def _reply_to_comment(self, comment_id: str, response: str):
        """Reply to a TikTok comment."""
        # TikTok comment reply functionality would be implemented here
        # This is a placeholder as the exact API endpoint may vary
        self.agent_logger.info(f"Would reply to comment {comment_id}: {response}")
    
    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent TikTok videos for engagement checking."""
        url = f"{self.base_url}/v2/video/list/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "max_count": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("data", {}).get("videos", [])
                else:
                    return []
    
    async def analyze_trends(self) -> Dict[str, Any]:
        """Analyze current TikTok trends for content optimization."""
        try:
            # Refresh trending data
            await self._load_trending_data()
            
            trend_analysis = {
                "trending_hashtags": self.trending_hashtags,
                "trending_sounds": self.trending_sounds,
                "content_recommendations": await self._generate_trend_recommendations(),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return trend_analysis
            
        except Exception as e:
            self.agent_logger.error(f"Error analyzing trends: {e}")
            return {}
    
    async def _generate_trend_recommendations(self) -> List[str]:
        """Generate content recommendations based on trends."""
        recommendations = []
        
        # Generate recommendations based on trending hashtags
        for hashtag in self.trending_hashtags[:5]:
            recommendation = f"Create content around #{hashtag} trend"
            recommendations.append(recommendation)
        
        # Add general TikTok content recommendations
        general_recommendations = [
            "Create behind-the-scenes content",
            "Participate in trending challenges",
            "Use trending sounds in videos",
            "Create educational content in short format",
            "Show authentic, unpolished moments"
        ]
        
        recommendations.extend(general_recommendations[:3])
        
        return recommendations

