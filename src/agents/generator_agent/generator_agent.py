"""
Generator Agent Implementation

The Generator Agent is responsible for analyzing business domains, creating content briefings,
and generating content suggestions that can be reviewed and approved by users.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import uuid

from ..base_agent import BaseAgent
from .business_analyzer import BusinessDomainAnalyzer
from .content_strategist import ContentStrategist
from .suggestion_engine import ContentSuggestionEngine
from ...content_generation.content_generator import ContentGenerator
from ...metrics.metrics_collector import MetricsCollector


class GeneratorAgent(BaseAgent):
    """
    Generator Agent for content briefing and suggestion generation.
    
    This agent analyzes business domains, creates content strategies,
    and generates batches of content suggestions for user approval.
    """
    
    def __init__(
        self,
        name: str = "generator_agent",
        config_manager=None,
        content_generator: ContentGenerator = None,
        metrics_collector: MetricsCollector = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the Generator Agent.
        
        Args:
            name (str): Agent name
            config_manager: Configuration manager instance
            content_generator: Content generator instance
            metrics_collector: Metrics collector instance
            config (Dict): Agent-specific configuration
        """
        super().__init__(name, config_manager, content_generator, metrics_collector, config)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.business_analyzer = BusinessDomainAnalyzer(config_manager)
        self.content_strategist = ContentStrategist(config_manager, content_generator)
        self.suggestion_engine = ContentSuggestionEngine(config_manager, content_generator)
        
        # Configuration
        self.default_batch_size = config.get("content_generation", {}).get("default_batch_size", 10)
        self.max_batch_size = config.get("content_generation", {}).get("max_batch_size", 50)
        self.creativity_level = config.get("suggestion_engine", {}).get("creativity_level", "balanced")
        
        # State management
        self.current_business_profile = None
        self.active_briefings = {}
        self.suggestion_history = []
        
        self.logger.info(f"Generator Agent '{name}' initialized")
    
    async def start(self) -> bool:
        """Start the Generator Agent."""
        try:
            self.logger.info("Starting Generator Agent...")
            
            # Initialize components
            await self.business_analyzer.initialize()
            await self.content_strategist.initialize()
            await self.suggestion_engine.initialize()
            
            # Set status
            self.status = "running"
            self.start_time = datetime.utcnow()
            
            self.logger.info("Generator Agent started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Generator Agent: {e}")
            self.status = "error"
            return False
    
    async def stop(self) -> bool:
        """Stop the Generator Agent."""
        try:
            self.logger.info("Stopping Generator Agent...")
            
            # Clean up components
            await self.business_analyzer.cleanup()
            await self.content_strategist.cleanup()
            await self.suggestion_engine.cleanup()
            
            # Set status
            self.status = "stopped"
            
            self.logger.info("Generator Agent stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Generator Agent: {e}")
            return False
    
    async def analyze_business_domain(
        self,
        business_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze business domain and create business profile.
        
        Args:
            business_info (Dict): Business information including:
                - business_name: Name of the business
                - industry: Industry/sector
                - description: Business description
                - target_audience: Target audience information
                - goals: Business goals and objectives
                - competitors: Competitor information (optional)
                - brand_voice: Brand voice preferences (optional)
        
        Returns:
            Dict: Business domain analysis results
        """
        try:
            self.logger.info(f"Analyzing business domain for: {business_info.get('business_name', 'Unknown')}")
            
            # Validate required fields
            required_fields = ['business_name', 'industry', 'description']
            for field in required_fields:
                if field not in business_info:
                    raise ValueError(f"Missing required field: {field}")
            
            # Perform business analysis
            analysis_result = await self.business_analyzer.analyze_domain(business_info)
            
            # Store business profile
            self.current_business_profile = {
                "id": str(uuid.uuid4()),
                "business_info": business_info,
                "analysis": analysis_result,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Record metrics
            await self.metrics_collector.store_metrics(
                agent_name=self.name,
                platform="generator",
                metrics={
                    "business_analyses_completed": 1,
                    "analysis_duration": analysis_result.get("processing_time", 0)
                }
            )
            
            self.logger.info("Business domain analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze business domain: {e}")
            raise
    
    async def create_content_briefing(
        self,
        business_profile: Optional[Dict[str, Any]] = None,
        campaign_objectives: Optional[List[str]] = None,
        time_period: Optional[str] = "weekly"
    ) -> Dict[str, Any]:
        """
        Create comprehensive content briefing based on business analysis.
        
        Args:
            business_profile (Dict, optional): Business profile to use. 
                If None, uses current business profile.
            campaign_objectives (List[str], optional): Specific campaign objectives
            time_period (str): Time period for content planning (daily, weekly, monthly)
        
        Returns:
            Dict: Content briefing with strategy and recommendations
        """
        try:
            # Use provided profile or current profile
            profile = business_profile or self.current_business_profile
            if not profile:
                raise ValueError("No business profile available. Please analyze business domain first.")
            
            self.logger.info(f"Creating content briefing for: {profile['business_info']['business_name']}")
            
            # Create content strategy
            briefing = await self.content_strategist.create_briefing(
                business_profile=profile,
                campaign_objectives=campaign_objectives,
                time_period=time_period
            )
            
            # Generate briefing ID and metadata
            briefing_id = str(uuid.uuid4())
            briefing_data = {
                "id": briefing_id,
                "business_profile_id": profile["id"],
                "briefing": briefing,
                "campaign_objectives": campaign_objectives or [],
                "time_period": time_period,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            # Store briefing
            self.active_briefings[briefing_id] = briefing_data
            
            # Record metrics
            await self.metrics_collector.store_metrics(
                agent_name=self.name,
                platform="generator",
                metrics={
                    "briefings_created": 1,
                    "briefing_complexity_score": briefing.get("complexity_score", 0)
                }
            )
            
            self.logger.info("Content briefing created successfully")
            return briefing_data
            
        except Exception as e:
            self.logger.error(f"Failed to create content briefing: {e}")
            raise
    
    async def suggest_content_batch(
        self,
        briefing_id: str,
        batch_size: Optional[int] = None,
        platforms: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of content suggestions based on briefing.
        
        Args:
            briefing_id (str): ID of the content briefing to use
            batch_size (int, optional): Number of suggestions to generate
            platforms (List[str], optional): Target platforms for content
            content_types (List[str], optional): Types of content to generate
            preferences (Dict, optional): User preferences for content generation
        
        Returns:
            List[Dict]: List of content suggestions
        """
        try:
            # Validate briefing
            if briefing_id not in self.active_briefings:
                raise ValueError(f"Briefing not found: {briefing_id}")
            
            briefing_data = self.active_briefings[briefing_id]
            briefing = briefing_data["briefing"]
            
            # Set defaults
            batch_size = min(batch_size or self.default_batch_size, self.max_batch_size)
            platforms = platforms or ["facebook", "twitter", "instagram", "linkedin"]
            content_types = content_types or ["text", "image"]
            
            self.logger.info(f"Generating {batch_size} content suggestions for briefing: {briefing_id}")
            
            # Generate content suggestions
            suggestions = await self.suggestion_engine.generate_suggestions(
                briefing=briefing,
                batch_size=batch_size,
                platforms=platforms,
                content_types=content_types,
                preferences=preferences,
                creativity_level=self.creativity_level
            )
            
            # Add metadata to suggestions
            for suggestion in suggestions:
                suggestion.update({
                    "id": str(uuid.uuid4()),
                    "briefing_id": briefing_id,
                    "business_profile_id": briefing_data["business_profile_id"],
                    "generated_at": datetime.utcnow(),
                    "status": "pending_review",
                    "feedback_score": None,
                    "approval_status": None
                })
            
            # Store suggestions in history
            self.suggestion_history.extend(suggestions)
            
            # Record metrics
            await self.metrics_collector.store_metrics(
                agent_name=self.name,
                platform="generator",
                metrics={
                    "content_suggestions_generated": len(suggestions),
                    "average_generation_time": sum(s.get("generation_time", 0) for s in suggestions) / len(suggestions),
                    "batch_size": batch_size
                }
            )
            
            self.logger.info(f"Generated {len(suggestions)} content suggestions successfully")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate content suggestions: {e}")
            raise
    
    async def get_suggestion_by_id(self, suggestion_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific content suggestion by ID.
        
        Args:
            suggestion_id (str): ID of the suggestion to retrieve
        
        Returns:
            Dict or None: Content suggestion data
        """
        for suggestion in self.suggestion_history:
            if suggestion.get("id") == suggestion_id:
                return suggestion
        return None
    
    async def update_suggestion_status(
        self,
        suggestion_id: str,
        status: str,
        feedback_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update the status of a content suggestion.
        
        Args:
            suggestion_id (str): ID of the suggestion to update
            status (str): New status (approved, rejected, modified, etc.)
            feedback_data (Dict, optional): Additional feedback data
        
        Returns:
            bool: True if update was successful
        """
        try:
            suggestion = await self.get_suggestion_by_id(suggestion_id)
            if not suggestion:
                return False
            
            # Update suggestion
            suggestion["status"] = status
            suggestion["updated_at"] = datetime.utcnow()
            
            if feedback_data:
                suggestion["feedback_data"] = feedback_data
            
            self.logger.info(f"Updated suggestion {suggestion_id} status to: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update suggestion status: {e}")
            return False
    
    async def get_suggestions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all suggestions with a specific status.
        
        Args:
            status (str): Status to filter by
        
        Returns:
            List[Dict]: List of matching suggestions
        """
        return [s for s in self.suggestion_history if s.get("status") == status]
    
    async def get_briefing_statistics(self, briefing_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific briefing.
        
        Args:
            briefing_id (str): ID of the briefing
        
        Returns:
            Dict: Statistics including suggestion counts, approval rates, etc.
        """
        try:
            if briefing_id not in self.active_briefings:
                return {}
            
            # Get all suggestions for this briefing
            briefing_suggestions = [
                s for s in self.suggestion_history 
                if s.get("briefing_id") == briefing_id
            ]
            
            if not briefing_suggestions:
                return {"total_suggestions": 0}
            
            # Calculate statistics
            total = len(briefing_suggestions)
            approved = len([s for s in briefing_suggestions if s.get("status") == "approved"])
            rejected = len([s for s in briefing_suggestions if s.get("status") == "rejected"])
            pending = len([s for s in briefing_suggestions if s.get("status") == "pending_review"])
            
            # Calculate average feedback score
            scored_suggestions = [s for s in briefing_suggestions if s.get("feedback_score") is not None]
            avg_score = sum(s["feedback_score"] for s in scored_suggestions) / len(scored_suggestions) if scored_suggestions else 0
            
            return {
                "briefing_id": briefing_id,
                "total_suggestions": total,
                "approved": approved,
                "rejected": rejected,
                "pending_review": pending,
                "approval_rate": (approved / total) * 100 if total > 0 else 0,
                "average_feedback_score": avg_score,
                "last_generated": max(s["generated_at"] for s in briefing_suggestions) if briefing_suggestions else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get briefing statistics: {e}")
            return {}
    
    async def regenerate_suggestion(
        self,
        suggestion_id: str,
        modification_instructions: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Regenerate a content suggestion with modifications.
        
        Args:
            suggestion_id (str): ID of the suggestion to regenerate
            modification_instructions (str, optional): Instructions for modification
        
        Returns:
            Dict or None: New content suggestion
        """
        try:
            original_suggestion = await self.get_suggestion_by_id(suggestion_id)
            if not original_suggestion:
                return None
            
            # Get briefing data
            briefing_id = original_suggestion["briefing_id"]
            briefing_data = self.active_briefings.get(briefing_id)
            if not briefing_data:
                return None
            
            # Regenerate with modifications
            new_suggestion = await self.suggestion_engine.regenerate_suggestion(
                original_suggestion=original_suggestion,
                briefing=briefing_data["briefing"],
                modification_instructions=modification_instructions
            )
            
            # Add metadata
            new_suggestion.update({
                "id": str(uuid.uuid4()),
                "briefing_id": briefing_id,
                "business_profile_id": briefing_data["business_profile_id"],
                "generated_at": datetime.utcnow(),
                "status": "pending_review",
                "parent_suggestion_id": suggestion_id,
                "modification_instructions": modification_instructions
            })
            
            # Add to history
            self.suggestion_history.append(new_suggestion)
            
            self.logger.info(f"Regenerated suggestion {suggestion_id} as {new_suggestion['id']}")
            return new_suggestion
            
        except Exception as e:
            self.logger.error(f"Failed to regenerate suggestion: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the Generator Agent.
        
        Returns:
            Dict: Health check results
        """
        try:
            health_status = {
                "agent_name": self.name,
                "status": self.status,
                "healthy": True,
                "uptime": str(datetime.utcnow() - self.start_time) if self.start_time else "0:00:00",
                "components": {}
            }
            
            # Check components
            components = [
                ("business_analyzer", self.business_analyzer),
                ("content_strategist", self.content_strategist),
                ("suggestion_engine", self.suggestion_engine)
            ]
            
            for component_name, component in components:
                try:
                    component_health = await component.health_check()
                    health_status["components"][component_name] = component_health
                    if not component_health.get("healthy", False):
                        health_status["healthy"] = False
                except Exception as e:
                    health_status["components"][component_name] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    health_status["healthy"] = False
            
            # Add statistics
            health_status["statistics"] = {
                "active_briefings": len(self.active_briefings),
                "total_suggestions": len(self.suggestion_history),
                "pending_suggestions": len(await self.get_suggestions_by_status("pending_review"))
            }
            
            return health_status
            
        except Exception as e:
            return {
                "agent_name": self.name,
                "healthy": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the Generator Agent.
        
        Returns:
            Dict: Current status information
        """
        return {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "current_business_profile": self.current_business_profile["id"] if self.current_business_profile else None,
            "active_briefings": len(self.active_briefings),
            "total_suggestions": len(self.suggestion_history),
            "configuration": {
                "default_batch_size": self.default_batch_size,
                "max_batch_size": self.max_batch_size,
                "creativity_level": self.creativity_level
            }
        }

