"""
External Integration Routes

API endpoints for external system integrations including webhooks,
notifications, email services, and data export functionality.
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
import requests
import json
import csv
import io
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import uuid

from src.models.tenant import Tenant
from src.models.subscription import Subscription
from src.models.analytics import ContentFeedback, SocialMediaMetrics
from src.models.social_connections import SocialConnection

external_bp = Blueprint('external', __name__)

# Webhook storage (in production, use a proper database)
WEBHOOKS = {}

@external_bp.route('/webhooks', methods=['GET'])
@jwt_required()
def get_webhooks():
    """
    Get all webhooks for the current tenant.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        tenant_webhooks = [
            webhook for webhook in WEBHOOKS.values() 
            if webhook.get('tenant_id') == tenant_id
        ]
        
        return jsonify({
            'webhooks': tenant_webhooks
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve webhooks',
            'message': str(e)
        }), 500

@external_bp.route('/webhooks', methods=['POST'])
@jwt_required()
def create_webhook():
    """
    Create a new webhook for external notifications.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        required_fields = ['url', 'events']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'{field} is required'
                }), 400
        
        # Validate URL
        url = data['url']
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'error': 'Invalid URL',
                'message': 'URL must start with http:// or https://'
            }), 400
        
        # Validate events
        valid_events = [
            'content.approved', 'content.rejected', 'content.posted',
            'campaign.created', 'campaign.completed', 'subscription.updated',
            'analytics.weekly_report', 'error.occurred'
        ]
        
        events = data['events']
        if not isinstance(events, list) or not events:
            return jsonify({
                'error': 'Invalid events',
                'message': 'Events must be a non-empty list'
            }), 400
        
        for event in events:
            if event not in valid_events:
                return jsonify({
                    'error': 'Invalid event',
                    'message': f'Event {event} is not supported. Valid events: {valid_events}'
                }), 400
        
        # Create webhook
        webhook_id = str(uuid.uuid4())
        webhook = {
            'id': webhook_id,
            'tenant_id': tenant_id,
            'url': url,
            'events': events,
            'name': data.get('name', f'Webhook {webhook_id[:8]}'),
            'description': data.get('description', ''),
            'secret': data.get('secret', ''),
            'is_active': data.get('is_active', True),
            'headers': data.get('headers', {}),
            'retry_count': data.get('retry_count', 3),
            'timeout': data.get('timeout', 30),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'last_triggered': None,
            'success_count': 0,
            'failure_count': 0
        }
        
        WEBHOOKS[webhook_id] = webhook
        
        return jsonify({
            'message': 'Webhook created successfully',
            'webhook': webhook
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create webhook',
            'message': str(e)
        }), 500

@external_bp.route('/webhooks/<webhook_id>', methods=['PUT'])
@jwt_required()
def update_webhook(webhook_id):
    """
    Update an existing webhook.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if webhook_id not in WEBHOOKS:
            return jsonify({
                'error': 'Webhook not found',
                'message': 'Invalid webhook ID'
            }), 404
        
        webhook = WEBHOOKS[webhook_id]
        if webhook['tenant_id'] != tenant_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You do not have access to this webhook'
            }), 403
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = ['url', 'events', 'name', 'description', 'secret', 'is_active', 'headers', 'retry_count', 'timeout']
        for field in updatable_fields:
            if field in data:
                webhook[field] = data[field]
        
        webhook['updated_at'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'message': 'Webhook updated successfully',
            'webhook': webhook
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update webhook',
            'message': str(e)
        }), 500

@external_bp.route('/webhooks/<webhook_id>', methods=['DELETE'])
@jwt_required()
def delete_webhook(webhook_id):
    """
    Delete a webhook.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if webhook_id not in WEBHOOKS:
            return jsonify({
                'error': 'Webhook not found',
                'message': 'Invalid webhook ID'
            }), 404
        
        webhook = WEBHOOKS[webhook_id]
        if webhook['tenant_id'] != tenant_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You do not have access to this webhook'
            }), 403
        
        del WEBHOOKS[webhook_id]
        
        return jsonify({
            'message': 'Webhook deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete webhook',
            'message': str(e)
        }), 500

@external_bp.route('/webhooks/<webhook_id>/test', methods=['POST'])
@jwt_required()
def test_webhook(webhook_id):
    """
    Test a webhook by sending a test payload.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if webhook_id not in WEBHOOKS:
            return jsonify({
                'error': 'Webhook not found',
                'message': 'Invalid webhook ID'
            }), 404
        
        webhook = WEBHOOKS[webhook_id]
        if webhook['tenant_id'] != tenant_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You do not have access to this webhook'
            }), 403
        
        # Send test payload
        test_payload = {
            'event': 'webhook.test',
            'timestamp': datetime.utcnow().isoformat(),
            'tenant_id': tenant_id,
            'data': {
                'message': 'This is a test webhook payload',
                'webhook_id': webhook_id
            }
        }
        
        success = trigger_webhook(webhook, test_payload)
        
        return jsonify({
            'message': 'Webhook test completed',
            'success': success,
            'payload': test_payload
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to test webhook',
            'message': str(e)
        }), 500

