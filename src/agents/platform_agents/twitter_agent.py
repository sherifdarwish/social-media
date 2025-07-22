"""
Twitter Agent

This module implements the X (Twitter)-specific social media agent.
"""

import asyncio
import tweepy.asynchronous
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from ..base_agent import BaseAgent, ContentItem, ContentType, PostResult, AgentMetrics
from ...config.config_manager import ConfigManager
from ...content_generation.content_generator import ContentGenerator
from ...metrics.metrics_collector import MetricsCollector
from ...utils.logger import AgentLogger


class TwitterAgent(BaseAgent):
    """
    X (Twitter)-specific social media agent.
    
    Handles content creation, posting, and engagement for Twitter accounts.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the Twitter agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="X (Twitter) Content Agent",
            platform="twitter",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("TwitterAgent", "twitter")
        
        # Twitter-specific configuration
        self.api_key = self.platform_config.get("api_key")
        self.api_secret = self.platform_config.get("api_secret")
        self.access_token = self.platform_config.get("access_token")
        self.access_token_secret = self.platform_config.get("access_token_secret")
        self.bearer_token = self.platform_config.get("bearer_token")
        
        # Twitter API client
        self.client = None
        
        # Content settings
        self.max_text_length = 280
        self.max_hashtags = 5
        
        self.agent_logger.info("Twitter agent initialized")
    
    async def _initialize_platform_connection(self):
        """Initialize connection to Twitter API."""
        try:
            self.client = tweepy.asynchronous.AsyncClient(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            
            # Verify credentials
            response = await self.client.get_me()
            user = response.data
            
            if not user:
                raise Exception("Invalid Twitter credentials")
            
            self.agent_logger.info(f"Twitter API connection verified for user: @{user.username}")
            
        except Exception as e:
            self.agent_logger.error(f"Failed to initialize Twitter connection: {e}")
            raise
    
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to Twitter."""
        try:
            if content.content_type == ContentType.TEXT:
                return await self._post_text_content(content)
            elif content.content_type == ContentType.IMAGE:
                return await self._post_image_content(content)
            elif content.content_type == ContentType.MIXED:
                return await self._post_mixed_content(content)
            else:
                raise ValueError(f"Unsupported content type for Twitter: {content.content_type}")
                
        except Exception as e:
            self.agent_logger.error(f"Error posting to Twitter: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_text_content(self, content: ContentItem) -> PostResult:
        """Post text content (tweet) to Twitter."""
        try:
            response = await self.client.create_tweet(text=content.text)
            tweet = response.data
            
            post_id = tweet.get("id")
            self.agent_logger.log_post_activity(post_id, "create", True)
            
            return PostResult(
                success=True,
                post_id=post_id,
                platform_response=tweet
            )
            
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_image_content(self, content: ContentItem) -> PostResult:
        """Post image content to Twitter."""
        # For Twitter, image content is posted as a tweet with media
        return await self._post_mixed_content(content)
    
    async def _post_mixed_content(self, content: ContentItem) -> PostResult:
        """Post mixed content (text + image) to Twitter."""
        try:
            # Upload media
            media_ids = []
            if content.image_url:
                # Download image data
                async with aiohttp.ClientSession() as session:
                    async with session.get(content.image_url) as resp:
                        image_data = await resp.read()
                
                # Upload to Twitter
                media_response = await self.client.media_upload(
                    media=image_data,
                    media_category="tweet_image"
                )
                media_ids.append(media_response.media_id)
            
            # Create tweet with media
            response = await self.client.create_tweet(
                text=content.text,
                media_ids=media_ids
            )
            tweet = response.data
            
            post_id = tweet.get("id")
            self.agent_logger.log_post_activity(post_id, "create", True, content_type="mixed")
            
            return PostResult(
                success=True,
                post_id=post_id,
                platform_response=tweet
            )
            
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from Twitter API."""
        try:
            # Get user metrics
            user_metrics = await self._get_user_metrics()
            
            # Get recent tweets metrics
            tweets_metrics = await self._get_tweets_metrics()
            
            # Combine metrics
            metrics = {
                **user_metrics,
                **tweets_metrics
            }
            
            return metrics
            
        except Exception as e:
            self.agent_logger.error(f"Error getting Twitter metrics: {e}")
            return {}
    
    async def _get_user_metrics(self) -> Dict[str, Any]:
        """Get user-level metrics."""
        try:
            response = await self.client.get_me(user_fields=["public_metrics"])
            user = response.data
            
            if user and user.public_metrics:
                return {
                    "followers_count": user.public_metrics.get("followers_count", 0),
                    "following_count": user.public_metrics.get("following_count", 0),
                    "tweet_count": user.public_metrics.get("tweet_count", 0),
                    "listed_count": user.public_metrics.get("listed_count", 0)
                }
            else:
                return {}
                
        except Exception as e:
            self.agent_logger.warning(f"Failed to get user metrics: {e}")
            return {}
    
    async def _get_tweets_metrics(self) -> Dict[str, Any]:
        """Get metrics for recent tweets."""
        try:
            response = await self.client.get_me()
            user_id = response.data.id
            
            tweets_response = await self.client.get_users_tweets(
                id=user_id,
                tweet_fields=["public_metrics"],
                max_results=20
            )
            tweets = tweets_response.data or []
            
            total_likes = 0
            total_retweets = 0
            total_replies = 0
            total_impressions = 0
            
            for tweet in tweets:
                if tweet.public_metrics:
                    total_likes += tweet.public_metrics.get("like_count", 0)
                    total_retweets += tweet.public_metrics.get("retweet_count", 0)
                    total_replies += tweet.public_metrics.get("reply_count", 0)
                    total_impressions += tweet.public_metrics.get("impression_count", 0)
            
            return {
                "recent_tweets_likes": total_likes,
                "recent_tweets_retweets": total_retweets,
                "recent_tweets_replies": total_replies,
                "recent_tweets_impressions": total_impressions,
                "recent_tweets_count": len(tweets)
            }
            
        except Exception as e:
            self.agent_logger.warning(f"Failed to get tweets metrics: {e}")
            return {}
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get Twitter-specific content requirements."""
        base_requirements = {
            "max_text_length": self.max_text_length,
            "max_hashtags": self.max_hashtags,
            "platform_style": "concise and impactful",
            "audience": "real-time news and trends followers",
            "tone": "witty and informative"
        }
        
        if content_type == ContentType.TEXT:
            return {
                **base_requirements,
                "focus": "breaking news, quick updates, and questions",
                "emoji_usage": "light"
            }
        elif content_type == ContentType.IMAGE or content_type == ContentType.MIXED:
            return {
                **base_requirements,
                "image_style": "infographics, memes, high-quality photos",
                "caption_length": "100-200 characters"
            }
        else:
            return base_requirements
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply Twitter-specific content optimizations."""
        # Optimize text length
        if content.text and len(content.text) > self.max_text_length:
            content.text = content.text[:self.max_text_length - 3] + "..."
        
        # Optimize hashtags
        if len(content.hashtags) > self.max_hashtags:
            content.hashtags = content.hashtags[:self.max_hashtags]
        
        # Add hashtags to text
        if content.text and content.hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in content.hashtags])
            content.text = f"{content.text}\n\n{hashtag_text}"
        
        # Add metadata
        content.metadata.update({
            "optimized_for": "twitter",
            "optimization_timestamp": datetime.utcnow().isoformat()
        })
        
        return content
    
    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """Twitter-specific content validation."""
        # Check text length
        if content.text and len(content.text) > self.max_text_length:
            self.agent_logger.warning(f"Tweet text too long: {len(content.text)} > {self.max_text_length}")
            return False
        
        # Check for client initialization
        if not self.client:
            self.agent_logger.error("Twitter client not initialized")
            return False
        
        return True
    
    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on tweets."""
        tweet_id = post.get("id")
        if not tweet_id:
            return
        
        try:
            # Check for mentions and replies
            mentions = await self._get_mentions(tweet_id)
            
            for mention in mentions:
                if await self._should_respond_to_mention(mention):
                    response = await self._generate_mention_response(mention)
                    await self._reply_to_tweet(mention.id, response)
            
        except Exception as e:
            self.agent_logger.error(f"Error handling tweet engagement: {e}")
    
    async def _get_mentions(self, tweet_id: str) -> List[Any]:
        """Get mentions for a tweet."""
        try:
            response = await self.client.get_tweet(tweet_id, expansions=["author_id"])
            # This is a simplified approach; a real implementation would search for mentions
            return []
        except Exception as e:
            self.agent_logger.warning(f"Failed to get mentions: {e}")
            return []
    
    async def _should_respond_to_mention(self, mention: Any) -> bool:
        """Determine if we should respond to a mention."""
        # Respond to direct questions and support requests
        text = mention.text.lower()
        if "?" in text or "help" in text or "support" in text:
            return True
        return False
    
    async def _generate_mention_response(self, mention: Any) -> str:
        """Generate a response to a mention."""
        mention_text = mention.text
        
        response_content = await self.content_generator.generate_content(
            platform="twitter",
            content_type=ContentType.TEXT,
            topic=f"Response to mention: {mention_text}",
            requirements={
                "max_text_length": 280,
                "tone": "helpful and concise"
            }
        )
        
        return response_content.text
    
    async def _reply_to_tweet(self, tweet_id: str, response: str):
        """Reply to a tweet."""
        try:
            await self.client.create_tweet(
                text=response,
                in_reply_to_tweet_id=tweet_id
            )
            self.agent_logger.info(f"Successfully replied to tweet {tweet_id}")
        except Exception as e:
            self.agent_logger.warning(f"Failed to reply to tweet: {e}")
    
    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent tweets for engagement checking."""
        try:
            response = await self.client.get_me()
            user_id = response.data.id
            
            tweets_response = await self.client.get_users_tweets(
                id=user_id,
                max_results=10
            )
            
            if tweets_response.data:
                return [tweet.data for tweet in tweets_response.data]
            else:
                return []
                
        except Exception as e:
            self.agent_logger.warning(f"Failed to get recent tweets: {e}")
            return []

