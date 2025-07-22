"""
Content Optimizer

Component responsible for optimizing content based on feedback analysis
and performance data.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import json

from ...utils.logger import get_logger


class ContentOptimizer:
    """
    Optimizes content based on feedback analysis and performance data.
    
    This component:
    1. Analyzes content performance patterns
    2. Generates optimization recommendations
    3. Provides platform-specific optimizations
    4. Suggests content improvements based on feedback
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Content Optimizer."""
        self.config = config
        self.logger = get_logger("content_optimizer")
        
        # Configuration
        self.optimization_threshold = config.get('optimization_threshold', 0.7)
        self.min_sample_size = config.get('min_sample_size', 10)
        self.platform_weights = config.get('platform_weights', {})
        
        # Platform-specific configurations
        self.platform_configs = {
            'twitter': {
                'max_length': 280,
                'optimal_hashtags': 2,
                'optimal_time': [9, 12, 15, 18]  # Hours
            },
            'facebook': {
                'max_length': 2000,
                'optimal_hashtags': 3,
                'optimal_time': [9, 13, 15]
            },
            'instagram': {
                'max_length': 2200,
                'optimal_hashtags': 11,
                'optimal_time': [11, 13, 17, 19]
            },
            'linkedin': {
                'max_length': 1300,
                'optimal_hashtags': 5,
                'optimal_time': [8, 12, 17]
            },
            'tiktok': {
                'max_length': 150,
                'optimal_hashtags': 4,
                'optimal_time': [18, 19, 20, 21]
            }
        }
        
        # Content type configurations
        self.content_type_configs = {
            'educational': {
                'preferred_length': 'medium',
                'call_to_action_importance': 0.8,
                'hashtag_strategy': 'informative'
            },
            'promotional': {
                'preferred_length': 'short',
                'call_to_action_importance': 0.9,
                'hashtag_strategy': 'branded'
            },
            'entertaining': {
                'preferred_length': 'short',
                'call_to_action_importance': 0.6,
                'hashtag_strategy': 'trending'
            },
            'inspirational': {
                'preferred_length': 'medium',
                'call_to_action_importance': 0.7,
                'hashtag_strategy': 'motivational'
            }
        }
        
        self.logger.info("Content Optimizer initialized")
    
    async def optimize_content(self, content_context: Dict[str, Any], 
                             analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize content based on context and analysis results.
        
        Args:
            content_context: Context about the content to optimize
            analysis_results: Results from feedback analysis
            
        Returns:
            Optimization recommendations
        """
        try:
            self.logger.info("Optimizing content based on analysis results")
            
            platform = content_context.get('platform', '')
            content_type = content_context.get('content_type', '')
            
            # Generate platform-specific optimizations
            platform_optimizations = self._generate_platform_optimizations(
                content_context, platform
            )
            
            # Generate content type optimizations
            content_type_optimizations = self._generate_content_type_optimizations(
                content_context, content_type
            )
            
            # Generate performance-based optimizations
            performance_optimizations = self._generate_performance_optimizations(
                content_context, analysis_results
            )
            
            # Generate timing optimizations
            timing_optimizations = self._generate_timing_optimizations(
                content_context, analysis_results
            )
            
            # Combine all optimizations
            combined_optimizations = self._combine_optimizations([
                platform_optimizations,
                content_type_optimizations,
                performance_optimizations,
                timing_optimizations
            ])
            
            return {
                'content_improvements': combined_optimizations.get('content_improvements', {}),
                'platform_optimizations': platform_optimizations,
                'content_type_optimizations': content_type_optimizations,
                'performance_optimizations': performance_optimizations,
                'timing_optimizations': timing_optimizations,
                'priority_recommendations': self._prioritize_optimizations(combined_optimizations),
                'optimization_score': self._calculate_optimization_score(combined_optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing content: {str(e)}")
            return {
                'error': str(e),
                'content_improvements': {}
            }
    
    async def generate_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate general optimization recommendations based on analysis results.
        
        Args:
            analysis_results: Results from feedback analysis
            
        Returns:
            General optimization recommendations
        """
        try:
            self.logger.info("Generating optimization recommendations")
            
            recommendations = {}
            
            # Analyze aggregate patterns
            if 'aggregate_analysis' in analysis_results:
                aggregate_recs = self._analyze_aggregate_patterns(
                    analysis_results['aggregate_analysis']
                )
                recommendations.update(aggregate_recs)
            
            # Analyze platform patterns
            if 'patterns' in analysis_results:
                pattern_recs = self._analyze_pattern_recommendations(
                    analysis_results['patterns']
                )
                recommendations.update(pattern_recs)
            
            # Analyze performance metrics
            if 'metrics' in analysis_results:
                metric_recs = self._analyze_metric_recommendations(
                    analysis_results['metrics']
                )
                recommendations.update(metric_recs)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return {'error': str(e)}
    
    async def generate_immediate_recommendations(self, feedback_data: Dict[str, Any], 
                                               analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate immediate recommendations based on specific feedback.
        
        Args:
            feedback_data: Specific feedback data
            analysis_result: Analysis result for the feedback
            
        Returns:
            Immediate recommendations
        """
        try:
            recommendations = {}
            
            feedback_type = feedback_data.get('feedback_type', '')
            urgency = analysis_result.get('urgency_level', 'medium')
            issues = analysis_result.get('content_issues', [])
            
            # High-priority recommendations for negative feedback
            if feedback_type in ['reject', 'thumbs_down'] or urgency == 'high':
                recommendations['immediate_actions'] = self._generate_immediate_actions(
                    feedback_data, issues
                )
            
            # Content-specific recommendations
            if issues:
                recommendations['content_fixes'] = self._generate_content_fixes(issues)
            
            # Platform-specific immediate recommendations
            platform = feedback_data.get('platform', '')
            if platform:
                recommendations['platform_fixes'] = self._generate_platform_fixes(
                    platform, feedback_data
                )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating immediate recommendations: {str(e)}")
            return {'error': str(e)}
    
    def _generate_platform_optimizations(self, content_context: Dict[str, Any], 
                                       platform: str) -> Dict[str, Any]:
        """Generate platform-specific optimizations."""
        optimizations = {}
        
        if platform not in self.platform_configs:
            return optimizations
        
        platform_config = self.platform_configs[platform]
        content_text = content_context.get('content_text', '')
        hashtags = content_context.get('hashtags', [])
        
        # Length optimization
        current_length = len(content_text)
        max_length = platform_config['max_length']
        
        if current_length > max_length:
            optimizations['length_reduction'] = {
                'current_length': current_length,
                'max_length': max_length,
                'reduction_needed': current_length - max_length,
                'priority': 0.9,
                'action': 'Reduce content length to fit platform limits'
            }
        elif current_length < max_length * 0.5:
            optimizations['length_expansion'] = {
                'current_length': current_length,
                'suggested_length': int(max_length * 0.7),
                'priority': 0.6,
                'action': 'Consider expanding content for better engagement'
            }
        
        # Hashtag optimization
        current_hashtag_count = len(hashtags)
        optimal_hashtags = platform_config['optimal_hashtags']
        
        if current_hashtag_count != optimal_hashtags:
            optimizations['hashtag_optimization'] = {
                'current_count': current_hashtag_count,
                'optimal_count': optimal_hashtags,
                'priority': 0.7,
                'action': f'Adjust hashtag count to {optimal_hashtags} for optimal {platform} performance'
            }
        
        # Timing optimization
        optimal_times = platform_config['optimal_time']
        optimizations['timing_suggestion'] = {
            'optimal_hours': optimal_times,
            'priority': 0.8,
            'action': f'Post during optimal hours for {platform}: {optimal_times}'
        }
        
        return optimizations
    
    def _generate_content_type_optimizations(self, content_context: Dict[str, Any], 
                                           content_type: str) -> Dict[str, Any]:
        """Generate content type specific optimizations."""
        optimizations = {}
        
        if content_type not in self.content_type_configs:
            return optimizations
        
        content_config = self.content_type_configs[content_type]
        
        # Call to action optimization
        has_cta = content_context.get('has_call_to_action', False)
        cta_importance = content_config['call_to_action_importance']
        
        if not has_cta and cta_importance > 0.7:
            optimizations['call_to_action'] = {
                'current': has_cta,
                'recommended': True,
                'importance': cta_importance,
                'priority': cta_importance,
                'action': f'Add call-to-action for {content_type} content'
            }
        
        # Length optimization based on content type
        preferred_length = content_config['preferred_length']
        content_length = len(content_context.get('content_text', ''))
        
        length_recommendations = {
            'short': (50, 150),
            'medium': (150, 300),
            'long': (300, 500)
        }
        
        if preferred_length in length_recommendations:
            min_len, max_len = length_recommendations[preferred_length]
            
            if content_length < min_len:
                optimizations['content_expansion'] = {
                    'current_length': content_length,
                    'recommended_range': (min_len, max_len),
                    'priority': 0.6,
                    'action': f'Expand content for {content_type} type'
                }
            elif content_length > max_len:
                optimizations['content_reduction'] = {
                    'current_length': content_length,
                    'recommended_range': (min_len, max_len),
                    'priority': 0.7,
                    'action': f'Reduce content length for {content_type} type'
                }
        
        # Hashtag strategy optimization
        hashtag_strategy = content_config['hashtag_strategy']
        optimizations['hashtag_strategy'] = {
            'recommended_strategy': hashtag_strategy,
            'priority': 0.5,
            'action': f'Use {hashtag_strategy} hashtag strategy for {content_type} content'
        }
        
        return optimizations
    
    def _generate_performance_optimizations(self, content_context: Dict[str, Any], 
                                          analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimizations based on performance analysis."""
        optimizations = {}
        
        # Check if we have performance data
        if 'metrics' not in analysis_results:
            return optimizations
        
        metrics = analysis_results['metrics']
        
        # Approval rate optimization
        approval_rate = metrics.get('approval_rate', 0.0)
        if approval_rate < self.optimization_threshold:
            optimizations['approval_improvement'] = {
                'current_rate': approval_rate,
                'target_rate': self.optimization_threshold,
                'priority': 0.9,
                'action': 'Focus on improving content quality and relevance'
            }
        
        # Engagement optimization
        avg_engagement = metrics.get('average_engagement_score', 0.0)
        if avg_engagement < 50:  # Assuming 0-100 scale
            optimizations['engagement_improvement'] = {
                'current_engagement': avg_engagement,
                'target_engagement': 70,
                'priority': 0.8,
                'action': 'Improve content engagement through better hooks and calls-to-action'
            }
        
        # Platform distribution optimization
        platform_distribution = metrics.get('platform_distribution', {})
        if platform_distribution:
            underperforming_platforms = [
                platform for platform, count in platform_distribution.items()
                if count < 5  # Minimum threshold
            ]
            
            if underperforming_platforms:
                optimizations['platform_diversification'] = {
                    'underperforming_platforms': underperforming_platforms,
                    'priority': 0.6,
                    'action': 'Increase content creation for underperforming platforms'
                }
        
        return optimizations
    
    def _generate_timing_optimizations(self, content_context: Dict[str, Any], 
                                     analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate timing-based optimizations."""
        optimizations = {}
        
        # Check for temporal patterns in analysis results
        if 'patterns' in analysis_results and 'temporal_patterns' in analysis_results['patterns']:
            temporal_patterns = analysis_results['patterns']['temporal_patterns']
            
            peak_hours = temporal_patterns.get('peak_feedback_hours', [])
            if peak_hours:
                optimizations['optimal_posting_times'] = {
                    'peak_hours': [hour_data['hour'] for hour_data in peak_hours],
                    'priority': 0.7,
                    'action': 'Schedule posts during peak engagement hours'
                }
        
        # Platform-specific timing
        platform = content_context.get('platform', '')
        if platform in self.platform_configs:
            optimal_times = self.platform_configs[platform]['optimal_time']
            optimizations['platform_timing'] = {
                'platform': platform,
                'optimal_hours': optimal_times,
                'priority': 0.6,
                'action': f'Post during optimal {platform} hours: {optimal_times}'
            }
        
        return optimizations
    
    def _combine_optimizations(self, optimization_lists: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple optimization dictionaries."""
        combined = {
            'content_improvements': {},
            'platform_optimizations': {},
            'performance_optimizations': {},
            'timing_optimizations': {}
        }
        
        for optimizations in optimization_lists:
            for category, items in optimizations.items():
                if category not in combined:
                    combined[category] = {}
                
                if isinstance(items, dict):
                    combined[category].update(items)
        
        return combined
    
    def _prioritize_optimizations(self, optimizations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize optimizations by importance and impact."""
        all_optimizations = []
        
        for category, items in optimizations.items():
            if isinstance(items, dict):
                for opt_id, opt_data in items.items():
                    if isinstance(opt_data, dict) and 'priority' in opt_data:
                        all_optimizations.append({
                            'id': opt_id,
                            'category': category,
                            'data': opt_data,
                            'priority': opt_data['priority']
                        })
        
        # Sort by priority (highest first)
        return sorted(all_optimizations, key=lambda x: x['priority'], reverse=True)
    
    def _calculate_optimization_score(self, optimizations: Dict[str, Any]) -> float:
        """Calculate overall optimization score."""
        total_score = 0.0
        total_weight = 0.0
        
        for category, items in optimizations.items():
            if isinstance(items, dict):
                for opt_data in items.values():
                    if isinstance(opt_data, dict) and 'priority' in opt_data:
                        priority = opt_data['priority']
                        total_score += priority
                        total_weight += 1.0
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _analyze_aggregate_patterns(self, aggregate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze aggregate patterns for recommendations."""
        recommendations = {}
        
        # Approval rate analysis
        approval_rate = aggregate_analysis.get('approval_rate', 0.0)
        if approval_rate < 0.6:
            recommendations['improve_approval_rate'] = {
                'current_rate': approval_rate,
                'target_rate': 0.7,
                'priority': 0.9,
                'action': 'Focus on content quality and audience alignment'
            }
        
        # Sentiment analysis
        avg_sentiment = aggregate_analysis.get('average_sentiment', 0.5)
        if avg_sentiment < 0.4:
            recommendations['improve_sentiment'] = {
                'current_sentiment': avg_sentiment,
                'target_sentiment': 0.6,
                'priority': 0.8,
                'action': 'Improve content tone and messaging'
            }
        
        # Platform distribution analysis
        platform_distribution = aggregate_analysis.get('platform_distribution', {})
        if platform_distribution:
            total_content = sum(platform_distribution.values())
            uneven_distribution = any(
                count / total_content < 0.1 for count in platform_distribution.values()
            )
            
            if uneven_distribution:
                recommendations['balance_platforms'] = {
                    'current_distribution': platform_distribution,
                    'priority': 0.6,
                    'action': 'Balance content distribution across platforms'
                }
        
        return recommendations
    
    def _analyze_pattern_recommendations(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns for recommendations."""
        recommendations = {}
        
        # Recurring issues analysis
        recurring_issues = patterns.get('recurring_issues', [])
        if recurring_issues:
            top_issue = recurring_issues[0]  # Highest frequency issue
            
            recommendations['address_recurring_issue'] = {
                'issue': top_issue['issue'],
                'frequency': top_issue['frequency'],
                'priority': 0.9,
                'action': f"Address recurring issue: {top_issue['issue']}"
            }
        
        # Platform patterns analysis
        platform_patterns = patterns.get('platform_patterns', {})
        for platform, pattern_data in platform_patterns.items():
            approval_rate = pattern_data.get('approval_rate', 0.0)
            
            if approval_rate < 0.5:
                recommendations[f'improve_{platform}_performance'] = {
                    'platform': platform,
                    'current_rate': approval_rate,
                    'priority': 0.7,
                    'action': f'Improve content strategy for {platform}'
                }
        
        return recommendations
    
    def _analyze_metric_recommendations(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metrics for recommendations."""
        recommendations = {}
        
        # Engagement analysis
        avg_engagement = metrics.get('average_engagement_score', 0.0)
        if avg_engagement < 50:
            recommendations['boost_engagement'] = {
                'current_engagement': avg_engagement,
                'target_engagement': 70,
                'priority': 0.8,
                'action': 'Implement engagement-boosting strategies'
            }
        
        # Comment rate analysis
        comment_rate = metrics.get('has_comments_rate', 0.0)
        if comment_rate > 0.3:  # High comment rate might indicate issues
            recommendations['review_content_quality'] = {
                'comment_rate': comment_rate,
                'priority': 0.7,
                'action': 'Review content quality - high comment rate may indicate issues'
            }
        
        return recommendations
    
    def _generate_immediate_actions(self, feedback_data: Dict[str, Any], 
                                  issues: List[str]) -> List[Dict[str, Any]]:
        """Generate immediate actions for negative feedback."""
        actions = []
        
        feedback_type = feedback_data.get('feedback_type', '')
        
        if feedback_type == 'reject':
            actions.append({
                'action': 'Review and revise content immediately',
                'priority': 1.0,
                'urgency': 'high'
            })
        
        if 'quality' in issues:
            actions.append({
                'action': 'Improve content quality and proofreading',
                'priority': 0.9,
                'urgency': 'high'
            })
        
        if 'relevance' in issues:
            actions.append({
                'action': 'Ensure content aligns with target audience',
                'priority': 0.8,
                'urgency': 'medium'
            })
        
        if 'platform' in issues:
            actions.append({
                'action': 'Optimize content for platform requirements',
                'priority': 0.7,
                'urgency': 'medium'
            })
        
        return actions
    
    def _generate_content_fixes(self, issues: List[str]) -> Dict[str, Dict[str, Any]]:
        """Generate specific content fixes for identified issues."""
        fixes = {}
        
        fix_mapping = {
            'length': {
                'action': 'Adjust content length',
                'priority': 0.7,
                'details': 'Review content length guidelines for the platform'
            },
            'tone': {
                'action': 'Adjust content tone',
                'priority': 0.8,
                'details': 'Ensure tone matches brand voice and audience expectations'
            },
            'relevance': {
                'action': 'Improve content relevance',
                'priority': 0.9,
                'details': 'Align content with target audience interests and needs'
            },
            'quality': {
                'action': 'Improve content quality',
                'priority': 0.9,
                'details': 'Review grammar, spelling, and overall content quality'
            },
            'timing': {
                'action': 'Optimize posting timing',
                'priority': 0.6,
                'details': 'Schedule posts during optimal engagement hours'
            }
        }
        
        for issue in issues:
            if issue in fix_mapping:
                fixes[issue] = fix_mapping[issue]
        
        return fixes
    
    def _generate_platform_fixes(self, platform: str, 
                               feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-specific fixes."""
        fixes = {}
        
        if platform in self.platform_configs:
            platform_config = self.platform_configs[platform]
            
            # Check content length
            content_length = len(feedback_data.get('content_text', ''))
            max_length = platform_config['max_length']
            
            if content_length > max_length:
                fixes['length_violation'] = {
                    'action': f'Reduce content to {max_length} characters for {platform}',
                    'priority': 0.9,
                    'current_length': content_length,
                    'max_length': max_length
                }
            
            # Check hashtag count
            hashtag_count = len(feedback_data.get('hashtags', []))
            optimal_hashtags = platform_config['optimal_hashtags']
            
            if abs(hashtag_count - optimal_hashtags) > 2:
                fixes['hashtag_optimization'] = {
                    'action': f'Adjust hashtags to ~{optimal_hashtags} for {platform}',
                    'priority': 0.6,
                    'current_count': hashtag_count,
                    'optimal_count': optimal_hashtags
                }
        
        return fixes

