"""
API Key Model

Database model for managing API keys for external integrations
and programmatic access to the SaaS platform.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import secrets
import hashlib

db = SQLAlchemy()

class APIKey(db.Model):
    """
    API Key model for external integrations and programmatic access.
    
    Provides secure API key management with scopes, rate limiting,
    and usage tracking.
    """
    
    __tablename__ = 'api_keys'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # API key information
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    key_hash = db.Column(db.String(64), nullable=False, unique=True)
    key_prefix = db.Column(db.String(8), nullable=False)
    
    # Tenant relationship
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # User who created the key
    created_by_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Permissions and scopes
    scopes = db.Column(db.JSON, default=list)  # List of allowed scopes
    permissions = db.Column(db.JSON, default=dict)  # Detailed permissions
    
    # Rate limiting
    rate_limit_per_hour = db.Column(db.Integer, default=1000)
    rate_limit_per_day = db.Column(db.Integer, default=10000)
    
    # Usage tracking
    total_requests = db.Column(db.Integer, default=0)
    requests_this_hour = db.Column(db.Integer, default=0)
    requests_this_day = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)
    last_used_ip = db.Column(db.String(45), nullable=True)
    
    # Status and lifecycle
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Security settings
    allowed_ips = db.Column(db.JSON, default=list)  # IP whitelist
    allowed_domains = db.Column(db.JSON, default=list)  # Domain whitelist
    
    def __init__(self, name, tenant_id, created_by_user_id, **kwargs):
        """Initialize a new API key."""
        self.name = name
        self.tenant_id = tenant_id
        self.created_by_user_id = created_by_user_id
        
        # Generate API key
        raw_key = self._generate_api_key()
        self.key_prefix = raw_key[:8]
        self.key_hash = self._hash_key(raw_key)
        
        # Set optional attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Store the raw key temporarily for return to user
        self._raw_key = raw_key
    
    def _generate_api_key(self):
        """Generate a secure API key."""
        # Generate a 32-byte random key and encode as hex
        return secrets.token_hex(32)
    
    def _hash_key(self, raw_key):
        """Hash the API key for secure storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    @classmethod
    def verify_key(cls, raw_key):
        """Verify an API key and return the corresponding record."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return cls.query.filter_by(key_hash=key_hash, is_active=True).first()
    
    def to_dict(self, include_sensitive=False):
        """Convert API key to dictionary representation."""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'key_prefix': self.key_prefix,
            'tenant_id': self.tenant_id,
            'created_by_user_id': self.created_by_user_id,
            'scopes': self.scopes,
            'permissions': self.permissions,
            'rate_limits': {
                'per_hour': self.rate_limit_per_hour,
                'per_day': self.rate_limit_per_day
            },
            'usage': {
                'total_requests': self.total_requests,
                'requests_this_hour': self.requests_this_hour,
                'requests_this_day': self.requests_this_day,
                'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
                'last_used_ip': self.last_used_ip
            },
            'security': {
                'allowed_ips': self.allowed_ips,
                'allowed_domains': self.allowed_domains
            },
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive and hasattr(self, '_raw_key'):
            data['api_key'] = self._raw_key
        
        return data
    
    def record_usage(self, ip_address=None):
        """Record API key usage."""
        self.total_requests += 1
        self.requests_this_hour += 1
        self.requests_this_day += 1
        self.last_used_at = datetime.utcnow()
        
        if ip_address:
            self.last_used_ip = ip_address
        
        db.session.commit()
    
    def check_rate_limit(self):
        """Check if API key has exceeded rate limits."""
        if self.requests_this_hour >= self.rate_limit_per_hour:
            return False, 'hourly_limit_exceeded'
        
        if self.requests_this_day >= self.rate_limit_per_day:
            return False, 'daily_limit_exceeded'
        
        return True, 'within_limits'
    
    def check_ip_whitelist(self, ip_address):
        """Check if IP address is allowed."""
        if not self.allowed_ips:
            return True  # No restrictions
        
        return ip_address in self.allowed_ips
    
    def check_domain_whitelist(self, domain):
        """Check if domain is allowed."""
        if not self.allowed_domains:
            return True  # No restrictions
        
        return domain in self.allowed_domains
    
    def has_scope(self, required_scope):
        """Check if API key has required scope."""
        if not self.scopes:
            return False
        
        return required_scope in self.scopes
    
    def has_permission(self, resource, action):
        """Check if API key has specific permission."""
        if not self.permissions:
            return False
        
        resource_perms = self.permissions.get(resource, {})
        return resource_perms.get(action, False)
    
    def is_expired(self):
        """Check if API key has expired."""
        if not self.expires_at:
            return False
        
        return datetime.utcnow() > self.expires_at
    
    def reset_hourly_usage(self):
        """Reset hourly usage counter."""
        self.requests_this_hour = 0
        db.session.commit()
    
    def reset_daily_usage(self):
        """Reset daily usage counter."""
        self.requests_this_day = 0
        db.session.commit()
    
    def revoke(self):
        """Revoke the API key."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def extend_expiry(self, days=90):
        """Extend API key expiry date."""
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_scopes(self, new_scopes):
        """Update API key scopes."""
        self.scopes = new_scopes
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_permissions(self, new_permissions):
        """Update API key permissions."""
        self.permissions = new_permissions
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """String representation of the API key."""
        return f'<APIKey {self.name} ({self.key_prefix}...)>'