@external_bp.route('/notifications', methods=['POST'])
@jwt_required()
def send_notification():
    """
    Send a notification via email or webhook.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        required_fields = ['type', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'{field} is required'
                }), 400
        
        notification_type = data['type']  # 'email', 'webhook', 'both'
        message = data['message']
        subject = data.get('subject', 'Social Media Agent Notification')
        recipients = data.get('recipients', [])
        
        results = []
        
        # Send email notification
        if notification_type in ['email', 'both']:
            if not recipients:
                # Get tenant admin email
                tenant = Tenant.query.get(tenant_id)
                if tenant and tenant.billing_email:
                    recipients = [tenant.billing_email]
            
            if recipients:
                email_result = send_email_notification(
                    recipients=recipients,
                    subject=subject,
                    message=message,
                    tenant_id=tenant_id
                )
                results.append({
                    'type': 'email',
                    'success': email_result['success'],
                    'message': email_result['message']
                })
        
        # Send webhook notification
        if notification_type in ['webhook', 'both']:
            webhook_payload = {
                'event': 'notification.sent',
                'timestamp': datetime.utcnow().isoformat(),
                'tenant_id': tenant_id,
                'data': {
                    'subject': subject,
                    'message': message,
                    'type': notification_type
                }
            }
            
            webhook_results = trigger_tenant_webhooks(tenant_id, 'notification.sent', webhook_payload)
            results.extend(webhook_results)
        
        return jsonify({
            'message': 'Notification sent',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to send notification',
            'message': str(e)
        }), 500

@external_bp.route('/export', methods=['POST'])
@jwt_required()
def export_data():
    """
    Export data in various formats (CSV, JSON).
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        export_type = data.get('type', 'feedback')  # feedback, metrics, connections
        format_type = data.get('format', 'csv')  # csv, json
        date_range = data.get('date_range', 30)  # days
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=date_range)
        
        # Export data based on type
        if export_type == 'feedback':
            export_data = export_feedback_data(tenant_id, start_date, end_date, format_type)
        elif export_type == 'metrics':
            export_data = export_metrics_data(tenant_id, start_date, end_date, format_type)
        elif export_type == 'connections':
            export_data = export_connections_data(tenant_id, format_type)
        else:
            return jsonify({
                'error': 'Invalid export type',
                'message': 'Supported types: feedback, metrics, connections'
            }), 400
        
        if not export_data:
            return jsonify({
                'error': 'No data to export',
                'message': f'No {export_type} data found for the specified period'
            }), 404
        
        # Create file
        filename = f"{export_type}_{tenant_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format_type}"
        
        if format_type == 'csv':
            return send_csv_response(export_data, filename)
        else:
            return send_json_response(export_data, filename)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to export data',
            'message': str(e)
        }), 500

@external_bp.route('/integrations/slack', methods=['POST'])
@jwt_required()
def slack_integration():
    """
    Send notifications to Slack.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        webhook_url = data.get('webhook_url')
        message = data.get('message')
        channel = data.get('channel', '#general')
        
        if not webhook_url or not message:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'webhook_url and message are required'
            }), 400
        
        # Send to Slack
        slack_payload = {
            'channel': channel,
            'text': message,
            'username': 'Social Media Agent',
            'icon_emoji': ':robot_face:'
        }
        
        response = requests.post(
            webhook_url,
            json=slack_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify({
                'message': 'Slack notification sent successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send Slack notification',
                'message': f'Slack API returned status {response.status_code}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to send Slack notification',
            'message': str(e)
        }), 500

@external_bp.route('/integrations/discord', methods=['POST'])
@jwt_required()
def discord_integration():
    """
    Send notifications to Discord.
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        webhook_url = data.get('webhook_url')
        message = data.get('message')
        
        if not webhook_url or not message:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'webhook_url and message are required'
            }), 400
        
        # Send to Discord
        discord_payload = {
            'content': message,
            'username': 'Social Media Agent'
        }
        
        response = requests.post(
            webhook_url,
            json=discord_payload,
            timeout=30
        )
        
        if response.status_code == 204:
            return jsonify({
                'message': 'Discord notification sent successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send Discord notification',
                'message': f'Discord API returned status {response.status_code}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to send Discord notification',
            'message': str(e)
        }), 500

