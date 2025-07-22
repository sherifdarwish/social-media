"""
Preference Learner

Machine learning component for learning user preferences and content patterns
from feedback data.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import math

from ...utils.logger import get_logger


class PreferenceLearner:
    """
    Learns user preferences from feedback data using machine learning techniques.
    
    This component:
    1. Builds preference models from user feedback
    2. Identifies content patterns that lead to positive feedback
    3. Predicts user preferences for new content
    4. Continuously updates models based on new feedback
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Preference Learner."""
        self.config = config
        self.logger = get_logger("preference_learner")
        
        # Configuration
        self.learning_rate = config.get('learning_rate', 0.1)
        self.feature_weights = config.get('feature_weights', {})
        self.min_training_samples = config.get('min_training_samples', 20)
        self.model_update_threshold = config.get('model_update_threshold', 0.05)
        
        # Model state
        self.feature_importance = {}
        self.preference_patterns = {}
        self.user_segments = {}
        self.model_performance = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'last_updated': None
        }
        
        self.logger.info("Preference Learner initialized")
    
    async def update_model(self, training_data: List[Dict[str, Any]], 
                          current_model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the preference learning model with new training data.
        
        Args:
            training_data: List of training examples with features and labels
            current_model: Current model state
            
        Returns:
            Updated model and training metrics
        """
        try:
            self.logger.info(f"Updating model with {len(training_data)} training samples")
            
            if len(training_data) < self.min_training_samples:
                return {
                    'model': current_model,
                    'metrics': {'error': 'Insufficient training data'},
                    'updated': False
                }
            
            # Extract features and labels
            features_list = [sample['features'] for sample in training_data]
            labels = [sample['label'] for sample in training_data]
            weights = [sample.get('weight', 1.0) for sample in training_data]
            
            # Update feature importance
            updated_importance = self._update_feature_importance(
                features_list, labels, weights, current_model.get('feature_importance', {})
            )
            
            # Update preference patterns
            updated_patterns = self._update_preference_patterns(
                features_list, labels, current_model.get('preference_patterns', {})
            )
            
            # Update user segments
            updated_segments = self._update_user_segments(
                training_data, current_model.get('user_segments', {})
            )
            
            # Create updated model
            updated_model = {
                'feature_importance': updated_importance,
                'preference_patterns': updated_patterns,
                'user_segments': updated_segments,
                'model_version': current_model.get('model_version', 0) + 1,
                'last_updated': datetime.utcnow().isoformat(),
                'training_samples': len(training_data)
            }
            
            # Calculate model performance
            performance_metrics = self._calculate_model_performance(
                features_list, labels, updated_model
            )
            
            updated_model['performance'] = performance_metrics
            
            return {
                'model': updated_model,
                'metrics': {
                    'training_samples': len(training_data),
                    'feature_count': len(updated_importance),
                    'pattern_count': len(updated_patterns),
                    'performance': performance_metrics
                },
                'updated': True
            }
            
        except Exception as e:
            self.logger.error(f"Error updating model: {str(e)}")
            return {
                'model': current_model,
                'metrics': {'error': str(e)},
                'updated': False
            }
    
    async def get_recommendations(self, content_context: Dict[str, Any], 
                                model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get content recommendations based on learned preferences.
        
        Args:
            content_context: Context about the content
            model: Current preference model
            
        Returns:
            Recommendations based on learned preferences
        """
        try:
            self.logger.info("Generating preference-based recommendations")
            
            if not model or not model.get('feature_importance'):
                return {
                    'content_improvements': {},
                    'style_adjustments': {},
                    'audience_targeting': {},
                    'confidence': 0.0
                }
            
            # Extract features from content context
            content_features = self._extract_content_features(content_context)
            
            # Predict preference score
            preference_score = self._predict_preference_score(content_features, model)
            
            # Generate specific recommendations
            content_improvements = self._generate_content_improvements(
                content_features, model
            )
            
            style_adjustments = self._generate_style_adjustments(
                content_features, model
            )
            
            audience_targeting = self._generate_audience_targeting(
                content_context, model
            )
            
            # Calculate confidence
            confidence = self._calculate_recommendation_confidence(
                content_features, model
            )
            
            return {
                'content_improvements': content_improvements,
                'style_adjustments': style_adjustments,
                'audience_targeting': audience_targeting,
                'preference_score': preference_score,
                'confidence': confidence,
                'model_version': model.get('model_version', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return {
                'error': str(e),
                'content_improvements': {},
                'style_adjustments': {},
                'audience_targeting': {}
            }
    
    async def predict_user_preference(self, content_features: Dict[str, Any], 
                                    model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict user preference for content with given features.
        
        Args:
            content_features: Features of the content
            model: Current preference model
            
        Returns:
            Preference prediction and confidence
        """
        try:
            if not model or not model.get('feature_importance'):
                return {
                    'preference_score': 0.5,
                    'confidence': 0.0,
                    'explanation': 'No model available'
                }
            
            # Calculate preference score
            preference_score = self._predict_preference_score(content_features, model)
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(content_features, model)
            
            # Generate explanation
            explanation = self._generate_prediction_explanation(
                content_features, model, preference_score
            )
            
            return {
                'preference_score': preference_score,
                'confidence': confidence,
                'explanation': explanation,
                'feature_contributions': self._calculate_feature_contributions(
                    content_features, model
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting preference: {str(e)}")
            return {
                'preference_score': 0.5,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _update_feature_importance(self, features_list: List[Dict[str, Any]], 
                                 labels: List[float], weights: List[float],
                                 current_importance: Dict[str, float]) -> Dict[str, float]:
        """Update feature importance based on training data."""
        feature_importance = current_importance.copy()
        
        # Calculate correlation between each feature and labels
        all_features = set()
        for features in features_list:
            all_features.update(features.keys())
        
        for feature in all_features:
            feature_values = []
            corresponding_labels = []
            corresponding_weights = []
            
            for i, features in enumerate(features_list):
                if feature in features:
                    feature_values.append(self._normalize_feature_value(features[feature]))
                    corresponding_labels.append(labels[i])
                    corresponding_weights.append(weights[i])
            
            if len(feature_values) >= 3:  # Minimum samples for correlation
                correlation = self._calculate_weighted_correlation(
                    feature_values, corresponding_labels, corresponding_weights
                )
                
                # Update importance with learning rate
                current_value = feature_importance.get(feature, 0.0)
                feature_importance[feature] = (
                    current_value * (1 - self.learning_rate) + 
                    abs(correlation) * self.learning_rate
                )
        
        return feature_importance
    
    def _update_preference_patterns(self, features_list: List[Dict[str, Any]], 
                                  labels: List[float],
                                  current_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Update preference patterns based on training data."""
        patterns = current_patterns.copy()
        
        # Group by platform
        platform_patterns = defaultdict(list)
        content_type_patterns = defaultdict(list)
        
        for i, features in enumerate(features_list):
            platform = features.get('platform', 'unknown')
            content_type = features.get('content_type', 'unknown')
            
            platform_patterns[platform].append((features, labels[i]))
            content_type_patterns[content_type].append((features, labels[i]))
        
        # Update platform patterns
        for platform, pattern_data in platform_patterns.items():
            if len(pattern_data) >= 5:  # Minimum samples for pattern
                avg_preference = statistics.mean([label for _, label in pattern_data])
                
                patterns[f'platform_{platform}'] = {
                    'average_preference': avg_preference,
                    'sample_count': len(pattern_data),
                    'preferred_features': self._identify_preferred_features(pattern_data)
                }
        
        # Update content type patterns
        for content_type, pattern_data in content_type_patterns.items():
            if len(pattern_data) >= 5:
                avg_preference = statistics.mean([label for _, label in pattern_data])
                
                patterns[f'content_type_{content_type}'] = {
                    'average_preference': avg_preference,
                    'sample_count': len(pattern_data),
                    'preferred_features': self._identify_preferred_features(pattern_data)
                }
        
        return patterns
    
    def _update_user_segments(self, training_data: List[Dict[str, Any]], 
                            current_segments: Dict[str, Any]) -> Dict[str, Any]:
        """Update user segments based on feedback patterns."""
        segments = current_segments.copy()
        
        # Simple segmentation based on feedback patterns
        high_engagement_users = []
        low_engagement_users = []
        
        user_feedback = defaultdict(list)
        
        for sample in training_data:
            user_id = sample.get('user_id', 'anonymous')
            user_feedback[user_id].append(sample['label'])
        
        for user_id, feedback_scores in user_feedback.items():
            if len(feedback_scores) >= 3:  # Minimum feedback for segmentation
                avg_score = statistics.mean(feedback_scores)
                
                if avg_score > 0.7:
                    high_engagement_users.append(user_id)
                elif avg_score < 0.3:
                    low_engagement_users.append(user_id)
        
        segments['high_engagement'] = {
            'users': high_engagement_users,
            'characteristics': self._analyze_segment_characteristics(
                [s for s in training_data if s.get('user_id') in high_engagement_users]
            )
        }
        
        segments['low_engagement'] = {
            'users': low_engagement_users,
            'characteristics': self._analyze_segment_characteristics(
                [s for s in training_data if s.get('user_id') in low_engagement_users]
            )
        }
        
        return segments
    
    def _predict_preference_score(self, content_features: Dict[str, Any], 
                                model: Dict[str, Any]) -> float:
        """Predict preference score for content features."""
        feature_importance = model.get('feature_importance', {})
        
        if not feature_importance:
            return 0.5  # Default neutral score
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for feature, value in content_features.items():
            if feature in feature_importance:
                importance = feature_importance[feature]
                normalized_value = self._normalize_feature_value(value)
                
                weighted_score += normalized_value * importance
                total_weight += importance
        
        if total_weight > 0:
            return max(0.0, min(1.0, weighted_score / total_weight))
        else:
            return 0.5
    
    def _generate_content_improvements(self, content_features: Dict[str, Any], 
                                     model: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content improvement recommendations."""
        improvements = {}
        feature_importance = model.get('feature_importance', {})
        patterns = model.get('preference_patterns', {})
        
        # Check content length
        if 'content_length' in content_features:
            current_length = content_features['content_length']
            optimal_length = self._get_optimal_content_length(patterns)
            
            if optimal_length and abs(current_length - optimal_length) > 50:
                improvements['content_length'] = {
                    'current': current_length,
                    'recommended': optimal_length,
                    'reason': 'Based on successful content patterns',
                    'priority': feature_importance.get('content_length', 0.5)
                }
        
        # Check hashtag usage
        if 'hashtag_count' in content_features:
            current_hashtags = content_features['hashtag_count']
            optimal_hashtags = self._get_optimal_hashtag_count(patterns)
            
            if optimal_hashtags and current_hashtags != optimal_hashtags:
                improvements['hashtag_usage'] = {
                    'current': current_hashtags,
                    'recommended': optimal_hashtags,
                    'reason': 'Optimize hashtag count for better engagement',
                    'priority': feature_importance.get('hashtag_count', 0.5)
                }
        
        # Check call to action
        if not content_features.get('has_call_to_action', False):
            cta_importance = feature_importance.get('has_call_to_action', 0.0)
            if cta_importance > 0.6:
                improvements['call_to_action'] = {
                    'current': False,
                    'recommended': True,
                    'reason': 'Content with call-to-action performs better',
                    'priority': cta_importance
                }
        
        return improvements
    
    def _generate_style_adjustments(self, content_features: Dict[str, Any], 
                                  model: Dict[str, Any]) -> Dict[str, Any]:
        """Generate style adjustment recommendations."""
        adjustments = {}
        patterns = model.get('preference_patterns', {})
        
        platform = content_features.get('platform', '')
        content_type = content_features.get('content_type', '')
        
        # Platform-specific adjustments
        platform_pattern_key = f'platform_{platform}'
        if platform_pattern_key in patterns:
            platform_prefs = patterns[platform_pattern_key]['preferred_features']
            
            for feature, preferred_value in platform_prefs.items():
                current_value = content_features.get(feature)
                if current_value != preferred_value:
                    adjustments[f'{platform}_{feature}'] = {
                        'current': current_value,
                        'recommended': preferred_value,
                        'reason': f'Optimized for {platform} platform',
                        'priority': 0.7
                    }
        
        # Content type adjustments
        content_type_pattern_key = f'content_type_{content_type}'
        if content_type_pattern_key in patterns:
            content_prefs = patterns[content_type_pattern_key]['preferred_features']
            
            for feature, preferred_value in content_prefs.items():
                current_value = content_features.get(feature)
                if current_value != preferred_value:
                    adjustments[f'{content_type}_{feature}'] = {
                        'current': current_value,
                        'recommended': preferred_value,
                        'reason': f'Optimized for {content_type} content',
                        'priority': 0.6
                    }
        
        return adjustments
    
    def _generate_audience_targeting(self, content_context: Dict[str, Any], 
                                   model: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audience targeting recommendations."""
        targeting = {}
        segments = model.get('user_segments', {})
        
        # Recommend targeting based on user segments
        if 'high_engagement' in segments:
            high_engagement_chars = segments['high_engagement']['characteristics']
            
            targeting['high_engagement_segment'] = {
                'recommended': True,
                'characteristics': high_engagement_chars,
                'reason': 'Target users with high engagement patterns',
                'priority': 0.8
            }
        
        # Platform-specific targeting
        platform = content_context.get('platform', '')
        if platform:
            targeting[f'{platform}_optimization'] = {
                'recommended': True,
                'reason': f'Optimize content specifically for {platform} audience',
                'priority': 0.6
            }
        
        return targeting
    
    def _calculate_recommendation_confidence(self, content_features: Dict[str, Any], 
                                           model: Dict[str, Any]) -> float:
        """Calculate confidence in recommendations."""
        feature_importance = model.get('feature_importance', {})
        
        if not feature_importance:
            return 0.0
        
        # Calculate confidence based on feature coverage
        covered_features = sum(1 for feature in content_features.keys() 
                             if feature in feature_importance)
        total_important_features = len(feature_importance)
        
        coverage_confidence = covered_features / total_important_features if total_important_features > 0 else 0
        
        # Adjust based on model performance
        model_performance = model.get('performance', {}).get('accuracy', 0.0)
        
        # Adjust based on training data size
        training_samples = model.get('training_samples', 0)
        data_confidence = min(training_samples / 100, 1.0)  # Full confidence at 100+ samples
        
        return (coverage_confidence + model_performance + data_confidence) / 3
    
    def _calculate_prediction_confidence(self, content_features: Dict[str, Any], 
                                       model: Dict[str, Any]) -> float:
        """Calculate confidence in preference prediction."""
        return self._calculate_recommendation_confidence(content_features, model)
    
    def _generate_prediction_explanation(self, content_features: Dict[str, Any], 
                                       model: Dict[str, Any], 
                                       preference_score: float) -> str:
        """Generate explanation for preference prediction."""
        feature_importance = model.get('feature_importance', {})
        
        if not feature_importance:
            return "No model data available for explanation"
        
        # Find most influential features
        feature_contributions = self._calculate_feature_contributions(content_features, model)
        top_features = sorted(feature_contributions.items(), 
                            key=lambda x: abs(x[1]), reverse=True)[:3]
        
        explanation_parts = []
        
        if preference_score > 0.7:
            explanation_parts.append("High preference predicted because:")
        elif preference_score < 0.3:
            explanation_parts.append("Low preference predicted because:")
        else:
            explanation_parts.append("Neutral preference predicted because:")
        
        for feature, contribution in top_features:
            if contribution > 0:
                explanation_parts.append(f"• {feature} contributes positively")
            else:
                explanation_parts.append(f"• {feature} contributes negatively")
        
        return " ".join(explanation_parts)
    
    def _calculate_feature_contributions(self, content_features: Dict[str, Any], 
                                       model: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how each feature contributes to the prediction."""
        feature_importance = model.get('feature_importance', {})
        contributions = {}
        
        for feature, value in content_features.items():
            if feature in feature_importance:
                importance = feature_importance[feature]
                normalized_value = self._normalize_feature_value(value)
                
                # Contribution is importance * (normalized_value - 0.5)
                # Positive if above average, negative if below
                contributions[feature] = importance * (normalized_value - 0.5)
        
        return contributions
    
    def _calculate_model_performance(self, features_list: List[Dict[str, Any]], 
                                   labels: List[float], 
                                   model: Dict[str, Any]) -> Dict[str, float]:
        """Calculate model performance metrics."""
        if len(features_list) < 5:
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0}
        
        # Make predictions
        predictions = []
        for features in features_list:
            pred_score = self._predict_preference_score(features, model)
            predictions.append(1 if pred_score > 0.5 else 0)
        
        # Convert labels to binary
        binary_labels = [1 if label > 0.5 else 0 for label in labels]
        
        # Calculate metrics
        correct = sum(1 for i in range(len(predictions)) 
                     if predictions[i] == binary_labels[i])
        accuracy = correct / len(predictions)
        
        # Calculate precision and recall
        true_positives = sum(1 for i in range(len(predictions)) 
                           if predictions[i] == 1 and binary_labels[i] == 1)
        false_positives = sum(1 for i in range(len(predictions)) 
                            if predictions[i] == 1 and binary_labels[i] == 0)
        false_negatives = sum(1 for i in range(len(predictions)) 
                            if predictions[i] == 0 and binary_labels[i] == 1)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall
        }
    
    def _normalize_feature_value(self, value: Any) -> float:
        """Normalize feature value to 0-1 range."""
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            # Simple normalization - in practice, this would be more sophisticated
            return max(0.0, min(1.0, value / 100))  # Assuming max value of 100
        elif isinstance(value, str):
            # String features - simple hash-based normalization
            return (hash(value) % 100) / 100
        else:
            return 0.5  # Default for unknown types
    
    def _calculate_weighted_correlation(self, values: List[float], 
                                      labels: List[float], 
                                      weights: List[float]) -> float:
        """Calculate weighted correlation between values and labels."""
        if len(values) < 2:
            return 0.0
        
        # Calculate weighted means
        total_weight = sum(weights)
        weighted_mean_values = sum(v * w for v, w in zip(values, weights)) / total_weight
        weighted_mean_labels = sum(l * w for l, w in zip(labels, weights)) / total_weight
        
        # Calculate weighted covariance and variances
        covariance = sum(w * (v - weighted_mean_values) * (l - weighted_mean_labels) 
                        for v, l, w in zip(values, labels, weights)) / total_weight
        
        var_values = sum(w * (v - weighted_mean_values) ** 2 
                        for v, w in zip(values, weights)) / total_weight
        var_labels = sum(w * (l - weighted_mean_labels) ** 2 
                        for l, w in zip(labels, weights)) / total_weight
        
        # Calculate correlation
        if var_values > 0 and var_labels > 0:
            correlation = covariance / math.sqrt(var_values * var_labels)
            return max(-1.0, min(1.0, correlation))
        else:
            return 0.0
    
    def _identify_preferred_features(self, pattern_data: List[Tuple[Dict[str, Any], float]]) -> Dict[str, Any]:
        """Identify preferred feature values from pattern data."""
        # Separate high-preference and low-preference samples
        high_pref_samples = [features for features, label in pattern_data if label > 0.7]
        low_pref_samples = [features for features, label in pattern_data if label < 0.3]
        
        preferred_features = {}
        
        if high_pref_samples:
            # Find common features in high-preference samples
            all_features = set()
            for features in high_pref_samples:
                all_features.update(features.keys())
            
            for feature in all_features:
                high_values = [features.get(feature) for features in high_pref_samples 
                             if feature in features]
                
                if high_values:
                    if isinstance(high_values[0], bool):
                        # For boolean features, use majority vote
                        preferred_features[feature] = sum(high_values) > len(high_values) / 2
                    elif isinstance(high_values[0], (int, float)):
                        # For numeric features, use mean
                        preferred_features[feature] = statistics.mean(high_values)
                    elif isinstance(high_values[0], str):
                        # For string features, use most common
                        preferred_features[feature] = Counter(high_values).most_common(1)[0][0]
        
        return preferred_features
    
    def _analyze_segment_characteristics(self, segment_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze characteristics of a user segment."""
        if not segment_data:
            return {}
        
        characteristics = {}
        
        # Analyze feature distributions
        all_features = set()
        for sample in segment_data:
            if 'features' in sample:
                all_features.update(sample['features'].keys())
        
        for feature in all_features:
            feature_values = [sample['features'].get(feature) 
                            for sample in segment_data 
                            if 'features' in sample and feature in sample['features']]
            
            if feature_values:
                if isinstance(feature_values[0], bool):
                    characteristics[feature] = {
                        'type': 'boolean',
                        'true_ratio': sum(feature_values) / len(feature_values)
                    }
                elif isinstance(feature_values[0], (int, float)):
                    characteristics[feature] = {
                        'type': 'numeric',
                        'mean': statistics.mean(feature_values),
                        'median': statistics.median(feature_values)
                    }
                elif isinstance(feature_values[0], str):
                    characteristics[feature] = {
                        'type': 'categorical',
                        'most_common': Counter(feature_values).most_common(3)
                    }
        
        return characteristics
    
    def _get_optimal_content_length(self, patterns: Dict[str, Any]) -> Optional[int]:
        """Get optimal content length from patterns."""
        length_data = []
        
        for pattern_key, pattern_info in patterns.items():
            if 'preferred_features' in pattern_info:
                content_length = pattern_info['preferred_features'].get('content_length')
                if content_length and isinstance(content_length, (int, float)):
                    length_data.append(content_length)
        
        if length_data:
            return int(statistics.median(length_data))
        
        return None
    
    def _get_optimal_hashtag_count(self, patterns: Dict[str, Any]) -> Optional[int]:
        """Get optimal hashtag count from patterns."""
        hashtag_data = []
        
        for pattern_key, pattern_info in patterns.items():
            if 'preferred_features' in pattern_info:
                hashtag_count = pattern_info['preferred_features'].get('hashtag_count')
                if hashtag_count and isinstance(hashtag_count, (int, float)):
                    hashtag_data.append(hashtag_count)
        
        if hashtag_data:
            return int(statistics.median(hashtag_data))
        
        return None
    
    def _extract_content_features(self, content_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from content context."""
        features = {}
        
        # Basic features
        features['platform'] = content_context.get('platform', '')
        features['content_type'] = content_context.get('content_type', '')
        features['content_length'] = len(content_context.get('content_text', ''))
        features['has_hashtags'] = bool(content_context.get('hashtags'))
        features['hashtag_count'] = len(content_context.get('hashtags', []))
        features['has_call_to_action'] = bool(content_context.get('call_to_action'))
        features['engagement_score'] = content_context.get('engagement_score', 0)
        
        # Time-based features
        if 'timestamp' in content_context:
            try:
                dt = datetime.fromisoformat(content_context['timestamp'])
                features['hour_of_day'] = dt.hour
                features['day_of_week'] = dt.weekday()
            except:
                pass
        
        return features

