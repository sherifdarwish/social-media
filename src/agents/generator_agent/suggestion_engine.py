"""
Content Suggestion Engine

This module provides functionality for generating content suggestions based on
content briefings, user preferences, and platform requirements.
"""

import asyncio
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid

from ...content_generation.content_generator import ContentGenerator


class ContentSuggestionEngine:
    """
    Generates content suggestions based on briefings and user preferences.
    Supports multiple content types and platform-specific optimization.
    """
    
    def __init__(self, config_manager=None, content_generator: ContentGenerator = None):
        """
        Initialize the Content Suggestion Engine.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generator instance
        """
        self.config_manager = config_manager
        self.content_generator = content_generator
        self.logger = logging.getLogger(__name__)
        
        # Suggestion templates and patterns
        self.suggestion_templates = self._load_suggestion_templates()
        self.content_patterns = self._load_content_patterns()
        self.platform_optimizations = self._load_platform_optimizations()
        
        # Creativity and variation settings
        self.creativity_levels = {
            "conservative": {"temperature": 0.3, "variation": 0.2},
            "balanced": {"temperature": 0.7, "variation": 0.5},
            "creative": {"temperature": 0.9, "variation": 0.8}
        }
        
        self.logger.info("Content Suggestion Engine initialized")
    
    async def initialize(self):
        """Initialize the suggestion engine components."""
        try:
            self.logger.info("Content Suggestion Engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Suggestion Engine: {e}")
            raise
    
    async def cleanup(self):
        """Clean up suggestion engine resources."""
        try:
            self.logger.info("Content Suggestion Engine cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to clean up Content Suggestion Engine: {e}")
    
    def _load_suggestion_templates(self) -> Dict[str, Any]:
        """Load content suggestion templates."""
        return {
            "educational": {
                "how_to": {
                    "structure": ["hook", "problem", "solution_steps", "benefits", "cta"],
                    "prompts": [
                        "How to {action} in {timeframe}",
                        "The complete guide to {topic}",
                        "Step-by-step: {process}",
                        "{number} ways to {achieve_goal}"
                    ]
                },
                "tips": {
                    "structure": ["introduction", "tip_list", "examples", "conclusion"],
                    "prompts": [
                        "{number} essential tips for {topic}",
                        "Pro tips: {subject}",
                        "Quick tips to {improve_something}",
                        "Expert advice on {topic}"
                    ]
                },
                "explanation": {
                    "structure": ["question", "simple_answer", "detailed_explanation", "examples"],
                    "prompts": [
                        "What is {concept} and why it matters",
                        "Understanding {topic} in simple terms",
                        "The science behind {phenomenon}",
                        "Demystifying {complex_topic}"
                    ]
                }
            },
            "promotional": {
                "product_highlight": {
                    "structure": ["hook", "problem", "solution", "features", "benefits", "cta"],
                    "prompts": [
                        "Introducing {product}: {main_benefit}",
                        "Why {product} is perfect for {target_audience}",
                        "Transform your {area} with {product}",
                        "The {adjective} solution you've been waiting for"
                    ]
                },
                "testimonial": {
                    "structure": ["customer_intro", "challenge", "solution", "results", "recommendation"],
                    "prompts": [
                        "How {customer} achieved {result} with {product}",
                        "Success story: {customer}'s journey",
                        "From {problem} to {solution}: {customer}'s experience",
                        "Real results: {customer} shares their story"
                    ]
                },
                "offer": {
                    "structure": ["urgency", "value", "details", "benefits", "cta"],
                    "prompts": [
                        "Limited time: {discount} off {product}",
                        "Exclusive offer for {audience}",
                        "Don't miss out: {special_deal}",
                        "Last chance to {get_benefit}"
                    ]
                }
            },
            "entertaining": {
                "behind_scenes": {
                    "structure": ["setup", "process", "insights", "engagement"],
                    "prompts": [
                        "Behind the scenes: {process}",
                        "A day in the life at {company}",
                        "How we {create_something}",
                        "The story behind {product/service}"
                    ]
                },
                "fun_facts": {
                    "structure": ["hook", "fact_list", "explanations", "engagement"],
                    "prompts": [
                        "{number} surprising facts about {topic}",
                        "Did you know? {interesting_facts}",
                        "Mind-blowing facts about {subject}",
                        "Things you never knew about {topic}"
                    ]
                },
                "challenges": {
                    "structure": ["introduction", "rules", "participation", "rewards"],
                    "prompts": [
                        "Join our {challenge_name} challenge",
                        "Can you {challenge_action}?",
                        "Challenge accepted: {activity}",
                        "Show us your {skill/creativity}"
                    ]
                }
            },
            "inspirational": {
                "success_story": {
                    "structure": ["challenge", "journey", "breakthrough", "lesson"],
                    "prompts": [
                        "From {starting_point} to {achievement}",
                        "The journey that changed everything",
                        "Overcoming {obstacle} to achieve {goal}",
                        "When {person} decided to {take_action}"
                    ]
                },
                "motivational": {
                    "structure": ["problem", "mindset", "action", "transformation"],
                    "prompts": [
                        "Why {belief} is holding you back",
                        "The power of {positive_action}",
                        "Transform your {area} with {approach}",
                        "Believe in your ability to {achieve}"
                    ]
                },
                "quote": {
                    "structure": ["quote", "context", "application", "reflection"],
                    "prompts": [
                        "'{inspirational_quote}' - {author}",
                        "Words to live by: {wisdom}",
                        "Monday motivation: {quote}",
                        "Remember: {encouraging_message}"
                    ]
                }
            }
        }
    
    def _load_content_patterns(self) -> Dict[str, Any]:
        """Load content patterns for different scenarios."""
        return {
            "engagement_boosters": [
                "Ask a question at the end",
                "Include a call-to-action",
                "Use relevant emojis",
                "Add trending hashtags",
                "Encourage sharing",
                "Request opinions",
                "Share personal experiences",
                "Use storytelling elements"
            ],
            "platform_hooks": {
                "facebook": [
                    "Did you know...",
                    "Here's something interesting...",
                    "Let me share a story...",
                    "I've been thinking about...",
                    "Quick question for you..."
                ],
                "twitter": [
                    "Thread: {topic} 🧵",
                    "Hot take:",
                    "Unpopular opinion:",
                    "PSA:",
                    "Today I learned..."
                ],
                "instagram": [
                    "Swipe to see...",
                    "Behind the scenes:",
                    "Can we talk about...",
                    "This is your reminder that...",
                    "POV:"
                ],
                "linkedin": [
                    "I've been reflecting on...",
                    "Here's what I learned...",
                    "Industry insight:",
                    "Professional tip:",
                    "Career advice:"
                ],
                "tiktok": [
                    "POV:",
                    "Tell me you're {X} without telling me...",
                    "This is your sign to...",
                    "When you realize...",
                    "Nobody talks about..."
                ]
            },
            "cta_templates": {
                "engagement": [
                    "What do you think?",
                    "Share your experience in the comments",
                    "Tag someone who needs to see this",
                    "Double tap if you agree",
                    "Save this for later"
                ],
                "conversion": [
                    "Learn more in our bio",
                    "DM us for details",
                    "Link in comments",
                    "Get started today",
                    "Book a consultation"
                ],
                "community": [
                    "Join the conversation",
                    "Follow for more tips",
                    "Turn on notifications",
                    "Share with your network",
                    "Be part of our community"
                ]
            }
        }
    
    def _load_platform_optimizations(self) -> Dict[str, Any]:
        """Load platform-specific optimization rules."""
        return {
            "facebook": {
                "max_length": 2000,
                "optimal_length": 400,
                "hashtag_limit": 5,
                "image_ratio": "16:9",
                "best_times": ["09:00", "13:00", "15:00"],
                "content_preferences": ["stories", "videos", "images", "links"]
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": 200,
                "hashtag_limit": 3,
                "image_ratio": "16:9",
                "best_times": ["08:00", "12:00", "17:00"],
                "content_preferences": ["threads", "images", "polls", "quotes"]
            },
            "instagram": {
                "max_length": 2200,
                "optimal_length": 300,
                "hashtag_limit": 30,
                "image_ratio": "1:1",
                "best_times": ["11:00", "14:00", "17:00"],
                "content_preferences": ["images", "videos", "stories", "reels"]
            },
            "linkedin": {
                "max_length": 3000,
                "optimal_length": 600,
                "hashtag_limit": 5,
                "image_ratio": "16:9",
                "best_times": ["07:00", "08:00", "17:00"],
                "content_preferences": ["articles", "images", "videos", "documents"]
            },
            "tiktok": {
                "max_length": 2200,
                "optimal_length": 100,
                "hashtag_limit": 10,
                "video_length": "15-60s",
                "best_times": ["06:00", "10:00", "19:00"],
                "content_preferences": ["videos", "challenges", "trends", "duets"]
            }
        }
    
    async def generate_suggestions(
        self,
        briefing: Dict[str, Any],
        batch_size: int = 10,
        platforms: List[str] = None,
        content_types: List[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        creativity_level: str = "balanced"
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of content suggestions based on briefing.
        
        Args:
            briefing (Dict): Content briefing with strategy and guidelines
            batch_size (int): Number of suggestions to generate
            platforms (List[str]): Target platforms for content
            content_types (List[str]): Types of content to generate
            preferences (Dict, optional): User preferences for content
            creativity_level (str): Level of creativity (conservative, balanced, creative)
        
        Returns:
            List[Dict]: List of content suggestions
        """
        try:
            start_time = datetime.utcnow()
            
            self.logger.info(f"Generating {batch_size} content suggestions")
            
            # Set defaults
            platforms = platforms or ["facebook", "twitter", "instagram", "linkedin"]
            content_types = content_types or ["educational", "promotional", "entertaining", "inspirational"]
            preferences = preferences or {}
            
            # Get creativity settings
            creativity_settings = self.creativity_levels.get(creativity_level, self.creativity_levels["balanced"])
            
            # Extract briefing information
            content_strategy = briefing.get("content_strategy", {})
            content_mix = content_strategy.get("content_mix", {})
            messaging_guidelines = briefing.get("messaging_guidelines", {})
            content_themes = briefing.get("content_themes", [])
            
            # Calculate content distribution
            content_distribution = self._calculate_content_distribution(content_mix, batch_size, content_types)
            
            # Generate suggestions
            suggestions = []
            suggestion_id = 0
            
            for content_type, count in content_distribution.items():
                for i in range(count):
                    # Select platform (rotate through platforms)
                    platform = platforms[suggestion_id % len(platforms)]
                    
                    # Generate suggestion
                    suggestion = await self._generate_single_suggestion(
                        content_type=content_type,
                        platform=platform,
                        briefing=briefing,
                        messaging_guidelines=messaging_guidelines,
                        content_themes=content_themes,
                        preferences=preferences,
                        creativity_settings=creativity_settings
                    )
                    
                    if suggestion:
                        suggestion["suggestion_id"] = suggestion_id
                        suggestions.append(suggestion)
                        suggestion_id += 1
            
            # Fill remaining slots if needed
            while len(suggestions) < batch_size:
                content_type = random.choice(content_types)
                platform = platforms[len(suggestions) % len(platforms)]
                
                suggestion = await self._generate_single_suggestion(
                    content_type=content_type,
                    platform=platform,
                    briefing=briefing,
                    messaging_guidelines=messaging_guidelines,
                    content_themes=content_themes,
                    preferences=preferences,
                    creativity_settings=creativity_settings
                )
                
                if suggestion:
                    suggestion["suggestion_id"] = len(suggestions)
                    suggestions.append(suggestion)
            
            # Add generation metadata
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            for suggestion in suggestions:
                suggestion["generation_time"] = generation_time / len(suggestions)
                suggestion["creativity_level"] = creativity_level
                suggestion["batch_id"] = str(uuid.uuid4())
            
            self.logger.info(f"Generated {len(suggestions)} suggestions in {generation_time:.2f} seconds")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate suggestions: {e}")
            raise
    
    def _calculate_content_distribution(
        self,
        content_mix: Dict[str, int],
        batch_size: int,
        content_types: List[str]
    ) -> Dict[str, int]:
        """Calculate how many suggestions to generate for each content type."""
        distribution = {}
        
        if content_mix:
            # Use provided content mix
            for content_type in content_types:
                if content_type in content_mix:
                    percentage = content_mix[content_type]
                    count = max(1, int((batch_size * percentage) / 100))
                    distribution[content_type] = count
        else:
            # Equal distribution
            count_per_type = max(1, batch_size // len(content_types))
            for content_type in content_types:
                distribution[content_type] = count_per_type
        
        # Adjust to match exact batch size
        total_assigned = sum(distribution.values())
        if total_assigned < batch_size:
            # Add remaining to first content type
            first_type = list(distribution.keys())[0]
            distribution[first_type] += (batch_size - total_assigned)
        elif total_assigned > batch_size:
            # Remove excess from largest allocation
            largest_type = max(distribution, key=distribution.get)
            distribution[largest_type] -= (total_assigned - batch_size)
        
        return distribution
    
    async def _generate_single_suggestion(
        self,
        content_type: str,
        platform: str,
        briefing: Dict[str, Any],
        messaging_guidelines: Dict[str, Any],
        content_themes: List[Dict[str, Any]],
        preferences: Dict[str, Any],
        creativity_settings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a single content suggestion."""
        try:
            # Select template and format
            template_info = self._select_template(content_type, preferences)
            if not template_info:
                return None
            
            # Select theme
            theme = self._select_theme(content_themes, content_type)
            
            # Generate content based on template
            content_data = await self._generate_content_from_template(
                template_info=template_info,
                platform=platform,
                theme=theme,
                briefing=briefing,
                messaging_guidelines=messaging_guidelines,
                creativity_settings=creativity_settings
            )
            
            if not content_data:
                return None
            
            # Optimize for platform
            optimized_content = self._optimize_for_platform(content_data, platform)
            
            # Add metadata
            suggestion = {
                "content_type": content_type,
                "platform": platform,
                "template": template_info,
                "theme": theme,
                "content": optimized_content,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "template_used": template_info["format"],
                    "theme_used": theme.get("theme", "general") if theme else "general",
                    "platform_optimized": True,
                    "estimated_engagement": self._estimate_engagement(optimized_content, platform)
                }
            }
            
            return suggestion
            
        except Exception as e:
            self.logger.error(f"Failed to generate single suggestion: {e}")
            return None
    
    def _select_template(self, content_type: str, preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select appropriate template for content type."""
        templates = self.suggestion_templates.get(content_type, {})
        if not templates:
            return None
        
        # Check user preferences
        preferred_formats = preferences.get("formats", {}).get(content_type, [])
        
        if preferred_formats:
            # Use preferred format if available
            for format_name in preferred_formats:
                if format_name in templates:
                    return {
                        "type": content_type,
                        "format": format_name,
                        "structure": templates[format_name]["structure"],
                        "prompts": templates[format_name]["prompts"]
                    }
        
        # Select random format
        format_name = random.choice(list(templates.keys()))
        return {
            "type": content_type,
            "format": format_name,
            "structure": templates[format_name]["structure"],
            "prompts": templates[format_name]["prompts"]
        }
    
    def _select_theme(self, content_themes: List[Dict[str, Any]], content_type: str) -> Optional[Dict[str, Any]]:
        """Select appropriate theme for content."""
        if not content_themes:
            return None
        
        # Filter themes suitable for content type
        suitable_themes = [
            theme for theme in content_themes
            if content_type in theme.get("suitable_for", [content_type])
        ]
        
        if suitable_themes:
            return random.choice(suitable_themes)
        else:
            return random.choice(content_themes) if content_themes else None
    
    async def _generate_content_from_template(
        self,
        template_info: Dict[str, Any],
        platform: str,
        theme: Optional[Dict[str, Any]],
        briefing: Dict[str, Any],
        messaging_guidelines: Dict[str, Any],
        creativity_settings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate content based on template and guidelines."""
        try:
            # Build prompt for content generation
            prompt = self._build_content_prompt(
                template_info, platform, theme, briefing, messaging_guidelines
            )
            
            # Generate content using LLM if available
            if self.content_generator:
                generated_text = await self.content_generator.generate_text(
                    prompt=prompt,
                    max_tokens=500,
                    temperature=creativity_settings.get("temperature", 0.7)
                )
            else:
                # Fallback to template-based generation
                generated_text = self._generate_template_content(template_info, theme, briefing)
            
            # Structure the content
            content_data = {
                "title": self._extract_title(generated_text),
                "body": self._extract_body(generated_text),
                "hashtags": self._generate_hashtags(theme, platform, briefing),
                "call_to_action": self._generate_cta(template_info["type"], platform),
                "raw_content": generated_text
            }
            
            return content_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate content from template: {e}")
            return None
    
    def _build_content_prompt(
        self,
        template_info: Dict[str, Any],
        platform: str,
        theme: Optional[Dict[str, Any]],
        briefing: Dict[str, Any],
        messaging_guidelines: Dict[str, Any]
    ) -> str:
        """Build prompt for content generation."""
        # Get business info
        business_profile = briefing.get("business_profile", {})
        business_name = business_profile.get("business_name", "the company")
        industry = business_profile.get("industry", "business")
        
        # Get brand voice
        brand_voice = messaging_guidelines.get("brand_voice", {})
        tone = brand_voice.get("tone", "professional")
        
        # Get theme info
        theme_name = theme.get("theme", "general business") if theme else "general business"
        theme_description = theme.get("description", "") if theme else ""
        
        # Get template info
        content_type = template_info["type"]
        format_name = template_info["format"]
        structure = template_info["structure"]
        
        # Select prompt template
        prompt_templates = template_info.get("prompts", [])
        base_prompt = random.choice(prompt_templates) if prompt_templates else f"Create {content_type} content about {theme_name}"
        
        # Build comprehensive prompt
        prompt = f"""
        Create {content_type} content for {platform} with the following specifications:
        
        Business: {business_name} ({industry} industry)
        Content Type: {content_type} - {format_name}
        Theme: {theme_name}
        {f"Theme Description: {theme_description}" if theme_description else ""}
        Tone: {tone}
        Platform: {platform}
        
        Content Structure: {" -> ".join(structure)}
        
        Base Prompt: {base_prompt}
        
        Requirements:
        - Write in {tone} tone
        - Focus on {theme_name}
        - Follow the {format_name} format
        - Optimize for {platform}
        - Include engaging elements
        - Make it valuable for the audience
        
        Generate the complete content:
        """
        
        return prompt
    
    def _generate_template_content(
        self,
        template_info: Dict[str, Any],
        theme: Optional[Dict[str, Any]],
        briefing: Dict[str, Any]
    ) -> str:
        """Generate content using template fallback method."""
        content_type = template_info["type"]
        format_name = template_info["format"]
        theme_name = theme.get("theme", "business") if theme else "business"
        
        # Simple template-based content generation
        if content_type == "educational" and format_name == "tips":
            return f"""
            {random.choice(['5 Essential', '7 Proven', '10 Expert'])} Tips for {theme_name}
            
            Here are some valuable insights to help you succeed with {theme_name}:
            
            1. Start with the basics and build your foundation
            2. Stay consistent with your efforts
            3. Learn from industry experts and best practices
            4. Measure your progress regularly
            5. Adapt and improve based on results
            
            Which tip resonates most with you? Share your thoughts below!
            """
        elif content_type == "promotional":
            return f"""
            Discover how our solutions can transform your {theme_name} approach.
            
            We understand the challenges you face with {theme_name}, and we're here to help.
            Our proven methods have helped countless businesses achieve their goals.
            
            Ready to see the difference? Get in touch with us today.
            """
        elif content_type == "inspirational":
            return f"""
            Every expert was once a beginner in {theme_name}.
            
            The journey to mastery isn't always easy, but every step forward counts.
            Remember that progress, not perfection, is the goal.
            
            What's one small step you can take today toward your {theme_name} goals?
            """
        else:
            return f"""
            Let's talk about {theme_name} and why it matters for your success.
            
            In today's competitive landscape, understanding {theme_name} can make all the difference.
            Here's what you need to know to get started.
            
            What questions do you have about {theme_name}? We're here to help!
            """
    
    def _extract_title(self, content: str) -> str:
        """Extract title from generated content."""
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Take first substantial line as title
                if len(line) > 10 and len(line) < 100:
                    return line
        
        # Fallback: use first line
        return lines[0].strip() if lines else "Untitled"
    
    def _extract_body(self, content: str) -> str:
        """Extract body content from generated content."""
        lines = content.strip().split('\n')
        
        # Skip title line and empty lines
        body_lines = []
        skip_first = True
        
        for line in lines:
            line = line.strip()
            if skip_first and line:
                skip_first = False
                continue
            if line:
                body_lines.append(line)
        
        return '\n\n'.join(body_lines)
    
    def _generate_hashtags(
        self,
        theme: Optional[Dict[str, Any]],
        platform: str,
        briefing: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant hashtags for the content."""
        hashtags = []
        
        # Platform-specific hashtag limits
        platform_opts = self.platform_optimizations.get(platform, {})
        max_hashtags = platform_opts.get("hashtag_limit", 5)
        
        # Theme-based hashtags
        if theme:
            theme_name = theme.get("theme", "").replace(" ", "")
            if theme_name:
                hashtags.append(f"#{theme_name}")
        
        # Business-related hashtags
        business_profile = briefing.get("business_profile", {})
        industry = business_profile.get("industry", "").replace(" ", "")
        if industry:
            hashtags.append(f"#{industry}")
        
        # Generic relevant hashtags
        generic_hashtags = [
            "#business", "#success", "#tips", "#motivation",
            "#growth", "#innovation", "#leadership", "#strategy"
        ]
        
        # Add generic hashtags up to limit
        for hashtag in generic_hashtags:
            if len(hashtags) >= max_hashtags:
                break
            if hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:max_hashtags]
    
    def _generate_cta(self, content_type: str, platform: str) -> str:
        """Generate appropriate call-to-action."""
        cta_templates = self.content_patterns.get("cta_templates", {})
        
        if content_type in ["educational", "inspirational"]:
            ctas = cta_templates.get("engagement", ["What do you think?"])
        elif content_type == "promotional":
            ctas = cta_templates.get("conversion", ["Learn more!"])
        else:
            ctas = cta_templates.get("community", ["Join the conversation!"])
        
        return random.choice(ctas)
    
    def _optimize_for_platform(self, content_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Optimize content for specific platform requirements."""
        platform_opts = self.platform_optimizations.get(platform, {})
        
        # Optimize text length
        max_length = platform_opts.get("max_length", 2000)
        optimal_length = platform_opts.get("optimal_length", 400)
        
        # Combine title and body
        full_text = f"{content_data['title']}\n\n{content_data['body']}"
        
        # Truncate if too long
        if len(full_text) > max_length:
            # Try to cut at sentence boundary
            sentences = full_text.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= max_length - 50:  # Leave room for CTA
                    truncated += sentence + '. '
                else:
                    break
            full_text = truncated.strip()
        
        # Add platform-specific hook
        hooks = self.content_patterns.get("platform_hooks", {}).get(platform, [])
        if hooks and not any(hook.split(':')[0] in full_text for hook in hooks):
            hook = random.choice(hooks)
            if not full_text.startswith(hook.split(':')[0]):
                full_text = f"{hook} {full_text}"
        
        # Add CTA and hashtags
        cta = content_data.get("call_to_action", "")
        hashtags = " ".join(content_data.get("hashtags", []))
        
        final_text = f"{full_text}\n\n{cta}"
        if hashtags:
            final_text += f"\n\n{hashtags}"
        
        # Final length check
        if len(final_text) > max_length:
            # Aggressive truncation
            available_length = max_length - len(cta) - len(hashtags) - 10
            full_text = full_text[:available_length] + "..."
            final_text = f"{full_text}\n\n{cta}"
            if hashtags:
                final_text += f"\n\n{hashtags}"
        
        return {
            "title": content_data["title"],
            "body": content_data["body"],
            "full_text": final_text,
            "hashtags": content_data.get("hashtags", []),
            "call_to_action": cta,
            "platform_optimized": True,
            "character_count": len(final_text),
            "within_limits": len(final_text) <= max_length
        }
    
    def _estimate_engagement(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Estimate potential engagement for the content."""
        # Simple engagement estimation based on content characteristics
        score = 50  # Base score
        
        # Length optimization
        char_count = content.get("character_count", 0)
        platform_opts = self.platform_optimizations.get(platform, {})
        optimal_length = platform_opts.get("optimal_length", 400)
        
        if abs(char_count - optimal_length) < optimal_length * 0.2:
            score += 10  # Good length
        
        # Hashtag usage
        hashtags = content.get("hashtags", [])
        hashtag_limit = platform_opts.get("hashtag_limit", 5)
        if len(hashtags) > 0 and len(hashtags) <= hashtag_limit:
            score += 5
        
        # CTA presence
        if content.get("call_to_action"):
            score += 10
        
        # Platform optimization
        if content.get("platform_optimized"):
            score += 15
        
        # Random variation
        score += random.randint(-10, 10)
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return {
            "engagement_score": score,
            "estimated_reach": f"{score * 10}-{score * 20}",
            "estimated_interactions": f"{score // 10}-{score // 5}",
            "confidence": "medium"
        }
    
    async def regenerate_suggestion(
        self,
        original_suggestion: Dict[str, Any],
        briefing: Dict[str, Any],
        modification_instructions: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Regenerate a content suggestion with modifications.
        
        Args:
            original_suggestion (Dict): Original suggestion to modify
            briefing (Dict): Content briefing
            modification_instructions (str, optional): Specific modification instructions
        
        Returns:
            Dict or None: New content suggestion
        """
        try:
            self.logger.info(f"Regenerating suggestion with modifications")
            
            # Extract original parameters
            content_type = original_suggestion.get("content_type")
            platform = original_suggestion.get("platform")
            theme = original_suggestion.get("theme")
            template_info = original_suggestion.get("template")
            
            # Apply modifications to template or theme if specified
            if modification_instructions:
                # Simple modification logic - in a real implementation, this would be more sophisticated
                if "more creative" in modification_instructions.lower():
                    creativity_settings = self.creativity_levels["creative"]
                elif "more conservative" in modification_instructions.lower():
                    creativity_settings = self.creativity_levels["conservative"]
                else:
                    creativity_settings = self.creativity_levels["balanced"]
            else:
                creativity_settings = self.creativity_levels["balanced"]
            
            # Generate new suggestion
            messaging_guidelines = briefing.get("messaging_guidelines", {})
            content_themes = briefing.get("content_themes", [])
            
            new_suggestion = await self._generate_single_suggestion(
                content_type=content_type,
                platform=platform,
                briefing=briefing,
                messaging_guidelines=messaging_guidelines,
                content_themes=content_themes,
                preferences={},
                creativity_settings=creativity_settings
            )
            
            if new_suggestion:
                new_suggestion["regenerated_from"] = original_suggestion.get("id")
                new_suggestion["modification_instructions"] = modification_instructions
            
            return new_suggestion
            
        except Exception as e:
            self.logger.error(f"Failed to regenerate suggestion: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the Content Suggestion Engine."""
        try:
            return {
                "component": "ContentSuggestionEngine",
                "healthy": True,
                "checks": {
                    "suggestion_templates": {
                        "healthy": bool(self.suggestion_templates),
                        "count": len(self.suggestion_templates)
                    },
                    "content_patterns": {
                        "healthy": bool(self.content_patterns),
                        "count": len(self.content_patterns)
                    },
                    "platform_optimizations": {
                        "healthy": bool(self.platform_optimizations),
                        "platforms_supported": len(self.platform_optimizations)
                    },
                    "content_generator": {
                        "healthy": self.content_generator is not None,
                        "available": bool(self.content_generator)
                    }
                }
            }
            
        except Exception as e:
            return {
                "component": "ContentSuggestionEngine",
                "healthy": False,
                "error": str(e)
            }

