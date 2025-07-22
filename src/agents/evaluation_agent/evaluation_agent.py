"""
Evaluation Agent

Main agent responsible for analyzing user feedback and improving content generation
through machine learning and feedback loops.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid

from ..base_agent import BaseAgent
from .feedback_analyzer import FeedbackAnalyzer
from .preference_learner import PreferenceLearner
from .content_optimizer import ContentOptimizer
from ...utils.logger import get_logger


class EvaluationAgent(BaseAgent):
    """
    Evaluation Agent for analyzing feedback and improving content generation.
    
    This agent:
    1. Collects and analyzes user feedback on content suggestions
    2. Learns user preferences and patterns
    3. Provides recommendations to improve content generation
    4. Optimizes content based on feedback patterns
    5. Tracks performance metrics and trends
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Evaluation Agent."""
        super().__init__(config)
        self.agent_type = "evaluation"
        self.logger = get_logger(f"{self.agent_type}_agent")
        
        # Initialize components
        self.feedback_analyzer = FeedbackAnalyzer(config.get('feedback_analyzer', {}))
        self.preference_learner = PreferenceLearner(config.get('preference_learner', {}))
        self.content_optimizer = ContentOptimizer(config.get('content_optimizer', {}))
        
        # Configuration
        self.evaluation_config = config.get('evaluation', {})
        self.learning_rate = self.evaluation_config.get('learning_rate', 0.1)
        self.feedback_threshold = self.evaluation_config.get('feedback_threshold', 5)
        self.analysis_interval = self.evaluation_config.get('analysis_interval', 3600)  # 1 hour
        self.min_feedback_count = self.evaluation_config.get('min_feedback_count', 10)
        
        # State tracking
        self.feedback_queue = []
        self.analysis_results = {}
        self.preference_model = {}
        self.optimization_recommendations = {}
        self.performance_metrics = {
            'total_feedback_processed': 0,
            'approval_rate_trend': [],
            'preference_accuracy': 0.0,
            'optimization_impact': 0.0
        }
        
        self.logger.info(f"Evaluation Agent initialized with config: {self.evaluation_config}")
    
    async def start(self):
        """Start the evaluation agent."""
        self.logger.info("Starting Evaluation Agent...")
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self._feedback_processing_loop())
        asyncio.create_task(self._periodic_analysis_loop())
        asyncio.create_task(self._preference_learning_loop())
        
        self.logger.info("Evaluation Agent started successfully")
    
    async def stop(self):
        """Stop the evaluation agent."""
        self.logger.info("Stopping Evaluation Agent...")
        self.is_running = False
        
        # Save current state
        await self._save_state()
        
        self.logger.info("Evaluation Agent stopped")
    
    async def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback on content suggestions.
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            Processing result and recommendations
        """
        try:
            self.logger.info(f"Processing feedback: {feedback_data.get('feedback_type', 'unknown')}")
            
            # Validate feedback data
            if not self._validate_feedback(feedback_data):
                raise ValueError("Invalid feedback data")
            
            # Add to feedback queue
            feedback_entry = {
                'id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'data': feedback_data,
                'processed': False
            }
            
            self.feedback_queue.append(feedback_entry)
            
            # Immediate analysis for high-priority feedback
            if self._is_high_priority_feedback(feedback_data):
                analysis_result = await self._analyze_feedback_immediate(feedback_data)
                
                # Generate immediate recommendations
                recommendations = await self._generate_immediate_recommendations(
                    feedback_data, analysis_result
                )
                
                return {
                    'success': True,
                    'feedback_id': feedback_entry['id'],
                    'immediate_analysis': analysis_result,
                    'recommendations': recommendations,
                    'processing_time': (datetime.utcnow() - datetime.fromisoformat(feedback_entry['timestamp'])).total_seconds()
                }
            
            return {
                'success': True,
                'feedback_id': feedback_entry['id'],
                'queued_for_processing': True,
                'queue_position': len(self.feedback_queue)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing feedback: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_content_recommendations(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendations for improving content based on learned preferences.
        
        Args:
            content_context: Context about the content to be improved
            
        Returns:
            Recommendations for content optimization
        """
        try:
            self.logger.info("Generating content recommendations")
            
            # Analyze content context
            context_analysis = await self._analyze_content_context(content_context)
            
            # Get preference-based recommendations
            preference_recommendations = await self.preference_learner.get_recommendations(
                content_context, self.preference_model
            )
            
            # Get optimization recommendations
            optimization_recommendations = await self.content_optimizer.optimize_content(
                content_context, self.analysis_results
            )
            
            # Combine recommendations
            combined_recommendations = self._combine_recommendations(
                preference_recommendations,
                optimization_recommendations,
                context_analysis
            )
            
            return {
                'success': True,
                'recommendations': combined_recommendations,
                'confidence_score': self._calculate_confidence_score(combined_recommendations),
                'context_analysis': context_analysis,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics and analytics."""
        try:
            # Calculate current metrics
            current_metrics = await self._calculate_current_metrics()
            
            # Get trend analysis
            trend_analysis = await self._analyze_performance_trends()
            
            # Get feedback statistics
            feedback_stats = await self._get_feedback_statistics()
            
            return {
                'success': True,
                'metrics': {
                    **self.performance_metrics,
                    **current_metrics
                },
                'trends': trend_analysis,
                'feedback_statistics': feedback_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_preference_model(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update the preference learning model with a batch of feedback.
        
        Args:
            feedback_batch: List of feedback entries
            
        Returns:
            Update result and model performance
        """
        try:
            self.logger.info(f"Updating preference model with {len(feedback_batch)} feedback entries")
            
            # Prepare training data
            training_data = await self._prepare_training_data(feedback_batch)
            
            # Update preference model
            update_result = await self.preference_learner.update_model(
                training_data, self.preference_model
            )
            
            # Validate model performance
            validation_result = await self._validate_model_performance(update_result['model'])
            
            # Update internal model if validation passes
            if validation_result['is_valid']:
                self.preference_model = update_result['model']
                self.performance_metrics['preference_accuracy'] = validation_result['accuracy']
            
            return {
                'success': True,
                'model_updated': validation_result['is_valid'],
                'performance': validation_result,
                'training_metrics': update_result['metrics'],
                'feedback_count': len(feedback_batch)
            }
            
        except Exception as e:
            self.logger.error(f"Error updating preference model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _feedback_processing_loop(self):
        """Background loop for processing feedback queue."""
        while self.is_running:
            try:
                if len(self.feedback_queue) >= self.feedback_threshold:
                    await self._process_feedback_batch()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in feedback processing loop: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _periodic_analysis_loop(self):
        """Background loop for periodic analysis."""
        while self.is_running:
            try:
                await self._perform_periodic_analysis()
                await asyncio.sleep(self.analysis_interval)
                
            except Exception as e:
                self.logger.error(f"Error in periodic analysis loop: {str(e)}")
                await asyncio.sleep(self.analysis_interval)
    
    async def _preference_learning_loop(self):
        """Background loop for preference learning updates."""
        while self.is_running:
            try:
                if self.performance_metrics['total_feedback_processed'] >= self.min_feedback_count:
                    await self._update_preference_learning()
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error in preference learning loop: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _process_feedback_batch(self):
        """Process a batch of feedback from the queue."""
        try:
            # Get unprocessed feedback
            unprocessed = [f for f in self.feedback_queue if not f['processed']]
            
            if not unprocessed:
                return
            
            self.logger.info(f"Processing batch of {len(unprocessed)} feedback entries")
            
            # Analyze feedback batch
            batch_analysis = await self.feedback_analyzer.analyze_batch(
                [f['data'] for f in unprocessed]
            )
            
            # Update analysis results
            self.analysis_results.update(batch_analysis)
            
            # Mark as processed
            for feedback in unprocessed:
                feedback['processed'] = True
                feedback['processed_at'] = datetime.utcnow().isoformat()
            
            # Update metrics
            self.performance_metrics['total_feedback_processed'] += len(unprocessed)
            
            # Clean up old feedback
            await self._cleanup_old_feedback()
            
            self.logger.info(f"Processed {len(unprocessed)} feedback entries successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing feedback batch: {str(e)}")
    
    async def _perform_periodic_analysis(self):
        """Perform periodic analysis of feedback and performance."""
        try:
            self.logger.info("Performing periodic analysis")
            
            # Analyze recent feedback trends
            trend_analysis = await self.feedback_analyzer.analyze_trends(
                self.feedback_queue, 
                time_window=timedelta(hours=24)
            )
            
            # Update performance metrics
            if trend_analysis.get('approval_rate'):
                self.performance_metrics['approval_rate_trend'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'rate': trend_analysis['approval_rate']
                })
            
            # Generate optimization recommendations
            optimization_recs = await self.content_optimizer.generate_recommendations(
                self.analysis_results
            )
            
            self.optimization_recommendations.update(optimization_recs)
            
            self.logger.info("Periodic analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error in periodic analysis: {str(e)}")
    
    async def _update_preference_learning(self):
        """Update preference learning model."""
        try:
            self.logger.info("Updating preference learning model")
            
            # Get recent feedback for training
            recent_feedback = [
                f for f in self.feedback_queue 
                if f['processed'] and 
                datetime.fromisoformat(f['timestamp']) > datetime.utcnow() - timedelta(days=7)
            ]
            
            if len(recent_feedback) >= self.min_feedback_count:
                await self.update_preference_model([f['data'] for f in recent_feedback])
            
        except Exception as e:
            self.logger.error(f"Error updating preference learning: {str(e)}")
    
    def _validate_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Validate feedback data structure."""
        required_fields = ['content_suggestion_id', 'feedback_type']
        return all(field in feedback_data for field in required_fields)
    
    def _is_high_priority_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Check if feedback requires immediate processing."""
        high_priority_types = ['reject', 'critical_issue']
        return feedback_data.get('feedback_type') in high_priority_types
    
    async def _analyze_feedback_immediate(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform immediate analysis of high-priority feedback."""
        return await self.feedback_analyzer.analyze_single(feedback_data)
    
    async def _generate_immediate_recommendations(self, feedback_data: Dict[str, Any], 
                                                analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate immediate recommendations based on feedback."""
        return await self.content_optimizer.generate_immediate_recommendations(
            feedback_data, analysis_result
        )
    
    async def _analyze_content_context(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content context for recommendation generation."""
        return {
            'platform': content_context.get('platform'),
            'content_type': content_context.get('content_type'),
            'target_audience': content_context.get('target_audience'),
            'business_domain': content_context.get('business_domain'),
            'historical_performance': await self._get_historical_performance(content_context)
        }
    
    def _combine_recommendations(self, preference_recs: Dict[str, Any], 
                               optimization_recs: Dict[str, Any],
                               context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine different types of recommendations."""
        return {
            'content_improvements': {
                **preference_recs.get('content_improvements', {}),
                **optimization_recs.get('content_improvements', {})
            },
            'style_adjustments': {
                **preference_recs.get('style_adjustments', {}),
                **optimization_recs.get('style_adjustments', {})
            },
            'platform_optimizations': optimization_recs.get('platform_optimizations', {}),
            'audience_targeting': preference_recs.get('audience_targeting', {}),
            'priority_actions': self._prioritize_recommendations(
                preference_recs, optimization_recs, context_analysis
            )
        }
    
    def _calculate_confidence_score(self, recommendations: Dict[str, Any]) -> float:
        """Calculate confidence score for recommendations."""
        # Simple confidence calculation based on data availability
        base_confidence = 0.5
        
        # Increase confidence based on feedback volume
        feedback_factor = min(self.performance_metrics['total_feedback_processed'] / 100, 0.3)
        
        # Increase confidence based on model accuracy
        accuracy_factor = self.performance_metrics.get('preference_accuracy', 0) * 0.2
        
        return min(base_confidence + feedback_factor + accuracy_factor, 1.0)
    
    def _prioritize_recommendations(self, preference_recs: Dict[str, Any], 
                                  optimization_recs: Dict[str, Any],
                                  context_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on impact and confidence."""
        all_recommendations = []
        
        # Add preference-based recommendations
        for category, recs in preference_recs.items():
            if isinstance(recs, dict):
                for rec_id, rec_data in recs.items():
                    all_recommendations.append({
                        'id': rec_id,
                        'category': category,
                        'type': 'preference',
                        'data': rec_data,
                        'priority': rec_data.get('priority', 0.5)
                    })
        
        # Add optimization recommendations
        for category, recs in optimization_recs.items():
            if isinstance(recs, dict):
                for rec_id, rec_data in recs.items():
                    all_recommendations.append({
                        'id': rec_id,
                        'category': category,
                        'type': 'optimization',
                        'data': rec_data,
                        'priority': rec_data.get('priority', 0.5)
                    })
        
        # Sort by priority
        return sorted(all_recommendations, key=lambda x: x['priority'], reverse=True)
    
    async def _calculate_current_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics."""
        # Calculate approval rate from recent feedback
        recent_feedback = [
            f for f in self.feedback_queue 
            if datetime.fromisoformat(f['timestamp']) > datetime.utcnow() - timedelta(hours=24)
        ]
        
        if recent_feedback:
            approved = sum(1 for f in recent_feedback 
                         if f['data'].get('feedback_type') == 'approve')
            approval_rate = approved / len(recent_feedback)
        else:
            approval_rate = 0.0
        
        return {
            'current_approval_rate': approval_rate,
            'recent_feedback_count': len(recent_feedback),
            'queue_size': len([f for f in self.feedback_queue if not f['processed']])
        }
    
    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        trends = self.performance_metrics.get('approval_rate_trend', [])
        
        if len(trends) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_rates = [t['rate'] for t in trends[-10:]]  # Last 10 data points
        
        if len(recent_rates) >= 2:
            trend_direction = 'improving' if recent_rates[-1] > recent_rates[0] else 'declining'
            trend_magnitude = abs(recent_rates[-1] - recent_rates[0])
        else:
            trend_direction = 'stable'
            trend_magnitude = 0.0
        
        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'data_points': len(trends),
            'latest_rate': recent_rates[-1] if recent_rates else 0.0
        }
    
    async def _get_feedback_statistics(self) -> Dict[str, Any]:
        """Get detailed feedback statistics."""
        feedback_types = {}
        platforms = {}
        content_types = {}
        
        for feedback in self.feedback_queue:
            data = feedback['data']
            
            # Count feedback types
            feedback_type = data.get('feedback_type', 'unknown')
            feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
            
            # Count platforms (if available in content context)
            platform = data.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
            
            # Count content types
            content_type = data.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return {
            'feedback_types': feedback_types,
            'platforms': platforms,
            'content_types': content_types,
            'total_feedback': len(self.feedback_queue)
        }
    
    async def _prepare_training_data(self, feedback_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare training data for preference learning."""
        training_data = []
        
        for feedback in feedback_batch:
            training_entry = {
                'features': self._extract_content_features(feedback),
                'label': self._convert_feedback_to_label(feedback),
                'weight': self._calculate_feedback_weight(feedback)
            }
            training_data.append(training_entry)
        
        return training_data
    
    def _extract_content_features(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from content for machine learning."""
        return {
            'platform': feedback.get('platform', ''),
            'content_type': feedback.get('content_type', ''),
            'content_length': len(feedback.get('content_text', '')),
            'has_hashtags': bool(feedback.get('hashtags')),
            'has_call_to_action': bool(feedback.get('call_to_action')),
            'engagement_score': feedback.get('engagement_score', 0),
            'time_of_day': datetime.fromisoformat(feedback.get('timestamp', datetime.utcnow().isoformat())).hour
        }
    
    def _convert_feedback_to_label(self, feedback: Dict[str, Any]) -> float:
        """Convert feedback to numerical label for training."""
        feedback_type = feedback.get('feedback_type', '')
        
        label_mapping = {
            'approve': 1.0,
            'thumbs_up': 0.8,
            'thumbs_down': 0.2,
            'reject': 0.0
        }
        
        return label_mapping.get(feedback_type, 0.5)
    
    def _calculate_feedback_weight(self, feedback: Dict[str, Any]) -> float:
        """Calculate weight for feedback in training."""
        # More recent feedback gets higher weight
        timestamp = datetime.fromisoformat(feedback.get('timestamp', datetime.utcnow().isoformat()))
        age_days = (datetime.utcnow() - timestamp).days
        
        # Exponential decay with 7-day half-life
        weight = 2 ** (-age_days / 7)
        
        # Boost weight for explicit feedback (approve/reject)
        if feedback.get('feedback_type') in ['approve', 'reject']:
            weight *= 1.5
        
        return weight
    
    async def _validate_model_performance(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model performance before updating."""
        # Simple validation - in practice, this would be more sophisticated
        accuracy = model.get('accuracy', 0.0)
        
        return {
            'is_valid': accuracy > 0.6,  # Minimum 60% accuracy
            'accuracy': accuracy,
            'validation_method': 'simple_threshold'
        }
    
    async def _get_historical_performance(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical performance for similar content."""
        # Filter feedback for similar content
        similar_feedback = []
        
        for feedback in self.feedback_queue:
            data = feedback['data']
            if (data.get('platform') == content_context.get('platform') and
                data.get('content_type') == content_context.get('content_type')):
                similar_feedback.append(data)
        
        if not similar_feedback:
            return {'performance': 'no_data'}
        
        # Calculate performance metrics
        approved = sum(1 for f in similar_feedback if f.get('feedback_type') == 'approve')
        approval_rate = approved / len(similar_feedback)
        
        avg_engagement = sum(f.get('engagement_score', 0) for f in similar_feedback) / len(similar_feedback)
        
        return {
            'approval_rate': approval_rate,
            'average_engagement': avg_engagement,
            'sample_size': len(similar_feedback)
        }
    
    async def _cleanup_old_feedback(self):
        """Clean up old feedback entries to manage memory."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        self.feedback_queue = [
            f for f in self.feedback_queue
            if datetime.fromisoformat(f['timestamp']) > cutoff_date
        ]
    
    async def _save_state(self):
        """Save current agent state."""
        state = {
            'preference_model': self.preference_model,
            'analysis_results': self.analysis_results,
            'performance_metrics': self.performance_metrics,
            'optimization_recommendations': self.optimization_recommendations
        }
        
        # In a real implementation, this would save to persistent storage
        self.logger.info("Agent state saved")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'agent_type': self.agent_type,
            'is_running': self.is_running,
            'feedback_queue_size': len(self.feedback_queue),
            'unprocessed_feedback': len([f for f in self.feedback_queue if not f['processed']]),
            'total_feedback_processed': self.performance_metrics['total_feedback_processed'],
            'preference_model_accuracy': self.performance_metrics.get('preference_accuracy', 0.0),
            'last_analysis': self.analysis_results.get('last_updated', 'never'),
            'uptime': (datetime.utcnow() - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }

