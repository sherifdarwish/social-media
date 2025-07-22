"""
Analytics Models

Database models for tracking content performance, user feedback,
and generating recommendations for the SaaS platform.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json
from sqlalchemy import func, and_, or_

db = SQLAlchemy()

class ContentFeedback(db.Model):
    """
    Model for tracking user feedback on generated content.
    """
    
    __tablename__ = 'content_feedback'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant and content relationships
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    content_id = db.Column(db.String(36), nullable=False)  # Reference to generated content
    campaign_id = db.Column(db.String(36), nullable=True)  # Reference to campaign
    
    # Content details
    platform = db.Column(db.String(50), nullable=False)  # facebook, twitter, linkedin, etc.
    content_type = db.Column(db.String(50), nullable=False)  # educational, promotional, etc.
    content_text = db.Column(db.Text, nullable=True)
    hashtags = db.Column(db.JSON, default=list)
    
    # Business context
    industry = db.Column(db.String(100), nullable=True)
    target_audience = db.Column(db.String(255), nullable=True)
    brand_voice = db.Column(db.String(50), nullable=True)
    
    # User feedback
    feedback_type = db.Column(db.String(20), nullable=False)  # approve, reject, thumbs_up, thumbs_down
    feedback_score = db.Column(db.Integer, nullable=True)  # 1-5 rating if applicable
    feedback_comment = db.Column(db.Text, nullable=True)
    
    # AI predictions vs actual feedback
    predicted_engagement = db.Column(db.Float, nullable=True)
    actual_performance = db.Column(db.JSON, nullable=True)  # Real social media metrics
    
    # Metadata
    metadata = db.Column(db.JSON, default=dict)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tenant_id, content_id, platform, content_type, feedback_type, **kwargs):
        """Initialize a new content feedback record."""
        self.tenant_id = tenant_id
        self.content_id = content_id
        self.platform = platform
        self.content_type = content_type
        self.feedback_type = feedback_type
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert content feedback to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'content_id': self.content_id,
            'campaign_id': self.campaign_id,
            'platform': self.platform,
            'content_type': self.content_type,
            'content_text': self.content_text,
            'hashtags': self.hashtags,
            'business_context': {
                'industry': self.industry,
                'target_audience': self.target_audience,
                'brand_voice': self.brand_voice
            },
            'feedback': {
                'type': self.feedback_type,
                'score': self.feedback_score,
                'comment': self.feedback_comment
            },
            'performance': {
                'predicted_engagement': self.predicted_engagement,
                'actual_performance': self.actual_performance
            },
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_positive_feedback(self):
        """Check if feedback is positive."""
        return self.feedback_type in ['approve', 'thumbs_up']
    
    def is_negative_feedback(self):
        """Check if feedback is negative."""
        return self.feedback_type in ['reject', 'thumbs_down']
    
    @classmethod
    def get_feedback_stats(cls, tenant_id, days=30):
        """Get feedback statistics for a tenant."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        total_feedback = cls.query.filter(
            cls.tenant_id == tenant_id,
            cls.created_at >= since_date
        ).count()
        
        positive_feedback = cls.query.filter(
            cls.tenant_id == tenant_id,
            cls.created_at >= since_date,
            cls.feedback_type.in_(['approve', 'thumbs_up'])
        ).count()
        
        negative_feedback = cls.query.filter(
            cls.tenant_id == tenant_id,
            cls.created_at >= since_date,
            cls.feedback_type.in_(['reject', 'thumbs_down'])
        ).count()
        
        approval_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            'total_feedback': total_feedback,
            'positive_feedback': positive_feedback,
            'negative_feedback': negative_feedback,
            'approval_rate': round(approval_rate, 2),
            'period_days': days
        }
    
    @classmethod
    def get_platform_performance(cls, tenant_id, days=30):
        """Get performance breakdown by platform."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        platform_stats = db.session.query(
            cls.platform,
            func.count(cls.id).label('total'),
            func.sum(func.case([(cls.feedback_type.in_(['approve', 'thumbs_up']), 1)], else_=0)).label('positive'),
            func.avg(cls.predicted_engagement).label('avg_predicted'),
            func.avg(cls.feedback_score).label('avg_score')
        ).filter(
            cls.tenant_id == tenant_id,
            cls.created_at >= since_date
        ).group_by(cls.platform).all()
        
        results = []
        for stat in platform_stats:
            approval_rate = (stat.positive / stat.total * 100) if stat.total > 0 else 0
            results.append({
                'platform': stat.platform,
                'total_content': stat.total,
                'positive_feedback': stat.positive,
                'approval_rate': round(approval_rate, 2),
                'avg_predicted_engagement': round(stat.avg_predicted or 0, 2),
                'avg_feedback_score': round(stat.avg_score or 0, 2)
            })
        
        return results
    
    def __repr__(self):
        """String representation of the content feedback."""
        return f'<ContentFeedback {self.platform} - {self.feedback_type}>'


class ContentRecommendation(db.Model):
    """
    Model for storing AI-generated content recommendations based on feedback patterns.
    """
    
    __tablename__ = 'content_recommendations'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Target tenant and business context
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    target_audience = db.Column(db.String(255), nullable=True)
    brand_voice = db.Column(db.String(50), nullable=True)
    
    # Recommendation details
    recommendation_type = db.Column(db.String(50), nullable=False)  # content_type, platform, timing, etc.
    recommendation_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)
    
    # Supporting data
    based_on_feedback_count = db.Column(db.Integer, default=0)
    similar_businesses_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, nullable=True)
    
    # Platform and content specifics
    platform = db.Column(db.String(50), nullable=True)
    content_type = db.Column(db.String(50), nullable=True)
    suggested_hashtags = db.Column(db.JSON, default=list)
    suggested_timing = db.Column(db.JSON, default=dict)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_implemented = db.Column(db.Boolean, default=False)
    implementation_result = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, tenant_id, recommendation_type, recommendation_text, confidence_score, **kwargs):
        """Initialize a new content recommendation."""
        self.tenant_id = tenant_id
        self.recommendation_type = recommendation_type
        self.recommendation_text = recommendation_text
        self.confidence_score = confidence_score
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert content recommendation to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'business_context': {
                'industry': self.industry,
                'target_audience': self.target_audience,
                'brand_voice': self.brand_voice
            },
            'recommendation': {
                'type': self.recommendation_type,
                'text': self.recommendation_text,
                'confidence_score': self.confidence_score
            },
            'supporting_data': {
                'based_on_feedback_count': self.based_on_feedback_count,
                'similar_businesses_count': self.similar_businesses_count,
                'success_rate': self.success_rate
            },
            'content_specifics': {
                'platform': self.platform,
                'content_type': self.content_type,
                'suggested_hashtags': self.suggested_hashtags,
                'suggested_timing': self.suggested_timing
            },
            'status': {
                'is_active': self.is_active,
                'is_implemented': self.is_implemented,
                'implementation_result': self.implementation_result
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_expired(self):
        """Check if recommendation has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def mark_implemented(self, result=None):
        """Mark recommendation as implemented."""
        self.is_implemented = True
        self.implementation_result = result
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_active_recommendations(cls, tenant_id, limit=10):
        """Get active recommendations for a tenant."""
        return cls.query.filter(
            cls.tenant_id == tenant_id,
            cls.is_active == True,
            or_(cls.expires_at.is_(None), cls.expires_at > datetime.utcnow())
        ).order_by(cls.confidence_score.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired recommendations."""
        expired_count = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
        return expired_count
    
    def __repr__(self):
        """String representation of the content recommendation."""
        return f'<ContentRecommendation {self.recommendation_type} (confidence: {self.confidence_score})>'


class SocialMediaMetrics(db.Model):
    """
    Model for storing real social media performance metrics.
    """
    
    __tablename__ = 'social_media_metrics'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Content and tenant relationships
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    content_id = db.Column(db.String(36), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    
    # Social media post details
    platform_post_id = db.Column(db.String(255), nullable=True)
    post_url = db.Column(db.String(500), nullable=True)
    posted_at = db.Column(db.DateTime, nullable=True)
    
    # Engagement metrics
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    # Calculated metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    
    # Audience insights
    audience_demographics = db.Column(db.JSON, default=dict)
    top_countries = db.Column(db.JSON, default=list)
    peak_engagement_time = db.Column(db.DateTime, nullable=True)
    
    # Performance comparison
    industry_benchmark = db.Column(db.Float, nullable=True)
    performance_score = db.Column(db.Float, nullable=True)  # Compared to tenant's average
    
    # Data collection info
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    data_source = db.Column(db.String(100), nullable=True)  # API source
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, tenant_id, content_id, platform, **kwargs):
        """Initialize a new social media metrics record."""
        self.tenant_id = tenant_id
        self.content_id = content_id
        self.platform = platform
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert social media metrics to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'content_id': self.content_id,
            'platform': self.platform,
            'post_details': {
                'platform_post_id': self.platform_post_id,
                'post_url': self.post_url,
                'posted_at': self.posted_at.isoformat() if self.posted_at else None
            },
            'engagement': {
                'likes': self.likes,
                'shares': self.shares,
                'comments': self.comments,
                'views': self.views,
                'clicks': self.clicks,
                'engagement_rate': self.engagement_rate,
                'reach': self.reach,
                'impressions': self.impressions
            },
            'audience': {
                'demographics': self.audience_demographics,
                'top_countries': self.top_countries,
                'peak_engagement_time': self.peak_engagement_time.isoformat() if self.peak_engagement_time else None
            },
            'performance': {
                'industry_benchmark': self.industry_benchmark,
                'performance_score': self.performance_score
            },
            'data_info': {
                'last_updated': self.last_updated.isoformat() if self.last_updated else None,
                'data_source': self.data_source
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate based on metrics."""
        if self.impressions > 0:
            total_engagement = self.likes + self.shares + self.comments
            self.engagement_rate = (total_engagement / self.impressions) * 100
        else:
            self.engagement_rate = 0.0
        
        return self.engagement_rate
    
    def calculate_performance_score(self, tenant_average=None):
        """Calculate performance score compared to tenant average."""
        if not tenant_average:
            # Get tenant's average engagement rate
            avg_result = db.session.query(
                func.avg(SocialMediaMetrics.engagement_rate)
            ).filter(
                SocialMediaMetrics.tenant_id == self.tenant_id,
                SocialMediaMetrics.platform == self.platform
            ).scalar()
            
            tenant_average = avg_result or 0.0
        
        if tenant_average > 0:
            self.performance_score = (self.engagement_rate / tenant_average) * 100
        else:
            self.performance_score = 100.0  # Default if no comparison data
        
        return self.performance_score
    
    @classmethod
    def get_platform_averages(cls, tenant_id, days=30):
        """Get average metrics by platform for a tenant."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        platform_averages = db.session.query(
            cls.platform,
            func.avg(cls.engagement_rate).label('avg_engagement'),
            func.avg(cls.likes).label('avg_likes'),
            func.avg(cls.shares).label('avg_shares'),
            func.avg(cls.comments).label('avg_comments'),
            func.avg(cls.views).label('avg_views'),
            func.count(cls.id).label('post_count')
        ).filter(
            cls.tenant_id == tenant_id,
            cls.created_at >= since_date
        ).group_by(cls.platform).all()
        
        results = []
        for avg in platform_averages:
            results.append({
                'platform': avg.platform,
                'avg_engagement_rate': round(avg.avg_engagement or 0, 2),
                'avg_likes': round(avg.avg_likes or 0, 1),
                'avg_shares': round(avg.avg_shares or 0, 1),
                'avg_comments': round(avg.avg_comments or 0, 1),
                'avg_views': round(avg.avg_views or 0, 1),
                'post_count': avg.post_count
            })
        
        return results
    
    def __repr__(self):
        """String representation of the social media metrics."""
        return f'<SocialMediaMetrics {self.platform} - {self.engagement_rate}% engagement>'


class BusinessSimilarity(db.Model):
    """
    Model for tracking business similarity for recommendation purposes.
    """
    
    __tablename__ = 'business_similarity'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant relationships
    tenant_a_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    tenant_b_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Similarity metrics
    industry_similarity = db.Column(db.Float, default=0.0)  # 0-1 score
    audience_similarity = db.Column(db.Float, default=0.0)  # 0-1 score
    content_similarity = db.Column(db.Float, default=0.0)  # 0-1 score
    overall_similarity = db.Column(db.Float, default=0.0)  # 0-1 score
    
    # Calculation metadata
    calculation_method = db.Column(db.String(100), nullable=True)
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tenant_a_id, tenant_b_id, **kwargs):
        """Initialize a new business similarity record."""
        self.tenant_a_id = tenant_a_id
        self.tenant_b_id = tenant_b_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert business similarity to dictionary representation."""
        return {
            'id': self.id,
            'tenant_a_id': self.tenant_a_id,
            'tenant_b_id': self.tenant_b_id,
            'similarity_scores': {
                'industry': self.industry_similarity,
                'audience': self.audience_similarity,
                'content': self.content_similarity,
                'overall': self.overall_similarity
            },
            'calculation_info': {
                'method': self.calculation_method,
                'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def find_similar_businesses(cls, tenant_id, min_similarity=0.7, limit=10):
        """Find businesses similar to the given tenant."""
        similar_businesses = cls.query.filter(
            or_(cls.tenant_a_id == tenant_id, cls.tenant_b_id == tenant_id),
            cls.overall_similarity >= min_similarity
        ).order_by(cls.overall_similarity.desc()).limit(limit).all()
        
        results = []
        for similarity in similar_businesses:
            other_tenant_id = similarity.tenant_b_id if similarity.tenant_a_id == tenant_id else similarity.tenant_a_id
            results.append({
                'tenant_id': other_tenant_id,
                'similarity_score': similarity.overall_similarity,
                'similarity_breakdown': {
                    'industry': similarity.industry_similarity,
                    'audience': similarity.audience_similarity,
                    'content': similarity.content_similarity
                }
            })
        
        return results
    
    def __repr__(self):
        """String representation of the business similarity."""
        return f'<BusinessSimilarity {self.tenant_a_id} <-> {self.tenant_b_id} ({self.overall_similarity})>'

