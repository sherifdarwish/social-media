"""
Content Optimizer

This module implements platform-specific content optimization to ensure
content is tailored for each social media platform's unique requirements.
"""

import re
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..agents.base_agent import ContentItem, ContentType
from ..utils.logger import get_logger


class OptimizationLevel(Enum):
    """Levels of content optimization."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"


@dataclass
class PlatformRequirements:
    """Platform-specific content requirements."""
    max_text_length: int
    max_hashtags: int
    optimal_hashtags: int
    supports_images: bool
    supports_videos: bool
    supports_links: bool
    optimal_image_ratio: str
    optimal_video_duration: int  # seconds
    character_limits: Dict[str, int]
    hashtag_placement: str  # "inline", "end", "separate"
    emoji_usage: str  # "minimal", "moderate", "heavy"
    link_handling: str  # "direct", "shortened", "bio"
    content_style: str  # "professional", "casual", "creative"


@dataclass
class OptimizationResult:
    """Result of content optimization."""
    original_content: ContentItem
    optimized_content: ContentItem
    changes_made: List[str]
    optimization_score: float
    warnings: List[str]
    suggestions: List[str]


class ContentOptimizer:
    """
    Platform-specific content optimizer.
    
    Optimizes content for each social media platform's unique requirements,
    character limits, hashtag conventions, and audience expectations.
    """
    
    def __init__(self):
        """Initialize the content optimizer."""
        self.logger = get_logger("content_optimizer")
        
        # Platform requirements
        self.platform_requirements = self._load_platform_requirements()
        
        # Optimization rules
        self.optimization_rules = self._load_optimization_rules()
        
        # Content analysis patterns
        self.analysis_patterns = self._load_analysis_patterns()
        
        self.logger.info("Content optimizer initialized")
    
    def _load_platform_requirements(self) -> Dict[str, PlatformRequirements]:
        """Load platform-specific requirements."""
        return {
            "facebook": PlatformRequirements(
                max_text_length=63206,
                max_hashtags=30,
                optimal_hashtags=3,
                supports_images=True,
                supports_videos=True,
                supports_links=True,
                optimal_image_ratio="16:9",
                optimal_video_duration=60,
                character_limits={"post": 63206, "comment": 8000},
                hashtag_placement="end",
                emoji_usage="moderate",
                link_handling="direct",
                content_style="casual"
            ),
            "twitter": PlatformRequirements(
                max_text_length=280,
                max_hashtags=10,
                optimal_hashtags=2,
                supports_images=True,
                supports_videos=True,
                supports_links=True,
                optimal_image_ratio="16:9",
                optimal_video_duration=140,
                character_limits={"tweet": 280, "thread": 280},
                hashtag_placement="inline",
                emoji_usage="moderate",
                link_handling="shortened",
                content_style="casual"
            ),
            "instagram": PlatformRequirements(
                max_text_length=2200,
                max_hashtags=30,
                optimal_hashtags=11,
                supports_images=True,
                supports_videos=True,
                supports_links=False,
                optimal_image_ratio="1:1",
                optimal_video_duration=60,
                character_limits={"caption": 2200, "comment": 2200, "bio": 150},
                hashtag_placement="end",
                emoji_usage="heavy",
                link_handling="bio",
                content_style="creative"
            ),
            "linkedin": PlatformRequirements(
                max_text_length=3000,
                max_hashtags=5,
                optimal_hashtags=3,
                supports_images=True,
                supports_videos=True,
                supports_links=True,
                optimal_image_ratio="1.91:1",
                optimal_video_duration=180,
                character_limits={"post": 3000, "comment": 1250, "headline": 220},
                hashtag_placement="end",
                emoji_usage="minimal",
                link_handling="direct",
                content_style="professional"
            ),
            "tiktok": PlatformRequirements(
                max_text_length=2200,
                max_hashtags=100,
                optimal_hashtags=5,
                supports_images=False,
                supports_videos=True,
                supports_links=False,
                optimal_image_ratio="9:16",
                optimal_video_duration=30,
                character_limits={"caption": 2200, "comment": 150},
                hashtag_placement="end",
                emoji_usage="heavy",
                link_handling="bio",
                content_style="creative"
            )
        }
    
    def _load_optimization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load optimization rules for each platform."""
        return {
            "facebook": {
                "text_optimization": {
                    "use_line_breaks": True,
                    "call_to_action": True,
                    "question_engagement": True,
                    "storytelling": True
                },
                "hashtag_optimization": {
                    "use_trending": True,
                    "mix_broad_specific": True,
                    "avoid_overuse": True
                },
                "timing_optimization": {
                    "peak_hours": ["9-10", "15-16", "20-21"],
                    "best_days": ["Tuesday", "Wednesday", "Thursday"]
                }
            },
            "twitter": {
                "text_optimization": {
                    "concise_messaging": True,
                    "thread_for_long_content": True,
                    "use_mentions": True,
                    "trending_topics": True
                },
                "hashtag_optimization": {
                    "trending_hashtags": True,
                    "event_hashtags": True,
                    "community_hashtags": True
                },
                "timing_optimization": {
                    "peak_hours": ["8-9", "12-13", "17-18"],
                    "best_days": ["Tuesday", "Wednesday", "Thursday"]
                }
            },
            "instagram": {
                "text_optimization": {
                    "storytelling": True,
                    "behind_scenes": True,
                    "user_generated_content": True,
                    "call_to_action": True
                },
                "hashtag_optimization": {
                    "niche_hashtags": True,
                    "location_hashtags": True,
                    "branded_hashtags": True,
                    "trending_hashtags": True
                },
                "visual_optimization": {
                    "high_quality_images": True,
                    "consistent_aesthetic": True,
                    "carousel_posts": True
                }
            },
            "linkedin": {
                "text_optimization": {
                    "professional_tone": True,
                    "industry_insights": True,
                    "thought_leadership": True,
                    "data_driven": True
                },
                "hashtag_optimization": {
                    "industry_hashtags": True,
                    "professional_hashtags": True,
                    "skill_hashtags": True
                },
                "engagement_optimization": {
                    "ask_questions": True,
                    "share_experiences": True,
                    "provide_value": True
                }
            },
            "tiktok": {
                "text_optimization": {
                    "hook_first_3_seconds": True,
                    "trending_sounds": True,
                    "challenge_participation": True,
                    "quick_tips": True
                },
                "hashtag_optimization": {
                    "trending_hashtags": True,
                    "challenge_hashtags": True,
                    "fyp_hashtags": True,
                    "niche_hashtags": True
                },
                "video_optimization": {
                    "vertical_format": True,
                    "quick_cuts": True,
                    "text_overlays": True,
                    "trending_effects": True
                }
            }
        }
    
    def _load_analysis_patterns(self) -> Dict[str, List[str]]:
        """Load content analysis patterns."""
        return {
            "engagement_triggers": [
                r"\b(how to|tips|guide|tutorial)\b",
                r"\b(question|ask|tell me|what do you think)\b",
                r"\b(free|discount|sale|offer)\b",
                r"\b(new|latest|breaking|update)\b",
                r"\b(behind the scenes|exclusive|sneak peek)\b"
            ],
            "call_to_action": [
                r"\b(click|tap|swipe|share|comment|like)\b",
                r"\b(visit|check out|learn more|sign up)\b",
                r"\b(download|get|try|start)\b",
                r"\b(follow|subscribe|join)\b"
            ],
            "emotional_words": [
                r"\b(amazing|incredible|awesome|fantastic)\b",
                r"\b(love|excited|thrilled|passionate)\b",
                r"\b(inspiring|motivating|empowering)\b",
                r"\b(shocking|surprising|unbelievable)\b"
            ],
            "urgency_words": [
                r"\b(now|today|limited|hurry|last chance)\b",
                r"\b(urgent|immediate|quick|fast)\b",
                r"\b(deadline|expires|ending soon)\b"
            ]
        }
    
    async def optimize_content(
        self,
        content: ContentItem,
        platform: str,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
        custom_requirements: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Optimize content for a specific platform.
        
        Args:
            content: Content to optimize
            platform: Target platform
            optimization_level: Level of optimization to apply
            custom_requirements: Custom optimization requirements
        
        Returns:
            Optimization result with optimized content and analysis
        """
        self.logger.info(f"Optimizing content for {platform}")
        
        # Get platform requirements
        requirements = self.platform_requirements.get(platform)
        if not requirements:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Apply custom requirements
        if custom_requirements:
            requirements = self._merge_requirements(requirements, custom_requirements)
        
        # Create optimized content copy
        optimized_content = ContentItem(
            content_type=content.content_type,
            text=content.text,
            image_url=content.image_url,
            video_url=content.video_url,
            hashtags=content.hashtags.copy() if content.hashtags else [],
            platform=platform,
            topic=content.topic,
            metadata=content.metadata.copy() if content.metadata else {}
        )
        
        changes_made = []
        warnings = []
        suggestions = []
        
        # Apply optimizations based on level
        if optimization_level in [OptimizationLevel.BASIC, OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED, OptimizationLevel.AGGRESSIVE]:
            # Text optimization
            optimized_content, text_changes = await self._optimize_text(
                optimized_content, platform, requirements, optimization_level
            )
            changes_made.extend(text_changes)
            
            # Hashtag optimization
            optimized_content, hashtag_changes = await self._optimize_hashtags(
                optimized_content, platform, requirements, optimization_level
            )
            changes_made.extend(hashtag_changes)
        
        if optimization_level in [OptimizationLevel.STANDARD, OptimizationLevel.ADVANCED, OptimizationLevel.AGGRESSIVE]:
            # Platform-specific optimization
            optimized_content, platform_changes = await self._optimize_platform_specific(
                optimized_content, platform, requirements, optimization_level
            )
            changes_made.extend(platform_changes)
            
            # Engagement optimization
            optimized_content, engagement_changes = await self._optimize_engagement(
                optimized_content, platform, requirements, optimization_level
            )
            changes_made.extend(engagement_changes)
        
        if optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.AGGRESSIVE]:
            # Advanced optimization
            optimized_content, advanced_changes = await self._optimize_advanced(
                optimized_content, platform, requirements, optimization_level
            )
            changes_made.extend(advanced_changes)
        
        # Generate warnings and suggestions
        warnings = await self._generate_warnings(optimized_content, platform, requirements)
        suggestions = await self._generate_suggestions(optimized_content, platform, requirements)
        
        # Calculate optimization score
        optimization_score = await self._calculate_optimization_score(
            content, optimized_content, platform, requirements
        )
        
        # Update metadata
        optimized_content.metadata.update({
            "optimized_for": platform,
            "optimization_level": optimization_level.value,
            "optimization_timestamp": datetime.utcnow().isoformat(),
            "optimization_score": optimization_score,
            "changes_count": len(changes_made)
        })
        
        return OptimizationResult(
            original_content=content,
            optimized_content=optimized_content,
            changes_made=changes_made,
            optimization_score=optimization_score,
            warnings=warnings,
            suggestions=suggestions
        )
    
    async def _optimize_text(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements,
        level: OptimizationLevel
    ) -> Tuple[ContentItem, List[str]]:
        """Optimize text content for platform."""
        changes = []
        
        if not content.text:
            return content, changes
        
        original_text = content.text
        optimized_text = original_text
        
        # Length optimization
        if len(optimized_text) > requirements.max_text_length:
            optimized_text = optimized_text[:requirements.max_text_length - 3] + "..."
            changes.append(f"Truncated text to {requirements.max_text_length} characters")
        
        # Platform-specific text formatting
        if platform == "twitter" and len(optimized_text) > 240:
            # Suggest thread for long content
            changes.append("Consider creating a Twitter thread for longer content")
        
        if platform == "linkedin":
            # Add professional formatting
            if not optimized_text.endswith(('.', '!', '?')):
                optimized_text += "."
                changes.append("Added proper punctuation for professional tone")
        
        if platform == "instagram":
            # Add line breaks for readability
            if '\n\n' not in optimized_text and len(optimized_text) > 100:
                # Add line breaks at sentence boundaries
                sentences = optimized_text.split('. ')
                if len(sentences) > 2:
                    mid_point = len(sentences) // 2
                    optimized_text = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
                    changes.append("Added line breaks for better readability")
        
        # Emoji optimization based on platform
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', optimized_text))
        
        if requirements.emoji_usage == "minimal" and emoji_count > 2:
            changes.append("Consider reducing emoji usage for professional platforms")
        elif requirements.emoji_usage == "heavy" and emoji_count < 3:
            changes.append("Consider adding more emojis for visual appeal")
        
        # Call-to-action optimization
        cta_patterns = self.analysis_patterns["call_to_action"]
        has_cta = any(re.search(pattern, optimized_text, re.IGNORECASE) for pattern in cta_patterns)
        
        if not has_cta and level in [OptimizationLevel.ADVANCED, OptimizationLevel.AGGRESSIVE]:
            platform_ctas = {
                "facebook": "What do you think? Share your thoughts below!",
                "twitter": "Retweet if you agree!",
                "instagram": "Double tap if you love this! 💖",
                "linkedin": "What's your experience with this? Share in the comments.",
                "tiktok": "Follow for more tips! 🔥"
            }
            
            if platform in platform_ctas:
                optimized_text += f"\n\n{platform_ctas[platform]}"
                changes.append("Added platform-specific call-to-action")
        
        content.text = optimized_text
        return content, changes
    
    async def _optimize_hashtags(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements,
        level: OptimizationLevel
    ) -> Tuple[ContentItem, List[str]]:
        """Optimize hashtags for platform."""
        changes = []
        
        if not content.hashtags:
            content.hashtags = []
        
        original_hashtags = content.hashtags.copy()
        
        # Remove excess hashtags
        if len(content.hashtags) > requirements.max_hashtags:
            content.hashtags = content.hashtags[:requirements.max_hashtags]
            changes.append(f"Reduced hashtags to platform limit of {requirements.max_hashtags}")
        
        # Optimize hashtag count
        if len(content.hashtags) < requirements.optimal_hashtags:
            # Add platform-specific hashtags
            platform_hashtags = {
                "facebook": ["trending", "viral", "share"],
                "twitter": ["trending", "news", "update"],
                "instagram": ["instagood", "photooftheday", "beautiful", "amazing", "love"],
                "linkedin": ["professional", "business", "networking", "career", "industry"],
                "tiktok": ["fyp", "viral", "trending", "foryou", "tiktok"]
            }
            
            suggested_hashtags = platform_hashtags.get(platform, [])
            needed = requirements.optimal_hashtags - len(content.hashtags)
            
            for hashtag in suggested_hashtags[:needed]:
                if hashtag not in content.hashtags:
                    content.hashtags.append(hashtag)
            
            if len(content.hashtags) > len(original_hashtags):
                changes.append(f"Added {len(content.hashtags) - len(original_hashtags)} platform-optimized hashtags")
        
        # Clean hashtags
        cleaned_hashtags = []
        for hashtag in content.hashtags:
            # Remove special characters and spaces
            clean_hashtag = re.sub(r'[^a-zA-Z0-9]', '', hashtag)
            if clean_hashtag and clean_hashtag not in cleaned_hashtags:
                cleaned_hashtags.append(clean_hashtag)
        
        if len(cleaned_hashtags) != len(content.hashtags):
            content.hashtags = cleaned_hashtags
            changes.append("Cleaned and deduplicated hashtags")
        
        # Platform-specific hashtag formatting
        if platform == "twitter":
            # Keep hashtags short for Twitter
            content.hashtags = [tag[:15] for tag in content.hashtags]
            changes.append("Shortened hashtags for Twitter")
        
        return content, changes
    
    async def _optimize_platform_specific(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements,
        level: OptimizationLevel
    ) -> Tuple[ContentItem, List[str]]:
        """Apply platform-specific optimizations."""
        changes = []
        
        # Platform-specific content adjustments
        if platform == "linkedin" and content.text:
            # Add professional elements
            if not any(word in content.text.lower() for word in ["insight", "experience", "professional", "industry", "business"]):
                changes.append("Consider adding professional context for LinkedIn")
        
        if platform == "instagram" and content.content_type == ContentType.IMAGE:
            # Suggest visual enhancements
            changes.append("Ensure high-quality, visually appealing image for Instagram")
        
        if platform == "tiktok" and content.content_type == ContentType.VIDEO:
            # Video-specific optimizations
            changes.append("Ensure vertical video format (9:16) for TikTok")
            changes.append("Add engaging hook in first 3 seconds")
        
        if platform == "facebook":
            # Facebook-specific optimizations
            if content.text and len(content.text) < 40:
                changes.append("Consider expanding content for better Facebook engagement")
        
        return content, changes
    
    async def _optimize_engagement(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements,
        level: OptimizationLevel
    ) -> Tuple[ContentItem, List[str]]:
        """Optimize content for engagement."""
        changes = []
        
        if not content.text:
            return content, changes
        
        # Check for engagement triggers
        engagement_patterns = self.analysis_patterns["engagement_triggers"]
        has_engagement_trigger = any(re.search(pattern, content.text, re.IGNORECASE) for pattern in engagement_patterns)
        
        if not has_engagement_trigger:
            changes.append("Consider adding engagement triggers (how-to, tips, questions)")
        
        # Check for emotional words
        emotional_patterns = self.analysis_patterns["emotional_words"]
        has_emotional_words = any(re.search(pattern, content.text, re.IGNORECASE) for pattern in emotional_patterns)
        
        if not has_emotional_words and level == OptimizationLevel.AGGRESSIVE:
            changes.append("Consider adding emotional words to increase engagement")
        
        # Platform-specific engagement optimization
        if platform == "instagram":
            # Check for storytelling elements
            if "story" not in content.text.lower() and "behind" not in content.text.lower():
                changes.append("Consider adding storytelling elements for Instagram")
        
        if platform == "linkedin":
            # Check for professional insights
            if not any(word in content.text.lower() for word in ["insight", "learn", "experience", "tip"]):
                changes.append("Consider adding professional insights or learnings")
        
        return content, changes
    
    async def _optimize_advanced(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements,
        level: OptimizationLevel
    ) -> Tuple[ContentItem, List[str]]:
        """Apply advanced optimizations."""
        changes = []
        
        # Advanced text analysis and optimization
        if content.text:
            # Readability optimization
            sentences = content.text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            if avg_sentence_length > 20:
                changes.append("Consider shorter sentences for better readability")
            
            # Keyword density analysis
            words = content.text.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Check for keyword stuffing
            total_words = len(words)
            for word, freq in word_freq.items():
                if freq / total_words > 0.1 and len(word) > 3:  # More than 10% frequency
                    changes.append(f"Consider reducing repetition of '{word}'")
        
        # Advanced hashtag analysis
        if content.hashtags:
            # Check hashtag relevance
            if content.topic:
                topic_words = content.topic.lower().split()
                relevant_hashtags = [tag for tag in content.hashtags if any(word in tag.lower() for word in topic_words)]
                
                if len(relevant_hashtags) < len(content.hashtags) * 0.5:
                    changes.append("Consider using more topic-relevant hashtags")
        
        return content, changes
    
    async def _generate_warnings(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements
    ) -> List[str]:
        """Generate warnings for potential issues."""
        warnings = []
        
        # Text length warnings
        if content.text:
            if len(content.text) > requirements.max_text_length * 0.9:
                warnings.append("Text is close to platform character limit")
            
            if len(content.text) < 20:
                warnings.append("Text might be too short for optimal engagement")
        
        # Hashtag warnings
        if len(content.hashtags) > requirements.optimal_hashtags * 1.5:
            warnings.append("Using more hashtags than optimal for this platform")
        
        if len(content.hashtags) == 0:
            warnings.append("No hashtags used - consider adding relevant hashtags")
        
        # Platform-specific warnings
        if platform == "instagram" and not content.image_url and content.content_type != ContentType.VIDEO:
            warnings.append("Instagram posts perform better with visual content")
        
        if platform == "linkedin" and content.text and "linkedin.com" in content.text.lower():
            warnings.append("Avoid self-referential LinkedIn links in posts")
        
        return warnings
    
    async def _generate_suggestions(
        self,
        content: ContentItem,
        platform: str,
        requirements: PlatformRequirements
    ) -> List[str]:
        """Generate suggestions for improvement."""
        suggestions = []
        
        # Platform-specific suggestions
        platform_suggestions = {
            "facebook": [
                "Consider asking a question to encourage comments",
                "Use Facebook's native video for better reach",
                "Post during peak hours (1-3 PM)"
            ],
            "twitter": [
                "Use trending hashtags for better visibility",
                "Engage with replies to boost engagement",
                "Consider creating a thread for complex topics"
            ],
            "instagram": [
                "Use Instagram Stories for behind-the-scenes content",
                "Create carousel posts for step-by-step content",
                "Use location tags for local discovery"
            ],
            "linkedin": [
                "Share industry insights and professional experiences",
                "Tag relevant professionals or companies",
                "Use LinkedIn articles for long-form content"
            ],
            "tiktok": [
                "Use trending sounds and effects",
                "Participate in popular challenges",
                "Keep videos under 60 seconds for better engagement"
            ]
        }
        
        suggestions.extend(platform_suggestions.get(platform, []))
        
        # Content-specific suggestions
        if content.content_type == ContentType.TEXT:
            suggestions.append("Consider adding visual elements (images/videos)")
        
        if not content.hashtags:
            suggestions.append("Add relevant hashtags to increase discoverability")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    async def _calculate_optimization_score(
        self,
        original: ContentItem,
        optimized: ContentItem,
        platform: str,
        requirements: PlatformRequirements
    ) -> float:
        """Calculate optimization score (0-100)."""
        score = 0.0
        max_score = 100.0
        
        # Text length score (20 points)
        if optimized.text:
            text_length = len(optimized.text)
            optimal_length = requirements.max_text_length * 0.7  # 70% of max is considered optimal
            
            if text_length <= optimal_length:
                score += 20.0
            else:
                # Deduct points for being too long
                excess_ratio = (text_length - optimal_length) / optimal_length
                score += max(0, 20.0 - (excess_ratio * 10))
        
        # Hashtag score (20 points)
        hashtag_count = len(optimized.hashtags)
        if hashtag_count == requirements.optimal_hashtags:
            score += 20.0
        elif hashtag_count > 0:
            # Partial score based on how close to optimal
            ratio = min(hashtag_count / requirements.optimal_hashtags, 2.0)  # Cap at 2x optimal
            score += 20.0 * (1 - abs(1 - ratio))
        
        # Platform compliance score (20 points)
        if text_length <= requirements.max_text_length:
            score += 10.0
        if hashtag_count <= requirements.max_hashtags:
            score += 10.0
        
        # Content quality score (20 points)
        if optimized.text:
            # Check for engagement elements
            engagement_patterns = self.analysis_patterns["engagement_triggers"]
            has_engagement = any(re.search(pattern, optimized.text, re.IGNORECASE) for pattern in engagement_patterns)
            if has_engagement:
                score += 10.0
            
            # Check for call-to-action
            cta_patterns = self.analysis_patterns["call_to_action"]
            has_cta = any(re.search(pattern, optimized.text, re.IGNORECASE) for pattern in cta_patterns)
            if has_cta:
                score += 10.0
        
        # Improvement score (20 points)
        changes_made = len(optimized.metadata.get("changes_count", 0))
        if changes_made > 0:
            score += min(20.0, changes_made * 5)  # 5 points per change, max 20
        
        return min(score, max_score)
    
    def _merge_requirements(
        self,
        base_requirements: PlatformRequirements,
        custom_requirements: Dict[str, Any]
    ) -> PlatformRequirements:
        """Merge custom requirements with base requirements."""
        # Create a copy of base requirements
        merged = PlatformRequirements(
            max_text_length=custom_requirements.get("max_text_length", base_requirements.max_text_length),
            max_hashtags=custom_requirements.get("max_hashtags", base_requirements.max_hashtags),
            optimal_hashtags=custom_requirements.get("optimal_hashtags", base_requirements.optimal_hashtags),
            supports_images=custom_requirements.get("supports_images", base_requirements.supports_images),
            supports_videos=custom_requirements.get("supports_videos", base_requirements.supports_videos),
            supports_links=custom_requirements.get("supports_links", base_requirements.supports_links),
            optimal_image_ratio=custom_requirements.get("optimal_image_ratio", base_requirements.optimal_image_ratio),
            optimal_video_duration=custom_requirements.get("optimal_video_duration", base_requirements.optimal_video_duration),
            character_limits=custom_requirements.get("character_limits", base_requirements.character_limits),
            hashtag_placement=custom_requirements.get("hashtag_placement", base_requirements.hashtag_placement),
            emoji_usage=custom_requirements.get("emoji_usage", base_requirements.emoji_usage),
            link_handling=custom_requirements.get("link_handling", base_requirements.link_handling),
            content_style=custom_requirements.get("content_style", base_requirements.content_style)
        )
        
        return merged
    
    async def batch_optimize(
        self,
        content_items: List[ContentItem],
        platform: str,
        optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    ) -> List[OptimizationResult]:
        """Optimize multiple content items in batch."""
        tasks = []
        for content in content_items:
            task = self.optimize_content(content, platform, optimization_level)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        optimization_results = []
        for result in results:
            if isinstance(result, OptimizationResult):
                optimization_results.append(result)
            else:
                self.logger.error(f"Batch optimization error: {result}")
        
        return optimization_results
    
    def get_platform_requirements(self, platform: str) -> Optional[PlatformRequirements]:
        """Get requirements for a specific platform."""
        return self.platform_requirements.get(platform)
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms."""
        return list(self.platform_requirements.keys())

