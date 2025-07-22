"""
Content Strategist

This module provides functionality for creating comprehensive content strategies
based on business domain analysis and campaign objectives.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import calendar

from ...content_generation.content_generator import ContentGenerator


class ContentStrategist:
    """
    Creates comprehensive content strategies and briefings based on
    business analysis and campaign objectives.
    """
    
    def __init__(self, config_manager=None, content_generator: ContentGenerator = None):
        """
        Initialize the Content Strategist.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generator instance
        """
        self.config_manager = config_manager
        self.content_generator = content_generator
        self.logger = logging.getLogger(__name__)
        
        # Strategy templates and frameworks
        self.strategy_frameworks = self._load_strategy_frameworks()
        self.content_templates = self._load_content_templates()
        self.campaign_types = self._load_campaign_types()
        
        self.logger.info("Content Strategist initialized")
    
    async def initialize(self):
        """Initialize the strategist components."""
        try:
            self.logger.info("Content Strategist initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Strategist: {e}")
            raise
    
    async def cleanup(self):
        """Clean up strategist resources."""
        try:
            self.logger.info("Content Strategist cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to clean up Content Strategist: {e}")
    
    def _load_strategy_frameworks(self) -> Dict[str, Any]:
        """Load content strategy frameworks."""
        return {
            "AIDA": {
                "name": "Attention, Interest, Desire, Action",
                "stages": ["attention", "interest", "desire", "action"],
                "description": "Classic marketing funnel for conversion-focused content",
                "content_types": ["awareness", "educational", "promotional", "call_to_action"]
            },
            "TOFU_MOFU_BOFU": {
                "name": "Top, Middle, Bottom of Funnel",
                "stages": ["awareness", "consideration", "decision"],
                "description": "Content strategy based on customer journey stages",
                "content_types": ["educational", "comparison", "testimonial", "demo"]
            },
            "PESO": {
                "name": "Paid, Earned, Shared, Owned",
                "stages": ["paid", "earned", "shared", "owned"],
                "description": "Media strategy framework for content distribution",
                "content_types": ["advertising", "pr", "social", "blog"]
            },
            "SMART": {
                "name": "Specific, Measurable, Achievable, Relevant, Time-bound",
                "stages": ["goal_setting", "measurement", "execution", "evaluation"],
                "description": "Goal-oriented content strategy framework",
                "content_types": ["goal_oriented", "measurable", "actionable", "relevant"]
            }
        }
    
    def _load_content_templates(self) -> Dict[str, Any]:
        """Load content templates for different purposes."""
        return {
            "educational": {
                "formats": ["how_to", "tutorial", "tips", "guide", "explanation"],
                "structures": {
                    "how_to": ["problem", "solution_steps", "benefits", "call_to_action"],
                    "tips": ["introduction", "tip_list", "examples", "conclusion"],
                    "guide": ["overview", "detailed_steps", "resources", "next_steps"]
                }
            },
            "promotional": {
                "formats": ["product_announcement", "feature_highlight", "offer", "testimonial"],
                "structures": {
                    "product_announcement": ["hook", "problem", "solution", "benefits", "cta"],
                    "offer": ["urgency", "value_proposition", "details", "cta"],
                    "testimonial": ["customer_story", "problem", "solution", "results"]
                }
            },
            "entertaining": {
                "formats": ["behind_scenes", "fun_facts", "memes", "stories", "challenges"],
                "structures": {
                    "behind_scenes": ["setup", "process", "insights", "engagement"],
                    "stories": ["hook", "narrative", "lesson", "connection"],
                    "challenges": ["introduction", "rules", "participation", "rewards"]
                }
            },
            "inspirational": {
                "formats": ["success_stories", "motivational", "quotes", "achievements"],
                "structures": {
                    "success_stories": ["challenge", "journey", "breakthrough", "inspiration"],
                    "motivational": ["problem", "mindset", "action", "transformation"],
                    "achievements": ["milestone", "journey", "gratitude", "future"]
                }
            }
        }
    
    def _load_campaign_types(self) -> Dict[str, Any]:
        """Load different campaign types and their characteristics."""
        return {
            "brand_awareness": {
                "objectives": ["increase_visibility", "build_recognition", "establish_presence"],
                "content_focus": ["brand_story", "values", "personality", "behind_scenes"],
                "metrics": ["reach", "impressions", "brand_mentions", "share_of_voice"],
                "duration": "long_term",
                "frequency": "consistent"
            },
            "lead_generation": {
                "objectives": ["capture_leads", "build_email_list", "generate_inquiries"],
                "content_focus": ["valuable_resources", "gated_content", "webinars", "free_tools"],
                "metrics": ["leads_generated", "conversion_rate", "cost_per_lead", "lead_quality"],
                "duration": "medium_term",
                "frequency": "regular"
            },
            "customer_engagement": {
                "objectives": ["increase_interaction", "build_community", "foster_loyalty"],
                "content_focus": ["interactive_content", "user_generated", "community_building", "conversations"],
                "metrics": ["engagement_rate", "comments", "shares", "community_growth"],
                "duration": "ongoing",
                "frequency": "high"
            },
            "product_launch": {
                "objectives": ["announce_product", "generate_excitement", "drive_adoption"],
                "content_focus": ["teasers", "features", "benefits", "demos", "testimonials"],
                "metrics": ["pre_orders", "sign_ups", "demo_requests", "social_buzz"],
                "duration": "short_term",
                "frequency": "intensive"
            },
            "thought_leadership": {
                "objectives": ["establish_expertise", "build_authority", "influence_industry"],
                "content_focus": ["insights", "trends", "opinions", "research", "predictions"],
                "metrics": ["shares", "citations", "speaking_invitations", "media_mentions"],
                "duration": "long_term",
                "frequency": "consistent"
            }
        }
    
    async def create_briefing(
        self,
        business_profile: Dict[str, Any],
        campaign_objectives: Optional[List[str]] = None,
        time_period: str = "weekly",
        strategy_framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive content briefing based on business profile.
        
        Args:
            business_profile (Dict): Business domain analysis results
            campaign_objectives (List[str], optional): Specific campaign objectives
            time_period (str): Time period for content planning
            strategy_framework (str, optional): Strategy framework to use
        
        Returns:
            Dict: Comprehensive content briefing
        """
        try:
            start_time = datetime.utcnow()
            
            self.logger.info(f"Creating content briefing for: {business_profile['business_info']['business_name']}")
            
            # Extract key information from business profile
            business_info = business_profile["business_info"]
            industry_analysis = business_profile["analysis"]["industry_classification"]
            audience_analysis = business_profile["analysis"]["audience_analysis"]
            brand_voice = business_profile["analysis"]["brand_voice_recommendations"]
            platform_recommendations = business_profile["analysis"]["platform_recommendations"]
            
            # Determine campaign type and strategy
            campaign_strategy = await self._determine_campaign_strategy(
                campaign_objectives, industry_analysis, audience_analysis
            )
            
            # Select strategy framework
            if not strategy_framework:
                strategy_framework = self._select_optimal_framework(campaign_strategy, business_info)
            
            # Create content strategy
            content_strategy = await self._create_content_strategy(
                business_profile, campaign_strategy, strategy_framework, time_period
            )
            
            # Generate content calendar
            content_calendar = await self._generate_content_calendar(
                content_strategy, time_period, platform_recommendations
            )
            
            # Create messaging guidelines
            messaging_guidelines = await self._create_messaging_guidelines(
                brand_voice, audience_analysis, campaign_strategy
            )
            
            # Generate content themes and topics
            content_themes = await self._generate_content_themes(
                industry_analysis, audience_analysis, campaign_strategy
            )
            
            # Create performance metrics framework
            metrics_framework = await self._create_metrics_framework(
                campaign_strategy, platform_recommendations
            )
            
            # Compile comprehensive briefing
            briefing = {
                "briefing_id": business_profile["id"],
                "business_profile": business_info,
                "campaign_strategy": campaign_strategy,
                "strategy_framework": strategy_framework,
                "content_strategy": content_strategy,
                "content_calendar": content_calendar,
                "messaging_guidelines": messaging_guidelines,
                "content_themes": content_themes,
                "platform_strategy": platform_recommendations,
                "metrics_framework": metrics_framework,
                "time_period": time_period,
                "created_at": start_time.isoformat(),
                "complexity_score": self._calculate_complexity_score(content_strategy)
            }
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            briefing["processing_time"] = processing_time
            
            self.logger.info(f"Content briefing created in {processing_time:.2f} seconds")
            return briefing
            
        except Exception as e:
            self.logger.error(f"Failed to create content briefing: {e}")
            raise
    
    async def _determine_campaign_strategy(
        self,
        campaign_objectives: Optional[List[str]],
        industry_analysis: Dict[str, Any],
        audience_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the optimal campaign strategy."""
        try:
            # If objectives are provided, match to campaign types
            if campaign_objectives:
                primary_campaign_type = self._match_objectives_to_campaign_type(campaign_objectives)
            else:
                # Infer campaign type from business context
                primary_campaign_type = self._infer_campaign_type(industry_analysis, audience_analysis)
            
            campaign_config = self.campaign_types.get(primary_campaign_type, {})
            
            return {
                "primary_type": primary_campaign_type,
                "objectives": campaign_objectives or campaign_config.get("objectives", []),
                "content_focus": campaign_config.get("content_focus", []),
                "success_metrics": campaign_config.get("metrics", []),
                "duration": campaign_config.get("duration", "medium_term"),
                "frequency": campaign_config.get("frequency", "regular"),
                "secondary_types": self._identify_secondary_campaign_types(campaign_objectives, industry_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to determine campaign strategy: {e}")
            return {"primary_type": "brand_awareness", "objectives": ["increase_visibility"]}
    
    def _match_objectives_to_campaign_type(self, objectives: List[str]) -> str:
        """Match campaign objectives to campaign type."""
        objective_keywords = {
            "brand_awareness": ["awareness", "visibility", "recognition", "brand"],
            "lead_generation": ["leads", "conversion", "signup", "download", "contact"],
            "customer_engagement": ["engagement", "community", "interaction", "loyalty"],
            "product_launch": ["launch", "product", "announcement", "release"],
            "thought_leadership": ["expertise", "authority", "leadership", "influence"]
        }
        
        scores = {}
        for campaign_type, keywords in objective_keywords.items():
            score = 0
            for objective in objectives:
                for keyword in keywords:
                    if keyword.lower() in objective.lower():
                        score += 1
            scores[campaign_type] = score
        
        # Return campaign type with highest score
        return max(scores, key=scores.get) if scores else "brand_awareness"
    
    def _infer_campaign_type(self, industry_analysis: Dict[str, Any], audience_analysis: Dict[str, Any]) -> str:
        """Infer campaign type from business context."""
        # Simple heuristics for campaign type inference
        industry = industry_analysis.get("primary_industry", "").lower()
        
        if "technology" in industry or "software" in industry:
            return "thought_leadership"
        elif "retail" in industry or "ecommerce" in industry:
            return "customer_engagement"
        elif "healthcare" in industry or "education" in industry:
            return "brand_awareness"
        else:
            return "brand_awareness"
    
    def _identify_secondary_campaign_types(self, objectives: Optional[List[str]], industry_analysis: Dict[str, Any]) -> List[str]:
        """Identify secondary campaign types to support primary strategy."""
        secondary_types = []
        
        # Always include customer engagement as secondary
        secondary_types.append("customer_engagement")
        
        # Add thought leadership for B2B industries
        industry = industry_analysis.get("primary_industry", "").lower()
        if any(term in industry for term in ["technology", "finance", "consulting", "healthcare"]):
            secondary_types.append("thought_leadership")
        
        # Add lead generation if not primary
        if objectives and any("lead" in obj.lower() for obj in objectives):
            secondary_types.append("lead_generation")
        
        return list(set(secondary_types))  # Remove duplicates
    
    def _select_optimal_framework(self, campaign_strategy: Dict[str, Any], business_info: Dict[str, Any]) -> str:
        """Select optimal strategy framework based on campaign and business context."""
        campaign_type = campaign_strategy["primary_type"]
        
        # Framework selection logic
        if campaign_type == "lead_generation":
            return "AIDA"
        elif campaign_type == "brand_awareness":
            return "TOFU_MOFU_BOFU"
        elif campaign_type == "customer_engagement":
            return "PESO"
        else:
            return "SMART"
    
    async def _create_content_strategy(
        self,
        business_profile: Dict[str, Any],
        campaign_strategy: Dict[str, Any],
        strategy_framework: str,
        time_period: str
    ) -> Dict[str, Any]:
        """Create detailed content strategy."""
        try:
            framework = self.strategy_frameworks.get(strategy_framework, {})
            campaign_type = campaign_strategy["primary_type"]
            
            # Content mix based on campaign type
            content_mix = self._determine_content_mix(campaign_type)
            
            # Content types and formats
            content_types = self._determine_content_types(campaign_strategy, business_profile)
            
            # Posting frequency and timing
            posting_strategy = self._determine_posting_strategy(campaign_strategy, time_period)
            
            return {
                "framework": framework,
                "content_mix": content_mix,
                "content_types": content_types,
                "posting_strategy": posting_strategy,
                "content_pillars": self._define_content_pillars(business_profile, campaign_strategy),
                "engagement_tactics": self._define_engagement_tactics(campaign_strategy),
                "distribution_strategy": self._create_distribution_strategy(business_profile)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create content strategy: {e}")
            return {}
    
    def _determine_content_mix(self, campaign_type: str) -> Dict[str, int]:
        """Determine content mix percentages based on campaign type."""
        content_mixes = {
            "brand_awareness": {
                "educational": 30,
                "entertaining": 25,
                "promotional": 20,
                "inspirational": 25
            },
            "lead_generation": {
                "educational": 40,
                "promotional": 35,
                "entertaining": 15,
                "inspirational": 10
            },
            "customer_engagement": {
                "entertaining": 35,
                "educational": 25,
                "inspirational": 25,
                "promotional": 15
            },
            "product_launch": {
                "promotional": 50,
                "educational": 25,
                "entertaining": 15,
                "inspirational": 10
            },
            "thought_leadership": {
                "educational": 50,
                "inspirational": 20,
                "entertaining": 15,
                "promotional": 15
            }
        }
        
        return content_mixes.get(campaign_type, content_mixes["brand_awareness"])
    
    def _determine_content_types(self, campaign_strategy: Dict[str, Any], business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Determine specific content types and formats."""
        campaign_type = campaign_strategy["primary_type"]
        platform_recommendations = business_profile["analysis"]["platform_recommendations"]
        
        # Get recommended platforms
        top_platforms = platform_recommendations.get("top_recommendations", ["facebook", "twitter", "linkedin"])
        
        content_types = {}
        for platform in top_platforms:
            platform_strategy = platform_recommendations["platform_strategy"].get(platform, {})
            content_types[platform] = platform_strategy.get("content_types", ["text", "image"])
        
        return content_types
    
    def _determine_posting_strategy(self, campaign_strategy: Dict[str, Any], time_period: str) -> Dict[str, Any]:
        """Determine posting frequency and timing strategy."""
        frequency_mapping = {
            "intensive": {"daily": 3, "weekly": 21, "monthly": 90},
            "high": {"daily": 2, "weekly": 14, "monthly": 60},
            "regular": {"daily": 1, "weekly": 7, "monthly": 30},
            "moderate": {"daily": 1, "weekly": 5, "monthly": 20},
            "low": {"daily": 1, "weekly": 3, "monthly": 12}
        }
        
        campaign_frequency = campaign_strategy.get("frequency", "regular")
        posts_per_period = frequency_mapping.get(campaign_frequency, {}).get(time_period, 7)
        
        return {
            "frequency": campaign_frequency,
            "posts_per_period": posts_per_period,
            "optimal_times": self._get_optimal_posting_times(),
            "time_period": time_period
        }
    
    def _get_optimal_posting_times(self) -> Dict[str, List[str]]:
        """Get optimal posting times for different platforms."""
        return {
            "facebook": ["09:00", "13:00", "15:00"],
            "twitter": ["08:00", "12:00", "17:00", "19:00"],
            "instagram": ["11:00", "14:00", "17:00"],
            "linkedin": ["07:00", "08:00", "17:00", "18:00"],
            "tiktok": ["06:00", "10:00", "19:00", "20:00"]
        }
    
    def _define_content_pillars(self, business_profile: Dict[str, Any], campaign_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define content pillars for the strategy."""
        industry_analysis = business_profile["analysis"]["industry_classification"]
        content_focus = campaign_strategy.get("content_focus", [])
        
        pillars = []
        
        # Industry-specific pillars
        industry = industry_analysis.get("primary_industry", "").lower()
        if "technology" in industry:
            pillars.extend([
                {"name": "Innovation", "description": "Latest tech trends and innovations", "percentage": 25},
                {"name": "Education", "description": "Technical tutorials and guides", "percentage": 30},
                {"name": "Company Culture", "description": "Behind-the-scenes and team content", "percentage": 20},
                {"name": "Industry Insights", "description": "Market analysis and predictions", "percentage": 25}
            ])
        elif "healthcare" in industry:
            pillars.extend([
                {"name": "Health Education", "description": "Health tips and medical information", "percentage": 35},
                {"name": "Patient Stories", "description": "Success stories and testimonials", "percentage": 25},
                {"name": "Wellness", "description": "Lifestyle and wellness content", "percentage": 25},
                {"name": "Medical Advances", "description": "Latest medical research and breakthroughs", "percentage": 15}
            ])
        else:
            # Generic pillars
            pillars.extend([
                {"name": "Educational", "description": "Informative and how-to content", "percentage": 30},
                {"name": "Behind the Scenes", "description": "Company culture and processes", "percentage": 25},
                {"name": "Customer Focus", "description": "Customer stories and testimonials", "percentage": 25},
                {"name": "Industry Leadership", "description": "Thought leadership and insights", "percentage": 20}
            ])
        
        return pillars
    
    def _define_engagement_tactics(self, campaign_strategy: Dict[str, Any]) -> List[str]:
        """Define engagement tactics based on campaign strategy."""
        base_tactics = [
            "Ask engaging questions",
            "Use relevant hashtags",
            "Respond to comments promptly",
            "Share user-generated content",
            "Create interactive polls",
            "Host live sessions"
        ]
        
        campaign_type = campaign_strategy["primary_type"]
        
        if campaign_type == "customer_engagement":
            base_tactics.extend([
                "Create community challenges",
                "Feature customer spotlights",
                "Run contests and giveaways",
                "Encourage user-generated content"
            ])
        elif campaign_type == "thought_leadership":
            base_tactics.extend([
                "Share industry insights",
                "Comment on industry trends",
                "Collaborate with industry experts",
                "Participate in industry discussions"
            ])
        elif campaign_type == "lead_generation":
            base_tactics.extend([
                "Offer valuable resources",
                "Create compelling CTAs",
                "Use lead magnets",
                "Promote webinars and events"
            ])
        
        return base_tactics
    
    def _create_distribution_strategy(self, business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create content distribution strategy."""
        platform_recommendations = business_profile["analysis"]["platform_recommendations"]
        
        return {
            "primary_platforms": platform_recommendations.get("top_recommendations", []),
            "platform_strategy": platform_recommendations.get("platform_strategy", {}),
            "cross_promotion": True,
            "repurposing_strategy": {
                "blog_to_social": True,
                "video_to_clips": True,
                "long_form_to_snippets": True
            }
        }
    
    async def _generate_content_calendar(
        self,
        content_strategy: Dict[str, Any],
        time_period: str,
        platform_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content calendar based on strategy."""
        try:
            posting_strategy = content_strategy.get("posting_strategy", {})
            posts_per_period = posting_strategy.get("posts_per_period", 7)
            content_mix = content_strategy.get("content_mix", {})
            
            # Calculate posts per content type
            posts_by_type = {}
            for content_type, percentage in content_mix.items():
                posts_by_type[content_type] = max(1, int((posts_per_period * percentage) / 100))
            
            # Generate calendar structure
            calendar_structure = self._create_calendar_structure(time_period, posts_per_period)
            
            # Assign content types to calendar slots
            content_calendar = self._assign_content_to_calendar(
                calendar_structure, posts_by_type, platform_recommendations
            )
            
            return {
                "time_period": time_period,
                "total_posts": posts_per_period,
                "posts_by_type": posts_by_type,
                "calendar": content_calendar,
                "posting_times": posting_strategy.get("optimal_times", {}),
                "content_themes": self._generate_weekly_themes()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate content calendar: {e}")
            return {}
    
    def _create_calendar_structure(self, time_period: str, posts_per_period: int) -> List[Dict[str, Any]]:
        """Create basic calendar structure."""
        calendar_slots = []
        
        if time_period == "weekly":
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            posts_per_day = max(1, posts_per_period // 7)
            
            for day in days:
                for post_num in range(posts_per_day):
                    calendar_slots.append({
                        "day": day,
                        "post_number": post_num + 1,
                        "content_type": None,
                        "platform": None,
                        "theme": None
                    })
        
        # Adjust for exact number of posts
        while len(calendar_slots) < posts_per_period:
            calendar_slots.append({
                "day": "additional",
                "post_number": len(calendar_slots) + 1,
                "content_type": None,
                "platform": None,
                "theme": None
            })
        
        return calendar_slots[:posts_per_period]
    
    def _assign_content_to_calendar(
        self,
        calendar_structure: List[Dict[str, Any]],
        posts_by_type: Dict[str, int],
        platform_recommendations: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Assign content types and platforms to calendar slots."""
        top_platforms = platform_recommendations.get("top_recommendations", ["facebook", "twitter"])
        
        # Create list of content assignments
        content_assignments = []
        for content_type, count in posts_by_type.items():
            for _ in range(count):
                content_assignments.append(content_type)
        
        # Assign to calendar slots
        for i, slot in enumerate(calendar_structure):
            if i < len(content_assignments):
                slot["content_type"] = content_assignments[i]
                slot["platform"] = top_platforms[i % len(top_platforms)]
                slot["theme"] = self._get_theme_for_day(slot["day"])
        
        return calendar_structure
    
    def _get_theme_for_day(self, day: str) -> str:
        """Get theme for specific day of week."""
        day_themes = {
            "monday": "Motivation Monday",
            "tuesday": "Tip Tuesday",
            "wednesday": "Wisdom Wednesday",
            "thursday": "Throwback Thursday",
            "friday": "Feature Friday",
            "saturday": "Social Saturday",
            "sunday": "Sunday Reflection"
        }
        return day_themes.get(day, "General Content")
    
    def _generate_weekly_themes(self) -> Dict[str, str]:
        """Generate weekly content themes."""
        return {
            "week_1": "Getting Started",
            "week_2": "Building Momentum",
            "week_3": "Overcoming Challenges",
            "week_4": "Celebrating Success"
        }
    
    async def _create_messaging_guidelines(
        self,
        brand_voice: Dict[str, Any],
        audience_analysis: Dict[str, Any],
        campaign_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create messaging guidelines for content creation."""
        try:
            return {
                "brand_voice": {
                    "tone": brand_voice.get("recommended_tone", "professional"),
                    "personality": brand_voice.get("personality_traits", []),
                    "communication_style": brand_voice.get("communication_guidelines", {})
                },
                "audience_considerations": {
                    "primary_segments": audience_analysis.get("primary_segments", []),
                    "pain_points": audience_analysis.get("pain_points", []),
                    "content_preferences": audience_analysis.get("content_preferences", {})
                },
                "key_messages": self._generate_key_messages(campaign_strategy),
                "messaging_framework": self._create_messaging_framework(brand_voice, campaign_strategy),
                "content_guidelines": self._create_content_guidelines(brand_voice, audience_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create messaging guidelines: {e}")
            return {}
    
    def _generate_key_messages(self, campaign_strategy: Dict[str, Any]) -> List[str]:
        """Generate key messages based on campaign strategy."""
        campaign_type = campaign_strategy["primary_type"]
        objectives = campaign_strategy.get("objectives", [])
        
        key_messages = []
        
        if campaign_type == "brand_awareness":
            key_messages.extend([
                "We are committed to excellence in our industry",
                "Our values drive everything we do",
                "Innovation and customer satisfaction are our priorities"
            ])
        elif campaign_type == "lead_generation":
            key_messages.extend([
                "Discover solutions that transform your business",
                "Get expert guidance tailored to your needs",
                "Join thousands of satisfied customers"
            ])
        elif campaign_type == "customer_engagement":
            key_messages.extend([
                "Your success is our success",
                "We're here to support your journey",
                "Join our community of achievers"
            ])
        
        return key_messages
    
    def _create_messaging_framework(self, brand_voice: Dict[str, Any], campaign_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create messaging framework for consistent communication."""
        return {
            "value_proposition": "Clear statement of unique value",
            "proof_points": ["Evidence supporting claims", "Customer testimonials", "Industry recognition"],
            "call_to_action_templates": [
                "Learn more about [topic]",
                "Get started with [solution]",
                "Join our community",
                "Contact us for [specific need]"
            ],
            "hashtag_strategy": {
                "branded_hashtags": ["#YourBrand", "#YourMission"],
                "industry_hashtags": ["#Industry", "#Trending"],
                "campaign_hashtags": ["#CampaignName", "#SpecialEvent"]
            }
        }
    
    def _create_content_guidelines(self, brand_voice: Dict[str, Any], audience_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create content creation guidelines."""
        return {
            "writing_style": {
                "tone": brand_voice.get("recommended_tone", "professional"),
                "voice": "active",
                "perspective": "second_person",
                "sentence_length": "varied"
            },
            "visual_guidelines": {
                "image_style": "professional",
                "color_scheme": "brand_colors",
                "typography": "readable_fonts"
            },
            "content_structure": {
                "hook": "Attention-grabbing opening",
                "body": "Value-driven content",
                "cta": "Clear call to action"
            },
            "do_and_dont": {
                "do": [
                    "Use clear, concise language",
                    "Include relevant hashtags",
                    "Engage with comments",
                    "Provide value in every post"
                ],
                "dont": [
                    "Use jargon without explanation",
                    "Post without purpose",
                    "Ignore negative feedback",
                    "Over-promote products"
                ]
            }
        }
    
    async def _generate_content_themes(
        self,
        industry_analysis: Dict[str, Any],
        audience_analysis: Dict[str, Any],
        campaign_strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate content themes and topics."""
        try:
            themes = []
            
            # Industry-based themes
            industry_keywords = industry_analysis.get("industry_keywords", [])
            for keyword in industry_keywords[:5]:  # Top 5 keywords
                themes.append({
                    "theme": keyword.title(),
                    "description": f"Content focused on {keyword}",
                    "content_ideas": [
                        f"How to leverage {keyword} for business growth",
                        f"Latest trends in {keyword}",
                        f"Common mistakes in {keyword} implementation"
                    ],
                    "target_audience": audience_analysis.get("primary_segments", [])
                })
            
            # Campaign-specific themes
            content_focus = campaign_strategy.get("content_focus", [])
            for focus_area in content_focus:
                themes.append({
                    "theme": focus_area.replace("_", " ").title(),
                    "description": f"Content highlighting {focus_area}",
                    "content_ideas": [
                        f"Showcase {focus_area} examples",
                        f"Benefits of {focus_area}",
                        f"How we excel in {focus_area}"
                    ],
                    "target_audience": audience_analysis.get("primary_segments", [])
                })
            
            return themes
            
        except Exception as e:
            self.logger.error(f"Failed to generate content themes: {e}")
            return []
    
    async def _create_metrics_framework(
        self,
        campaign_strategy: Dict[str, Any],
        platform_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create metrics and KPI framework."""
        try:
            success_metrics = campaign_strategy.get("success_metrics", [])
            platforms = platform_recommendations.get("top_recommendations", [])
            
            return {
                "primary_kpis": success_metrics,
                "platform_metrics": {
                    platform: self._get_platform_metrics(platform) 
                    for platform in platforms
                },
                "measurement_frequency": "weekly",
                "reporting_schedule": "monthly",
                "success_benchmarks": self._define_success_benchmarks(campaign_strategy),
                "tracking_tools": ["native_analytics", "social_media_management_tools", "google_analytics"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create metrics framework: {e}")
            return {}
    
    def _get_platform_metrics(self, platform: str) -> List[str]:
        """Get relevant metrics for each platform."""
        platform_metrics = {
            "facebook": ["reach", "engagement_rate", "page_likes", "post_clicks", "shares"],
            "twitter": ["impressions", "engagement_rate", "retweets", "likes", "replies"],
            "instagram": ["reach", "engagement_rate", "story_views", "saves", "profile_visits"],
            "linkedin": ["impressions", "engagement_rate", "clicks", "shares", "comments"],
            "tiktok": ["views", "engagement_rate", "shares", "comments", "profile_visits"]
        }
        return platform_metrics.get(platform, ["reach", "engagement_rate", "clicks"])
    
    def _define_success_benchmarks(self, campaign_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Define success benchmarks based on campaign type."""
        campaign_type = campaign_strategy["primary_type"]
        
        benchmarks = {
            "brand_awareness": {
                "reach_increase": "20%",
                "brand_mention_increase": "15%",
                "follower_growth": "10%"
            },
            "lead_generation": {
                "conversion_rate": "3%",
                "cost_per_lead": "$50",
                "lead_quality_score": "7/10"
            },
            "customer_engagement": {
                "engagement_rate": "5%",
                "response_rate": "90%",
                "community_growth": "15%"
            }
        }
        
        return benchmarks.get(campaign_type, benchmarks["brand_awareness"])
    
    def _calculate_complexity_score(self, content_strategy: Dict[str, Any]) -> float:
        """Calculate complexity score for the content strategy."""
        score = 0.0
        
        # Base complexity
        score += 1.0
        
        # Add complexity for multiple content types
        content_types = content_strategy.get("content_types", {})
        score += len(content_types) * 0.2
        
        # Add complexity for multiple platforms
        platforms = len(content_types.keys()) if content_types else 1
        score += platforms * 0.3
        
        # Add complexity for posting frequency
        posting_strategy = content_strategy.get("posting_strategy", {})
        posts_per_period = posting_strategy.get("posts_per_period", 7)
        score += min(posts_per_period * 0.1, 2.0)
        
        return min(score, 10.0)  # Cap at 10.0
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the Content Strategist."""
        try:
            return {
                "component": "ContentStrategist",
                "healthy": True,
                "checks": {
                    "strategy_frameworks": {
                        "healthy": bool(self.strategy_frameworks),
                        "count": len(self.strategy_frameworks)
                    },
                    "content_templates": {
                        "healthy": bool(self.content_templates),
                        "count": len(self.content_templates)
                    },
                    "campaign_types": {
                        "healthy": bool(self.campaign_types),
                        "count": len(self.campaign_types)
                    }
                }
            }
            
        except Exception as e:
            return {
                "component": "ContentStrategist",
                "healthy": False,
                "error": str(e)
            }

