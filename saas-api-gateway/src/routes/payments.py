"""
Payment Routes

API endpoints for subscription management and Stripe integration
for the SaaS platform.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
import stripe
import os

from src.models.subscription import (
    SubscriptionPlan, Subscription, PaymentMethod, 
    create_default_plans, db
)
from src.models.tenant import Tenant

payments_bp = Blueprint('payments', __name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

@payments_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """
    Get all available subscription plans.
    """
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve plans',
            'message': str(e)
        }), 500

@payments_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """
    Get current subscription status for the tenant.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        subscription = Subscription.query.filter_by(
            tenant_id=tenant_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            # Create free subscription if none exists
            free_plan = SubscriptionPlan.get_free_plan()
            if free_plan:
                subscription = Subscription(
                    tenant_id=tenant_id,
                    plan_id=free_plan.id,
                    status='active'
                )
                db.session.add(subscription)
                db.session.commit()
        
        return jsonify({
            'subscription': subscription.to_dict() if subscription else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve subscription',
            'message': str(e)
        }), 500

@payments_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """
    Create a Stripe payment intent for subscription.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({
                'error': 'Missing plan ID',
                'message': 'plan_id is required'
            }), 400
        
        # Get the plan
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({
                'error': 'Plan not found',
                'message': 'Invalid plan ID'
            }), 404
        
        # Get tenant for customer info
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({
                'error': 'Tenant not found',
                'message': 'Invalid tenant'
            }), 404
        
        # Create or get Stripe customer
        stripe_customer = None
        existing_subscription = Subscription.query.filter_by(tenant_id=tenant_id).first()
        
        if existing_subscription and existing_subscription.stripe_customer_id:
            try:
                stripe_customer = stripe.Customer.retrieve(existing_subscription.stripe_customer_id)
            except stripe.error.StripeError:
                stripe_customer = None
        
        if not stripe_customer:
            stripe_customer = stripe.Customer.create(
                email=tenant.billing_email or f"billing@{tenant.name.lower().replace(' ', '')}.com",
                name=tenant.name,
                metadata={
                    'tenant_id': tenant_id,
                    'tenant_name': tenant.name
                }
            )
        
        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(plan.price * 100),  # Convert to cents
            currency=plan.currency.lower(),
            customer=stripe_customer.id,
            metadata={
                'tenant_id': tenant_id,
                'plan_id': plan_id,
                'plan_name': plan.name
            },
            automatic_payment_methods={
                'enabled': True
            }
        )
        
        return jsonify({
            'client_secret': payment_intent.client_secret,
            'customer_id': stripe_customer.id,
            'amount': plan.price,
            'currency': plan.currency
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Stripe error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Payment intent creation failed',
            'message': str(e)
        }), 500

@payments_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def create_subscription():
    """
    Create a new subscription after successful payment.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        payment_method_id = data.get('payment_method_id')
        
        if not plan_id:
            return jsonify({
                'error': 'Missing plan ID',
                'message': 'plan_id is required'
            }), 400
        
        # Get the plan
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({
                'error': 'Plan not found',
                'message': 'Invalid plan ID'
            }), 404
        
        # Get tenant
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({
                'error': 'Tenant not found',
                'message': 'Invalid tenant'
            }), 404
        
        # Handle free plan
        if plan.price == 0:
            # Cancel existing subscription if any
            existing_subscription = Subscription.query.filter_by(
                tenant_id=tenant_id,
                status='active'
            ).first()
            
            if existing_subscription:
                existing_subscription.cancel()
            
            # Create free subscription
            subscription = Subscription(
                tenant_id=tenant_id,
                plan_id=plan_id,
                status='active',
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            return jsonify({
                'message': 'Free subscription created successfully',
                'subscription': subscription.to_dict()
            }), 201
        
        # Handle paid plan with Stripe
        if not payment_method_id:
            return jsonify({
                'error': 'Missing payment method',
                'message': 'payment_method_id is required for paid plans'
            }), 400
        
        # Get or create Stripe customer
        stripe_customer = None
        existing_subscription = Subscription.query.filter_by(tenant_id=tenant_id).first()
        
        if existing_subscription and existing_subscription.stripe_customer_id:
            try:
                stripe_customer = stripe.Customer.retrieve(existing_subscription.stripe_customer_id)
            except stripe.error.StripeError:
                stripe_customer = None
        
        if not stripe_customer:
            stripe_customer = stripe.Customer.create(
                email=tenant.billing_email or f"billing@{tenant.name.lower().replace(' ', '')}.com",
                name=tenant.name,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                },
                metadata={
                    'tenant_id': tenant_id,
                    'tenant_name': tenant.name
                }
            )
        else:
            # Attach payment method to existing customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer.id
            )
            
            # Update default payment method
            stripe.Customer.modify(
                stripe_customer.id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer.id,
            items=[{
                'price': plan.stripe_price_id
            }] if plan.stripe_price_id else [{
                'price_data': {
                    'currency': plan.currency.lower(),
                    'product_data': {
                        'name': plan.name,
                        'description': plan.description
                    },
                    'unit_amount': int(plan.price * 100),
                    'recurring': {
                        'interval': plan.billing_interval
                    }
                }
            }],
            metadata={
                'tenant_id': tenant_id,
                'plan_id': plan_id
            },
            expand=['latest_invoice.payment_intent']
        )
        
        # Cancel existing subscription if any
        existing_subscription = Subscription.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).first()
        
        if existing_subscription and existing_subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(existing_subscription.stripe_subscription_id)
            except stripe.error.StripeError:
                pass
            existing_subscription.cancel()
        
        # Create new subscription record
        subscription = Subscription(
            tenant_id=tenant_id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=stripe_customer.id,
            stripe_payment_method_id=payment_method_id,
            status=stripe_subscription.status
        )
        
        subscription.update_from_stripe(stripe_subscription)
        
        db.session.add(subscription)
        db.session.commit()
        
        # Store payment method
        payment_method = PaymentMethod(
            tenant_id=tenant_id,
            stripe_payment_method_id=payment_method_id,
            stripe_customer_id=stripe_customer.id,
            is_default=True
        )
        
        # Get payment method details from Stripe
        try:
            stripe_pm = stripe.PaymentMethod.retrieve(payment_method_id)
            if stripe_pm.card:
                payment_method.type = 'card'
                payment_method.brand = stripe_pm.card.brand
                payment_method.last4 = stripe_pm.card.last4
                payment_method.exp_month = stripe_pm.card.exp_month
                payment_method.exp_year = stripe_pm.card.exp_year
        except stripe.error.StripeError:
            pass
        
        db.session.add(payment_method)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription.to_dict(),
            'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret if stripe_subscription.latest_invoice.payment_intent else None
        }), 201
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Stripe error',
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Subscription creation failed',
            'message': str(e)
        }), 500

