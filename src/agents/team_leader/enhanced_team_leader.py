"""
Enhanced Team Leader Agent

Enhanced version that integrates with Generator Agent and Evaluation Agent
for content approval workflow and feedback-driven improvements.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

from ..base_agent import BaseAgent
from ..generator_agent.generator_agent import GeneratorAgent
from ..evaluation_agent.evaluation_agent import EvaluationAgent
from ..platform_agents.facebook_agent import FacebookAgent
from ..platform_agents.twitter_agent import TwitterAgent
from ..platform_agents.instagram_agent import InstagramAgent
from ..platform_agents.linkedin_agent import LinkedInAgent
from ..platform_agents.tiktok_agent import TikTokAgent
from .coordination_system import CoordinationSystem
from .report_generator import ReportGenerator
from ...utils.logger import get_logger


class EnhancedTeamLeaderAgent(BaseAgent):
    """
    Enhanced Team Leader Agent with content approval workflow.
    
    This agent:
    1. Coordinates content generation and approval workflow
    2. Manages platform-specific agents
    3. Oversees content evaluation and feedback processing
    4. Generates comprehensive reports
    5. Ensures consistent brand messaging across platforms
    6. Manages posting schedules and coordination
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Enhanced Team Leader Agent."""
        super().__init__(config)
        self.agent_type = "enhanced_team_leader"
        self.logger = get_logger(f"{self.agent_type}_agent")
        
        # Initialize new agents
        self.generator_agent = GeneratorAgent(config.get('generator_agent', {}))
        self.evaluation_agent = EvaluationAgent(config.get('evaluation_agent', {}))
        
        # Initialize platform agents
        self.platform_agents = {
            'facebook': FacebookAgent(config.get('facebook_agent', {})),
            'twitter': TwitterAgent(config.get('twitter_agent', {})),
            'instagram': InstagramAgent(config.get('instagram_agent', {})),
            'linkedin': LinkedInAgent(config.get('linkedin_agent', {})),
            'tiktok': TikTokAgent(config.get('tiktok_agent', {}))
        }
        
        # Initialize coordination and reporting systems
        self.coordination_system = CoordinationSystem(config.get('coordination', {}))
        self.report_generator = ReportGenerator(config.get('reporting', {}))
        
        # Configuration
        self.team_config = config.get('team_leader', {})
        self.workflow_config = config.get('workflow', {})
        self.approval_required = self.workflow_config.get('approval_required', True)
        self.auto_post_threshold = self.workflow_config.get('auto_post_threshold', 0.8)
        self.reporting_schedule = self.team_config.get('reporting_schedule', 'weekly')
        
        # State tracking
        self.active_campaigns = {}
        self.pending_approvals = {}
        self.posted_content = {}
        self.performance_metrics = {
            'total_content_generated': 0,
            'total_content_posted': 0,
            'approval_rate': 0.0,
            'average_engagement': 0.0,
            'platform_performance': {}
        }
        
        self.logger.info(f"Enhanced Team Leader Agent initialized with {len(self.platform_agents)} platform agents")
    
    async def start(self):
        """Start the team leader and all sub-agents."""
        self.logger.info("Starting Enhanced Team Leader Agent and all sub-agents...")
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        # Start all agents
        await self.generator_agent.start()
        await self.evaluation_agent.start()
        
        for platform, agent in self.platform_agents.items():
            await agent.start()
            self.logger.info(f"Started {platform} agent")
        
        # Start coordination system
        await self.coordination_system.start()
        
        # Start background tasks
        asyncio.create_task(self._content_workflow_loop())
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._reporting_loop())
        asyncio.create_task(self._approval_management_loop())
        
        self.logger.info("Enhanced Team Leader Agent and all sub-agents started successfully")
    
    async def stop(self):
        """Stop the team leader and all sub-agents."""
        self.logger.info("Stopping Enhanced Team Leader Agent and all sub-agents...")
        self.is_running = False
        
        # Stop all agents
        await self.generator_agent.stop()
        await self.evaluation_agent.stop()
        
        for platform, agent in self.platform_agents.items():
            await agent.stop()
            self.logger.info(f"Stopped {platform} agent")
        
        # Stop coordination system
        await self.coordination_system.stop()
        
        self.logger.info("Enhanced Team Leader Agent and all sub-agents stopped")
    
    async def create_content_campaign(self, campaign_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new content campaign with content generation and approval workflow.
        
        Args:
            campaign_request: Campaign requirements and parameters
            
        Returns:
            Campaign creation result with generated content suggestions
        """
        try:
            self.logger.info(f"Creating content campaign: {campaign_request.get('name', 'Unnamed')}")
            
            campaign_id = str(uuid.uuid4())
            
            # Step 1: Generate business briefing
            briefing_result = await self.generator_agent.create_business_briefing(
                campaign_request.get('business_info', {})
            )
            
            if not briefing_result.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to create business briefing',
                    'details': briefing_result
                }
            
            # Step 2: Generate content suggestions
            content_request = {
                'briefing_id': briefing_result['briefing']['id'],
                'platforms': campaign_request.get('platforms', ['facebook', 'twitter', 'instagram']),
                'content_count': campaign_request.get('content_count', 10),
                'content_types': campaign_request.get('content_types', ['educational', 'promotional']),
                'campaign_objectives': campaign_request.get('objectives', [])
            }
            
            suggestions_result = await self.generator_agent.generate_content_suggestions(content_request)
            
            if not suggestions_result.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to generate content suggestions',
                    'details': suggestions_result
                }
            
            # Step 3: Create campaign record
            campaign = {
                'id': campaign_id,
                'name': campaign_request.get('name', f'Campaign_{campaign_id[:8]}'),
                'briefing_id': briefing_result['briefing']['id'],
                'business_profile_id': briefing_result['briefing']['business_profile_id'],
                'platforms': content_request['platforms'],
                'content_suggestions': suggestions_result['suggestions'],
                'status': 'pending_approval' if self.approval_required else 'ready_to_post',
                'created_at': datetime.utcnow().isoformat(),
                'objectives': campaign_request.get('objectives', []),
                'target_audience': campaign_request.get('target_audience', {}),
                'posting_schedule': campaign_request.get('posting_schedule', {})
            }
            
            self.active_campaigns[campaign_id] = campaign
            
            # Step 4: Add to approval queue if required
            if self.approval_required:
                await self._add_to_approval_queue(campaign)
            
            # Step 5: Update metrics
            self.performance_metrics['total_content_generated'] += len(suggestions_result['suggestions'])
            
            return {
                'success': True,
                'campaign': campaign,
                'briefing': briefing_result['briefing'],
                'content_suggestions': suggestions_result['suggestions'],
                'approval_required': self.approval_required,
                'next_steps': 'Content pending approval' if self.approval_required else 'Ready for posting'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating content campaign: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_content_approval(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content approval decisions and update workflow.
        
        Args:
            approval_data: Approval decisions for content suggestions
            
        Returns:
            Processing result and next steps
        """
        try:
            self.logger.info("Processing content approval decisions")
            
            campaign_id = approval_data.get('campaign_id')
            approvals = approval_data.get('approvals', {})
            
            if campaign_id not in self.active_campaigns:
                return {
                    'success': False,
                    'error': 'Campaign not found'
                }
            
            campaign = self.active_campaigns[campaign_id]
            
            # Process each approval decision
            approved_content = []
            rejected_content = []
            feedback_data = []
            
            for suggestion_id, decision in approvals.items():
                # Find the content suggestion
                suggestion = None
                for content in campaign['content_suggestions']:
                    if content['id'] == suggestion_id:
                        suggestion = content
                        break
                
                if not suggestion:
                    continue
                
                # Process decision
                if decision['action'] in ['approve', 'thumbs_up']:
                    suggestion['status'] = 'approved'
                    suggestion['approved_at'] = datetime.utcnow().isoformat()
                    approved_content.append(suggestion)
                elif decision['action'] in ['reject', 'thumbs_down']:
                    suggestion['status'] = 'rejected'
                    suggestion['rejected_at'] = datetime.utcnow().isoformat()
                    rejected_content.append(suggestion)
                
                # Collect feedback for evaluation agent
                feedback_entry = {
                    'content_suggestion_id': suggestion_id,
                    'feedback_type': decision['action'],
                    'feedback_comments': decision.get('comments', ''),
                    'platform': suggestion.get('platform'),
                    'content_type': suggestion.get('content_type'),
                    'timestamp': datetime.utcnow().isoformat(),
                    'content_text': suggestion.get('full_text', ''),
                    'hashtags': suggestion.get('hashtags', []),
                    'engagement_score': suggestion.get('engagement_score', 0)
                }
                
                feedback_data.append(feedback_entry)
            
            # Send feedback to evaluation agent
            for feedback in feedback_data:
                await self.evaluation_agent.process_feedback(feedback)
            
            # Update campaign status
            if approved_content:
                campaign['status'] = 'ready_to_post'
                campaign['approved_content'] = approved_content
            
            # Schedule approved content for posting
            if approved_content:
                scheduling_result = await self._schedule_approved_content(campaign, approved_content)
            else:
                scheduling_result = {'scheduled_posts': 0}
            
            # Update metrics
            approval_rate = len(approved_content) / len(approvals) if approvals else 0
            self.performance_metrics['approval_rate'] = (
                self.performance_metrics['approval_rate'] + approval_rate
            ) / 2  # Simple moving average
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'approved_count': len(approved_content),
                'rejected_count': len(rejected_content),
                'scheduling_result': scheduling_result,
                'campaign_status': campaign['status'],
                'feedback_processed': len(feedback_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing content approval: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_content_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get content improvement recommendations from evaluation agent.
        
        Args:
            request_data: Request parameters for recommendations
            
        Returns:
            Content recommendations and optimization suggestions
        """
        try:
            self.logger.info("Getting content recommendations from evaluation agent")
            
            # Get recommendations from evaluation agent
            recommendations = await self.evaluation_agent.get_content_recommendations(request_data)
            
            if not recommendations.get('success'):
                return recommendations
            
            # Enhance recommendations with platform-specific insights
            enhanced_recommendations = await self._enhance_recommendations_with_platform_insights(
                recommendations, request_data
            )
            
            return {
                'success': True,
                'recommendations': enhanced_recommendations,
                'evaluation_agent_recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting content recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_performance_report(self, report_type: str = 'weekly') -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            
        Returns:
            Comprehensive performance report
        """
        try:
            self.logger.info(f"Generating {report_type} performance report")
            
            # Collect data from all agents
            generator_metrics = await self.generator_agent.get_performance_metrics()
            evaluation_metrics = await self.evaluation_agent.get_performance_metrics()
            
            platform_metrics = {}
            for platform, agent in self.platform_agents.items():
                platform_metrics[platform] = await agent.get_performance_metrics()
            
            # Generate comprehensive report
            report = await self.report_generator.generate_comprehensive_report({
                'report_type': report_type,
                'team_leader_metrics': self.performance_metrics,
                'generator_metrics': generator_metrics,
                'evaluation_metrics': evaluation_metrics,
                'platform_metrics': platform_metrics,
                'active_campaigns': self.active_campaigns,
                'posted_content': self.posted_content
            })
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_team_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all team agents."""
        try:
            status = {
                'enhanced_team_leader': {
                    'is_running': self.is_running,
                    'active_campaigns': len(self.active_campaigns),
                    'pending_approvals': len(self.pending_approvals),
                    'performance_metrics': self.performance_metrics
                },
                'generator_agent': await self.generator_agent.get_status(),
                'evaluation_agent': await self.evaluation_agent.get_status(),
                'platform_agents': {}
            }
            
            for platform, agent in self.platform_agents.items():
                status['platform_agents'][platform] = await agent.get_status()
            
            return {
                'success': True,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting team status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _content_workflow_loop(self):
        """Background loop for managing content workflow."""
        while self.is_running:
            try:
                # Process scheduled posts
                await self._process_scheduled_posts()
                
                # Check for auto-approval candidates
                if self.approval_required:
                    await self._check_auto_approval_candidates()
                
                # Update campaign statuses
                await self._update_campaign_statuses()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in content workflow loop: {str(e)}")
                await asyncio.sleep(300)
    
    async def _performance_monitoring_loop(self):
        """Background loop for monitoring performance metrics."""
        while self.is_running:
            try:
                # Collect performance data from all agents
                await self._collect_performance_metrics()
                
                # Update team-level metrics
                await self._update_team_metrics()
                
                # Check for performance alerts
                await self._check_performance_alerts()
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {str(e)}")
                await asyncio.sleep(1800)
    
    async def _reporting_loop(self):
        """Background loop for generating scheduled reports."""
        while self.is_running:
            try:
                # Check if it's time for scheduled report
                if await self._is_report_time():
                    report = await self.generate_performance_report(self.reporting_schedule)
                    
                    if report.get('success'):
                        # Store or send report (implementation depends on requirements)
                        await self._handle_scheduled_report(report)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in reporting loop: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _approval_management_loop(self):
        """Background loop for managing approval workflow."""
        while self.is_running:
            try:
                # Check for expired approval requests
                await self._check_expired_approvals()
                
                # Process auto-approval candidates
                await self._process_auto_approvals()
                
                # Update approval queue priorities
                await self._update_approval_priorities()
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error in approval management loop: {str(e)}")
                await asyncio.sleep(600)
    
    async def _add_to_approval_queue(self, campaign: Dict[str, Any]):
        """Add campaign content to approval queue."""
        approval_entry = {
            'campaign_id': campaign['id'],
            'campaign_name': campaign['name'],
            'content_count': len(campaign['content_suggestions']),
            'priority': self._calculate_approval_priority(campaign),
            'added_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        self.pending_approvals[campaign['id']] = approval_entry
        self.logger.info(f"Added campaign {campaign['id']} to approval queue")
    
    async def _schedule_approved_content(self, campaign: Dict[str, Any], 
                                       approved_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Schedule approved content for posting."""
        scheduled_posts = 0
        
        posting_schedule = campaign.get('posting_schedule', {})
        
        for content in approved_content:
            platform = content.get('platform')
            
            if platform in self.platform_agents:
                # Calculate posting time
                posting_time = self._calculate_posting_time(content, posting_schedule)
                
                # Schedule with platform agent
                schedule_result = await self.platform_agents[platform].schedule_post({
                    'content': content,
                    'posting_time': posting_time,
                    'campaign_id': campaign['id']
                })
                
                if schedule_result.get('success'):
                    scheduled_posts += 1
                    content['scheduled_at'] = posting_time
                    content['status'] = 'scheduled'
        
        return {
            'scheduled_posts': scheduled_posts,
            'total_approved': len(approved_content)
        }
    
    async def _enhance_recommendations_with_platform_insights(self, 
                                                            recommendations: Dict[str, Any],
                                                            request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance recommendations with platform-specific insights."""
        enhanced = recommendations.copy()
        
        platform = request_data.get('platform')
        if platform and platform in self.platform_agents:
            platform_insights = await self.platform_agents[platform].get_content_insights(request_data)
            
            if platform_insights.get('success'):
                enhanced['platform_insights'] = platform_insights['insights']
        
        return enhanced
    
    async def _process_scheduled_posts(self):
        """Process posts that are scheduled for posting."""
        current_time = datetime.utcnow()
        
        for campaign in self.active_campaigns.values():
            if 'approved_content' not in campaign:
                continue
            
            for content in campaign['approved_content']:
                if (content.get('status') == 'scheduled' and 
                    'scheduled_at' in content):
                    
                    scheduled_time = datetime.fromisoformat(content['scheduled_at'])
                    
                    if current_time >= scheduled_time:
                        # Time to post
                        platform = content.get('platform')
                        
                        if platform in self.platform_agents:
                            post_result = await self.platform_agents[platform].post_content(content)
                            
                            if post_result.get('success'):
                                content['status'] = 'posted'
                                content['posted_at'] = current_time.isoformat()
                                content['post_id'] = post_result.get('post_id')
                                
                                # Track posted content
                                self.posted_content[content['id']] = content
                                self.performance_metrics['total_content_posted'] += 1
                                
                                self.logger.info(f"Posted content {content['id']} to {platform}")
    
    async def _check_auto_approval_candidates(self):
        """Check for content that can be auto-approved based on confidence scores."""
        for campaign_id, approval_entry in self.pending_approvals.items():
            if campaign_id not in self.active_campaigns:
                continue
            
            campaign = self.active_campaigns[campaign_id]
            auto_approved = []
            
            for content in campaign['content_suggestions']:
                if content.get('status') == 'pending_review':
                    # Get recommendation confidence from evaluation agent
                    confidence_result = await self.evaluation_agent.predict_user_preference(
                        self._extract_content_features(content),
                        {}  # Current model
                    )
                    
                    confidence = confidence_result.get('confidence', 0.0)
                    preference_score = confidence_result.get('preference_score', 0.5)
                    
                    if (confidence > 0.8 and 
                        preference_score > self.auto_post_threshold):
                        
                        content['status'] = 'auto_approved'
                        content['auto_approved_at'] = datetime.utcnow().isoformat()
                        content['confidence_score'] = confidence
                        auto_approved.append(content)
            
            if auto_approved:
                self.logger.info(f"Auto-approved {len(auto_approved)} content items for campaign {campaign_id}")
                
                # Schedule auto-approved content
                await self._schedule_approved_content(campaign, auto_approved)
    
    def _calculate_approval_priority(self, campaign: Dict[str, Any]) -> float:
        """Calculate priority for approval queue."""
        base_priority = 0.5
        
        # Increase priority based on campaign objectives
        objectives = campaign.get('objectives', [])
        if 'urgent' in objectives:
            base_priority += 0.3
        if 'time_sensitive' in objectives:
            base_priority += 0.2
        
        # Increase priority based on content count
        content_count = len(campaign.get('content_suggestions', []))
        if content_count > 10:
            base_priority += 0.1
        
        return min(base_priority, 1.0)
    
    def _calculate_posting_time(self, content: Dict[str, Any], 
                              posting_schedule: Dict[str, Any]) -> str:
        """Calculate optimal posting time for content."""
        platform = content.get('platform', '')
        
        # Get platform-specific optimal times
        platform_config = self.workflow_config.get('platform_schedules', {}).get(platform, {})
        optimal_hours = platform_config.get('optimal_hours', [9, 12, 15, 18])
        
        # Get next optimal time
        current_time = datetime.utcnow()
        
        # Find next optimal hour
        for hour in optimal_hours:
            if hour > current_time.hour:
                posting_time = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                break
        else:
            # Next day, first optimal hour
            posting_time = (current_time + timedelta(days=1)).replace(
                hour=optimal_hours[0], minute=0, second=0, microsecond=0
            )
        
        return posting_time.isoformat()
    
    def _extract_content_features(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from content for evaluation."""
        return {
            'platform': content.get('platform', ''),
            'content_type': content.get('content_type', ''),
            'content_length': len(content.get('full_text', '')),
            'has_hashtags': bool(content.get('hashtags')),
            'hashtag_count': len(content.get('hashtags', [])),
            'has_call_to_action': bool(content.get('call_to_action')),
            'engagement_score': content.get('engagement_score', 0)
        }
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics from all agents."""
        # This would collect and aggregate metrics from all agents
        pass
    
    async def _update_team_metrics(self):
        """Update team-level performance metrics."""
        # Calculate team-level metrics from individual agent metrics
        pass
    
    async def _check_performance_alerts(self):
        """Check for performance issues that need attention."""
        # Monitor for performance degradation or issues
        pass
    
    async def _is_report_time(self) -> bool:
        """Check if it's time to generate a scheduled report."""
        # Implementation depends on reporting schedule configuration
        return False
    
    async def _handle_scheduled_report(self, report: Dict[str, Any]):
        """Handle a scheduled report (save, send, etc.)."""
        # Implementation depends on reporting requirements
        pass
    
    async def _check_expired_approvals(self):
        """Check for and handle expired approval requests."""
        current_time = datetime.utcnow()
        expired_approvals = []
        
        for campaign_id, approval_entry in self.pending_approvals.items():
            expires_at = datetime.fromisoformat(approval_entry['expires_at'])
            
            if current_time > expires_at:
                expired_approvals.append(campaign_id)
        
        for campaign_id in expired_approvals:
            del self.pending_approvals[campaign_id]
            self.logger.warning(f"Approval request expired for campaign {campaign_id}")
    
    async def _process_auto_approvals(self):
        """Process content that qualifies for auto-approval."""
        # Implementation for auto-approval logic
        pass
    
    async def _update_approval_priorities(self):
        """Update priorities in the approval queue."""
        # Implementation for dynamic priority updates
        pass
    
    async def _update_campaign_statuses(self):
        """Update campaign statuses based on current state."""
        for campaign in self.active_campaigns.values():
            if campaign.get('status') == 'ready_to_post':
                # Check if all content has been posted
                approved_content = campaign.get('approved_content', [])
                posted_count = sum(1 for content in approved_content 
                                 if content.get('status') == 'posted')
                
                if posted_count == len(approved_content):
                    campaign['status'] = 'completed'
                    campaign['completed_at'] = datetime.utcnow().isoformat()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'agent_type': self.agent_type,
            'is_running': self.is_running,
            'active_campaigns': len(self.active_campaigns),
            'pending_approvals': len(self.pending_approvals),
            'posted_content_count': len(self.posted_content),
            'performance_metrics': self.performance_metrics,
            'platform_agents_count': len(self.platform_agents),
            'approval_required': self.approval_required,
            'uptime': (datetime.utcnow() - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }

