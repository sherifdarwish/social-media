"""
Content Suggestion Model

Database model for storing content suggestions and their metadata.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class ContentSuggestion(db.Model):
    """Model for content suggestions."""
    
    __tablename__ = 'content_suggestions'
    
    id = db.Column(db.String(36), primary_key=True)
    briefing_id = db.Column(db.String(36), nullable=False)
    business_profile_id = db.Column(db.String(36), nullable=False)
    
    # Content details
    content_type = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    full_text = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.Text)  # JSON string
    call_to_action = db.Column(db.Text)
    
    # Template and theme info
    template_type = db.Column(db.String(50))
    template_format = db.Column(db.String(50))
    theme_name = db.Column(db.String(100))
    theme_description = db.Column(db.Text)
    
    # Status and feedback
    status = db.Column(db.String(50), default='pending_review')
    approval_status = db.Column(db.String(50))
    feedback_score = db.Column(db.Integer)
    feedback_comments = db.Column(db.Text)
    
    # Metadata
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generation_time = db.Column(db.Float)
    creativity_level = db.Column(db.String(20))
    batch_id = db.Column(db.String(36))
    
    # Engagement estimation
    engagement_score = db.Column(db.Integer)
    estimated_reach = db.Column(db.String(50))
    estimated_interactions = db.Column(db.String(50))
    
    # Platform optimization
    character_count = db.Column(db.Integer)
    within_limits = db.Column(db.Boolean, default=True)
    platform_optimized = db.Column(db.Boolean, default=True)
    
    def __init__(self, **kwargs):
        """Initialize content suggestion."""
        super(ContentSuggestion, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'briefing_id': self.briefing_id,
            'business_profile_id': self.business_profile_id,
            'content_type': self.content_type,
            'platform': self.platform,
            'title': self.title,
            'body': self.body,
            'full_text': self.full_text,
            'hashtags': json.loads(self.hashtags) if self.hashtags else [],
            'call_to_action': self.call_to_action,
            'template_type': self.template_type,
            'template_format': self.template_format,
            'theme_name': self.theme_name,
            'theme_description': self.theme_description,
            'status': self.status,
            'approval_status': self.approval_status,
            'feedback_score': self.feedback_score,
            'feedback_comments': self.feedback_comments,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'generation_time': self.generation_time,
            'creativity_level': self.creativity_level,
            'batch_id': self.batch_id,
            'engagement_score': self.engagement_score,
            'estimated_reach': self.estimated_reach,
            'estimated_interactions': self.estimated_interactions,
            'character_count': self.character_count,
            'within_limits': self.within_limits,
            'platform_optimized': self.platform_optimized
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        # Convert hashtags to JSON string
        if 'hashtags' in data and isinstance(data['hashtags'], list):
            data['hashtags'] = json.dumps(data['hashtags'])
        
        return cls(**data)
    
    def update_from_dict(self, data):
        """Update instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                if key == 'hashtags' and isinstance(value, list):
                    value = json.dumps(value)
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()


class UserFeedback(db.Model):
    """Model for user feedback on content suggestions."""
    
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    content_suggestion_id = db.Column(db.String(36), db.ForeignKey('content_suggestions.id'), nullable=False)
    
    # Feedback details
    feedback_type = db.Column(db.String(50), nullable=False)  # approve, reject, thumbs_up, thumbs_down
    feedback_score = db.Column(db.Integer)  # 1-5 rating scale
    feedback_comments = db.Column(db.Text)
    
    # User info
    user_id = db.Column(db.String(100))
    user_session = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    content_suggestion = db.relationship('ContentSuggestion', backref='feedback_entries')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'content_suggestion_id': self.content_suggestion_id,
            'feedback_type': self.feedback_type,
            'feedback_score': self.feedback_score,
            'feedback_comments': self.feedback_comments,
            'user_id': self.user_id,
            'user_session': self.user_session,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BusinessProfile(db.Model):
    """Model for business profiles."""
    
    __tablename__ = 'business_profiles'
    
    id = db.Column(db.String(36), primary_key=True)
    business_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Target audience info
    target_audience = db.Column(db.Text)  # JSON string
    
    # Brand voice
    brand_voice = db.Column(db.Text)  # JSON string
    
    # Analysis results
    analysis_data = db.Column(db.Text)  # JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'business_name': self.business_name,
            'industry': self.industry,
            'description': self.description,
            'target_audience': json.loads(self.target_audience) if self.target_audience else {},
            'brand_voice': json.loads(self.brand_voice) if self.brand_voice else {},
            'analysis_data': json.loads(self.analysis_data) if self.analysis_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContentBriefing(db.Model):
    """Model for content briefings."""
    
    __tablename__ = 'content_briefings'
    
    id = db.Column(db.String(36), primary_key=True)
    business_profile_id = db.Column(db.String(36), db.ForeignKey('business_profiles.id'), nullable=False)
    
    # Briefing details
    campaign_objectives = db.Column(db.Text)  # JSON string
    time_period = db.Column(db.String(50))
    strategy_framework = db.Column(db.String(50))
    
    # Briefing data
    briefing_data = db.Column(db.Text)  # JSON string
    
    # Status
    status = db.Column(db.String(50), default='active')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    complexity_score = db.Column(db.Float)
    processing_time = db.Column(db.Float)
    
    # Relationship
    business_profile = db.relationship('BusinessProfile', backref='briefings')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'business_profile_id': self.business_profile_id,
            'campaign_objectives': json.loads(self.campaign_objectives) if self.campaign_objectives else [],
            'time_period': self.time_period,
            'strategy_framework': self.strategy_framework,
            'briefing_data': json.loads(self.briefing_data) if self.briefing_data else {},
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'complexity_score': self.complexity_score,
            'processing_time': self.processing_time
        }

