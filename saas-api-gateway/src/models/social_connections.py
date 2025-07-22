"""
Social Media Connections Model

Database model for managing OAuth connections to social media platforms
for automated posting and metrics collection.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json
from cryptography.fernet import Fernet
import os
import base64

db = SQLAlchemy()

class SocialConnection(db.Model):
    """
    Model for storing OAuth connections to social media platforms.
    """
    
    __tablename__ = 'social_connections'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant relationship
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Platform information
    platform = db.Column(db.String(50), nullable=False)  # facebook, twitter, linkedin, instagram, tiktok
    platform_user_id = db.Column(db.String(255), nullable=False)
    platform_username = db.Column(db.String(255), nullable=True)
    platform_display_name = db.Column(db.String(255), nullable=True)
    
    # OAuth tokens (encrypted)
    access_token_encrypted = db.Column(db.Text, nullable=False)
    refresh_token_encrypted = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Platform-specific data
    platform_data = db.Column(db.JSON, default=dict)  # Store platform-specific info
    
    # Permissions and scopes
    granted_scopes = db.Column(db.JSON, default=list)
    required_scopes = db.Column(db.JSON, default=list)
    
    # Connection status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Usage tracking
    posts_count = db.Column(db.Integer, default=0)
    last_post_at = db.Column(db.DateTime, nullable=True)
    last_metrics_sync = db.Column(db.DateTime, nullable=True)
    
    # Error tracking
    last_error = db.Column(db.Text, nullable=True)
    error_count = db.Column(db.Integer, default=0)
    last_error_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tenant_id, platform, platform_user_id, access_token, **kwargs):
        """Initialize a new social connection."""
        self.tenant_id = tenant_id
        self.platform = platform
        self.platform_user_id = platform_user_id
        self.set_access_token(access_token)
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['access_token_encrypted']:
                setattr(self, key, value)
    
    @property
    def encryption_key(self):
        """Get or create encryption key for tokens."""
        key = os.environ.get('SOCIAL_TOKEN_ENCRYPTION_KEY')
        if not key:
            # Generate a new key if not set (for development)
            key = Fernet.generate_key()
            os.environ['SOCIAL_TOKEN_ENCRYPTION_KEY'] = key.decode()
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def set_access_token(self, token):
        """Encrypt and store access token."""
        if token:
            fernet = Fernet(self.encryption_key)
            self.access_token_encrypted = fernet.encrypt(token.encode()).decode()
    
    def get_access_token(self):
        """Decrypt and return access token."""
        if self.access_token_encrypted:
            fernet = Fernet(self.encryption_key)
            return fernet.decrypt(self.access_token_encrypted.encode()).decode()
        return None
    
    def set_refresh_token(self, token):
        """Encrypt and store refresh token."""
        if token:
            fernet = Fernet(self.encryption_key)
            self.refresh_token_encrypted = fernet.encrypt(token.encode()).decode()
    
    def get_refresh_token(self):
        """Decrypt and return refresh token."""
        if self.refresh_token_encrypted:
            fernet = Fernet(self.encryption_key)
            return fernet.decrypt(self.refresh_token_encrypted.encode()).decode()
        return None
    
    def to_dict(self, include_tokens=False):
        """Convert social connection to dictionary representation."""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'platform': self.platform,
            'platform_user_id': self.platform_user_id,
            'platform_username': self.platform_username,
            'platform_display_name': self.platform_display_name,
            'platform_data': self.platform_data,
            'granted_scopes': self.granted_scopes,
            'required_scopes': self.required_scopes,
            'status': {
                'is_active': self.is_active,
                'is_verified': self.is_verified,
                'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
                'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
            },
            'usage': {
                'posts_count': self.posts_count,
                'last_post_at': self.last_post_at.isoformat() if self.last_post_at else None,
                'last_metrics_sync': self.last_metrics_sync.isoformat() if self.last_metrics_sync else None
            },
            'errors': {
                'last_error': self.last_error,
                'error_count': self.error_count,
                'last_error_at': self.last_error_at.isoformat() if self.last_error_at else None
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_tokens:
            data['access_token'] = self.get_access_token()
            data['refresh_token'] = self.get_refresh_token()
        
        return data
    
    def is_token_expired(self):
        """Check if access token is expired."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() >= self.token_expires_at
    
    def needs_refresh(self, buffer_minutes=30):
        """Check if token needs refresh (with buffer time)."""
        if not self.token_expires_at:
            return False
        buffer_time = datetime.utcnow() + timedelta(minutes=buffer_minutes)
        return buffer_time >= self.token_expires_at
    
    def update_tokens(self, access_token, refresh_token=None, expires_in=None):
        """Update OAuth tokens."""
        self.set_access_token(access_token)
        if refresh_token:
            self.set_refresh_token(refresh_token)
        
        if expires_in:
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def record_post(self):
        """Record a successful post."""
        self.posts_count += 1
        self.last_post_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def record_error(self, error_message):
        """Record an error."""
        self.last_error = error_message
        self.error_count += 1
        self.last_error_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Deactivate if too many errors
        if self.error_count >= 5:
            self.is_active = False
        
        db.session.commit()
    
    def clear_errors(self):
        """Clear error tracking."""
        self.last_error = None
        self.error_count = 0
        self.last_error_at = None
        self.is_active = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def verify_connection(self):
        """Mark connection as verified."""
        self.is_verified = True
        self.last_verified_at = datetime.utcnow()
        self.clear_errors()
        db.session.commit()
    
    def disconnect(self):
        """Disconnect the social media account."""
        self.is_active = False
        self.access_token_encrypted = None
        self.refresh_token_encrypted = None
        self.token_expires_at = None
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_active_connections(cls, tenant_id, platform=None):
        """Get active connections for a tenant."""
        query = cls.query.filter_by(tenant_id=tenant_id, is_active=True)
        if platform:
            query = query.filter_by(platform=platform)
        return query.all()
    
    @classmethod
    def get_connection(cls, tenant_id, platform):
        """Get connection for a specific platform."""
        return cls.query.filter_by(
            tenant_id=tenant_id,
            platform=platform,
            is_active=True
        ).first()
    
    def __repr__(self):
        """String representation of the social connection."""
        return f'<SocialConnection {self.platform} - {self.platform_username}>'


