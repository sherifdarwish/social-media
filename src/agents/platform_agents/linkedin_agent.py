"""
LinkedIn Agent

This module implements the LinkedIn-specific social media agent focused on
professional content and business networking.
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


class LinkedInAgent(BaseAgent):
    """
    LinkedIn-specific social media agent.
    
    Handles professional content creation, posting, and business networking
    for LinkedIn company pages and personal profiles.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the LinkedIn agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="LinkedIn Professional Agent",
            platform="linkedin",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("LinkedInAgent", "linkedin")
        
        # LinkedIn-specific configuration
        self.client_id = self.platform_config.get("client_id")
        self.client_secret = self.platform_config.get("client_secret")
        self.access_token = self.platform_config.get("access_token")
        self.organization_id = self.platform_config.get("organization_id")
        
        # LinkedIn API endpoints
        self.base_url = "https://api.linkedin.com/v2"
        
        # Content settings
        self.max_text_length = 3000
        self.optimal_text_length = 1300
        self.max_hashtags = 10
        self.optimal_hashtags = 5
        
        self.agent_logger.info("LinkedIn agent initialized")
    
    async def _initialize_platform_connection(self):
        """Initialize connection to LinkedIn API."""
        try:
            # Verify access token
            await self._verify_access_token()
            
            # Verify organization access if configured
            if self.organization_id:
                await self._verify_organization_access()
            
            self.agent_logger.info("LinkedIn API connection verified")
            
        except Exception as e:
            self.agent_logger.error(f"Failed to initialize LinkedIn connection: {e}")
            raise
    
    async def _verify_access_token(self):
        """Verify the LinkedIn access token is valid."""
        url = f"{self.base_url}/me"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Invalid LinkedIn access token: {error_data}")
                
                data = await response.json()
                self.agent_logger.debug(f"Access token verified for user: {data.get('localizedFirstName')} {data.get('localizedLastName')}")
    
    async def _verify_organization_access(self):
        """Verify access to the LinkedIn organization."""
        url = f"{self.base_url}/organizations/{self.organization_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Cannot access LinkedIn organization: {error_data}")
                
                data = await response.json()
                self.agent_logger.debug(f"Organization access verified: {data.get('localizedName')}")
    
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Post content to LinkedIn."""
        try:
            if content.content_type == ContentType.TEXT:
                return await self._post_text_content(content)
            elif content.content_type == ContentType.IMAGE:
                return await self._post_image_content(content)
            elif content.content_type == ContentType.MIXED:
                return await self._post_mixed_content(content)
            else:
                raise ValueError(f"Unsupported content type for LinkedIn: {content.content_type}")
                
        except Exception as e:
            self.agent_logger.error(f"Error posting to LinkedIn: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_text_content(self, content: ContentItem) -> PostResult:
        """Post text content to LinkedIn."""
        try:
            # Determine the author (person or organization)
            author = self._get_author_urn()
            
            # Prepare post data
            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content.text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add scheduled publishing if specified
            if content.scheduled_time:
                post_data["lifecycleState"] = "DRAFT"
                # LinkedIn doesn't support scheduled publishing via API directly
                # This would need to be handled by a scheduler service
            
            url = f"{self.base_url}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=post_data, headers=headers) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        post_id = response_data.get("id")
                        self.agent_logger.log_post_activity(post_id, "create", True)
                        
                        return PostResult(
                            success=True,
                            post_id=post_id,
                            platform_response=response_data
                        )
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("message", "Unknown error")
                        self.agent_logger.log_post_activity("", "create", False, error=error_msg)
                        
                        return PostResult(
                            success=False,
                            error_message=error_msg,
                            platform_response=error_data
                        )
                        
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_image_content(self, content: ContentItem) -> PostResult:
        """Post image content to LinkedIn."""
        try:
            # Step 1: Register upload for image
            upload_url, asset_id = await self._register_image_upload()
            
            # Step 2: Upload image
            await self._upload_image(upload_url, content.image_url)
            
            # Step 3: Create post with image
            author = self._get_author_urn()
            
            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content.text or ""
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": content.text or ""
                                },
                                "media": asset_id,
                                "title": {
                                    "text": "Image Post"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            url = f"{self.base_url}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=post_data, headers=headers) as response:
                    if response.status == 201:
                        response_data = await response.json()
                        post_id = response_data.get("id")
                        self.agent_logger.log_post_activity(post_id, "create", True, content_type="image")
                        
                        return PostResult(
                            success=True,
                            post_id=post_id,
                            platform_response=response_data
                        )
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("message", "Unknown error")
                        self.agent_logger.log_post_activity("", "create", False, error=error_msg)
                        
                        return PostResult(
                            success=False,
                            error_message=error_msg,
                            platform_response=error_data
                        )
                        
        except Exception as e:
            self.agent_logger.log_post_activity("", "create", False, error=str(e))
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    async def _post_mixed_content(self, content: ContentItem) -> PostResult:
        """Post mixed content to LinkedIn."""
        # For LinkedIn, mixed content is posted as an image with text
        return await self._post_image_content(content)
    
    async def _register_image_upload(self) -> tuple[str, str]:
        """Register an image upload with LinkedIn."""
        author = self._get_author_urn()
        
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        url = f"{self.base_url}/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=register_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    asset_id = data["value"]["asset"]
                    return upload_url, asset_id
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to register upload: {error_data}")
    
    async def _upload_image(self, upload_url: str, image_url: str):
        """Upload image to LinkedIn."""
        # Download image data
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                image_data = await resp.read()
        
        # Upload to LinkedIn
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(upload_url, data=image_data, headers=headers) as response:
                if response.status != 201:
                    raise Exception(f"Failed to upload image: {response.status}")
    
    def _get_author_urn(self) -> str:
        """Get the author URN for posting."""
        if self.organization_id:
            return f"urn:li:organization:{self.organization_id}"
        else:
            # For personal posts, we'd need the person ID
            # This is a simplified approach
            return "urn:li:person:PERSON_ID"
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get metrics from LinkedIn API."""
        try:
            # Get organization metrics if available
            if self.organization_id:
                org_metrics = await self._get_organization_metrics()
            else:
                org_metrics = {}
            
            # Get post metrics
            post_metrics = await self._get_post_metrics()
            
            # Combine metrics
            metrics = {
                **org_metrics,
                **post_metrics
            }
            
            return metrics
            
        except Exception as e:
            self.agent_logger.error(f"Error getting LinkedIn metrics: {e}")
            return {}
    
    async def _get_organization_metrics(self) -> Dict[str, Any]:
        """Get LinkedIn organization metrics."""
        url = f"{self.base_url}/organizationalEntityFollowerStatistics"
        
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": f"urn:li:organization:{self.organization_id}"
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    elements = data.get("elements", [])
                    
                    if elements:
                        latest = elements[-1]
                        return {
                            "follower_count": latest.get("followerCount", 0),
                            "organic_follower_count": latest.get("organicFollowerCount", 0),
                            "paid_follower_count": latest.get("paidFollowerCount", 0)
                        }
                    else:
                        return {}
                else:
                    self.agent_logger.warning(f"Failed to get organization metrics: {response.status}")
                    return {}
    
    async def _get_post_metrics(self) -> Dict[str, Any]:
        """Get metrics for recent posts."""
        # This is a simplified implementation
        # In practice, you'd need to get recent posts and their analytics
        return {
            "recent_posts_likes": 0,
            "recent_posts_comments": 0,
            "recent_posts_shares": 0,
            "recent_posts_views": 0
        }
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Get LinkedIn-specific content requirements."""
        base_requirements = {
            "max_text_length": self.max_text_length,
            "optimal_text_length": self.optimal_text_length,
            "max_hashtags": self.max_hashtags,
            "optimal_hashtags": self.optimal_hashtags,
            "platform_style": "professional and thought-provoking",
            "audience": "business professionals and decision makers",
            "tone": "authoritative yet approachable"
        }
        
        if content_type == ContentType.TEXT:
            return {
                **base_requirements,
                "focus": "industry insights, thought leadership, professional development",
                "structure": "hook, value, call-to-action",
                "emoji_usage": "minimal and professional"
            }
        elif content_type == ContentType.IMAGE:
            return {
                **base_requirements,
                "image_style": "professional, infographics, charts, business-appropriate",
                "caption_focus": "context and insights"
            }
        else:
            return base_requirements
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Apply LinkedIn-specific content optimizations."""
        # Optimize text length for engagement
        if content.text and len(content.text) > self.optimal_text_length:
            # For LinkedIn, longer content can work, but optimize for readability
            content.text = self._format_long_content(content.text)
        
        # Optimize hashtags
        if len(content.hashtags) > self.optimal_hashtags:
            content.hashtags = content.hashtags[:self.optimal_hashtags]
        
        # Add professional formatting
        if content.text:
            content.text = self._add_professional_formatting(content.text, content.hashtags)
        
        # Add metadata
        content.metadata.update({
            "optimized_for": "linkedin",
            "optimization_timestamp": datetime.utcnow().isoformat(),
            "professional_content": True
        })
        
        return content
    
    def _format_long_content(self, text: str) -> str:
        """Format long content for better LinkedIn readability."""
        # Add line breaks for better readability
        sentences = text.split('. ')
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            formatted_sentences.append(sentence)
            # Add line break every 2-3 sentences
            if (i + 1) % 3 == 0 and i < len(sentences) - 1:
                formatted_sentences.append('\n')
        
        return '. '.join(formatted_sentences)
    
    def _add_professional_formatting(self, text: str, hashtags: List[str]) -> str:
        """Add professional formatting to LinkedIn content."""
        # Add hashtags at the end
        if hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
            text = f"{text}\n\n{hashtag_text}"
        
        # Add professional call-to-action
        if not any(phrase in text.lower() for phrase in ["what do you think", "share your thoughts", "comment below"]):
            text += "\n\nWhat are your thoughts on this? Share your perspective in the comments."
        
        return text
    
    async def _platform_specific_validation(self, content: ContentItem) -> bool:
        """LinkedIn-specific content validation."""
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
            self.agent_logger.error("LinkedIn access token not configured")
            return False
        
        # Validate professional tone
        if content.text and not self._is_professional_content(content.text):
            self.agent_logger.warning("Content may not meet professional standards")
            # Don't fail validation, just warn
        
        return True
    
    def _is_professional_content(self, text: str) -> bool:
        """Check if content meets professional standards."""
        # Simple check for professional language
        unprofessional_words = ["awesome", "cool", "sick", "lit", "fire"]
        text_lower = text.lower()
        
        for word in unprofessional_words:
            if word in text_lower:
                return False
        
        return True
    
    async def _handle_post_engagement(self, post: Dict[str, Any]):
        """Handle engagement on LinkedIn posts."""
        post_id = post.get("id")
        if not post_id:
            return
        
        try:
            # LinkedIn engagement handling would involve:
            # 1. Monitoring comments and responding professionally
            # 2. Engaging with relevant industry discussions
            # 3. Following up on business inquiries
            
            # This is a simplified implementation
            self.agent_logger.info(f"Monitoring engagement for post {post_id}")
            
        except Exception as e:
            self.agent_logger.error(f"Error handling LinkedIn engagement: {e}")
    
    async def _get_recent_posts(self) -> List[Dict[str, Any]]:
        """Get recent LinkedIn posts for engagement checking."""
        # This would require getting posts from the user's or organization's feed
        # LinkedIn API has restrictions on accessing post data
        return []

