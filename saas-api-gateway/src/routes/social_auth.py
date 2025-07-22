"""
Social Media OAuth Routes

API endpoints for managing OAuth authentication with social media platforms
for automated posting and metrics collection.
"""

from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
import requests
import secrets
import urllib.parse
import os

from src.models.social_connections import (
    SocialConnection, OAuthState, get_oauth_config, db
)
from src.models.tenant import Tenant

social_auth_bp = Blueprint('social_auth', __name__)

# OAuth client configurations (should be in environment variables)
OAUTH_CLIENTS = {
    'facebook': {
        'client_id': os.environ.get('FACEBOOK_CLIENT_ID'),
        'client_secret': os.environ.get('FACEBOOK_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/api/v1/social/auth/facebook/callback')
    },
    'twitter': {
        'client_id': os.environ.get('TWITTER_CLIENT_ID'),
        'client_secret': os.environ.get('TWITTER_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('TWITTER_REDIRECT_URI', 'http://localhost:5000/api/v1/social/auth/twitter/callback')
    },
    'linkedin': {
        'client_id': os.environ.get('LINKEDIN_CLIENT_ID'),
        'client_secret': os.environ.get('LINKEDIN_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/api/v1/social/auth/linkedin/callback')
    },
    'instagram': {
        'client_id': os.environ.get('INSTAGRAM_CLIENT_ID'),
        'client_secret': os.environ.get('INSTAGRAM_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('INSTAGRAM_REDIRECT_URI', 'http://localhost:5000/api/v1/social/auth/instagram/callback')
    },
    'tiktok': {
        'client_id': os.environ.get('TIKTOK_CLIENT_ID'),
        'client_secret': os.environ.get('TIKTOK_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('TIKTOK_REDIRECT_URI', 'http://localhost:5000/api/v1/social/auth/tiktok/callback')
    }
}

@social_auth_bp.route('/connections', methods=['GET'])
@jwt_required()
def get_social_connections():
    """
    Get all social media connections for the current tenant.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        connections = SocialConnection.get_active_connections(tenant_id)
        
        return jsonify({
            'connections': [conn.to_dict() for conn in connections]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve connections',
            'message': str(e)
        }), 500

@social_auth_bp.route('/connections/<platform>', methods=['GET'])
@jwt_required()
def get_platform_connection(platform):
    """
    Get connection details for a specific platform.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        connection = SocialConnection.get_connection(tenant_id, platform.lower())
        
        if not connection:
            return jsonify({
                'error': 'Connection not found',
                'message': f'No active connection found for {platform}'
            }), 404
        
        return jsonify({
            'connection': connection.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve connection',
            'message': str(e)
        }), 500

@social_auth_bp.route('/auth/<platform>/initiate', methods=['POST'])
@jwt_required()
def initiate_oauth(platform):
    """
    Initiate OAuth flow for a social media platform.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        platform = platform.lower()
        
        # Check if platform is supported
        if platform not in OAUTH_CLIENTS:
            return jsonify({
                'error': 'Unsupported platform',
                'message': f'Platform {platform} is not supported'
            }), 400
        
        # Get OAuth configuration
        oauth_config = get_oauth_config(platform)
        client_config = OAUTH_CLIENTS[platform]
        
        if not client_config['client_id'] or not client_config['client_secret']:
            return jsonify({
                'error': 'OAuth not configured',
                'message': f'OAuth credentials not configured for {platform}'
            }), 500
        
        # Generate state parameter
        state = secrets.token_urlsafe(32)
        
        # Store OAuth state
        oauth_state = OAuthState(
            state=state,
            tenant_id=tenant_id,
            platform=platform,
            redirect_uri=client_config['redirect_uri'],
            scopes=oauth_config.get('required_scopes', [])
        )
        
        db.session.add(oauth_state)
        db.session.commit()
        
        # Build authorization URL
        auth_params = {
            'client_id': client_config['client_id'],
            'redirect_uri': client_config['redirect_uri'],
            'state': state,
            'response_type': 'code'
        }
        
        # Add platform-specific parameters
        if platform == 'facebook':
            auth_params['scope'] = ','.join(oauth_config['required_scopes'])
        elif platform == 'twitter':
            auth_params['scope'] = ' '.join(oauth_config['required_scopes'])
            auth_params['code_challenge'] = 'challenge'  # PKCE for Twitter
            auth_params['code_challenge_method'] = 'plain'
        elif platform == 'linkedin':
            auth_params['scope'] = ' '.join(oauth_config['required_scopes'])
        elif platform == 'instagram':
            auth_params['scope'] = ','.join(oauth_config['required_scopes'])
        elif platform == 'tiktok':
            auth_params['scope'] = ','.join(oauth_config['required_scopes'])
        
        auth_url = f"{oauth_config['auth_url']}?{urllib.parse.urlencode(auth_params)}"
        
        return jsonify({
            'auth_url': auth_url,
            'state': state,
            'platform': platform
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to initiate OAuth',
            'message': str(e)
        }), 500

@social_auth_bp.route('/auth/<platform>/callback', methods=['GET', 'POST'])
def oauth_callback(platform):
    """
    Handle OAuth callback from social media platform.
    """
    try:
        platform = platform.lower()
        
        # Get authorization code and state
        code = request.args.get('code') or request.form.get('code')
        state = request.args.get('state') or request.form.get('state')
        error = request.args.get('error')
        
        if error:
            return jsonify({
                'error': 'OAuth authorization failed',
                'message': f'Platform returned error: {error}'
            }), 400
        
        if not code or not state:
            return jsonify({
                'error': 'Missing OAuth parameters',
                'message': 'Authorization code or state parameter missing'
            }), 400
        
        # Validate state
        oauth_state = OAuthState.find_valid_state(state)
        if not oauth_state:
            return jsonify({
                'error': 'Invalid OAuth state',
                'message': 'OAuth state is invalid or expired'
            }), 400
        
        if oauth_state.platform != platform:
            return jsonify({
                'error': 'Platform mismatch',
                'message': 'OAuth state platform does not match callback platform'
            }), 400
        
        # Mark state as used
        oauth_state.mark_used()
        
        # Exchange code for access token
        token_data = exchange_code_for_token(platform, code, oauth_state)
        if not token_data:
            return jsonify({
                'error': 'Token exchange failed',
                'message': 'Failed to exchange authorization code for access token'
            }), 400
        
        # Get user information
        user_info = get_user_info(platform, token_data['access_token'])
        if not user_info:
            return jsonify({
                'error': 'User info retrieval failed',
                'message': 'Failed to retrieve user information from platform'
            }), 400
        
        # Check if connection already exists
        existing_connection = SocialConnection.get_connection(
            oauth_state.tenant_id, 
            platform
        )
        
        if existing_connection:
            # Update existing connection
            existing_connection.update_tokens(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                expires_in=token_data.get('expires_in')
            )
            existing_connection.platform_username = user_info.get('username')
            existing_connection.platform_display_name = user_info.get('display_name')
            existing_connection.platform_data = user_info
            existing_connection.granted_scopes = token_data.get('scope', [])
            existing_connection.verify_connection()
            
            connection = existing_connection
        else:
            # Create new connection
            connection = SocialConnection(
                tenant_id=oauth_state.tenant_id,
                platform=platform,
                platform_user_id=user_info['user_id'],
                access_token=token_data['access_token'],
                platform_username=user_info.get('username'),
                platform_display_name=user_info.get('display_name'),
                platform_data=user_info,
                granted_scopes=token_data.get('scope', []),
                required_scopes=get_oauth_config(platform).get('required_scopes', [])
            )
            
            if token_data.get('refresh_token'):
                connection.set_refresh_token(token_data['refresh_token'])
            
            if token_data.get('expires_in'):
                connection.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=token_data['expires_in']
                )
            
            connection.verify_connection()
            
            db.session.add(connection)
            db.session.commit()
        
        # Redirect to frontend success page
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/social-connections?success=true&platform={platform}")
        
    except Exception as e:
        current_app.logger.error(f"OAuth callback error: {str(e)}")
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/social-connections?error=true&message={urllib.parse.quote(str(e))}")

@social_auth_bp.route('/connections/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_platform(platform):
    """
    Disconnect a social media platform.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        connection = SocialConnection.get_connection(tenant_id, platform.lower())
        
        if not connection:
            return jsonify({
                'error': 'Connection not found',
                'message': f'No active connection found for {platform}'
            }), 404
        
        # Revoke tokens if possible
        try:
            revoke_platform_token(platform.lower(), connection.get_access_token())
        except Exception as e:
            current_app.logger.warning(f"Failed to revoke token for {platform}: {str(e)}")
        
        # Disconnect locally
        connection.disconnect()
        
        return jsonify({
            'message': f'{platform} disconnected successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to disconnect platform',
            'message': str(e)
        }), 500

@social_auth_bp.route('/connections/<platform>/verify', methods=['POST'])
@jwt_required()
def verify_connection(platform):
    """
    Verify a social media connection by testing API access.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        connection = SocialConnection.get_connection(tenant_id, platform.lower())
        
        if not connection:
            return jsonify({
                'error': 'Connection not found',
                'message': f'No active connection found for {platform}'
            }), 404
        
        # Test API access
        is_valid = test_platform_connection(platform.lower(), connection.get_access_token())
        
        if is_valid:
            connection.verify_connection()
            return jsonify({
                'message': f'{platform} connection verified successfully',
                'is_valid': True
            }), 200
        else:
            connection.record_error('Connection verification failed')
            return jsonify({
                'error': 'Connection verification failed',
                'message': f'Unable to verify {platform} connection',
                'is_valid': False
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to verify connection',
            'message': str(e)
        }), 500

def exchange_code_for_token(platform, code, oauth_state):
    """
    Exchange authorization code for access token.
    """
    try:
        oauth_config = get_oauth_config(platform)
        client_config = OAUTH_CLIENTS[platform]
        
        token_data = {
            'client_id': client_config['client_id'],
            'client_secret': client_config['client_secret'],
            'code': code,
            'redirect_uri': client_config['redirect_uri']
        }
        
        if platform == 'facebook':
            token_data['grant_type'] = 'authorization_code'
        elif platform == 'twitter':
            token_data['grant_type'] = 'authorization_code'
            token_data['code_verifier'] = 'challenge'  # PKCE verifier
        elif platform == 'linkedin':
            token_data['grant_type'] = 'authorization_code'
        elif platform in ['instagram', 'tiktok']:
            token_data['grant_type'] = 'authorization_code'
        
        response = requests.post(
            oauth_config['token_url'],
            data=token_data,
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            token_response = response.json()
            
            # Normalize response format
            normalized_token = {
                'access_token': token_response.get('access_token'),
                'refresh_token': token_response.get('refresh_token'),
                'expires_in': token_response.get('expires_in'),
                'scope': token_response.get('scope', '').split() if token_response.get('scope') else []
            }
            
            return normalized_token
        else:
            current_app.logger.error(f"Token exchange failed for {platform}: {response.text}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Token exchange error for {platform}: {str(e)}")
        return None

def get_user_info(platform, access_token):
    """
    Get user information from social media platform.
    """
    try:
        oauth_config = get_oauth_config(platform)
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Platform-specific API calls
        if platform == 'facebook':
            response = requests.get(
                f"{oauth_config['api_base']}/me?fields=id,name,email",
                headers=headers
            )
        elif platform == 'twitter':
            response = requests.get(
                f"{oauth_config['api_base']}/users/me",
                headers=headers
            )
        elif platform == 'linkedin':
            response = requests.get(
                f"{oauth_config['api_base']}/people/~:(id,firstName,lastName,emailAddress)",
                headers=headers
            )
        elif platform == 'instagram':
            response = requests.get(
                f"{oauth_config['api_base']}/me?fields=id,username",
                headers=headers
            )
        elif platform == 'tiktok':
            response = requests.get(
                f"{oauth_config['api_base']}/v1/user/info/",
                headers=headers
            )
        else:
            return None
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Normalize user info format
            if platform == 'facebook':
                return {
                    'user_id': user_data.get('id'),
                    'username': user_data.get('name'),
                    'display_name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'raw_data': user_data
                }
            elif platform == 'twitter':
                data = user_data.get('data', {})
                return {
                    'user_id': data.get('id'),
                    'username': data.get('username'),
                    'display_name': data.get('name'),
                    'raw_data': user_data
                }
            elif platform == 'linkedin':
                return {
                    'user_id': user_data.get('id'),
                    'username': f"{user_data.get('firstName', {}).get('localized', {}).get('en_US', '')} {user_data.get('lastName', {}).get('localized', {}).get('en_US', '')}".strip(),
                    'display_name': f"{user_data.get('firstName', {}).get('localized', {}).get('en_US', '')} {user_data.get('lastName', {}).get('localized', {}).get('en_US', '')}".strip(),
                    'email': user_data.get('emailAddress'),
                    'raw_data': user_data
                }
            elif platform == 'instagram':
                return {
                    'user_id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'display_name': user_data.get('username'),
                    'raw_data': user_data
                }
            elif platform == 'tiktok':
                data = user_data.get('data', {}).get('user', {})
                return {
                    'user_id': data.get('open_id'),
                    'username': data.get('display_name'),
                    'display_name': data.get('display_name'),
                    'raw_data': user_data
                }
        else:
            current_app.logger.error(f"User info retrieval failed for {platform}: {response.text}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"User info error for {platform}: {str(e)}")
        return None

def test_platform_connection(platform, access_token):
    """
    Test if a platform connection is still valid.
    """
    try:
        user_info = get_user_info(platform, access_token)
        return user_info is not None
    except Exception:
        return False

def revoke_platform_token(platform, access_token):
    """
    Revoke access token for a platform (if supported).
    """
    try:
        if platform == 'facebook':
            response = requests.delete(
                f'https://graph.facebook.com/me/permissions',
                params={'access_token': access_token}
            )
            return response.status_code == 200
        elif platform == 'twitter':
            # Twitter OAuth 2.0 doesn't have a revoke endpoint
            return True
        elif platform == 'linkedin':
            # LinkedIn doesn't have a public revoke endpoint
            return True
        elif platform in ['instagram', 'tiktok']:
            # Platform-specific revocation if available
            return True
        
        return True
    except Exception:
        return False

# Cleanup expired OAuth states periodically
@social_auth_bp.before_app_first_request
def cleanup_expired_states():
    """Clean up expired OAuth states."""
    try:
        OAuthState.cleanup_expired()
    except Exception as e:
        current_app.logger.error(f"Failed to cleanup expired OAuth states: {str(e)}")

