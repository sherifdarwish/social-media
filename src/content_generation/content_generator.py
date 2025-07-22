"""
Content Generator

This module provides the main content generation functionality using various LLM providers.
"""

import asyncio
import random
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass

from ..agents.base_agent import ContentItem, ContentType
from ..config.config_manager import ConfigManager
from ..utils.logger import get_logger
from .llm_providers import LLMProvider, OpenAIProvider, AnthropicProvider, StabilityProvider


@dataclass
class ContentRequest:
    """Request for content generation."""
    platform: str
    content_type: ContentType
    topic: Optional[str] = None
    style: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None
    keywords: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None


class ContentGenerator:
    """
    Main content generation service that coordinates with various LLM providers
    to create platform-optimized content.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the content generator.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = get_logger("content_generator")
        
        # Initialize LLM providers
        self.llm_providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()
        
        # Load content templates and brand voice
        self.content_config = config_manager.get_content_config()
        self.brand_voice = self.content_config.get("brand_voice", {})
        
        self.logger.info("Content generator initialized")

    def _initialize_providers(self):
        """Initialize all configured LLM providers."""
        llm_config = self.config_manager.get_llm_config()
        
        # Initialize OpenAI provider
        if "openai" in llm_config:
            try:
                self.llm_providers["openai"] = OpenAIProvider(llm_config["openai"])
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Initialize Anthropic provider
        if "anthropic" in llm_config:
            try:
                self.llm_providers["anthropic"] = AnthropicProvider(llm_config["anthropic"])
                self.logger.info("Anthropic provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic provider: {e}")
        
        # Initialize Stability AI provider
        if "stability" in llm_config:
            try:
                self.llm_providers["stability"] = StabilityProvider(llm_config["stability"])
                self.logger.info("Stability AI provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Stability AI provider: {e}")

    async def generate_content(
        self,
        platform: str,
        content_type: ContentType,
        topic: Optional[str] = None,
        style: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ContentItem:
        """
        Generate content for a specific platform.
        
        Args:
            platform: Target platform (facebook, twitter, instagram, etc.)
            content_type: Type of content to generate
            topic: Optional topic for the content
            style: Optional style specification
            requirements: Platform-specific requirements
            **kwargs: Additional parameters
            
        Returns:
            Generated content item
        """
        try:
            # Create content request
            request = ContentRequest(
                platform=platform,
                content_type=content_type,
                topic=topic,
                style=style,
                requirements=requirements or {},
                target_audience=kwargs.get("target_audience"),
                brand_voice=self.brand_voice.get("tone"),
                keywords=kwargs.get("keywords"),
                hashtags=kwargs.get("hashtags")
            )
            
            # Generate content based on type
            if content_type == ContentType.TEXT:
                return await self._generate_text_content(request)
            elif content_type == ContentType.IMAGE:
                return await self._generate_image_content(request)
            elif content_type == ContentType.VIDEO:
                return await self._generate_video_content(request)
            elif content_type == ContentType.MIXED:
                return await self._generate_mixed_content(request)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            raise

    async def _generate_text_content(self, request: ContentRequest) -> ContentItem:
        """Generate text-based content."""
        # Select best provider for text generation
        provider = self._select_text_provider()
        
        # Build prompt for content generation
        prompt = self._build_text_prompt(request)
        
        # Generate text content
        text_content = await provider.generate_text(
            prompt=prompt,
            max_tokens=self._get_max_tokens(request.platform),
            temperature=0.7
        )
        
        # Generate hashtags if needed
        hashtags = await self._generate_hashtags(request, text_content)
        
        # Create content item
        content = ContentItem(
            content_type=ContentType.TEXT,
            text=text_content,
            hashtags=hashtags,
            metadata={
                "platform": request.platform,
                "topic": request.topic,
                "generated_at": datetime.utcnow().isoformat(),
                "provider": provider.name
            }
        )
        
        return content

    async def _generate_image_content(self, request: ContentRequest) -> ContentItem:
        """Generate image-based content."""
        # Select best provider for image generation
        provider = self._select_image_provider()
        
        # Build prompt for image generation
        prompt = self._build_image_prompt(request)
        
        # Generate image
        image_url = await provider.generate_image(
            prompt=prompt,
            size=self._get_image_size(request.platform),
            style=request.style or "photorealistic"
        )
        
        # Generate accompanying text if needed
        text_content = None
        if request.platform in ["facebook", "instagram", "linkedin"]:
            text_provider = self._select_text_provider()
            text_prompt = self._build_image_caption_prompt(request, prompt)
            text_content = await text_provider.generate_text(
                prompt=text_prompt,
                max_tokens=200,
                temperature=0.7
            )
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(request, text_content or prompt)
        
        # Create content item
        content = ContentItem(
            content_type=ContentType.IMAGE,
            text=text_content,
            image_url=image_url,
            hashtags=hashtags,
            metadata={
                "platform": request.platform,
                "topic": request.topic,
                "generated_at": datetime.utcnow().isoformat(),
                "image_provider": provider.name,
                "image_prompt": prompt
            }
        )
        
        return content

    async def _generate_video_content(self, request: ContentRequest) -> ContentItem:
        """Generate video-based content."""
        # For now, we'll generate a video concept and script
        # Actual video generation would require additional services
        
        provider = self._select_text_provider()
        
        # Generate video script
        script_prompt = self._build_video_script_prompt(request)
        script = await provider.generate_text(
            prompt=script_prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(request, script)
        
        # Create content item (video_url would be generated by video service)
        content = ContentItem(
            content_type=ContentType.VIDEO,
            text=script,
            hashtags=hashtags,
            metadata={
                "platform": request.platform,
                "topic": request.topic,
                "generated_at": datetime.utcnow().isoformat(),
                "provider": provider.name,
                "video_concept": True
            }
        )
        
        return content

    async def _generate_mixed_content(self, request: ContentRequest) -> ContentItem:
        """Generate mixed content (text + image)."""
        # Generate text content first
        text_request = ContentRequest(
            platform=request.platform,
            content_type=ContentType.TEXT,
            topic=request.topic,
            style=request.style,
            requirements=request.requirements,
            target_audience=request.target_audience,
            brand_voice=request.brand_voice
        )
        
        text_content_item = await self._generate_text_content(text_request)
        
        # Generate complementary image
        image_request = ContentRequest(
            platform=request.platform,
            content_type=ContentType.IMAGE,
            topic=request.topic,
            style=request.style,
            requirements=request.requirements
        )
        
        image_content_item = await self._generate_image_content(image_request)
        
        # Combine into mixed content
        content = ContentItem(
            content_type=ContentType.MIXED,
            text=text_content_item.text,
            image_url=image_content_item.image_url,
            hashtags=list(set(text_content_item.hashtags + image_content_item.hashtags)),
            metadata={
                "platform": request.platform,
                "topic": request.topic,
                "generated_at": datetime.utcnow().isoformat(),
                "text_provider": text_content_item.metadata.get("provider"),
                "image_provider": image_content_item.metadata.get("image_provider")
            }
        )
        
        return content

    def _select_text_provider(self) -> LLMProvider:
        """Select the best available text generation provider."""
        # Prefer OpenAI for text generation, fallback to Anthropic
        if "openai" in self.llm_providers:
            return self.llm_providers["openai"]
        elif "anthropic" in self.llm_providers:
            return self.llm_providers["anthropic"]
        else:
            raise RuntimeError("No text generation providers available")

    def _select_image_provider(self) -> LLMProvider:
        """Select the best available image generation provider."""
        # Prefer Stability AI for image generation, fallback to OpenAI
        if "stability" in self.llm_providers:
            return self.llm_providers["stability"]
        elif "openai" in self.llm_providers:
            return self.llm_providers["openai"]
        else:
            raise RuntimeError("No image generation providers available")

    def _build_text_prompt(self, request: ContentRequest) -> str:
        """Build prompt for text content generation."""
        platform_templates = self.content_config.get("templates", {})
        platform_template = platform_templates.get(request.platform, {})
        
        # Base prompt structure
        prompt_parts = [
            f"Create engaging {request.platform} content",
        ]
        
        # Add topic if specified
        if request.topic:
            prompt_parts.append(f"about {request.topic}")
        
        # Add brand voice
        if request.brand_voice:
            prompt_parts.append(f"in a {request.brand_voice} tone")
        
        # Add target audience
        if request.target_audience:
            prompt_parts.append(f"for {request.target_audience}")
        
        # Add platform-specific requirements
        if platform_template:
            length = platform_template.get("post_length", "")
            if length:
                prompt_parts.append(f"with length {length} characters")
            
            emoji_usage = platform_template.get("emoji_usage", "moderate")
            prompt_parts.append(f"using {emoji_usage} emoji usage")
        
        # Add brand personality traits
        traits = self.brand_voice.get("personality_traits", [])
        if traits:
            prompt_parts.append(f"reflecting these brand traits: {', '.join(traits)}")
        
        # Add things to avoid
        avoid = self.brand_voice.get("avoid", [])
        if avoid:
            prompt_parts.append(f"avoiding: {', '.join(avoid)}")
        
        # Add keywords if specified
        if request.keywords:
            prompt_parts.append(f"incorporating keywords: {', '.join(request.keywords)}")
        
        prompt = " ".join(prompt_parts) + "."
        
        return prompt

    def _build_image_prompt(self, request: ContentRequest) -> str:
        """Build prompt for image generation."""
        prompt_parts = []
        
        # Add topic
        if request.topic:
            prompt_parts.append(f"Image about {request.topic}")
        else:
            prompt_parts.append("Engaging visual content")
        
        # Add style
        if request.style:
            prompt_parts.append(f"in {request.style} style")
        else:
            prompt_parts.append("in professional, high-quality style")
        
        # Add platform-specific visual requirements
        if request.platform == "instagram":
            prompt_parts.append("optimized for Instagram, visually striking, good composition")
        elif request.platform == "linkedin":
            prompt_parts.append("professional, business-appropriate, clean design")
        elif request.platform == "facebook":
            prompt_parts.append("engaging, shareable, broad appeal")
        
        # Add brand elements
        prompt_parts.append("consistent with modern brand aesthetics")
        
        return ", ".join(prompt_parts)

    def _build_image_caption_prompt(self, request: ContentRequest, image_prompt: str) -> str:
        """Build prompt for image caption generation."""
        return f"Write an engaging {request.platform} caption for an image that shows: {image_prompt}. " \
               f"Make it {request.brand_voice or 'engaging'} and include relevant context."

    def _build_video_script_prompt(self, request: ContentRequest) -> str:
        """Build prompt for video script generation."""
        prompt_parts = [
            f"Create a {request.platform} video script",
        ]
        
        if request.topic:
            prompt_parts.append(f"about {request.topic}")
        
        # Platform-specific video requirements
        if request.platform == "tiktok":
            prompt_parts.append("for a 30-60 second TikTok video, engaging and trendy")
        elif request.platform == "instagram":
            prompt_parts.append("for an Instagram Reel, visually engaging")
        elif request.platform == "linkedin":
            prompt_parts.append("for a professional LinkedIn video, informative")
        
        prompt_parts.append(f"in a {request.brand_voice or 'engaging'} tone")
        
        return " ".join(prompt_parts) + ". Include scene descriptions and dialogue."

    async def _generate_hashtags(self, request: ContentRequest, content: str) -> List[str]:
        """Generate relevant hashtags for the content."""
        if request.hashtags:
            return request.hashtags
        
        provider = self._select_text_provider()
        
        # Get platform-specific hashtag requirements
        platform_templates = self.content_config.get("templates", {})
        platform_template = platform_templates.get(request.platform, {})
        hashtag_count = platform_template.get("hashtag_count", "3-5")
        
        prompt = f"Generate {hashtag_count} relevant hashtags for this {request.platform} content: {content[:200]}... " \
                f"Return only the hashtags, one per line, without the # symbol."
        
        hashtag_text = await provider.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.5
        )
        
        # Parse hashtags
        hashtags = [
            line.strip().replace("#", "")
            for line in hashtag_text.split("\n")
            if line.strip()
        ]
        
        return hashtags[:10]  # Limit to 10 hashtags max

    def _get_max_tokens(self, platform: str) -> int:
        """Get maximum tokens for platform content."""
        platform_limits = {
            "twitter": 100,
            "facebook": 300,
            "instagram": 400,
            "linkedin": 500,
            "tiktok": 200
        }
        return platform_limits.get(platform, 300)

    def _get_image_size(self, platform: str) -> str:
        """Get optimal image size for platform."""
        platform_sizes = {
            "instagram": "1024x1024",
            "facebook": "1200x630",
            "twitter": "1200x675",
            "linkedin": "1200x627",
            "tiktok": "1080x1920"
        }
        return platform_sizes.get(platform, "1024x1024")

    async def generate_content_variations(
        self,
        base_content: ContentItem,
        num_variations: int = 3
    ) -> List[ContentItem]:
        """
        Generate variations of existing content for A/B testing.
        
        Args:
            base_content: Original content to create variations from
            num_variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        variations = []
        provider = self._select_text_provider()
        
        for i in range(num_variations):
            if base_content.content_type == ContentType.TEXT:
                prompt = f"Rewrite this social media post in a different style while keeping the same message: {base_content.text}"
                
                variation_text = await provider.generate_text(
                    prompt=prompt,
                    max_tokens=self._get_max_tokens(base_content.metadata.get("platform", "facebook")),
                    temperature=0.8
                )
                
                variation = ContentItem(
                    content_type=ContentType.TEXT,
                    text=variation_text,
                    hashtags=base_content.hashtags.copy(),
                    metadata={
                        **base_content.metadata,
                        "variation_of": base_content.metadata.get("generated_at"),
                        "variation_number": i + 1
                    }
                )
                
                variations.append(variation)
        
        return variations

