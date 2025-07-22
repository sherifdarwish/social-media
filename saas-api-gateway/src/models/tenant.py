"""
Tenant Model

Database model for multi-tenant SaaS architecture.
Each tenant represents a business or organization using the platform.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Tenant(db.Model):
    """
    Tenant model for multi-tenant SaaS platform.
    
    Each tenant represents a separate business or organization
    with isolated data and configuration.
    """
    
    __tablename__ = 'tenants'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic tenant information
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), unique=True, nullable=True)
    subdomain = db.Column(db.String(100), unique=True, nullable=True)
    
    # Business information
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Subscription and billing
    subscription_plan = db.Column(db.String(50), default='free')
    subscription_status = db.Column(db.String(20), default='active')
    billing_email = db.Column(db.String(255), nullable=True)
    
    # Usage limits and quotas
    max_users = db.Column(db.Integer, default=5)
    max_campaigns = db.Column(db.Integer, default=10)
    max_posts_per_month = db.Column(db.Integer, default=100)
    max_api_calls_per_hour = db.Column(db.Integer, default=1000)
    
    # Current usage tracking
    current_users = db.Column(db.Integer, default=0)
    current_campaigns = db.Column(db.Integer, default=0)
    posts_this_month = db.Column(db.Integer, default=0)
    api_calls_this_hour = db.Column(db.Integer, default=0)
    
    # Configuration settings
    settings = db.Column(db.JSON, default=dict)
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True, cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, **kwargs):
        """Initialize a new tenant."""
        self.name = name
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert tenant to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'subdomain': self.subdomain,
            'industry': self.industry,
            'company_size': self.company_size,
            'country': self.country,
            'timezone': self.timezone,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'usage_limits': {
                'max_users': self.max_users,
                'max_campaigns': self.max_campaigns,
                'max_posts_per_month': self.max_posts_per_month,
                'max_api_calls_per_hour': self.max_api_calls_per_hour
            },
            'current_usage': {
                'users': self.current_users,
                'campaigns': self.current_campaigns,
                'posts_this_month': self.posts_this_month,
                'api_calls_this_hour': self.api_calls_this_hour
            },
            'settings': self.settings,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def update_usage(self, metric, increment=1):
        """Update usage metrics for the tenant."""
        if metric == 'users':
            self.current_users += increment
        elif metric == 'campaigns':
            self.current_campaigns += increment
        elif metric == 'posts':
            self.posts_this_month += increment
        elif metric == 'api_calls':
            self.api_calls_this_hour += increment
        
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def check_limits(self, metric):
        """Check if tenant has exceeded usage limits."""
        limits = {
            'users': (self.current_users, self.max_users),
            'campaigns': (self.current_campaigns, self.max_campaigns),
            'posts': (self.posts_this_month, self.max_posts_per_month),
            'api_calls': (self.api_calls_this_hour, self.max_api_calls_per_hour)
        }
        
        if metric in limits:
            current, maximum = limits[metric]
            return current < maximum
        
        return True
    
    def get_usage_percentage(self, metric):
        """Get usage percentage for a specific metric."""
        limits = {
            'users': (self.current_users, self.max_users),
            'campaigns': (self.current_campaigns, self.max_campaigns),
            'posts': (self.posts_this_month, self.max_posts_per_month),
            'api_calls': (self.api_calls_this_hour, self.max_api_calls_per_hour)
        }
        
        if metric in limits:
            current, maximum = limits[metric]
            if maximum > 0:
                return (current / maximum) * 100
        
        return 0
    
    def reset_monthly_usage(self):
        """Reset monthly usage counters."""
        self.posts_this_month = 0
        db.session.commit()
    
    def reset_hourly_usage(self):
        """Reset hourly usage counters."""
        self.api_calls_this_hour = 0
        db.session.commit()
    
    def update_settings(self, new_settings):
        """Update tenant settings."""
        if self.settings is None:
            self.settings = {}
        
        self.settings.update(new_settings)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_setting(self, key, default=None):
        """Get a specific setting value."""
        if self.settings:
            return self.settings.get(key, default)
        return default
    
    def is_feature_enabled(self, feature):
        """Check if a specific feature is enabled for this tenant."""
        feature_map = {
            'advanced_analytics': ['premium', 'enterprise'],
            'custom_branding': ['premium', 'enterprise'],
            'api_access': ['premium', 'enterprise'],
            'priority_support': ['enterprise'],
            'white_labeling': ['enterprise'],
            'unlimited_campaigns': ['enterprise']
        }
        
        if feature in feature_map:
            return self.subscription_plan in feature_map[feature]
        
        return False
    
    def __repr__(self):
        """String representation of the tenant."""
        return f'<Tenant {self.name} ({self.id})>'


class TenantSettings:
    """Helper class for managing tenant settings."""
    
    DEFAULT_SETTINGS = {
        'branding': {
            'logo_url': None,
            'primary_color': '#1a73e8',
            'secondary_color': '#34a853',
            'company_name': None
        },
        'notifications': {
            'email_enabled': True,
            'webhook_enabled': False,
            'slack_enabled': False
        },
        'content_generation': {
            'default_tone': 'professional',
            'default_style': 'informative',
            'auto_hashtags': True,
            'content_approval_required': True
        },
        'posting_schedule': {
            'timezone': 'UTC',
            'business_hours_start': 9,
            'business_hours_end': 17,
            'weekend_posting': False
        },
        'analytics': {
            'retention_days': 90,
            'export_enabled': True,
            'real_time_updates': True
        },
        'security': {
            'two_factor_required': False,
            'session_timeout': 3600,
            'ip_whitelist': [],
            'api_key_rotation_days': 90
        }
    }
    
    @classmethod
    def get_default_settings(cls):
        """Get default settings for new tenants."""
        return cls.DEFAULT_SETTINGS.copy()
    
    @classmethod
    def validate_settings(cls, settings):
        """Validate tenant settings structure."""
        # Add validation logic here
        return True

