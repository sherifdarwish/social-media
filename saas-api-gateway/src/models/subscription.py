"""
Subscription Model

Database model for managing subscription plans and billing
with Stripe integration for the SaaS platform.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json

db = SQLAlchemy()

class SubscriptionPlan(db.Model):
    """
    Subscription plan model defining different pricing tiers.
    """
    
    __tablename__ = 'subscription_plans'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Plan information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Decimal(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), default='USD')
    billing_interval = db.Column(db.String(20), default='month')  # month, year
    
    # Stripe integration
    stripe_price_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_product_id = db.Column(db.String(255), nullable=True)
    
    # Plan limits and features
    max_posts_per_week = db.Column(db.Integer, default=5)
    max_campaigns = db.Column(db.Integer, default=1)
    max_users = db.Column(db.Integer, default=1)
    max_platforms = db.Column(db.Integer, default=3)
    
    # Feature flags
    features = db.Column(db.JSON, default=dict)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)
    
    def __init__(self, name, price, **kwargs):
        """Initialize a new subscription plan."""
        self.name = name
        self.price = price
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert subscription plan to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'currency': self.currency,
            'billing_interval': self.billing_interval,
            'stripe_price_id': self.stripe_price_id,
            'stripe_product_id': self.stripe_product_id,
            'limits': {
                'max_posts_per_week': self.max_posts_per_week,
                'max_campaigns': self.max_campaigns,
                'max_users': self.max_users,
                'max_platforms': self.max_platforms
            },
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_free_plan(cls):
        """Get the free plan."""
        return cls.query.filter_by(name='Free', price=0.00).first()
    
    @classmethod
    def get_premium_plan(cls):
        """Get the premium plan."""
        return cls.query.filter_by(name='Premium').first()
    
    def __repr__(self):
        """String representation of the subscription plan."""
        return f'<SubscriptionPlan {self.name} (${self.price}/{self.billing_interval})>'


class Subscription(db.Model):
    """
    Subscription model for tracking tenant subscriptions.
    """
    
    __tablename__ = 'subscriptions'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant relationship
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Plan relationship
    plan_id = db.Column(db.String(36), db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Stripe integration
    stripe_subscription_id = db.Column(db.String(255), unique=True, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_payment_method_id = db.Column(db.String(255), nullable=True)
    
    # Subscription status
    status = db.Column(db.String(50), default='active')  # active, canceled, past_due, unpaid
    
    # Billing information
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    trial_start = db.Column(db.DateTime, nullable=True)
    trial_end = db.Column(db.DateTime, nullable=True)
    
    # Usage tracking
    posts_this_week = db.Column(db.Integer, default=0)
    week_start_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # Metadata
    metadata = db.Column(db.JSON, default=dict)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, tenant_id, plan_id, **kwargs):
        """Initialize a new subscription."""
        self.tenant_id = tenant_id
        self.plan_id = plan_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert subscription to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'plan_id': self.plan_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'stripe_subscription_id': self.stripe_subscription_id,
            'stripe_customer_id': self.stripe_customer_id,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'trial_start': self.trial_start.isoformat() if self.trial_start else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'usage': {
                'posts_this_week': self.posts_this_week,
                'week_start_date': self.week_start_date.isoformat() if self.week_start_date else None
            },
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'canceled_at': self.canceled_at.isoformat() if self.canceled_at else None
        }
    
    def is_active(self):
        """Check if subscription is active."""
        return self.status == 'active'
    
    def is_trial(self):
        """Check if subscription is in trial period."""
        if not self.trial_end:
            return False
        return datetime.utcnow() <= self.trial_end
    
    def days_until_renewal(self):
        """Get days until next renewal."""
        if not self.current_period_end:
            return None
        
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def can_post(self):
        """Check if tenant can post based on plan limits."""
        if not self.plan:
            return False
        
        # Reset weekly counter if needed
        self._reset_weekly_usage_if_needed()
        
        return self.posts_this_week < self.plan.max_posts_per_week
    
    def record_post(self):
        """Record a post and update usage."""
        self._reset_weekly_usage_if_needed()
        self.posts_this_week += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def _reset_weekly_usage_if_needed(self):
        """Reset weekly usage counter if a new week has started."""
        today = datetime.utcnow().date()
        
        # Check if we need to reset (Monday is start of week)
        if not self.week_start_date:
            self.week_start_date = today
            self.posts_this_week = 0
        else:
            # Calculate days since week start
            days_since_start = (today - self.week_start_date).days
            
            # If it's been 7 or more days, reset
            if days_since_start >= 7:
                # Find the Monday of current week
                days_since_monday = today.weekday()
                monday = today - timedelta(days=days_since_monday)
                
                self.week_start_date = monday
                self.posts_this_week = 0
    
    def get_usage_percentage(self):
        """Get usage percentage for current week."""
        if not self.plan or self.plan.max_posts_per_week == 0:
            return 0
        
        self._reset_weekly_usage_if_needed()
        return (self.posts_this_week / self.plan.max_posts_per_week) * 100
    
    def get_remaining_posts(self):
        """Get remaining posts for current week."""
        if not self.plan:
            return 0
        
        self._reset_weekly_usage_if_needed()
        return max(0, self.plan.max_posts_per_week - self.posts_this_week)
    
    def cancel(self):
        """Cancel the subscription."""
        self.status = 'canceled'
        self.canceled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def reactivate(self):
        """Reactivate a canceled subscription."""
        self.status = 'active'
        self.canceled_at = None
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_from_stripe(self, stripe_subscription):
        """Update subscription from Stripe subscription object."""
        self.stripe_subscription_id = stripe_subscription.id
        self.status = stripe_subscription.status
        
        if stripe_subscription.current_period_start:
            self.current_period_start = datetime.fromtimestamp(
                stripe_subscription.current_period_start
            )
        
        if stripe_subscription.current_period_end:
            self.current_period_end = datetime.fromtimestamp(
                stripe_subscription.current_period_end
            )
        
        if stripe_subscription.trial_start:
            self.trial_start = datetime.fromtimestamp(
                stripe_subscription.trial_start
            )
        
        if stripe_subscription.trial_end:
            self.trial_end = datetime.fromtimestamp(
                stripe_subscription.trial_end
            )
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """String representation of the subscription."""
        return f'<Subscription {self.tenant_id} - {self.plan.name if self.plan else "Unknown"}>'


class PaymentMethod(db.Model):
    """
    Payment method model for storing customer payment information.
    """
    
    __tablename__ = 'payment_methods'
    
    # Primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tenant relationship
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Stripe integration
    stripe_payment_method_id = db.Column(db.String(255), unique=True, nullable=False)
    stripe_customer_id = db.Column(db.String(255), nullable=False)
    
    # Payment method details
    type = db.Column(db.String(50), nullable=False)  # card, bank_account, etc.
    brand = db.Column(db.String(50), nullable=True)  # visa, mastercard, etc.
    last4 = db.Column(db.String(4), nullable=True)
    exp_month = db.Column(db.Integer, nullable=True)
    exp_year = db.Column(db.Integer, nullable=True)
    
    # Status
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, tenant_id, stripe_payment_method_id, stripe_customer_id, **kwargs):
        """Initialize a new payment method."""
        self.tenant_id = tenant_id
        self.stripe_payment_method_id = stripe_payment_method_id
        self.stripe_customer_id = stripe_customer_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert payment method to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'stripe_payment_method_id': self.stripe_payment_method_id,
            'type': self.type,
            'brand': self.brand,
            'last4': self.last4,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_as_default(self):
        """Set this payment method as default for the tenant."""
        # Remove default flag from other payment methods
        PaymentMethod.query.filter_by(
            tenant_id=self.tenant_id,
            is_default=True
        ).update({'is_default': False})
        
        # Set this as default
        self.is_default = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """String representation of the payment method."""
        return f'<PaymentMethod {self.brand} ****{self.last4}>'


# Default subscription plans
DEFAULT_PLANS = [
    {
        'name': 'Free',
        'description': 'Perfect for getting started with social media automation',
        'price': 0.00,
        'max_posts_per_week': 5,
        'max_campaigns': 1,
        'max_users': 1,
        'max_platforms': 3,
        'features': {
            'content_generation': True,
            'basic_analytics': True,
            'email_support': True,
            'api_access': False,
            'advanced_analytics': False,
            'priority_support': False,
            'custom_branding': False,
            'webhook_integrations': False
        }
    },
    {
        'name': 'Premium',
        'description': 'Advanced features for growing businesses',
        'price': 20.00,
        'max_posts_per_week': 20,
        'max_campaigns': 10,
        'max_users': 5,
        'max_platforms': 5,
        'features': {
            'content_generation': True,
            'basic_analytics': True,
            'advanced_analytics': True,
            'email_support': True,
            'priority_support': True,
            'api_access': True,
            'custom_branding': True,
            'webhook_integrations': True,
            'a_b_testing': True,
            'advanced_scheduling': True
        }
    }
]

def create_default_plans():
    """Create default subscription plans if they don't exist."""
    for plan_data in DEFAULT_PLANS:
        existing_plan = SubscriptionPlan.query.filter_by(name=plan_data['name']).first()
        if not existing_plan:
            plan = SubscriptionPlan(**plan_data)
            db.session.add(plan)
    
    db.session.commit()