@payments_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """
    Cancel the current subscription.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        subscription = Subscription.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({
                'error': 'No active subscription',
                'message': 'No active subscription found'
            }), 404
        
        # Cancel Stripe subscription if exists
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            except stripe.error.StripeError as e:
                return jsonify({
                    'error': 'Stripe cancellation failed',
                    'message': str(e)
                }), 400
        
        # Cancel local subscription
        subscription.cancel()
        
        # Create free subscription
        free_plan = SubscriptionPlan.get_free_plan()
        if free_plan:
            free_subscription = Subscription(
                tenant_id=tenant_id,
                plan_id=free_plan.id,
                status='active',
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            
            db.session.add(free_subscription)
            db.session.commit()
        
        return jsonify({
            'message': 'Subscription canceled successfully',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Subscription cancellation failed',
            'message': str(e)
        }), 500

@payments_bp.route('/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """
    Get payment methods for the current tenant.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        payment_methods = PaymentMethod.query.filter_by(
            tenant_id=tenant_id,
            is_active=True
        ).all()
        
        return jsonify({
            'payment_methods': [pm.to_dict() for pm in payment_methods]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve payment methods',
            'message': str(e)
        }), 500

@payments_bp.route('/payment-method', methods=['PUT'])
@jwt_required()
def update_payment_method():
    """
    Update the default payment method.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        payment_method_id = data.get('payment_method_id')
        
        if not payment_method_id:
            return jsonify({
                'error': 'Missing payment method ID',
                'message': 'payment_method_id is required'
            }), 400
        
        # Find the payment method
        payment_method = PaymentMethod.query.filter_by(
            tenant_id=tenant_id,
            stripe_payment_method_id=payment_method_id,
            is_active=True
        ).first()
        
        if not payment_method:
            return jsonify({
                'error': 'Payment method not found',
                'message': 'Invalid payment method ID'
            }), 404
        
        # Set as default
        payment_method.set_as_default()
        
        # Update Stripe customer default payment method
        subscription = Subscription.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).first()
        
        if subscription and subscription.stripe_customer_id:
            try:
                stripe.Customer.modify(
                    subscription.stripe_customer_id,
                    invoice_settings={
                        'default_payment_method': payment_method_id
                    }
                )
            except stripe.error.StripeError as e:
                return jsonify({
                    'error': 'Stripe update failed',
                    'message': str(e)
                }), 400
        
        return jsonify({
            'message': 'Payment method updated successfully',
            'payment_method': payment_method.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Payment method update failed',
            'message': str(e)
        }), 500

@payments_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_usage_stats():
    """
    Get usage statistics for the current subscription.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        subscription = Subscription.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({
                'error': 'No active subscription',
                'message': 'No active subscription found'
            }), 404
        
        usage_stats = {
            'current_plan': subscription.plan.to_dict() if subscription.plan else None,
            'posts_this_week': subscription.posts_this_week,
            'posts_remaining': subscription.get_remaining_posts(),
            'usage_percentage': subscription.get_usage_percentage(),
            'week_start_date': subscription.week_start_date.isoformat() if subscription.week_start_date else None,
            'can_post': subscription.can_post(),
            'days_until_renewal': subscription.days_until_renewal()
        }
        
        return jsonify({
            'usage': usage_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve usage stats',
            'message': str(e)
        }), 500

@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhooks for subscription events.
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    
    return jsonify({'status': 'success'}), 200

def handle_payment_succeeded(invoice):
    """Handle successful payment."""
    subscription_id = invoice.get('subscription')
    if subscription_id:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = 'active'
            db.session.commit()

def handle_payment_failed(invoice):
    """Handle failed payment."""
    subscription_id = invoice.get('subscription')
    if subscription_id:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = 'past_due'
            db.session.commit()

def handle_subscription_updated(stripe_subscription):
    """Handle subscription update."""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription['id']
    ).first()
    
    if subscription:
        subscription.update_from_stripe(stripe_subscription)

def handle_subscription_deleted(stripe_subscription):
    """Handle subscription deletion."""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=stripe_subscription['id']
    ).first()
    
    if subscription:
        subscription.cancel()

# Initialize default plans
@payments_bp.before_app_first_request
def initialize_plans():
    """Initialize default subscription plans."""
    create_default_plans()

