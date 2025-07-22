"""
Authentication Routes

API endpoints for user authentication, registration, and session management
in the SaaS platform.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import re

from src.models.user import User, db
from src.models.tenant import Tenant, TenantSettings
from src.models.api_key import APIKey, APIKeyScopes, APIKeyPermissions

auth_bp = Blueprint('auth', __name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user and tenant.
    
    Creates both a new tenant (organization) and the first admin user.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'company_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': 'Missing required field',
                    'field': field,
                    'message': f'{field} is required'
                }), 400
        
        # Validate email format
        if not EMAIL_REGEX.match(data['email']):
            return jsonify({
                'error': 'Invalid email format',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': 'User already exists',
                'message': 'An account with this email already exists'
            }), 409
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({
                'error': 'Weak password',
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        # Create tenant first
        tenant_data = {
            'industry': data.get('industry'),
            'company_size': data.get('company_size'),
            'country': data.get('country'),
            'timezone': data.get('timezone', 'UTC')
        }
        
        tenant = Tenant(name=data['company_name'], **tenant_data)
        tenant.settings = TenantSettings.get_default_settings()
        
        db.session.add(tenant)
        db.session.flush()  # Get tenant ID
        
        # Create admin user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            tenant_id=tenant.id,
            role='admin',
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        
        # Update tenant user count
        tenant.current_users = 1
        
        db.session.commit()
        
        # Create access tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': tenant.id,
                'role': user.role,
                'email': user.email
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'tenant': tenant.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return access tokens.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Email and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'error': 'Account disabled',
                'message': 'Your account has been disabled'
            }), 403
        
        # Check if tenant is active
        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.is_active:
            return jsonify({
                'error': 'Account suspended',
                'message': 'Your organization account has been suspended'
            }), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        tenant.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Create access tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': tenant.id,
                'role': user.role,
                'email': user.email
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'tenant': tenant.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'message': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'error': 'Invalid user',
                'message': 'User not found or inactive'
            }), 401
        
        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.is_active:
            return jsonify({
                'error': 'Account suspended',
                'message': 'Organization account is suspended'
            }), 403
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': tenant.id,
                'role': user.role,
                'email': user.email
            }
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Token refresh failed',
            'message': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client-side token removal).
    """
    # In a production system, you might want to blacklist the token
    return jsonify({
        'message': 'Logout successful'
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile information.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'Current user not found'
            }), 404
        
        tenant = Tenant.query.get(user.tenant_id)
        
        return jsonify({
            'user': user.to_dict(),
            'tenant': tenant.to_dict() if tenant else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Profile retrieval failed',
            'message': str(e)
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user profile information.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'Current user not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone', 'preferences']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Profile update failed',
            'message': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'Current user not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                'error': 'Missing passwords',
                'message': 'Current password and new password are required'
            }), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({
                'error': 'Invalid password',
                'message': 'Current password is incorrect'
            }), 401
        
        # Validate new password
        new_password = data['new_password']
        if len(new_password) < 8:
            return jsonify({
                'error': 'Weak password',
                'message': 'New password must be at least 8 characters long'
            }), 400
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Password change failed',
            'message': str(e)
        }), 500

@auth_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def list_api_keys():
    """
    List API keys for the current tenant.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        api_keys = APIKey.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        
        return jsonify({
            'api_keys': [key.to_dict() for key in api_keys]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'API key listing failed',
            'message': str(e)
        }), 500

@auth_bp.route('/api-keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """
    Create a new API key for external integrations.
    """
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'error': 'Missing name',
                'message': 'API key name is required'
            }), 400
        
        # Create API key
        api_key = APIKey(
            name=data['name'],
            description=data.get('description'),
            tenant_id=tenant_id,
            created_by_user_id=current_user_id,
            scopes=data.get('scopes', APIKeyScopes.get_read_only_scopes()),
            permissions=data.get('permissions', APIKeyPermissions.get_read_only_permissions()),
            rate_limit_per_hour=data.get('rate_limit_per_hour', 1000),
            rate_limit_per_day=data.get('rate_limit_per_day', 10000),
            allowed_ips=data.get('allowed_ips', []),
            allowed_domains=data.get('allowed_domains', [])
        )
        
        # Set expiry if provided
        if data.get('expires_in_days'):
            api_key.expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])
        
        db.session.add(api_key)
        db.session.commit()
        
        return jsonify({
            'message': 'API key created successfully',
            'api_key': api_key.to_dict(include_sensitive=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'API key creation failed',
            'message': str(e)
        }), 500

@auth_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@jwt_required()
def revoke_api_key(key_id):
    """
    Revoke an API key.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        api_key = APIKey.query.filter_by(id=key_id, tenant_id=tenant_id).first()
        
        if not api_key:
            return jsonify({
                'error': 'API key not found',
                'message': 'API key not found or access denied'
            }), 404
        
        api_key.revoke()
        
        return jsonify({
            'message': 'API key revoked successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'API key revocation failed',
            'message': str(e)
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """
    Verify if the current token is valid.
    """
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({
                'valid': False,
                'message': 'Invalid or inactive user'
            }), 401
        
        tenant = Tenant.query.get(claims.get('tenant_id'))
        if not tenant or not tenant.is_active:
            return jsonify({
                'valid': False,
                'message': 'Invalid or inactive tenant'
            }), 401
        
        return jsonify({
            'valid': True,
            'user_id': current_user_id,
            'tenant_id': claims.get('tenant_id'),
            'role': claims.get('role'),
            'email': claims.get('email')
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': str(e)
        }), 401

