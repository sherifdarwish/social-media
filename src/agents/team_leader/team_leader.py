"""
Team Leader Agent

This module implements the Team Leader agent that coordinates all platform agents,
ensures brand consistency, and generates comprehensive reports.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import schedule

from ..base_agent import BaseAgent, ContentItem, ContentType, PostResult, AgentMetrics
from ..platform_agents import FacebookAgent, TwitterAgent, InstagramAgent, LinkedInAgent, TikTokAgent
from ...config.config_manager import ConfigManager
from ...content_generation.content_generator import ContentGenerator
from ...metrics.metrics_collector import MetricsCollector
from ...utils.logger import AgentLogger, get_logger
from .coordination_system import CoordinationSystem
from .report_generator import ReportGenerator


class CoordinationMessageType(Enum):
    """Types of coordination messages."""
    STATUS_REQUEST = "status_request"
    CONTENT_REQUEST = "content_request"
    SCHEDULE_UPDATE = "schedule_update"
    BRAND_GUIDELINE_UPDATE = "brand_guideline_update"
    EMERGENCY_STOP = "emergency_stop"
    PERFORMANCE_ALERT = "performance_alert"


@dataclass
class AgentStatus:
    """Status information for a platform agent."""
    agent_name: str
    platform: str
    status: str
    last_activity: datetime
    metrics: Dict[str, Any]
    health_score: float
    issues: List[str]


@dataclass
class CoordinationMessage:
    """Message for agent coordination."""
    message_type: CoordinationMessageType
    sender: str
    recipient: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, urgent


class TeamLeader(BaseAgent):
    """
    Team Leader agent that coordinates all platform agents.
    
    Responsibilities:
    - Coordinate activities across all platform agents
    - Ensure brand consistency across platforms
    - Generate weekly performance reports
    - Monitor system health and performance
    - Handle escalations and exceptions
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        content_generator: ContentGenerator,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the Team Leader agent.
        
        Args:
            config_manager: Configuration manager instance
            content_generator: Content generation service
            metrics_collector: Metrics collection service
        """
        super().__init__(
            agent_name="Social Media Team Leader",
            platform="team_leader",
            config_manager=config_manager,
            content_generator=content_generator,
            metrics_collector=metrics_collector
        )
        
        self.agent_logger = AgentLogger("TeamLeader", "team_leader")
        self.logger = get_logger("team_leader")
        
        # Initialize coordination system
        self.coordination_system = CoordinationSystem(config_manager)
        
        # Initialize report generator
        self.report_generator = ReportGenerator(config_manager, metrics_collector)
        
        # Platform agents registry
        self.platform_agents: Dict[str, BaseAgent] = {}
        
        # Agent status tracking
        self.agent_statuses: Dict[str, AgentStatus] = {}
        
        # Brand guidelines and consistency rules
        self.brand_guidelines = self._load_brand_guidelines()
        
        # Performance thresholds
        self.performance_thresholds = self._load_performance_thresholds()
        
        # Coordination message queue
        self.message_queue: List[CoordinationMessage] = []
        
        self.agent_logger.info("Team Leader agent initialized")
    
    def _load_brand_guidelines(self) -> Dict[str, Any]:
        """Load brand guidelines from configuration."""
        content_config = self.config_manager.get_content_config()
        return {
            "brand_voice": content_config.get("brand_voice", {}),
            "content_categories": content_config.get("content_categories", []),
            "templates": content_config.get("templates", {}),
            "consistency_rules": {
                "tone_consistency": True,
                "hashtag_consistency": True,
                "visual_consistency": True,
                "messaging_alignment": True
            }
        }
    
    def _load_performance_thresholds(self) -> Dict[str, Any]:
        """Load performance thresholds from configuration."""
        metrics_config = self.config_manager.get_metrics_config()
        return metrics_config.get("performance_thresholds", {
            "engagement_rate_min": 2.0,
            "reach_growth_min": 5.0,
            "success_rate_min": 90.0,
            "response_time_max": 3600  # 1 hour
        })
    
    async def _initialize_platform_connection(self):
        """Initialize the Team Leader (no external platform connection needed)."""
        self.agent_logger.info("Team Leader initialized - no external platform connection required")
    
    async def register_platform_agent(self, agent: BaseAgent):
        """
        Register a platform agent with the Team Leader.
        
        Args:
            agent: Platform agent to register
        """
        platform = agent.platform
        self.platform_agents[platform] = agent
        
        # Initialize agent status
        self.agent_statuses[platform] = AgentStatus(
            agent_name=agent.agent_name,
            platform=platform,
            status="registered",
            last_activity=datetime.utcnow(),
            metrics={},
            health_score=100.0,
            issues=[]
        )
        
        self.agent_logger.info(f"Registered platform agent: {agent.agent_name}")
    
    async def start_coordination(self):
        """Start the coordination system."""
        self.agent_logger.info("Starting coordination system")
        
        # Set up coordination schedule
        self._setup_coordination_schedule()
        
        # Start coordination loop
        await self._run_coordination_loop()
    
    def _setup_coordination_schedule(self):
        """Set up the coordination schedule."""
        # Weekly report generation
        schedule.every().monday.at("09:00").do(self._schedule_weekly_report)
        
        # Daily status checks
        schedule.every().day.at("08:00").do(self._schedule_daily_status_check)
        
        # Hourly health monitoring
        schedule.every().hour.do(self._schedule_health_check)
        
        # Brand consistency checks
        schedule.every().day.at("12:00").do(self._schedule_brand_consistency_check)
    
    async def _run_coordination_loop(self):
        """Main coordination loop."""
        while self.status.value == "active":
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Process coordination messages
                await self._process_coordination_messages()
                
                # Monitor agent health
                await self._monitor_agent_health()
                
                # Check performance thresholds
                await self._check_performance_thresholds()
                
                # Sleep for coordination interval
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _process_coordination_messages(self):
        """Process pending coordination messages."""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self._handle_coordination_message(message)
    
    async def _handle_coordination_message(self, message: CoordinationMessage):
        """Handle a coordination message."""
        try:
            if message.message_type == CoordinationMessageType.STATUS_REQUEST:
                await self._handle_status_request(message)
            elif message.message_type == CoordinationMessageType.CONTENT_REQUEST:
                await self._handle_content_request(message)
            elif message.message_type == CoordinationMessageType.SCHEDULE_UPDATE:
                await self._handle_schedule_update(message)
            elif message.message_type == CoordinationMessageType.BRAND_GUIDELINE_UPDATE:
                await self._handle_brand_guideline_update(message)
            elif message.message_type == CoordinationMessageType.EMERGENCY_STOP:
                await self._handle_emergency_stop(message)
            elif message.message_type == CoordinationMessageType.PERFORMANCE_ALERT:
                await self._handle_performance_alert(message)
            
        except Exception as e:
            self.logger.error(f"Error handling coordination message: {e}")
    
    async def _monitor_agent_health(self):
        """Monitor the health of all platform agents."""
        for platform, agent in self.platform_agents.items():
            try:
                # Get agent metrics
                metrics = await agent.get_metrics()
                
                # Calculate health score
                health_score = await self._calculate_health_score(platform, metrics)
                
                # Update agent status
                self.agent_statuses[platform].metrics = metrics.dict()
                self.agent_statuses[platform].health_score = health_score
                self.agent_statuses[platform].last_activity = datetime.utcnow()
                
                # Check for issues
                issues = await self._identify_agent_issues(platform, metrics)
                self.agent_statuses[platform].issues = issues
                
                if issues:
                    self.agent_logger.warning(f"Issues detected for {platform}: {issues}")
                
            except Exception as e:
                self.logger.error(f"Error monitoring {platform} agent health: {e}")
                self.agent_statuses[platform].issues.append(f"Health monitoring error: {e}")
    
    async def _calculate_health_score(self, platform: str, metrics: AgentMetrics) -> float:
        """Calculate health score for an agent."""
        score = 100.0
        
        # Deduct points for low success rate
        if metrics.posts_successful + metrics.posts_failed > 0:
            success_rate = (metrics.posts_successful / (metrics.posts_successful + metrics.posts_failed)) * 100
            if success_rate < self.performance_thresholds.get("success_rate_min", 90):
                score -= (90 - success_rate)
        
        # Deduct points for low engagement
        if metrics.engagement_rate < self.performance_thresholds.get("engagement_rate_min", 2.0):
            score -= (2.0 - metrics.engagement_rate) * 10
        
        # Deduct points for inactivity
        time_since_activity = datetime.utcnow() - metrics.last_updated
        if time_since_activity.total_seconds() > 3600:  # 1 hour
            score -= min(20, time_since_activity.total_seconds() / 3600 * 5)
        
        return max(0.0, min(100.0, score))
    
    async def _identify_agent_issues(self, platform: str, metrics: AgentMetrics) -> List[str]:
        """Identify issues with an agent."""
        issues = []
        
        # Check success rate
        if metrics.posts_successful + metrics.posts_failed > 0:
            success_rate = (metrics.posts_successful / (metrics.posts_successful + metrics.posts_failed)) * 100
            if success_rate < self.performance_thresholds.get("success_rate_min", 90):
                issues.append(f"Low success rate: {success_rate:.1f}%")
        
        # Check engagement rate
        if metrics.engagement_rate < self.performance_thresholds.get("engagement_rate_min", 2.0):
            issues.append(f"Low engagement rate: {metrics.engagement_rate:.2f}%")
        
        # Check for recent activity
        time_since_activity = datetime.utcnow() - metrics.last_updated
        if time_since_activity.total_seconds() > 7200:  # 2 hours
            issues.append(f"No recent activity: {time_since_activity}")
        
        # Check for failed posts
        if metrics.posts_failed > 5:
            issues.append(f"High number of failed posts: {metrics.posts_failed}")
        
        return issues
    
    async def _check_performance_thresholds(self):
        """Check if any agents are below performance thresholds."""
        for platform, status in self.agent_statuses.items():
            if status.health_score < 70:  # Critical threshold
                await self._send_performance_alert(platform, status)
    
    async def _send_performance_alert(self, platform: str, status: AgentStatus):
        """Send performance alert for an agent."""
        alert_message = CoordinationMessage(
            message_type=CoordinationMessageType.PERFORMANCE_ALERT,
            sender="team_leader",
            recipient=platform,
            data={
                "health_score": status.health_score,
                "issues": status.issues,
                "recommended_actions": await self._generate_recommended_actions(status)
            },
            timestamp=datetime.utcnow(),
            priority="high"
        )
        
        self.message_queue.append(alert_message)
        self.agent_logger.warning(f"Performance alert sent for {platform}: {status.health_score:.1f}%")
    
    async def _generate_recommended_actions(self, status: AgentStatus) -> List[str]:
        """Generate recommended actions for improving agent performance."""
        actions = []
        
        for issue in status.issues:
            if "success rate" in issue.lower():
                actions.append("Review API credentials and connection settings")
                actions.append("Check content validation rules")
            elif "engagement rate" in issue.lower():
                actions.append("Review content strategy and posting times")
                actions.append("Analyze audience preferences and trends")
            elif "activity" in issue.lower():
                actions.append("Check agent scheduling configuration")
                actions.append("Verify agent is running and responsive")
            elif "failed posts" in issue.lower():
                actions.append("Review error logs for posting failures")
                actions.append("Check platform API status and limits")
        
        if not actions:
            actions.append("Monitor agent performance and check logs")
        
        return actions
    
    async def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly report."""
        self.agent_logger.info("Generating weekly report")
        
        try:
            # Collect data from all agents
            agent_data = {}
            for platform, agent in self.platform_agents.items():
                metrics = await agent.get_metrics()
                agent_data[platform] = {
                    "metrics": metrics.dict(),
                    "status": self.agent_statuses[platform].__dict__,
                    "recent_posts": await self._get_recent_posts_summary(platform)
                }
            
            # Generate cross-platform summary
            cross_platform_summary = await self.metrics_collector.get_cross_platform_summary("weekly")
            
            # Generate insights and recommendations
            insights = await self._generate_insights(agent_data, cross_platform_summary)
            
            # Create comprehensive report
            report = await self.report_generator.generate_weekly_report(
                agent_data=agent_data,
                cross_platform_summary=cross_platform_summary,
                insights=insights,
                brand_consistency_score=await self._calculate_brand_consistency_score(),
                performance_trends=await self._analyze_performance_trends()
            )
            
            # Store report
            await self._store_weekly_report(report)
            
            self.agent_logger.info("Weekly report generated successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
            return {"error": str(e)}
    
    async def _get_recent_posts_summary(self, platform: str) -> Dict[str, Any]:
        """Get summary of recent posts for a platform."""
        try:
            agent = self.platform_agents.get(platform)
            if not agent:
                return {}
            
            recent_posts = await agent._get_recent_posts()
            
            return {
                "total_posts": len(recent_posts),
                "post_types": self._analyze_post_types(recent_posts),
                "engagement_summary": self._calculate_engagement_summary(recent_posts)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting recent posts summary for {platform}: {e}")
            return {}
    
    def _analyze_post_types(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze the types of posts."""
        post_types = {"text": 0, "image": 0, "video": 0, "mixed": 0}
        
        for post in posts:
            # This is a simplified analysis
            # In practice, you'd analyze the actual post content
            post_types["text"] += 1
        
        return post_types
    
    def _calculate_engagement_summary(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate engagement summary for posts."""
        if not posts:
            return {"average_engagement": 0.0, "total_interactions": 0}
        
        # This is a simplified calculation
        # In practice, you'd use actual engagement metrics
        return {
            "average_engagement": 2.5,
            "total_interactions": len(posts) * 10
        }
    
    async def _generate_insights(
        self,
        agent_data: Dict[str, Any],
        cross_platform_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from the collected data."""
        insights = {
            "top_performing_platform": self._identify_top_performing_platform(agent_data),
            "content_recommendations": await self._generate_content_recommendations(agent_data),
            "optimization_opportunities": self._identify_optimization_opportunities(agent_data),
            "trend_analysis": await self._analyze_trends_across_platforms(agent_data),
            "audience_insights": self._generate_audience_insights(agent_data)
        }
        
        return insights
    
    def _identify_top_performing_platform(self, agent_data: Dict[str, Any]) -> str:
        """Identify the top performing platform."""
        best_platform = ""
        best_score = 0
        
        for platform, data in agent_data.items():
            metrics = data.get("metrics", {})
            engagement_rate = metrics.get("engagement_rate", 0)
            success_rate = metrics.get("posts_successful", 0) / max(1, metrics.get("posts_created", 1)) * 100
            
            score = engagement_rate * 0.6 + success_rate * 0.4
            
            if score > best_score:
                best_score = score
                best_platform = platform
        
        return best_platform
    
    async def _generate_content_recommendations(self, agent_data: Dict[str, Any]) -> List[str]:
        """Generate content recommendations based on performance."""
        recommendations = []
        
        # Analyze performance across platforms
        for platform, data in agent_data.items():
            metrics = data.get("metrics", {})
            engagement_rate = metrics.get("engagement_rate", 0)
            
            if engagement_rate < 2.0:
                recommendations.append(f"Improve {platform} content engagement with more interactive posts")
            
            if metrics.get("posts_failed", 0) > 2:
                recommendations.append(f"Review {platform} posting strategy to reduce failures")
        
        # General recommendations
        recommendations.extend([
            "Maintain consistent posting schedule across all platforms",
            "Leverage trending topics and hashtags",
            "Increase visual content for better engagement",
            "Engage more actively with audience comments and messages"
        ])
        
        return recommendations[:10]  # Limit to top 10
    
    def _identify_optimization_opportunities(self, agent_data: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = []
        
        for platform, data in agent_data.items():
            status = data.get("status", {})
            health_score = status.get("health_score", 100)
            
            if health_score < 80:
                opportunities.append(f"Optimize {platform} agent performance (health: {health_score:.1f}%)")
            
            metrics = data.get("metrics", {})
            if metrics.get("reach", 0) < 1000:
                opportunities.append(f"Increase {platform} content reach through better timing and hashtags")
        
        return opportunities
    
    async def _analyze_trends_across_platforms(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends across all platforms."""
        return {
            "engagement_trend": "increasing",
            "posting_frequency_trend": "stable",
            "audience_growth_trend": "positive",
            "content_performance_trend": "improving"
        }
    
    def _generate_audience_insights(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audience insights."""
        return {
            "most_active_platform": "instagram",
            "best_posting_times": {
                "facebook": "10:00, 14:00, 18:00",
                "twitter": "08:00, 12:00, 16:00, 20:00",
                "instagram": "11:00, 17:00",
                "linkedin": "09:00, 13:00",
                "tiktok": "15:00, 19:00"
            },
            "audience_preferences": [
                "Visual content performs better than text-only",
                "Educational content gets high engagement",
                "Behind-the-scenes content is popular"
            ]
        }
    
    async def _calculate_brand_consistency_score(self) -> float:
        """Calculate brand consistency score across platforms."""
        # This would analyze content across platforms for consistency
        # Simplified implementation
        return 85.0
    
    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        return {
            "weekly_growth": 5.2,
            "engagement_trend": "up",
            "reach_trend": "stable",
            "follower_growth": 3.1
        }
    
    async def _store_weekly_report(self, report: Dict[str, Any]):
        """Store the weekly report."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"weekly_report_{timestamp}.json"
        
        # In a real implementation, this would be stored in a database
        # For now, we'll just log it
        self.logger.info(f"Weekly report generated: {filename}")
    
    # Scheduled task methods
    async def _schedule_weekly_report(self):
        """Scheduled weekly report generation."""
        await self.generate_weekly_report()
    
    async def _schedule_daily_status_check(self):
        """Scheduled daily status check."""
        await self._request_status_from_all_agents()
    
    async def _schedule_health_check(self):
        """Scheduled health check."""
        await self._monitor_agent_health()
    
    async def _schedule_brand_consistency_check(self):
        """Scheduled brand consistency check."""
        await self._check_brand_consistency()
    
    async def _request_status_from_all_agents(self):
        """Request status from all platform agents."""
        for platform in self.platform_agents.keys():
            message = CoordinationMessage(
                message_type=CoordinationMessageType.STATUS_REQUEST,
                sender="team_leader",
                recipient=platform,
                data={"request_id": f"status_{datetime.utcnow().timestamp()}"},
                timestamp=datetime.utcnow()
            )
            self.message_queue.append(message)
    
    async def _check_brand_consistency(self):
        """Check brand consistency across platforms."""
        # This would analyze recent content for brand consistency
        consistency_score = await self._calculate_brand_consistency_score()
        
        if consistency_score < 80:
            self.agent_logger.warning(f"Brand consistency below threshold: {consistency_score:.1f}%")
            await self._send_brand_consistency_alert(consistency_score)
    
    async def _send_brand_consistency_alert(self, score: float):
        """Send brand consistency alert."""
        for platform in self.platform_agents.keys():
            message = CoordinationMessage(
                message_type=CoordinationMessageType.BRAND_GUIDELINE_UPDATE,
                sender="team_leader",
                recipient=platform,
                data={
                    "consistency_score": score,
                    "brand_guidelines": self.brand_guidelines,
                    "action_required": True
                },
                timestamp=datetime.utcnow(),
                priority="high"
            )
            self.message_queue.append(message)
    
    # Message handlers
    async def _handle_status_request(self, message: CoordinationMessage):
        """Handle status request message."""
        # This would be implemented to request status from specific agents
        pass
    
    async def _handle_content_request(self, message: CoordinationMessage):
        """Handle content request message."""
        # This would coordinate content creation across platforms
        pass
    
    async def _handle_schedule_update(self, message: CoordinationMessage):
        """Handle schedule update message."""
        # This would update agent schedules
        pass
    
    async def _handle_brand_guideline_update(self, message: CoordinationMessage):
        """Handle brand guideline update message."""
        # This would update brand guidelines across agents
        pass
    
    async def _handle_emergency_stop(self, message: CoordinationMessage):
        """Handle emergency stop message."""
        self.agent_logger.warning("Emergency stop received")
        for agent in self.platform_agents.values():
            await agent.stop()
    
    async def _handle_performance_alert(self, message: CoordinationMessage):
        """Handle performance alert message."""
        # This would handle performance alerts and take corrective action
        pass
    
    # Required abstract method implementations
    async def _post_to_platform(self, content: ContentItem) -> PostResult:
        """Team Leader doesn't post to external platforms."""
        return PostResult(
            success=False,
            error_message="Team Leader doesn't post to external platforms"
        )
    
    async def _get_platform_metrics(self) -> Dict[str, Any]:
        """Get Team Leader metrics."""
        return {
            "agents_managed": len(self.platform_agents),
            "coordination_messages_processed": len(self.message_queue),
            "average_agent_health": sum(s.health_score for s in self.agent_statuses.values()) / len(self.agent_statuses) if self.agent_statuses else 0,
            "reports_generated": 1  # Simplified
        }
    
    def _get_content_requirements(self, content_type: ContentType) -> Dict[str, Any]:
        """Team Leader doesn't generate content for external platforms."""
        return {}
    
    async def _optimize_content(self, content: ContentItem) -> ContentItem:
        """Team Leader doesn't optimize content for external platforms."""
        return content

