"""
Business Domain Analyzer

This module provides functionality for analyzing business domains, industries,
target audiences, and competitive landscapes to inform content strategy.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re

from ...content_generation.llm_providers import LLMProviderManager


class BusinessDomainAnalyzer:
    """
    Analyzes business domains and creates comprehensive business profiles
    for content strategy development.
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize the Business Domain Analyzer.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM provider for analysis
        self.llm_provider = LLMProviderManager(config_manager) if config_manager else None
        
        # Industry knowledge base
        self.industry_database = self._load_industry_database()
        
        # Analysis templates
        self.analysis_templates = self._load_analysis_templates()
        
        self.logger.info("Business Domain Analyzer initialized")
    
    async def initialize(self):
        """Initialize the analyzer components."""
        try:
            if self.llm_provider:
                await self.llm_provider.initialize()
            self.logger.info("Business Domain Analyzer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Business Domain Analyzer: {e}")
            raise
    
    async def cleanup(self):
        """Clean up analyzer resources."""
        try:
            if self.llm_provider:
                await self.llm_provider.cleanup()
            self.logger.info("Business Domain Analyzer cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to clean up Business Domain Analyzer: {e}")
    
    def _load_industry_database(self) -> Dict[str, Any]:
        """Load industry knowledge database."""
        # In a real implementation, this would load from a file or database
        return {
            "technology": {
                "keywords": ["software", "AI", "machine learning", "cloud", "SaaS", "mobile app"],
                "audience_segments": ["developers", "IT professionals", "tech enthusiasts", "businesses"],
                "content_themes": ["innovation", "efficiency", "digital transformation", "automation"],
                "posting_frequency": "high",
                "best_platforms": ["linkedin", "twitter", "facebook"],
                "content_types": ["educational", "thought leadership", "product updates", "tutorials"]
            },
            "healthcare": {
                "keywords": ["medical", "health", "wellness", "treatment", "patient care", "telemedicine"],
                "audience_segments": ["patients", "healthcare professionals", "caregivers", "health-conscious individuals"],
                "content_themes": ["health education", "wellness tips", "medical breakthroughs", "patient stories"],
                "posting_frequency": "moderate",
                "best_platforms": ["facebook", "linkedin", "instagram"],
                "content_types": ["educational", "inspirational", "awareness", "testimonials"]
            },
            "retail": {
                "keywords": ["shopping", "products", "fashion", "lifestyle", "deals", "customer service"],
                "audience_segments": ["consumers", "shoppers", "brand enthusiasts", "deal seekers"],
                "content_themes": ["product showcases", "lifestyle", "customer satisfaction", "trends"],
                "posting_frequency": "high",
                "best_platforms": ["instagram", "facebook", "tiktok", "twitter"],
                "content_types": ["visual", "promotional", "user-generated", "behind-the-scenes"]
            },
            "finance": {
                "keywords": ["banking", "investment", "financial planning", "insurance", "loans", "wealth"],
                "audience_segments": ["investors", "savers", "business owners", "financial advisors"],
                "content_themes": ["financial literacy", "investment tips", "market insights", "security"],
                "posting_frequency": "moderate",
                "best_platforms": ["linkedin", "twitter", "facebook"],
                "content_types": ["educational", "market analysis", "tips", "thought leadership"]
            },
            "education": {
                "keywords": ["learning", "courses", "training", "skills", "certification", "academic"],
                "audience_segments": ["students", "professionals", "educators", "lifelong learners"],
                "content_themes": ["skill development", "career growth", "knowledge sharing", "success stories"],
                "posting_frequency": "moderate",
                "best_platforms": ["linkedin", "facebook", "instagram", "twitter"],
                "content_types": ["educational", "motivational", "success stories", "tips"]
            }
        }
    
    def _load_analysis_templates(self) -> Dict[str, str]:
        """Load analysis prompt templates."""
        return {
            "industry_analysis": """
            Analyze the following business information and provide a comprehensive industry analysis:
            
            Business Name: {business_name}
            Industry: {industry}
            Description: {description}
            
            Please provide:
            1. Industry classification and sub-sectors
            2. Market size and growth trends
            3. Key competitors and market leaders
            4. Target audience demographics and psychographics
            5. Industry-specific challenges and opportunities
            6. Recommended content themes and messaging
            7. Optimal social media platforms for this industry
            8. Content frequency and timing recommendations
            
            Format the response as a structured JSON object.
            """,
            
            "audience_analysis": """
            Based on the business information provided, analyze the target audience:
            
            Business: {business_name}
            Industry: {industry}
            Target Audience Info: {target_audience}
            
            Provide detailed audience analysis including:
            1. Primary audience segments
            2. Demographics (age, gender, location, income)
            3. Psychographics (interests, values, lifestyle)
            4. Pain points and challenges
            5. Content preferences and consumption habits
            6. Social media platform usage patterns
            7. Optimal posting times and frequency
            8. Engagement preferences (visual, text, video)
            
            Return as structured JSON.
            """,
            
            "competitive_analysis": """
            Perform a competitive analysis for this business:
            
            Business: {business_name}
            Industry: {industry}
            Competitors: {competitors}
            
            Analyze:
            1. Direct and indirect competitors
            2. Competitor social media presence and strategy
            3. Content themes and messaging used by competitors
            4. Engagement rates and audience response
            5. Gaps in competitor content strategy
            6. Opportunities for differentiation
            7. Best practices to adopt
            8. Content positioning recommendations
            
            Provide structured JSON response.
            """,
            
            "brand_voice_analysis": """
            Analyze and recommend brand voice based on business information:
            
            Business: {business_name}
            Industry: {industry}
            Description: {description}
            Current Brand Voice: {brand_voice}
            
            Recommend:
            1. Tone of voice (professional, casual, friendly, authoritative, etc.)
            2. Personality traits (helpful, innovative, trustworthy, etc.)
            3. Communication style guidelines
            4. Language and terminology preferences
            5. Emotional tone for different content types
            6. Brand voice examples and templates
            7. Do's and don'ts for brand communication
            8. Platform-specific voice adaptations
            
            Return as structured JSON.
            """
        }
    
    async def analyze_domain(self, business_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive business domain analysis.
        
        Args:
            business_info (Dict): Business information including name, industry, description, etc.
        
        Returns:
            Dict: Comprehensive domain analysis results
        """
        try:
            start_time = datetime.utcnow()
            
            self.logger.info(f"Starting domain analysis for: {business_info.get('business_name')}")
            
            # Extract key information
            business_name = business_info.get("business_name", "")
            industry = business_info.get("industry", "").lower()
            description = business_info.get("description", "")
            target_audience = business_info.get("target_audience", {})
            competitors = business_info.get("competitors", [])
            brand_voice = business_info.get("brand_voice", {})
            
            # Initialize analysis results
            analysis_results = {
                "business_info": business_info,
                "analysis_timestamp": start_time.isoformat(),
                "industry_classification": {},
                "audience_analysis": {},
                "competitive_landscape": {},
                "brand_voice_recommendations": {},
                "content_strategy_recommendations": {},
                "platform_recommendations": {},
                "confidence_scores": {}
            }
            
            # 1. Industry Classification and Analysis
            industry_analysis = await self._analyze_industry(business_name, industry, description)
            analysis_results["industry_classification"] = industry_analysis
            
            # 2. Audience Analysis
            audience_analysis = await self._analyze_audience(business_name, industry, target_audience)
            analysis_results["audience_analysis"] = audience_analysis
            
            # 3. Competitive Analysis (if competitors provided)
            if competitors:
                competitive_analysis = await self._analyze_competitors(business_name, industry, competitors)
                analysis_results["competitive_landscape"] = competitive_analysis
            
            # 4. Brand Voice Analysis
            brand_analysis = await self._analyze_brand_voice(business_name, industry, description, brand_voice)
            analysis_results["brand_voice_recommendations"] = brand_analysis
            
            # 5. Content Strategy Recommendations
            content_strategy = await self._generate_content_strategy(analysis_results)
            analysis_results["content_strategy_recommendations"] = content_strategy
            
            # 6. Platform Recommendations
            platform_recommendations = await self._recommend_platforms(analysis_results)
            analysis_results["platform_recommendations"] = platform_recommendations
            
            # 7. Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(analysis_results)
            analysis_results["confidence_scores"] = confidence_scores
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            analysis_results["processing_time"] = processing_time
            
            self.logger.info(f"Domain analysis completed in {processing_time:.2f} seconds")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Failed to analyze domain: {e}")
            raise
    
    async def _analyze_industry(self, business_name: str, industry: str, description: str) -> Dict[str, Any]:
        """Analyze industry classification and characteristics."""
        try:
            # Check if industry exists in our database
            industry_data = self.industry_database.get(industry.lower(), {})
            
            # Use LLM for detailed analysis if available
            if self.llm_provider:
                prompt = self.analysis_templates["industry_analysis"].format(
                    business_name=business_name,
                    industry=industry,
                    description=description
                )
                
                llm_analysis = await self.llm_provider.generate_text(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.3
                )
                
                # Parse LLM response (assuming JSON format)
                try:
                    llm_data = json.loads(llm_analysis)
                except json.JSONDecodeError:
                    llm_data = {"raw_analysis": llm_analysis}
            else:
                llm_data = {}
            
            # Combine database knowledge with LLM analysis
            return {
                "primary_industry": industry,
                "industry_keywords": industry_data.get("keywords", []),
                "market_characteristics": llm_data.get("market_characteristics", {}),
                "growth_trends": llm_data.get("growth_trends", {}),
                "key_challenges": llm_data.get("key_challenges", []),
                "opportunities": llm_data.get("opportunities", []),
                "database_match": bool(industry_data),
                "llm_analysis": llm_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze industry: {e}")
            return {"error": str(e)}
    
    async def _analyze_audience(self, business_name: str, industry: str, target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze target audience characteristics."""
        try:
            # Get industry-specific audience data
            industry_data = self.industry_database.get(industry.lower(), {})
            default_segments = industry_data.get("audience_segments", [])
            
            # Use LLM for detailed audience analysis
            if self.llm_provider:
                prompt = self.analysis_templates["audience_analysis"].format(
                    business_name=business_name,
                    industry=industry,
                    target_audience=json.dumps(target_audience)
                )
                
                llm_analysis = await self.llm_provider.generate_text(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.3
                )
                
                try:
                    llm_data = json.loads(llm_analysis)
                except json.JSONDecodeError:
                    llm_data = {"raw_analysis": llm_analysis}
            else:
                llm_data = {}
            
            return {
                "primary_segments": llm_data.get("primary_segments", default_segments),
                "demographics": llm_data.get("demographics", target_audience.get("demographics", {})),
                "psychographics": llm_data.get("psychographics", target_audience.get("psychographics", {})),
                "pain_points": llm_data.get("pain_points", []),
                "content_preferences": llm_data.get("content_preferences", {}),
                "platform_usage": llm_data.get("platform_usage", {}),
                "engagement_patterns": llm_data.get("engagement_patterns", {}),
                "provided_info": target_audience
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze audience: {e}")
            return {"error": str(e)}
    
    async def _analyze_competitors(self, business_name: str, industry: str, competitors: List[str]) -> Dict[str, Any]:
        """Analyze competitive landscape."""
        try:
            if not self.llm_provider:
                return {"competitors": competitors, "analysis": "LLM not available for competitive analysis"}
            
            prompt = self.analysis_templates["competitive_analysis"].format(
                business_name=business_name,
                industry=industry,
                competitors=", ".join(competitors)
            )
            
            llm_analysis = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.3
            )
            
            try:
                llm_data = json.loads(llm_analysis)
            except json.JSONDecodeError:
                llm_data = {"raw_analysis": llm_analysis}
            
            return {
                "identified_competitors": competitors,
                "competitive_analysis": llm_data,
                "differentiation_opportunities": llm_data.get("differentiation_opportunities", []),
                "best_practices": llm_data.get("best_practices", []),
                "content_gaps": llm_data.get("content_gaps", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze competitors: {e}")
            return {"error": str(e)}
    
    async def _analyze_brand_voice(self, business_name: str, industry: str, description: str, brand_voice: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and recommend brand voice."""
        try:
            if not self.llm_provider:
                return {"current_brand_voice": brand_voice, "analysis": "LLM not available for brand voice analysis"}
            
            prompt = self.analysis_templates["brand_voice_analysis"].format(
                business_name=business_name,
                industry=industry,
                description=description,
                brand_voice=json.dumps(brand_voice)
            )
            
            llm_analysis = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            try:
                llm_data = json.loads(llm_analysis)
            except json.JSONDecodeError:
                llm_data = {"raw_analysis": llm_analysis}
            
            return {
                "current_brand_voice": brand_voice,
                "recommended_tone": llm_data.get("recommended_tone", "professional"),
                "personality_traits": llm_data.get("personality_traits", []),
                "communication_guidelines": llm_data.get("communication_guidelines", {}),
                "platform_adaptations": llm_data.get("platform_adaptations", {}),
                "examples": llm_data.get("examples", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze brand voice: {e}")
            return {"error": str(e)}
    
    async def _generate_content_strategy(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content strategy recommendations based on analysis."""
        try:
            industry = analysis_results["business_info"].get("industry", "").lower()
            industry_data = self.industry_database.get(industry, {})
            
            # Extract insights from analysis
            audience_segments = analysis_results.get("audience_analysis", {}).get("primary_segments", [])
            content_preferences = analysis_results.get("audience_analysis", {}).get("content_preferences", {})
            brand_tone = analysis_results.get("brand_voice_recommendations", {}).get("recommended_tone", "professional")
            
            # Generate strategy recommendations
            strategy = {
                "content_themes": industry_data.get("content_themes", []),
                "content_types": industry_data.get("content_types", []),
                "posting_frequency": industry_data.get("posting_frequency", "moderate"),
                "audience_targeting": {
                    "primary_segments": audience_segments,
                    "content_preferences": content_preferences
                },
                "brand_alignment": {
                    "tone": brand_tone,
                    "messaging_guidelines": []
                },
                "content_calendar_suggestions": self._generate_content_calendar_suggestions(industry_data),
                "engagement_strategies": self._generate_engagement_strategies(analysis_results)
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to generate content strategy: {e}")
            return {"error": str(e)}
    
    async def _recommend_platforms(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend optimal social media platforms."""
        try:
            industry = analysis_results["business_info"].get("industry", "").lower()
            industry_data = self.industry_database.get(industry, {})
            
            # Get platform usage from audience analysis
            platform_usage = analysis_results.get("audience_analysis", {}).get("platform_usage", {})
            
            # Default platform recommendations from industry data
            recommended_platforms = industry_data.get("best_platforms", ["facebook", "twitter", "linkedin"])
            
            platform_recommendations = {}
            for platform in ["facebook", "twitter", "instagram", "linkedin", "tiktok"]:
                score = 0
                reasons = []
                
                # Score based on industry fit
                if platform in recommended_platforms:
                    score += 30
                    reasons.append("Industry best practice")
                
                # Score based on audience usage
                if platform in platform_usage:
                    usage_score = platform_usage[platform].get("usage_percentage", 0)
                    score += usage_score * 0.5
                    reasons.append(f"Audience usage: {usage_score}%")
                
                # Platform-specific scoring
                if platform == "linkedin" and "business" in industry.lower():
                    score += 20
                    reasons.append("B2B focus")
                
                if platform == "instagram" and industry in ["retail", "fashion", "food", "lifestyle"]:
                    score += 25
                    reasons.append("Visual content industry")
                
                if platform == "tiktok" and "young" in str(analysis_results.get("audience_analysis", {})).lower():
                    score += 15
                    reasons.append("Young audience preference")
                
                platform_recommendations[platform] = {
                    "score": min(score, 100),
                    "recommended": score >= 50,
                    "reasons": reasons,
                    "content_types": self._get_platform_content_types(platform),
                    "posting_frequency": self._get_platform_posting_frequency(platform, industry_data)
                }
            
            # Sort by score
            sorted_platforms = sorted(
                platform_recommendations.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )
            
            return {
                "platform_scores": platform_recommendations,
                "top_recommendations": [p[0] for p in sorted_platforms[:3]],
                "platform_strategy": {p[0]: p[1] for p in sorted_platforms}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to recommend platforms: {e}")
            return {"error": str(e)}
    
    def _generate_content_calendar_suggestions(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content calendar suggestions."""
        content_themes = industry_data.get("content_themes", [])
        
        # Weekly content structure
        weekly_structure = {
            "monday": "motivation_monday",
            "tuesday": "tip_tuesday", 
            "wednesday": "wisdom_wednesday",
            "thursday": "throwback_thursday",
            "friday": "feature_friday",
            "saturday": "social_saturday",
            "sunday": "sunday_reflection"
        }
        
        # Map themes to days
        theme_mapping = {}
        for i, theme in enumerate(content_themes):
            day = list(weekly_structure.keys())[i % 7]
            theme_mapping[day] = theme
        
        return {
            "weekly_structure": weekly_structure,
            "theme_mapping": theme_mapping,
            "content_mix": {
                "educational": 40,
                "promotional": 20,
                "entertaining": 25,
                "inspirational": 15
            }
        }
    
    def _generate_engagement_strategies(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate engagement strategies based on analysis."""
        strategies = [
            "Ask questions to encourage comments",
            "Share behind-the-scenes content",
            "Use relevant hashtags for discoverability",
            "Respond promptly to comments and messages",
            "Share user-generated content",
            "Post at optimal times for your audience"
        ]
        
        # Add industry-specific strategies
        industry = analysis_results["business_info"].get("industry", "").lower()
        if "technology" in industry:
            strategies.extend([
                "Share technical tutorials and how-tos",
                "Discuss industry trends and innovations",
                "Showcase product features and updates"
            ])
        elif "healthcare" in industry:
            strategies.extend([
                "Share health tips and wellness advice",
                "Feature patient success stories",
                "Provide educational health content"
            ])
        
        return strategies
    
    def _get_platform_content_types(self, platform: str) -> List[str]:
        """Get recommended content types for a platform."""
        platform_content = {
            "facebook": ["text", "image", "video", "link", "event"],
            "twitter": ["text", "image", "thread", "poll"],
            "instagram": ["image", "video", "story", "reel", "igtv"],
            "linkedin": ["text", "article", "image", "video", "document"],
            "tiktok": ["video", "live", "duet", "challenge"]
        }
        return platform_content.get(platform, ["text", "image"])
    
    def _get_platform_posting_frequency(self, platform: str, industry_data: Dict[str, Any]) -> str:
        """Get recommended posting frequency for a platform."""
        base_frequency = industry_data.get("posting_frequency", "moderate")
        
        # Platform-specific adjustments
        if platform == "twitter":
            return "high"  # Twitter allows more frequent posting
        elif platform == "linkedin":
            return "low"   # LinkedIn prefers quality over quantity
        elif platform == "instagram":
            return "moderate"
        else:
            return base_frequency
    
    def _calculate_confidence_scores(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different analysis components."""
        scores = {}
        
        # Industry analysis confidence
        industry_analysis = analysis_results.get("industry_classification", {})
        if industry_analysis.get("database_match"):
            scores["industry_analysis"] = 0.9
        elif industry_analysis.get("llm_analysis"):
            scores["industry_analysis"] = 0.7
        else:
            scores["industry_analysis"] = 0.3
        
        # Audience analysis confidence
        audience_analysis = analysis_results.get("audience_analysis", {})
        if audience_analysis.get("provided_info"):
            scores["audience_analysis"] = 0.8
        else:
            scores["audience_analysis"] = 0.5
        
        # Competitive analysis confidence
        competitive_analysis = analysis_results.get("competitive_landscape", {})
        if competitive_analysis.get("identified_competitors"):
            scores["competitive_analysis"] = 0.7
        else:
            scores["competitive_analysis"] = 0.2
        
        # Overall confidence
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the Business Domain Analyzer."""
        try:
            health_status = {
                "component": "BusinessDomainAnalyzer",
                "healthy": True,
                "checks": {}
            }
            
            # Check LLM provider
            if self.llm_provider:
                try:
                    llm_health = await self.llm_provider.health_check()
                    health_status["checks"]["llm_provider"] = llm_health
                    if not llm_health.get("healthy", False):
                        health_status["healthy"] = False
                except Exception as e:
                    health_status["checks"]["llm_provider"] = {"healthy": False, "error": str(e)}
                    health_status["healthy"] = False
            
            # Check industry database
            health_status["checks"]["industry_database"] = {
                "healthy": bool(self.industry_database),
                "industries_loaded": len(self.industry_database)
            }
            
            # Check analysis templates
            health_status["checks"]["analysis_templates"] = {
                "healthy": bool(self.analysis_templates),
                "templates_loaded": len(self.analysis_templates)
            }
            
            return health_status
            
        except Exception as e:
            return {
                "component": "BusinessDomainAnalyzer",
                "healthy": False,
                "error": str(e)
            }

