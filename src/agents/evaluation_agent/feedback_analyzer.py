"""
Feedback Analyzer

Component responsible for analyzing user feedback patterns and extracting insights
for content improvement.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import json

from ...utils.logger import get_logger


class FeedbackAnalyzer:
    """
    Analyzes user feedback to extract patterns and insights.
    
    This component:
    1. Analyzes individual feedback entries
    2. Identifies patterns in feedback data
    3. Calculates performance metrics
    4. Generates insights for content improvement
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Feedback Analyzer."""
        self.config = config
        self.logger = get_logger("feedback_analyzer")
        
        # Configuration
        self.sentiment_threshold = config.get('sentiment_threshold', 0.6)
        self.pattern_min_occurrences = config.get('pattern_min_occurrences', 3)
        self.trend_window_hours = config.get('trend_window_hours', 24)
        
        # Analysis cache
        self.analysis_cache = {}
        self.pattern_cache = {}
        
        self.logger.info("Feedback Analyzer initialized")
    
    async def analyze_single(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single feedback entry.
        
        Args:
            feedback_data: Individual feedback entry
            
        Returns:
            Analysis results for the feedback
        """
        try:
            analysis = {
                'feedback_id': feedback_data.get('id', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'feedback_type': feedback_data.get('feedback_type'),
                'sentiment_score': self._calculate_sentiment_score(feedback_data),
                'urgency_level': self._assess_urgency(feedback_data),
                'content_issues': self._identify_content_issues(feedback_data),
                'improvement_suggestions': self._generate_improvement_suggestions(feedback_data)
            }
            
            # Add platform-specific analysis
            if feedback_data.get('platform'):
                analysis['platform_analysis'] = self._analyze_platform_specific(feedback_data)
            
            # Add content type analysis
            if feedback_data.get('content_type'):
                analysis['content_type_analysis'] = self._analyze_content_type_specific(feedback_data)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing single feedback: {str(e)}")
            return {
                'error': str(e),
                'feedback_id': feedback_data.get('id', 'unknown')
            }
    
    async def analyze_batch(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a batch of feedback entries.
        
        Args:
            feedback_batch: List of feedback entries
            
        Returns:
            Batch analysis results
        """
        try:
            self.logger.info(f"Analyzing batch of {len(feedback_batch)} feedback entries")
            
            # Individual analyses
            individual_analyses = []
            for feedback in feedback_batch:
                analysis = await self.analyze_single(feedback)
                individual_analyses.append(analysis)
            
            # Aggregate analysis
            aggregate_analysis = self._perform_aggregate_analysis(individual_analyses, feedback_batch)
            
            # Pattern detection
            patterns = self._detect_patterns(feedback_batch)
            
            # Performance metrics
            metrics = self._calculate_batch_metrics(feedback_batch)
            
            return {
                'batch_size': len(feedback_batch),
                'individual_analyses': individual_analyses,
                'aggregate_analysis': aggregate_analysis,
                'patterns': patterns,
                'metrics': metrics,
                'analyzed_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing feedback batch: {str(e)}")
            return {
                'error': str(e),
                'batch_size': len(feedback_batch) if feedback_batch else 0
            }
    
    async def analyze_trends(self, feedback_history: List[Dict[str, Any]], 
                           time_window: timedelta = None) -> Dict[str, Any]:
        """
        Analyze trends in feedback over time.
        
        Args:
            feedback_history: Historical feedback data
            time_window: Time window for trend analysis
            
        Returns:
            Trend analysis results
        """
        try:
            if time_window is None:
                time_window = timedelta(hours=self.trend_window_hours)
            
            # Filter feedback within time window
            cutoff_time = datetime.utcnow() - time_window
            recent_feedback = [
                f for f in feedback_history
                if datetime.fromisoformat(f.get('timestamp', datetime.utcnow().isoformat())) > cutoff_time
            ]
            
            if not recent_feedback:
                return {'trend': 'no_data', 'message': 'No feedback in specified time window'}
            
            # Extract feedback data
            feedback_data = [f.get('data', f) for f in recent_feedback]
            
            # Calculate trend metrics
            approval_trend = self._calculate_approval_trend(feedback_data)
            engagement_trend = self._calculate_engagement_trend(feedback_data)
            platform_trends = self._calculate_platform_trends(feedback_data)
            content_type_trends = self._calculate_content_type_trends(feedback_data)
            
            # Identify emerging patterns
            emerging_patterns = self._identify_emerging_patterns(feedback_data)
            
            return {
                'time_window_hours': time_window.total_seconds() / 3600,
                'feedback_count': len(recent_feedback),
                'approval_trend': approval_trend,
                'engagement_trend': engagement_trend,
                'platform_trends': platform_trends,
                'content_type_trends': content_type_trends,
                'emerging_patterns': emerging_patterns,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {
                'error': str(e),
                'time_window_hours': time_window.total_seconds() / 3600 if time_window else 0
            }
    
    def _calculate_sentiment_score(self, feedback_data: Dict[str, Any]) -> float:
        """Calculate sentiment score for feedback."""
        feedback_type = feedback_data.get('feedback_type', '')
        
        # Basic sentiment mapping
        sentiment_mapping = {
            'approve': 1.0,
            'thumbs_up': 0.8,
            'thumbs_down': 0.2,
            'reject': 0.0
        }
        
        base_score = sentiment_mapping.get(feedback_type, 0.5)
        
        # Adjust based on feedback score if available
        if 'feedback_score' in feedback_data:
            score_adjustment = (feedback_data['feedback_score'] - 3) / 10  # Normalize 1-5 scale
            base_score = max(0, min(1, base_score + score_adjustment))
        
        # Adjust based on comments sentiment (simplified)
        if feedback_data.get('feedback_comments'):
            comment_sentiment = self._analyze_comment_sentiment(feedback_data['feedback_comments'])
            base_score = (base_score + comment_sentiment) / 2
        
        return base_score
    
    def _assess_urgency(self, feedback_data: Dict[str, Any]) -> str:
        """Assess urgency level of feedback."""
        feedback_type = feedback_data.get('feedback_type', '')
        
        # High urgency feedback types
        if feedback_type in ['reject', 'critical_issue']:
            return 'high'
        
        # Medium urgency for negative feedback with comments
        if feedback_type in ['thumbs_down'] and feedback_data.get('feedback_comments'):
            return 'medium'
        
        # Low urgency for positive feedback
        if feedback_type in ['approve', 'thumbs_up']:
            return 'low'
        
        return 'medium'
    
    def _identify_content_issues(self, feedback_data: Dict[str, Any]) -> List[str]:
        """Identify potential content issues from feedback."""
        issues = []
        
        feedback_type = feedback_data.get('feedback_type', '')
        comments = feedback_data.get('feedback_comments', '').lower()
        
        # Identify issues based on feedback type
        if feedback_type in ['reject', 'thumbs_down']:
            issues.append('negative_feedback')
        
        # Identify issues from comments (simplified keyword matching)
        issue_keywords = {
            'length': ['too long', 'too short', 'length'],
            'tone': ['tone', 'voice', 'style'],
            'relevance': ['irrelevant', 'off-topic', 'not relevant'],
            'quality': ['poor quality', 'low quality', 'bad'],
            'timing': ['timing', 'schedule', 'when'],
            'platform': ['platform', 'format', 'doesn\'t fit']
        }
        
        for issue_type, keywords in issue_keywords.items():
            if any(keyword in comments for keyword in keywords):
                issues.append(issue_type)
        
        return issues
    
    def _generate_improvement_suggestions(self, feedback_data: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on feedback."""
        suggestions = []
        
        issues = self._identify_content_issues(feedback_data)
        feedback_type = feedback_data.get('feedback_type', '')
        
        # Generate suggestions based on identified issues
        suggestion_mapping = {
            'length': 'Consider adjusting content length',
            'tone': 'Review brand voice and tone guidelines',
            'relevance': 'Ensure content aligns with target audience interests',
            'quality': 'Improve content quality and proofreading',
            'timing': 'Review posting schedule and timing',
            'platform': 'Optimize content for specific platform requirements'
        }
        
        for issue in issues:
            if issue in suggestion_mapping:
                suggestions.append(suggestion_mapping[issue])
        
        # Add general suggestions based on feedback type
        if feedback_type == 'reject':
            suggestions.append('Review content strategy and guidelines')
        elif feedback_type == 'thumbs_down':
            suggestions.append('Analyze similar successful content for patterns')
        
        return suggestions
    
    def _analyze_platform_specific(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze platform-specific feedback patterns."""
        platform = feedback_data.get('platform', '')
        
        platform_analysis = {
            'platform': platform,
            'feedback_type': feedback_data.get('feedback_type'),
            'platform_specific_issues': []
        }
        
        # Platform-specific issue detection
        platform_issues = {
            'twitter': ['character_limit', 'hashtag_usage'],
            'instagram': ['visual_quality', 'hashtag_strategy'],
            'linkedin': ['professional_tone', 'industry_relevance'],
            'facebook': ['engagement_format', 'community_guidelines'],
            'tiktok': ['video_format', 'trending_content']
        }
        
        if platform in platform_issues:
            # Check for platform-specific issues (simplified)
            comments = feedback_data.get('feedback_comments', '').lower()
            for issue in platform_issues[platform]:
                if any(keyword in comments for keyword in issue.split('_')):
                    platform_analysis['platform_specific_issues'].append(issue)
        
        return platform_analysis
    
    def _analyze_content_type_specific(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content type specific feedback patterns."""
        content_type = feedback_data.get('content_type', '')
        
        return {
            'content_type': content_type,
            'feedback_type': feedback_data.get('feedback_type'),
            'type_specific_metrics': self._calculate_content_type_metrics(feedback_data)
        }
    
    def _calculate_content_type_metrics(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics specific to content type."""
        content_type = feedback_data.get('content_type', '')
        
        # Basic metrics calculation
        metrics = {
            'engagement_score': feedback_data.get('engagement_score', 0),
            'character_count': len(feedback_data.get('content_text', '')),
            'has_call_to_action': bool(feedback_data.get('call_to_action')),
            'hashtag_count': len(feedback_data.get('hashtags', []))
        }
        
        # Content type specific metrics
        if content_type == 'educational':
            metrics['educational_value'] = self._assess_educational_value(feedback_data)
        elif content_type == 'promotional':
            metrics['promotional_effectiveness'] = self._assess_promotional_effectiveness(feedback_data)
        elif content_type == 'entertaining':
            metrics['entertainment_value'] = self._assess_entertainment_value(feedback_data)
        
        return metrics
    
    def _perform_aggregate_analysis(self, individual_analyses: List[Dict[str, Any]], 
                                  feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform aggregate analysis on batch of feedback."""
        if not individual_analyses:
            return {}
        
        # Calculate aggregate metrics
        sentiment_scores = [a.get('sentiment_score', 0.5) for a in individual_analyses]
        urgency_levels = [a.get('urgency_level', 'medium') for a in individual_analyses]
        
        # Count feedback types
        feedback_types = Counter(fb.get('feedback_type', 'unknown') for fb in feedback_batch)
        
        # Count platforms
        platforms = Counter(fb.get('platform', 'unknown') for fb in feedback_batch)
        
        # Count content types
        content_types = Counter(fb.get('content_type', 'unknown') for fb in feedback_batch)
        
        # Calculate approval rate
        total_feedback = len(feedback_batch)
        approved = sum(1 for fb in feedback_batch if fb.get('feedback_type') == 'approve')
        approval_rate = approved / total_feedback if total_feedback > 0 else 0
        
        return {
            'average_sentiment': statistics.mean(sentiment_scores) if sentiment_scores else 0,
            'sentiment_distribution': {
                'positive': sum(1 for s in sentiment_scores if s > 0.6),
                'neutral': sum(1 for s in sentiment_scores if 0.4 <= s <= 0.6),
                'negative': sum(1 for s in sentiment_scores if s < 0.4)
            },
            'urgency_distribution': dict(Counter(urgency_levels)),
            'feedback_type_distribution': dict(feedback_types),
            'platform_distribution': dict(platforms),
            'content_type_distribution': dict(content_types),
            'approval_rate': approval_rate,
            'total_feedback': total_feedback
        }
    
    def _detect_patterns(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in feedback batch."""
        patterns = {
            'recurring_issues': self._find_recurring_issues(feedback_batch),
            'platform_patterns': self._find_platform_patterns(feedback_batch),
            'content_type_patterns': self._find_content_type_patterns(feedback_batch),
            'temporal_patterns': self._find_temporal_patterns(feedback_batch)
        }
        
        return patterns
    
    def _find_recurring_issues(self, feedback_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find recurring issues in feedback."""
        issue_counts = defaultdict(int)
        
        for feedback in feedback_batch:
            comments = feedback.get('feedback_comments', '').lower()
            
            # Simple keyword-based issue detection
            issue_keywords = {
                'length_issues': ['too long', 'too short'],
                'tone_issues': ['wrong tone', 'inappropriate'],
                'timing_issues': ['bad timing', 'wrong time'],
                'quality_issues': ['poor quality', 'low quality']
            }
            
            for issue_type, keywords in issue_keywords.items():
                if any(keyword in comments for keyword in keywords):
                    issue_counts[issue_type] += 1
        
        # Return issues that occur frequently enough
        recurring_issues = [
            {'issue': issue, 'count': count, 'frequency': count / len(feedback_batch)}
            for issue, count in issue_counts.items()
            if count >= self.pattern_min_occurrences
        ]
        
        return sorted(recurring_issues, key=lambda x: x['count'], reverse=True)
    
    def _find_platform_patterns(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find platform-specific patterns."""
        platform_feedback = defaultdict(list)
        
        for feedback in feedback_batch:
            platform = feedback.get('platform', 'unknown')
            platform_feedback[platform].append(feedback)
        
        platform_patterns = {}
        for platform, feedback_list in platform_feedback.items():
            if len(feedback_list) >= self.pattern_min_occurrences:
                approval_rate = sum(1 for f in feedback_list if f.get('feedback_type') == 'approve') / len(feedback_list)
                
                platform_patterns[platform] = {
                    'feedback_count': len(feedback_list),
                    'approval_rate': approval_rate,
                    'dominant_feedback_type': Counter(f.get('feedback_type') for f in feedback_list).most_common(1)[0][0]
                }
        
        return platform_patterns
    
    def _find_content_type_patterns(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find content type specific patterns."""
        content_type_feedback = defaultdict(list)
        
        for feedback in feedback_batch:
            content_type = feedback.get('content_type', 'unknown')
            content_type_feedback[content_type].append(feedback)
        
        content_patterns = {}
        for content_type, feedback_list in content_type_feedback.items():
            if len(feedback_list) >= self.pattern_min_occurrences:
                approval_rate = sum(1 for f in feedback_list if f.get('feedback_type') == 'approve') / len(feedback_list)
                
                content_patterns[content_type] = {
                    'feedback_count': len(feedback_list),
                    'approval_rate': approval_rate,
                    'average_engagement': statistics.mean([f.get('engagement_score', 0) for f in feedback_list])
                }
        
        return content_patterns
    
    def _find_temporal_patterns(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find temporal patterns in feedback."""
        hourly_feedback = defaultdict(list)
        
        for feedback in feedback_batch:
            timestamp = feedback.get('timestamp', datetime.utcnow().isoformat())
            try:
                dt = datetime.fromisoformat(timestamp)
                hour = dt.hour
                hourly_feedback[hour].append(feedback)
            except:
                continue
        
        # Find peak feedback hours
        peak_hours = sorted(hourly_feedback.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        
        return {
            'peak_feedback_hours': [{'hour': hour, 'count': len(feedback_list)} for hour, feedback_list in peak_hours],
            'total_hours_with_feedback': len(hourly_feedback)
        }
    
    def _calculate_batch_metrics(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for feedback batch."""
        if not feedback_batch:
            return {}
        
        total_feedback = len(feedback_batch)
        
        # Count feedback types
        feedback_type_counts = Counter(fb.get('feedback_type', 'unknown') for fb in feedback_batch)
        
        # Calculate rates
        approval_rate = feedback_type_counts.get('approve', 0) / total_feedback
        rejection_rate = feedback_type_counts.get('reject', 0) / total_feedback
        positive_rate = (feedback_type_counts.get('approve', 0) + feedback_type_counts.get('thumbs_up', 0)) / total_feedback
        
        # Calculate engagement metrics
        engagement_scores = [fb.get('engagement_score', 0) for fb in feedback_batch if fb.get('engagement_score')]
        avg_engagement = statistics.mean(engagement_scores) if engagement_scores else 0
        
        return {
            'total_feedback': total_feedback,
            'approval_rate': approval_rate,
            'rejection_rate': rejection_rate,
            'positive_feedback_rate': positive_rate,
            'average_engagement_score': avg_engagement,
            'feedback_type_distribution': dict(feedback_type_counts),
            'has_comments_rate': sum(1 for fb in feedback_batch if fb.get('feedback_comments')) / total_feedback
        }
    
    def _calculate_approval_trend(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate approval rate trend."""
        if not feedback_data:
            return {'trend': 'no_data'}
        
        # Sort by timestamp
        sorted_feedback = sorted(feedback_data, key=lambda x: x.get('timestamp', ''))
        
        # Calculate approval rate over time (simplified)
        total_feedback = len(sorted_feedback)
        approved = sum(1 for f in sorted_feedback if f.get('feedback_type') == 'approve')
        current_rate = approved / total_feedback
        
        # Simple trend calculation (would be more sophisticated in practice)
        first_half = sorted_feedback[:total_feedback//2]
        second_half = sorted_feedback[total_feedback//2:]
        
        if first_half and second_half:
            first_half_rate = sum(1 for f in first_half if f.get('feedback_type') == 'approve') / len(first_half)
            second_half_rate = sum(1 for f in second_half if f.get('feedback_type') == 'approve') / len(second_half)
            
            trend_direction = 'improving' if second_half_rate > first_half_rate else 'declining'
            trend_magnitude = abs(second_half_rate - first_half_rate)
        else:
            trend_direction = 'stable'
            trend_magnitude = 0.0
        
        return {
            'current_rate': current_rate,
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'sample_size': total_feedback
        }
    
    def _calculate_engagement_trend(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement score trend."""
        engagement_scores = [f.get('engagement_score', 0) for f in feedback_data if f.get('engagement_score')]
        
        if not engagement_scores:
            return {'trend': 'no_data'}
        
        avg_engagement = statistics.mean(engagement_scores)
        
        # Simple trend calculation
        if len(engagement_scores) >= 4:
            first_half = engagement_scores[:len(engagement_scores)//2]
            second_half = engagement_scores[len(engagement_scores)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            trend_direction = 'improving' if second_avg > first_avg else 'declining'
            trend_magnitude = abs(second_avg - first_avg)
        else:
            trend_direction = 'stable'
            trend_magnitude = 0.0
        
        return {
            'average_engagement': avg_engagement,
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'sample_size': len(engagement_scores)
        }
    
    def _calculate_platform_trends(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate platform-specific trends."""
        platform_metrics = defaultdict(list)
        
        for feedback in feedback_data:
            platform = feedback.get('platform', 'unknown')
            if feedback.get('feedback_type') == 'approve':
                platform_metrics[platform].append(1)
            else:
                platform_metrics[platform].append(0)
        
        platform_trends = {}
        for platform, scores in platform_metrics.items():
            if len(scores) >= 3:  # Minimum data points for trend
                approval_rate = statistics.mean(scores)
                platform_trends[platform] = {
                    'approval_rate': approval_rate,
                    'feedback_count': len(scores),
                    'performance': 'good' if approval_rate > 0.7 else 'needs_improvement'
                }
        
        return platform_trends
    
    def _calculate_content_type_trends(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate content type specific trends."""
        content_type_metrics = defaultdict(list)
        
        for feedback in feedback_data:
            content_type = feedback.get('content_type', 'unknown')
            if feedback.get('feedback_type') == 'approve':
                content_type_metrics[content_type].append(1)
            else:
                content_type_metrics[content_type].append(0)
        
        content_trends = {}
        for content_type, scores in content_type_metrics.items():
            if len(scores) >= 3:
                approval_rate = statistics.mean(scores)
                content_trends[content_type] = {
                    'approval_rate': approval_rate,
                    'feedback_count': len(scores),
                    'performance': 'good' if approval_rate > 0.7 else 'needs_improvement'
                }
        
        return content_trends
    
    def _identify_emerging_patterns(self, feedback_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify emerging patterns in recent feedback."""
        patterns = []
        
        # Look for sudden changes in feedback patterns
        if len(feedback_data) >= 10:
            recent_feedback = feedback_data[-5:]  # Last 5 feedback entries
            earlier_feedback = feedback_data[-10:-5]  # Previous 5 feedback entries
            
            # Compare approval rates
            recent_approval = sum(1 for f in recent_feedback if f.get('feedback_type') == 'approve') / len(recent_feedback)
            earlier_approval = sum(1 for f in earlier_feedback if f.get('feedback_type') == 'approve') / len(earlier_feedback)
            
            if abs(recent_approval - earlier_approval) > 0.3:  # Significant change
                patterns.append({
                    'type': 'approval_rate_change',
                    'description': f"Approval rate changed from {earlier_approval:.2f} to {recent_approval:.2f}",
                    'magnitude': abs(recent_approval - earlier_approval),
                    'direction': 'improvement' if recent_approval > earlier_approval else 'decline'
                })
        
        return patterns
    
    def _analyze_comment_sentiment(self, comment: str) -> float:
        """Analyze sentiment of feedback comment (simplified)."""
        positive_words = ['good', 'great', 'excellent', 'love', 'like', 'amazing', 'perfect']
        negative_words = ['bad', 'terrible', 'hate', 'dislike', 'awful', 'poor', 'wrong']
        
        comment_lower = comment.lower()
        
        positive_count = sum(1 for word in positive_words if word in comment_lower)
        negative_count = sum(1 for word in negative_words if word in comment_lower)
        
        if positive_count > negative_count:
            return 0.7
        elif negative_count > positive_count:
            return 0.3
        else:
            return 0.5
    
    def _assess_educational_value(self, feedback_data: Dict[str, Any]) -> float:
        """Assess educational value of content (simplified)."""
        # Simple assessment based on content characteristics
        content_text = feedback_data.get('content_text', '').lower()
        
        educational_indicators = ['learn', 'tip', 'how to', 'guide', 'tutorial', 'fact', 'did you know']
        
        score = sum(1 for indicator in educational_indicators if indicator in content_text)
        return min(score / len(educational_indicators), 1.0)
    
    def _assess_promotional_effectiveness(self, feedback_data: Dict[str, Any]) -> float:
        """Assess promotional effectiveness (simplified)."""
        content_text = feedback_data.get('content_text', '').lower()
        
        promotional_indicators = ['buy', 'sale', 'discount', 'offer', 'deal', 'limited time', 'call to action']
        
        score = sum(1 for indicator in promotional_indicators if indicator in content_text)
        
        # Adjust based on feedback type
        if feedback_data.get('feedback_type') == 'approve':
            score *= 1.5
        elif feedback_data.get('feedback_type') == 'reject':
            score *= 0.5
        
        return min(score / len(promotional_indicators), 1.0)
    
    def _assess_entertainment_value(self, feedback_data: Dict[str, Any]) -> float:
        """Assess entertainment value (simplified)."""
        content_text = feedback_data.get('content_text', '').lower()
        
        entertainment_indicators = ['fun', 'funny', 'humor', 'joke', 'entertaining', 'amusing', 'lol']
        
        score = sum(1 for indicator in entertainment_indicators if indicator in content_text)
        return min(score / len(entertainment_indicators), 1.0)