def trigger_webhook(webhook, payload):
    """
    Trigger a single webhook with payload.
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Social-Media-Agent-Webhook/1.0'
        }
        
        # Add custom headers
        if webhook.get('headers'):
            headers.update(webhook['headers'])
        
        # Add signature if secret is provided
        if webhook.get('secret'):
            import hmac
            import hashlib
            
            signature = hmac.new(
                webhook['secret'].encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f'sha256={signature}'
        
        response = requests.post(
            webhook['url'],
            json=payload,
            headers=headers,
            timeout=webhook.get('timeout', 30)
        )
        
        # Update webhook stats
        webhook['last_triggered'] = datetime.utcnow().isoformat()
        
        if response.status_code == 200:
            webhook['success_count'] += 1
            return True
        else:
            webhook['failure_count'] += 1
            return False
            
    except Exception as e:
        webhook['failure_count'] += 1
        current_app.logger.error(f"Webhook trigger failed: {str(e)}")
        return False

def trigger_tenant_webhooks(tenant_id, event, payload):
    """
    Trigger all webhooks for a tenant that listen to a specific event.
    """
    results = []
    
    for webhook in WEBHOOKS.values():
        if (webhook.get('tenant_id') == tenant_id and 
            webhook.get('is_active', True) and 
            event in webhook.get('events', [])):
            
            success = trigger_webhook(webhook, payload)
            results.append({
                'type': 'webhook',
                'webhook_id': webhook['id'],
                'success': success,
                'message': 'Webhook triggered successfully' if success else 'Webhook trigger failed'
            })
    
    return results

def send_email_notification(recipients, subject, message, tenant_id):
    """
    Send email notification using SMTP.
    """
    try:
        # Email configuration (should be in environment variables)
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        from_email = os.environ.get('FROM_EMAIL', smtp_username)
        
        if not smtp_username or not smtp_password:
            return {
                'success': False,
                'message': 'SMTP credentials not configured'
            }
        
        # Create message
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MimeText(message, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        text = msg.as_string()
        server.sendmail(from_email, recipients, text)
        server.quit()
        
        return {
            'success': True,
            'message': f'Email sent to {len(recipients)} recipients'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }

def export_feedback_data(tenant_id, start_date, end_date, format_type):
    """
    Export content feedback data.
    """
    try:
        feedback_records = ContentFeedback.query.filter(
            ContentFeedback.tenant_id == tenant_id,
            ContentFeedback.created_at >= start_date,
            ContentFeedback.created_at <= end_date
        ).all()
        
        if format_type == 'csv':
            return [
                {
                    'Date': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Platform': record.platform,
                    'Content Type': record.content_type,
                    'Feedback Type': record.feedback_type,
                    'Content': record.content_text[:100] + '...' if record.content_text and len(record.content_text) > 100 else record.content_text,
                    'Predicted Engagement': record.predicted_engagement,
                    'Industry': record.industry,
                    'Brand Voice': record.brand_voice
                }
                for record in feedback_records
            ]
        else:
            return [record.to_dict() for record in feedback_records]
            
    except Exception as e:
        current_app.logger.error(f"Failed to export feedback data: {str(e)}")
        return []

def export_metrics_data(tenant_id, start_date, end_date, format_type):
    """
    Export social media metrics data.
    """
    try:
        metrics_records = SocialMediaMetrics.query.filter(
            SocialMediaMetrics.tenant_id == tenant_id,
            SocialMediaMetrics.created_at >= start_date,
            SocialMediaMetrics.created_at <= end_date
        ).all()
        
        if format_type == 'csv':
            return [
                {
                    'Date': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Platform': record.platform,
                    'Likes': record.likes,
                    'Shares': record.shares,
                    'Comments': record.comments,
                    'Views': record.views,
                    'Engagement Rate': record.engagement_rate,
                    'Reach': record.reach,
                    'Impressions': record.impressions
                }
                for record in metrics_records
            ]
        else:
            return [record.to_dict() for record in metrics_records]
            
    except Exception as e:
        current_app.logger.error(f"Failed to export metrics data: {str(e)}")
        return []

def export_connections_data(tenant_id, format_type):
    """
    Export social media connections data.
    """
    try:
        connections = SocialConnection.get_active_connections(tenant_id)
        
        if format_type == 'csv':
            return [
                {
                    'Platform': conn.platform,
                    'Username': conn.platform_username,
                    'Display Name': conn.platform_display_name,
                    'Connected Date': conn.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Posts Count': conn.posts_count,
                    'Last Post': conn.last_post_at.strftime('%Y-%m-%d %H:%M:%S') if conn.last_post_at else 'Never',
                    'Is Verified': conn.is_verified,
                    'Status': 'Active' if conn.is_active else 'Inactive'
                }
                for conn in connections
            ]
        else:
            return [conn.to_dict() for conn in connections]
            
    except Exception as e:
        current_app.logger.error(f"Failed to export connections data: {str(e)}")
        return []

def send_csv_response(data, filename):
    """
    Send CSV data as file response.
    """
    output = io.StringIO()
    
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

def send_json_response(data, filename):
    """
    Send JSON data as file response.
    """
    output = io.BytesIO()
    output.write(json.dumps(data, indent=2, default=str).encode())
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