class APIKeyScopes:
    """Predefined API key scopes for different access levels."""
    
    # Read-only scopes
    READ_CAMPAIGNS = 'campaigns:read'
    READ_CONTENT = 'content:read'
    READ_ANALYTICS = 'analytics:read'
    READ_USERS = 'users:read'
    READ_SETTINGS = 'settings:read'
    
    # Write scopes
    WRITE_CAMPAIGNS = 'campaigns:write'
    WRITE_CONTENT = 'content:write'
    WRITE_USERS = 'users:write'
    WRITE_SETTINGS = 'settings:write'
    
    # Admin scopes
    ADMIN_TENANT = 'tenant:admin'
    ADMIN_USERS = 'users:admin'
    ADMIN_API_KEYS = 'api_keys:admin'
    
    # External integration scopes
    WEBHOOKS = 'webhooks:manage'
    EXPORTS = 'data:export'
    INTEGRATIONS = 'integrations:manage'
    
    @classmethod
    def get_all_scopes(cls):
        """Get all available scopes."""
        return [
            cls.READ_CAMPAIGNS, cls.READ_CONTENT, cls.READ_ANALYTICS,
            cls.READ_USERS, cls.READ_SETTINGS, cls.WRITE_CAMPAIGNS,
            cls.WRITE_CONTENT, cls.WRITE_USERS, cls.WRITE_SETTINGS,
            cls.ADMIN_TENANT, cls.ADMIN_USERS, cls.ADMIN_API_KEYS,
            cls.WEBHOOKS, cls.EXPORTS, cls.INTEGRATIONS
        ]
    
    @classmethod
    def get_read_only_scopes(cls):
        """Get read-only scopes."""
        return [
            cls.READ_CAMPAIGNS, cls.READ_CONTENT, cls.READ_ANALYTICS,
            cls.READ_USERS, cls.READ_SETTINGS
        ]
    
    @classmethod
    def get_admin_scopes(cls):
        """Get admin scopes."""
        return [
            cls.ADMIN_TENANT, cls.ADMIN_USERS, cls.ADMIN_API_KEYS
        ]


class APIKeyPermissions:
    """Helper class for managing API key permissions."""
    
    DEFAULT_PERMISSIONS = {
        'campaigns': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False
        },
        'content': {
            'generate': False,
            'approve': False,
            'schedule': False,
            'publish': False
        },
        'analytics': {
            'view': False,
            'export': False
        },
        'users': {
            'invite': False,
            'manage': False,
            'remove': False
        },
        'settings': {
            'view': False,
            'update': False
        },
        'integrations': {
            'configure': False,
            'manage': False
        }
    }
    
    @classmethod
    def get_default_permissions(cls):
        """Get default permissions structure."""
        return cls.DEFAULT_PERMISSIONS.copy()
    
    @classmethod
    def get_read_only_permissions(cls):
        """Get read-only permissions."""
        permissions = cls.get_default_permissions()
        permissions['campaigns']['read'] = True
        permissions['analytics']['view'] = True
        permissions['settings']['view'] = True
        return permissions
    
    @classmethod
    def get_full_permissions(cls):
        """Get full permissions for admin access."""
        permissions = cls.get_default_permissions()
        for resource in permissions:
            for action in permissions[resource]:
                permissions[resource][action] = True
        return permissions

