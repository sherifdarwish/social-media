# Social Media Agent API Documentation

This document provides comprehensive API documentation for the Social Media Agent system, including all classes, methods, and configuration options.

## Table of Contents

1. [Core API](#core-api)
2. [Agent Classes](#agent-classes)
3. [Content Generation](#content-generation)
4. [Configuration Management](#configuration-management)
5. [Metrics and Reporting](#metrics-and-reporting)
6. [Platform Integrations](#platform-integrations)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Core API

### SocialMediaAgent

The main entry point for the social media agent system.

```python
class SocialMediaAgent:
    """
    Main social media agent system coordinator.
    
    This class provides the primary interface for managing all platform agents,
    coordinating content creation, and generating reports.
    """
    
    def __init__(self, config_path: str, log_level: str = "INFO"):
        """
        Initialize the social media agent system.
        
        Args:
            config_path (str): Path to the configuration file
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        
        Raises:
            ConfigurationError: If configuration file is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
    
    async def start_all_agents(self) -> bool:
        """
        Start all configured platform agents.
        
        Returns:
            bool: True if all agents started successfully, False otherwise
        
        Raises:
            AgentStartupError: If any agent fails to start
        """
    
    async def stop_all_agents(self) -> bool:
        """
        Stop all running platform agents.
        
        Returns:
            bool: True if all agents stopped successfully, False otherwise
        """
    
    async def create_coordinated_post(
        self, 
        content_brief: str, 
        platforms: Optional[List[str]] = None,
        content_type: str = "text",
        schedule_time: Optional[datetime] = None,
        **kwargs
    ) -> Dict[str, PostResult]:
        """
        Create and post content across specified platforms.
        
        Args:
            content_brief (str): Brief description of content to create
            platforms (List[str], optional): List of platforms to post to.
                If None, posts to all enabled platforms.
            content_type (str): Type of content ("text", "image", "video")
            schedule_time (datetime, optional): When to post the content.
                If None, posts immediately.
            **kwargs: Additional parameters for content generation
        
        Returns:
            Dict[str, PostResult]: Results for each platform
        
        Raises:
            ContentGenerationError: If content generation fails
            PlatformError: If posting to platform fails
        """
    
    async def generate_weekly_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly performance report.
        
        Args:
            start_date (datetime, optional): Start date for report period
            end_date (datetime, optional): End date for report period
            format (str): Output format ("html", "pdf", "json", "markdown")
        
        Returns:
            Dict[str, Any]: Report data and metadata
        
        Raises:
            ReportGenerationError: If report generation fails
        """
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status and health information.
        
        Returns:
            Dict[str, Any]: System status including agent states, metrics, and health
        """
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dict[str, Any]: Health check results for all components
        """
```

### PostResult

Data class representing the result of a posting operation.

```python
@dataclass
class PostResult:
    """
    Result of a content posting operation.
    
    Attributes:
        success (bool): Whether the post was successful
        post_id (str, optional): Platform-specific post ID
        url (str, optional): URL to the posted content
        content (str, optional): The actual content that was posted
        platform (str): Platform where content was posted
        timestamp (datetime): When the post was created
        error_message (str, optional): Error message if posting failed
        metadata (Dict[str, Any]): Additional platform-specific metadata
    """
    success: bool
    platform: str
    timestamp: datetime
    post_id: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PostResult to dictionary."""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PostResult':
        """Create PostResult from dictionary."""
```

## Agent Classes

### BaseAgent

Abstract base class for all platform-specific agents.

```python
class BaseAgent(ABC):
    """
    Abstract base class for all social media platform agents.
    
    This class defines the common interface and functionality that all
    platform-specific agents must implement.
    """
    
    def __init__(
        self,
        name: str,
        platform: str,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector,
        config: Dict[str, Any]
    ):
        """
        Initialize base agent.
        
        Args:
            name (str): Agent name
            platform (str): Platform name
            config_manager (ConfigManager): Configuration manager instance
            content_generator (ContentGenerator): Content generator instance
            metrics_collector (MetricsCollector): Metrics collector instance
            config (Dict[str, Any]): Agent-specific configuration
        """
    
    @abstractmethod
    async def start(self) -> bool:
        """Start the agent. Must be implemented by subclasses."""
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the agent. Must be implemented by subclasses."""
    
    @abstractmethod
    async def create_post(
        self, 
        content_type: str, 
        prompt: str,
        **kwargs
    ) -> PostResult:
        """Create and post content. Must be implemented by subclasses."""
    
    @abstractmethod
    async def _post_to_platform(
        self, 
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post content to platform. Must be implemented by subclasses."""
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Dict[str, Any]: Agent status information
        """
    
    async def collect_metrics(self) -> None:
        """Collect and store agent metrics."""
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform agent health check.
        
        Returns:
            Dict[str, Any]: Health check results
        """
```

### Platform-Specific Agents

#### FacebookAgent

```python
class FacebookAgent(BaseAgent):
    """
    Facebook-specific social media agent.
    
    Handles Facebook posts, stories, and page management with
    Facebook-specific optimizations and features.
    """
    
    async def create_post(
        self,
        content_type: str,
        prompt: str,
        post_type: str = "feed",  # "feed", "story", "reel"
        target_audience: Optional[str] = None,
        **kwargs
    ) -> PostResult:
        """
        Create and post content to Facebook.
        
        Args:
            content_type (str): Type of content ("text", "image", "video")
            prompt (str): Content generation prompt
            post_type (str): Facebook post type
            target_audience (str, optional): Target audience for the post
            **kwargs: Additional Facebook-specific parameters
        
        Returns:
            PostResult: Result of the posting operation
        """
    
    async def create_story(
        self,
        content: Dict[str, Any],
        duration: int = 24
    ) -> PostResult:
        """
        Create a Facebook story.
        
        Args:
            content (Dict[str, Any]): Story content
            duration (int): Story duration in hours
        
        Returns:
            PostResult: Result of the story creation
        """
    
    async def get_page_insights(self) -> Dict[str, Any]:
        """
        Get Facebook page insights and analytics.
        
        Returns:
            Dict[str, Any]: Page insights data
        """
```

#### TwitterAgent

```python
class TwitterAgent(BaseAgent):
    """
    Twitter/X-specific social media agent.
    
    Handles tweets, threads, and Twitter-specific features with
    real-time engagement and trending topic integration.
    """
    
    async def create_post(
        self,
        content_type: str,
        prompt: str,
        thread: bool = False,
        reply_to: Optional[str] = None,
        **kwargs
    ) -> PostResult:
        """
        Create and post content to Twitter.
        
        Args:
            content_type (str): Type of content ("text", "image", "video")
            prompt (str): Content generation prompt
            thread (bool): Whether to create a thread
            reply_to (str, optional): Tweet ID to reply to
            **kwargs: Additional Twitter-specific parameters
        
        Returns:
            PostResult: Result of the posting operation
        """
    
    async def create_thread(
        self,
        content_parts: List[str],
        **kwargs
    ) -> List[PostResult]:
        """
        Create a Twitter thread.
        
        Args:
            content_parts (List[str]): List of thread parts
            **kwargs: Additional parameters
        
        Returns:
            List[PostResult]: Results for each thread part
        """
    
    async def get_trending_topics(self, location: str = "worldwide") -> List[str]:
        """
        Get current trending topics.
        
        Args:
            location (str): Location for trending topics
        
        Returns:
            List[str]: List of trending topics
        """
```

#### LinkedInAgent

```python
class LinkedInAgent(BaseAgent):
    """
    LinkedIn-specific social media agent.
    
    Optimizes content for professional networking and business
    development with industry-specific content generation.
    """
    
    async def create_post(
        self,
        content_type: str,
        prompt: str,
        post_format: str = "article",  # "article", "post", "video"
        professional_tone: bool = True,
        **kwargs
    ) -> PostResult:
        """
        Create and post content to LinkedIn.
        
        Args:
            content_type (str): Type of content ("text", "image", "video")
            prompt (str): Content generation prompt
            post_format (str): LinkedIn post format
            professional_tone (bool): Use professional tone
            **kwargs: Additional LinkedIn-specific parameters
        
        Returns:
            PostResult: Result of the posting operation
        """
    
    async def publish_article(
        self,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> PostResult:
        """
        Publish a LinkedIn article.
        
        Args:
            title (str): Article title
            content (str): Article content
            tags (List[str], optional): Article tags
        
        Returns:
            PostResult: Result of the article publication
        """
    
    async def get_professional_insights(self) -> Dict[str, Any]:
        """
        Get LinkedIn professional insights and analytics.
        
        Returns:
            Dict[str, Any]: Professional insights data
        """
```

## Content Generation

### ContentGenerator

```python
class ContentGenerator:
    """
    AI-powered content generation system.
    
    Integrates with multiple LLM providers to generate text and image
    content optimized for different social media platforms.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        api_key_manager: APIKeyManager
    ):
        """
        Initialize content generator.
        
        Args:
            config_manager (ConfigManager): Configuration manager
            api_key_manager (APIKeyManager): API key manager
        """
    
    async def generate_text_content(
        self,
        prompt: str,
        platform: str,
        content_type: str = "text",
        max_length: Optional[int] = None,
        tone: str = "professional",
        include_hashtags: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text content using LLM.
        
        Args:
            prompt (str): Content generation prompt
            platform (str): Target platform
            content_type (str): Type of content
            max_length (int, optional): Maximum content length
            tone (str): Content tone
            include_hashtags (bool): Whether to include hashtags
            **kwargs: Additional generation parameters
        
        Returns:
            Dict[str, Any]: Generated content with metadata
        """
    
    async def generate_image_content(
        self,
        prompt: str,
        style: str = "professional",
        dimensions: str = "1080x1080",
        provider: str = "openai",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image content using AI.
        
        Args:
            prompt (str): Image generation prompt
            style (str): Image style
            dimensions (str): Image dimensions
            provider (str): AI provider to use
            **kwargs: Additional generation parameters
        
        Returns:
            Dict[str, Any]: Generated image with metadata
        """
    
    async def optimize_for_platform(
        self,
        content: str,
        platform: str,
        content_type: str = "text"
    ) -> str:
        """
        Optimize content for specific platform.
        
        Args:
            content (str): Original content
            platform (str): Target platform
            content_type (str): Type of content
        
        Returns:
            str: Optimized content
        """
    
    async def generate_hashtags(
        self,
        content: str,
        platform: str,
        max_hashtags: int = 5
    ) -> List[str]:
        """
        Generate relevant hashtags for content.
        
        Args:
            content (str): Content to generate hashtags for
            platform (str): Target platform
            max_hashtags (int): Maximum number of hashtags
        
        Returns:
            List[str]: Generated hashtags
        """
```

### LLMProvider

```python
class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using the LLM."""
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """Generate image using the LLM."""
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate the API key."""
```

## Configuration Management

### ConfigManager

```python
class ConfigManager:
    """
    Centralized configuration management system.
    
    Handles loading, validation, and management of all system
    configuration including API keys, platform settings, and
    content generation parameters.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to configuration file
        
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ConfigurationError: If configuration is invalid
        """
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get complete configuration.
        
        Returns:
            Dict[str, Any]: Complete configuration data
        """
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get specific configuration section.
        
        Args:
            section (str): Section name
        
        Returns:
            Dict[str, Any]: Section configuration
        """
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get LLM provider configuration.
        
        Args:
            provider (str, optional): Specific provider name
        
        Returns:
            Dict[str, Any]: LLM configuration
        """
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific configuration.
        
        Args:
            platform (str): Platform name
        
        Returns:
            Dict[str, Any]: Platform configuration
        """
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
    
    def save_config(self) -> None:
        """Save configuration to file."""
    
    def backup_config(self) -> str:
        """
        Create configuration backup.
        
        Returns:
            str: Path to backup file
        """
```

### APIKeyManager

```python
class APIKeyManager:
    """
    Secure API key management system.
    
    Handles encryption, storage, and retrieval of API keys
    for various LLM providers and social media platforms.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize API key manager.
        
        Args:
            config_manager (ConfigManager): Configuration manager instance
        """
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for provider.
        
        Args:
            provider (str): Provider name
        
        Returns:
            str: Decrypted API key or None if not found
        """
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for provider.
        
        Args:
            provider (str): Provider name
            api_key (str): API key to encrypt and store
        """
    
    def validate_key_access(self, provider: str) -> bool:
        """
        Validate API key access.
        
        Args:
            provider (str): Provider name
        
        Returns:
            bool: True if key is valid and accessible
        """
    
    def rotate_keys(self) -> Dict[str, bool]:
        """
        Rotate all API keys.
        
        Returns:
            Dict[str, bool]: Rotation results for each provider
        """
```

## Metrics and Reporting

### MetricsCollector

```python
class MetricsCollector:
    """
    Comprehensive metrics collection and storage system.
    
    Collects performance metrics from all agents and platforms,
    stores them in a database, and provides analytics capabilities.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize metrics collector.
        
        Args:
            config_manager (ConfigManager): Configuration manager instance
        """
    
    async def store_metrics(
        self,
        agent_name: str,
        platform: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Store metrics for an agent.
        
        Args:
            agent_name (str): Name of the agent
            platform (str): Platform name
            metrics (Dict[str, Any]): Metrics data
        """
    
    async def get_agent_metrics(
        self,
        agent_name: str,
        platform: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricSnapshot]:
        """
        Get metrics for a specific agent.
        
        Args:
            agent_name (str): Agent name
            platform (str): Platform name
            start_time (datetime, optional): Start time for metrics
            end_time (datetime, optional): End time for metrics
        
        Returns:
            List[MetricSnapshot]: List of metric snapshots
        """
    
    async def get_platform_summary(
        self,
        platform: str,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get summary metrics for a platform.
        
        Args:
            platform (str): Platform name
            period (str): Summary period
        
        Returns:
            Dict[str, Any]: Platform summary metrics
        """
```

### ReportGenerator

```python
class ReportGenerator:
    """
    Comprehensive report generation system.
    
    Generates various types of reports including weekly summaries,
    performance analytics, and custom dashboards with visualizations.
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        config: Optional[ReportConfig] = None
    ):
        """
        Initialize report generator.
        
        Args:
            metrics_collector (MetricsCollector): Metrics collector instance
            config (ReportConfig, optional): Report configuration
        """
    
    async def generate_weekly_report(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None,
        platforms: Optional[List[str]] = None
    ) -> WeeklyReport:
        """
        Generate comprehensive weekly report.
        
        Args:
            week_start (datetime, optional): Start of the week
            week_end (datetime, optional): End of the week
            platforms (List[str], optional): Platforms to include
        
        Returns:
            WeeklyReport: Generated weekly report
        """
    
    async def export_report(
        self,
        report: WeeklyReport,
        output_path: str,
        format: ReportFormat = ReportFormat.HTML
    ) -> str:
        """
        Export report to specified format.
        
        Args:
            report (WeeklyReport): Report to export
            output_path (str): Output file path
            format (ReportFormat): Export format
        
        Returns:
            str: Path to exported file
        """
```

## Error Handling

### Custom Exceptions

```python
class SocialMediaAgentError(Exception):
    """Base exception for all social media agent errors."""
    pass

class ConfigurationError(SocialMediaAgentError):
    """Raised when configuration is invalid or missing."""
    pass

class AgentStartupError(SocialMediaAgentError):
    """Raised when agent fails to start."""
    pass

class ContentGenerationError(SocialMediaAgentError):
    """Raised when content generation fails."""
    pass

class PlatformError(SocialMediaAgentError):
    """Raised when platform operation fails."""
    pass

class ReportGenerationError(SocialMediaAgentError):
    """Raised when report generation fails."""
    pass

class APIKeyError(SocialMediaAgentError):
    """Raised when API key is invalid or missing."""
    pass

class RateLimitError(SocialMediaAgentError):
    """Raised when API rate limit is exceeded."""
    pass
```

### Error Handling Patterns

```python
# Example error handling in agent methods
async def create_post(self, content_type: str, prompt: str) -> PostResult:
    try:
        # Generate content
        content = await self.content_generator.generate_text_content(
            prompt, self.platform, content_type
        )
        
        # Post to platform
        result = await self._post_to_platform(content)
        
        return PostResult(
            success=True,
            platform=self.platform,
            timestamp=datetime.utcnow(),
            **result
        )
        
    except RateLimitError as e:
        self.logger.warning(f"Rate limit exceeded: {e}")
        # Implement retry with backoff
        await asyncio.sleep(60)
        return await self.create_post(content_type, prompt)
        
    except ContentGenerationError as e:
        self.logger.error(f"Content generation failed: {e}")
        return PostResult(
            success=False,
            platform=self.platform,
            timestamp=datetime.utcnow(),
            error_message=str(e)
        )
        
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        return PostResult(
            success=False,
            platform=self.platform,
            timestamp=datetime.utcnow(),
            error_message=f"Unexpected error: {str(e)}"
        )
```

## Examples

### Basic Usage

```python
import asyncio
from social_media_agent import SocialMediaAgent

async def main():
    # Initialize agent
    agent = SocialMediaAgent("config/config.yaml")
    
    # Start all agents
    await agent.start_all_agents()
    
    # Create coordinated post
    result = await agent.create_coordinated_post(
        content_brief="Share productivity tips for remote workers",
        platforms=["facebook", "twitter", "linkedin"]
    )
    
    # Check results
    for platform, post_result in result.items():
        if post_result.success:
            print(f"✅ {platform}: {post_result.post_id}")
        else:
            print(f"❌ {platform}: {post_result.error_message}")
    
    # Generate weekly report
    report = await agent.generate_weekly_report()
    print(f"Report generated with {len(report['recommendations'])} recommendations")
    
    # Stop all agents
    await agent.stop_all_agents()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Agent Implementation

```python
from src.agents.base_agent import BaseAgent
from src.agents.base_agent import PostResult

class CustomPlatformAgent(BaseAgent):
    """Custom platform agent implementation."""
    
    async def start(self) -> bool:
        """Start the custom agent."""
        try:
            # Initialize platform client
            self.client = await self._initialize_platform_client()
            self.status = AgentStatus.RUNNING
            self.logger.info(f"{self.name} started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start {self.name}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the custom agent."""
        self.status = AgentStatus.STOPPED
        self.logger.info(f"{self.name} stopped")
        return True
    
    async def create_post(
        self, 
        content_type: str, 
        prompt: str,
        **kwargs
    ) -> PostResult:
        """Create and post content to custom platform."""
        try:
            # Generate content
            content = await self.content_generator.generate_text_content(
                prompt, self.platform, content_type
            )
            
            # Post to platform
            result = await self._post_to_platform(content)
            
            return PostResult(
                success=True,
                platform=self.platform,
                timestamp=datetime.utcnow(),
                post_id=result["id"],
                url=result["url"],
                content=content["content"]
            )
            
        except Exception as e:
            return PostResult(
                success=False,
                platform=self.platform,
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _post_to_platform(
        self, 
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post content to the custom platform."""
        # Implement platform-specific posting logic
        response = await self.client.create_post(
            text=content["content"],
            hashtags=content.get("hashtags", [])
        )
        return {
            "id": response["post_id"],
            "url": response["post_url"]
        }
```

### Content Generation Customization

```python
from src.content_generation.content_generator import ContentGenerator

class CustomContentGenerator(ContentGenerator):
    """Custom content generator with specialized templates."""
    
    async def generate_text_content(
        self,
        prompt: str,
        platform: str,
        content_type: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate custom text content."""
        
        # Use custom templates based on content type
        if content_type == "tip":
            template = self._get_tip_template(platform)
        elif content_type == "question":
            template = self._get_question_template(platform)
        else:
            template = self._get_default_template(platform)
        
        # Generate content using template
        full_prompt = template.format(prompt=prompt, **kwargs)
        
        # Call LLM provider
        content = await self.llm_provider.generate_text(
            full_prompt,
            max_tokens=self._get_max_tokens(platform),
            temperature=0.7
        )
        
        # Generate hashtags
        hashtags = await self.generate_hashtags(content, platform)
        
        return {
            "content": content,
            "hashtags": hashtags,
            "metadata": {
                "template": template,
                "platform": platform,
                "content_type": content_type
            }
        }
    
    def _get_tip_template(self, platform: str) -> str:
        """Get tip template for platform."""
        templates = {
            "twitter": "💡 Pro tip: {prompt}\n\nWhat's your experience with this?",
            "linkedin": "Professional insight: {prompt}\n\nI'd love to hear your thoughts on this approach.",
            "facebook": "Here's a helpful tip: {prompt}\n\nHave you tried this before? Let me know in the comments!"
        }
        return templates.get(platform, templates["twitter"])
```

### Metrics and Reporting

```python
from src.metrics.metrics_collector import MetricsCollector
from src.metrics.report_generator import ReportGenerator

async def generate_custom_report():
    """Generate a custom analytics report."""
    
    # Initialize components
    metrics_collector = MetricsCollector(config_manager)
    report_generator = ReportGenerator(metrics_collector)
    
    # Collect metrics for specific period
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    # Generate comprehensive report
    report = await report_generator.generate_weekly_report(
        week_start=start_date,
        week_end=end_date,
        platforms=["facebook", "twitter", "linkedin"]
    )
    
    # Export in multiple formats
    await report_generator.export_report(
        report, "reports/monthly_report.html", ReportFormat.HTML
    )
    await report_generator.export_report(
        report, "reports/monthly_report.pdf", ReportFormat.PDF
    )
    await report_generator.export_report(
        report, "reports/monthly_report.json", ReportFormat.JSON
    )
    
    # Print summary
    print(f"Report Period: {start_date.date()} to {end_date.date()}")
    print(f"Total Posts: {report.summary['totals']['posts']}")
    print(f"Total Engagement: {report.summary['totals']['engagement']}")
    print(f"Average Engagement Rate: {report.summary['averages']['engagement_rate']}%")
    print(f"Recommendations: {len(report.recommendations)}")
```

## Rate Limiting and Best Practices

### Rate Limiting

```python
from src.utils.rate_limiter import RateLimiter

class PlatformAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    
    async def create_post(self, *args, **kwargs):
        # Check rate limits before posting
        await self.rate_limiter.acquire()
        
        try:
            return await super().create_post(*args, **kwargs)
        finally:
            # Release rate limit slot
            self.rate_limiter.release()
```

### Best Practices

1. **Error Handling**: Always implement comprehensive error handling
2. **Rate Limiting**: Respect platform API rate limits
3. **Logging**: Use structured logging for debugging and monitoring
4. **Configuration**: Use environment variables for sensitive data
5. **Testing**: Write unit and integration tests for all components
6. **Security**: Encrypt API keys and use secure communication
7. **Monitoring**: Implement health checks and metrics collection
8. **Documentation**: Keep API documentation up to date

For more examples and tutorials, see the [examples directory](../examples/) and [tutorials](../tutorials/).