class OAuthState(db.Model):
    """
    Model for tracking OAuth state during authentication flow.
    """
    
    __tablename__ = 'oauth_states'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # OAuth state
    state = db.Column(db.String(255), unique=True, nullable=False)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    
    # Additional data
    redirect_uri = db.Column(db.String(500), nullable=True)
    scopes = db.Column(db.JSON, default=list)
    metadata = db.Column(db.JSON, default=dict)
    
    # Status
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    
    def __init__(self, state, tenant_id, platform, **kwargs):
        """Initialize a new OAuth state."""
        self.state = state
        self.tenant_id = tenant_id
        self.platform = platform
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert OAuth state to dictionary representation."""
        return {
            'id': self.id,
            'state': self.state,
            'tenant_id': self.tenant_id,
            'platform': self.platform,
            'redirect_uri': self.redirect_uri,
            'scopes': self.scopes,
            'metadata': self.metadata,
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def is_expired(self):
        """Check if OAuth state is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if OAuth state is valid for use."""
        return not self.is_used and not self.is_expired()
    
    def mark_used(self):
        """Mark OAuth state as used."""
        self.is_used = True
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired OAuth states."""
        expired_count = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
        return expired_count
    
    @classmethod
    def find_valid_state(cls, state):
        """Find a valid OAuth state."""
        oauth_state = cls.query.filter_by(state=state).first()
        if oauth_state and oauth_state.is_valid():
            return oauth_state
        return None
    
    def __repr__(self):
        """String representation of the OAuth state."""
        return f'<OAuthState {self.platform} - {self.state[:8]}...>'


# Platform-specific OAuth configurations
OAUTH_CONFIGS = {
    'facebook': {
        'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
        'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
        'api_base': 'https://graph.facebook.com/v18.0',
        'required_scopes': ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list'],
        'user_info_endpoint': '/me',
        'pages_endpoint': '/me/accounts'
    },
    'twitter': {
        'auth_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'api_base': 'https://api.twitter.com/2',
        'required_scopes': ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        'user_info_endpoint': '/users/me'
    },
    'linkedin': {
        'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'api_base': 'https://api.linkedin.com/v2',
        'required_scopes': ['w_member_social', 'r_liteprofile', 'r_emailaddress'],
        'user_info_endpoint': '/people/~'
    },
    'instagram': {
        'auth_url': 'https://api.instagram.com/oauth/authorize',
        'token_url': 'https://api.instagram.com/oauth/access_token',
        'api_base': 'https://graph.instagram.com',
        'required_scopes': ['user_profile', 'user_media'],
        'user_info_endpoint': '/me'
    },
    'tiktok': {
        'auth_url': 'https://www.tiktok.com/auth/authorize/',
        'token_url': 'https://open-api.tiktok.com/oauth/access_token/',
        'api_base': 'https://open-api.tiktok.com',
        'required_scopes': ['user.info.basic', 'video.publish'],
        'user_info_endpoint': '/v1/user/info/'
    }
}

def get_oauth_config(platform):
    """Get OAuth configuration for a platform."""
    return OAUTH_CONFIGS.get(platform.lower(), {})

