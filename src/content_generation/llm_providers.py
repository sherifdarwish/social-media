"""
LLM Provider Implementations

This module contains implementations for various LLM providers including
OpenAI, Anthropic, and Stability AI.
"""

import asyncio
import aiohttp
import openai
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import base64
import io

from ..utils.logger import get_logger


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times = []
        self.token_usage = []
        
    async def wait_if_needed(self, estimated_tokens: int = 0):
        """Wait if rate limits would be exceeded."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self.request_times = [t for t in self.request_times if t > minute_ago]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > minute_ago]
        
        # Check request rate limit
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Check token rate limit
        current_tokens = sum(tokens for _, tokens in self.token_usage)
        if current_tokens + estimated_tokens > self.tokens_per_minute:
            sleep_time = 60 - (now - self.token_usage[0][0]).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Record this request
        self.request_times.append(now)
        if estimated_tokens > 0:
            self.token_usage.append((now, estimated_tokens))


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.logger = get_logger(f"llm_provider.{self.name.lower()}")
        
        # Initialize rate limiter
        rate_limits = config.get("rate_limits", {})
        self.rate_limiter = RateLimiter(
            requests_per_minute=rate_limits.get("requests_per_minute", 60),
            tokens_per_minute=rate_limits.get("tokens_per_minute", 150000)
        )
        
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text content."""
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
        **kwargs
    ) -> str:
        """Generate image and return URL."""
        pass
    
    async def is_available(self) -> bool:
        """Check if the provider is available."""
        try:
            # Simple test request
            await self.generate_text("Test", max_tokens=1)
            return True
        except Exception as e:
            self.logger.error(f"Provider availability check failed: {e}")
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for text and image generation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=config["api_key"],
            base_url=config.get("api_base", "https://api.openai.com/v1")
        )
        
        self.text_model = config.get("models", {}).get("text", "gpt-4-turbo-preview")
        self.image_model = config.get("models", {}).get("image", "dall-e-3")
        
        self.logger.info(f"OpenAI provider initialized with models: {self.text_model}, {self.image_model}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI's GPT models."""
        try:
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed(estimated_tokens=max_tokens)
            
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "You are a helpful social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            content = response.choices[0].message.content
            self.logger.debug(f"Generated text: {content[:100]}...")
            
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
        **kwargs
    ) -> str:
        """Generate image using OpenAI's DALL-E."""
        try:
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed()
            
            response = await self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                quality="standard",
                style=style,
                n=1
            )
            
            image_url = response.data[0].url
            self.logger.debug(f"Generated image: {image_url}")
            
            return image_url
            
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider for text generation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.api_key = config["api_key"]
        self.api_base = config.get("api_base", "https://api.anthropic.com")
        self.model = config.get("models", {}).get("text", "claude-3-opus-20240229")
        
        self.logger.info(f"Anthropic provider initialized with model: {self.model}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Anthropic's Claude."""
        try:
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed(estimated_tokens=max_tokens)
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": f"You are a helpful social media content creator. {prompt}"
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/v1/messages",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["content"][0]["text"]
                        self.logger.debug(f"Generated text: {content[:100]}...")
                        return content.strip()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
        **kwargs
    ) -> str:
        """Anthropic doesn't support image generation."""
        raise NotImplementedError("Anthropic provider doesn't support image generation")


class StabilityProvider(LLMProvider):
    """Stability AI provider for image generation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.api_key = config["api_key"]
        self.api_base = config.get("api_base", "https://api.stability.ai")
        self.model = config.get("models", {}).get("image", "stable-diffusion-xl-1024-v1-0")
        
        self.logger.info(f"Stability AI provider initialized with model: {self.model}")
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Stability AI doesn't support text generation."""
        raise NotImplementedError("Stability AI provider doesn't support text generation")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
        **kwargs
    ) -> str:
        """Generate image using Stability AI."""
        try:
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Parse size
            width, height = map(int, size.split("x"))
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,
                "style_preset": style if style in ["enhance", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "analog-film", "neon-punk", "isometric", "low-poly", "origami", "modeling-compound", "cinematic", "3d-model", "pixel-art", "tile-texture"] else "photographic"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/v1/generation/{self.model}/text-to-image",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Stability AI returns base64 encoded images
                        image_data = result["artifacts"][0]["base64"]
                        
                        # For now, we'll return a placeholder URL
                        # In a real implementation, you'd upload this to a CDN
                        image_url = f"data:image/png;base64,{image_data}"
                        
                        self.logger.debug(f"Generated image with Stability AI")
                        return image_url
                    else:
                        error_text = await response.text()
                        raise Exception(f"Stability AI API error: {response.status} - {error_text}")
                        
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            raise


class ProviderManager:
    """Manages multiple LLM providers with fallback support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.providers: Dict[str, LLMProvider] = {}
        self.logger = get_logger("provider_manager")
        
        # Initialize all configured providers
        for provider_name, provider_config in config.items():
            try:
                if provider_name == "openai":
                    self.providers[provider_name] = OpenAIProvider(provider_config)
                elif provider_name == "anthropic":
                    self.providers[provider_name] = AnthropicProvider(provider_config)
                elif provider_name == "stability":
                    self.providers[provider_name] = StabilityProvider(provider_config)
                else:
                    self.logger.warning(f"Unknown provider: {provider_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {provider_name}: {e}")
    
    async def generate_text(
        self,
        prompt: str,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text with fallback support."""
        providers_to_try = []
        
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
        
        # Add other text-capable providers
        for name, provider in self.providers.items():
            if name not in providers_to_try and hasattr(provider, 'generate_text'):
                try:
                    # Check if provider supports text generation
                    await provider.generate_text("test", max_tokens=1)
                    providers_to_try.append(name)
                except NotImplementedError:
                    continue
                except Exception:
                    continue
        
        # Try each provider until one succeeds
        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                result = await provider.generate_text(prompt, **kwargs)
                self.logger.debug(f"Text generated successfully with {provider_name}")
                return result
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        raise Exception("All text generation providers failed")
    
    async def generate_image(
        self,
        prompt: str,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate image with fallback support."""
        providers_to_try = []
        
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
        
        # Add other image-capable providers
        for name, provider in self.providers.items():
            if name not in providers_to_try and hasattr(provider, 'generate_image'):
                try:
                    # Check if provider supports image generation
                    await provider.generate_image("test image", size="512x512")
                    providers_to_try.append(name)
                except NotImplementedError:
                    continue
                except Exception:
                    continue
        
        # Try each provider until one succeeds
        for provider_name in providers_to_try:
            try:
                provider = self.providers[provider_name]
                result = await provider.generate_image(prompt, **kwargs)
                self.logger.debug(f"Image generated successfully with {provider_name}")
                return result
            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        raise Exception("All image generation providers failed")
    
    async def check_provider_health(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health_status = {}
        
        for name, provider in self.providers.items():
            try:
                health_status[name] = await provider.is_available()
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                health_status[name] = False
        
        return health_status

