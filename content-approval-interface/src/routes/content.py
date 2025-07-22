"""
Content Routes

Flask routes for content suggestion management and approval interface.
"""

from flask import Blueprint, request, jsonify, session
from src.models.content_suggestion import db, ContentSuggestion, UserFeedback, BusinessProfile, ContentBriefing
import uuid
import json
from datetime import datetime

content_bp = Blueprint('content', __name__)


@content_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """Get content suggestions with optional filtering."""
    try:
        # Get query parameters
        status = request.args.get('status', 'pending_review')
        platform = request.args.get('platform')
        content_type = request.args.get('content_type')
        briefing_id = request.args.get('briefing_id')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = ContentSuggestion.query
        
        if status:
            query = query.filter(ContentSuggestion.status == status)
        if platform:
            query = query.filter(ContentSuggestion.platform == platform)
        if content_type:
            query = query.filter(ContentSuggestion.content_type == content_type)
        if briefing_id:
            query = query.filter(ContentSuggestion.briefing_id == briefing_id)
        
        # Order by creation date (newest first)
        query = query.order_by(ContentSuggestion.generated_at.desc())
        
        # Apply pagination
        suggestions = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        # Convert to dictionaries
        suggestions_data = [suggestion.to_dict() for suggestion in suggestions]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions/<suggestion_id>', methods=['GET'])
def get_suggestion(suggestion_id):
    """Get a specific content suggestion."""
    try:
        suggestion = ContentSuggestion.query.get(suggestion_id)
        
        if not suggestion:
            return jsonify({
                'success': False,
                'error': 'Suggestion not found'
            }), 404
        
        return jsonify({
            'success': True,
            'suggestion': suggestion.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions', methods=['POST'])
def create_suggestion():
    """Create a new content suggestion."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        # Create suggestion
        suggestion = ContentSuggestion.from_dict(data)
        
        db.session.add(suggestion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'suggestion': suggestion.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions/<suggestion_id>', methods=['PUT'])
def update_suggestion(suggestion_id):
    """Update a content suggestion."""
    try:
        suggestion = ContentSuggestion.query.get(suggestion_id)
        
        if not suggestion:
            return jsonify({
                'success': False,
                'error': 'Suggestion not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update suggestion
        suggestion.update_from_dict(data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'suggestion': suggestion.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions/<suggestion_id>/feedback', methods=['POST'])
def submit_feedback(suggestion_id):
    """Submit feedback for a content suggestion."""
    try:
        suggestion = ContentSuggestion.query.get(suggestion_id)
        
        if not suggestion:
            return jsonify({
                'success': False,
                'error': 'Suggestion not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No feedback data provided'
            }), 400
        
        feedback_type = data.get('feedback_type')
        if not feedback_type:
            return jsonify({
                'success': False,
                'error': 'Feedback type is required'
            }), 400
        
        # Get or create user session
        if 'user_session' not in session:
            session['user_session'] = str(uuid.uuid4())
        
        # Create feedback record
        feedback = UserFeedback(
            content_suggestion_id=suggestion_id,
            feedback_type=feedback_type,
            feedback_score=data.get('feedback_score'),
            feedback_comments=data.get('feedback_comments'),
            user_id=data.get('user_id'),
            user_session=session['user_session']
        )
        
        db.session.add(feedback)
        
        # Update suggestion based on feedback
        if feedback_type == 'approve':
            suggestion.status = 'approved'
            suggestion.approval_status = 'approved'
        elif feedback_type == 'reject':
            suggestion.status = 'rejected'
            suggestion.approval_status = 'rejected'
        elif feedback_type in ['thumbs_up', 'thumbs_down']:
            # Keep status as pending but record feedback
            suggestion.feedback_score = data.get('feedback_score', 
                5 if feedback_type == 'thumbs_up' else 1)
        
        if data.get('feedback_comments'):
            suggestion.feedback_comments = data.get('feedback_comments')
        
        suggestion.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict(),
            'suggestion': suggestion.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions/batch-action', methods=['POST'])
def batch_action():
    """Perform batch action on multiple suggestions."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        suggestion_ids = data.get('suggestion_ids', [])
        action = data.get('action')
        
        if not suggestion_ids or not action:
            return jsonify({
                'success': False,
                'error': 'Suggestion IDs and action are required'
            }), 400
        
        # Get suggestions
        suggestions = ContentSuggestion.query.filter(
            ContentSuggestion.id.in_(suggestion_ids)
        ).all()
        
        if not suggestions:
            return jsonify({
                'success': False,
                'error': 'No suggestions found'
            }), 404
        
        # Get or create user session
        if 'user_session' not in session:
            session['user_session'] = str(uuid.uuid4())
        
        updated_suggestions = []
        
        for suggestion in suggestions:
            # Create feedback record
            feedback = UserFeedback(
                content_suggestion_id=suggestion.id,
                feedback_type=action,
                feedback_comments=data.get('comments'),
                user_session=session['user_session']
            )
            
            db.session.add(feedback)
            
            # Update suggestion
            if action == 'approve':
                suggestion.status = 'approved'
                suggestion.approval_status = 'approved'
            elif action == 'reject':
                suggestion.status = 'rejected'
                suggestion.approval_status = 'rejected'
            
            suggestion.updated_at = datetime.utcnow()
            updated_suggestions.append(suggestion.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_suggestions': updated_suggestions,
            'action': action,
            'count': len(updated_suggestions)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/suggestions/<suggestion_id>/status', methods=['PUT'])
def update_status(suggestion_id):
    """Update the status of a content suggestion."""
    try:
        suggestion = ContentSuggestion.query.get(suggestion_id)
        
        if not suggestion:
            return jsonify({
                'success': False,
                'error': 'Suggestion not found'
            }), 404
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        suggestion.status = data['status']
        if 'approval_status' in data:
            suggestion.approval_status = data['approval_status']
        
        suggestion.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'suggestion': suggestion.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/business-profiles', methods=['GET'])
def get_business_profiles():
    """Get all business profiles."""
    try:
        profiles = BusinessProfile.query.order_by(BusinessProfile.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'profiles': [profile.to_dict() for profile in profiles]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/business-profiles', methods=['POST'])
def create_business_profile():
    """Create a new business profile."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        # Convert nested objects to JSON strings
        if 'target_audience' in data and isinstance(data['target_audience'], dict):
            data['target_audience'] = json.dumps(data['target_audience'])
        
        if 'brand_voice' in data and isinstance(data['brand_voice'], dict):
            data['brand_voice'] = json.dumps(data['brand_voice'])
        
        if 'analysis_data' in data and isinstance(data['analysis_data'], dict):
            data['analysis_data'] = json.dumps(data['analysis_data'])
        
        # Create profile
        profile = BusinessProfile(**data)
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/briefings', methods=['GET'])
def get_briefings():
    """Get all content briefings."""
    try:
        briefings = ContentBriefing.query.order_by(ContentBriefing.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'briefings': [briefing.to_dict() for briefing in briefings]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/briefings', methods=['POST'])
def create_briefing():
    """Create a new content briefing."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        
        # Convert nested objects to JSON strings
        if 'campaign_objectives' in data and isinstance(data['campaign_objectives'], list):
            data['campaign_objectives'] = json.dumps(data['campaign_objectives'])
        
        if 'briefing_data' in data and isinstance(data['briefing_data'], dict):
            data['briefing_data'] = json.dumps(data['briefing_data'])
        
        # Create briefing
        briefing = ContentBriefing(**data)
        
        db.session.add(briefing)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'briefing': briefing.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary for content suggestions."""
    try:
        # Get total counts by status
        total_suggestions = ContentSuggestion.query.count()
        pending_suggestions = ContentSuggestion.query.filter_by(status='pending_review').count()
        approved_suggestions = ContentSuggestion.query.filter_by(status='approved').count()
        rejected_suggestions = ContentSuggestion.query.filter_by(status='rejected').count()
        
        # Get counts by platform
        platform_counts = {}
        platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok']
        for platform in platforms:
            count = ContentSuggestion.query.filter_by(platform=platform).count()
            platform_counts[platform] = count
        
        # Get counts by content type
        content_type_counts = {}
        content_types = ['educational', 'promotional', 'entertaining', 'inspirational']
        for content_type in content_types:
            count = ContentSuggestion.query.filter_by(content_type=content_type).count()
            content_type_counts[content_type] = count
        
        # Calculate approval rate
        approval_rate = 0
        if total_suggestions > 0:
            approval_rate = (approved_suggestions / total_suggestions) * 100
        
        # Get average engagement score
        avg_engagement = db.session.query(db.func.avg(ContentSuggestion.engagement_score)).scalar() or 0
        
        return jsonify({
            'success': True,
            'summary': {
                'total_suggestions': total_suggestions,
                'pending_suggestions': pending_suggestions,
                'approved_suggestions': approved_suggestions,
                'rejected_suggestions': rejected_suggestions,
                'approval_rate': round(approval_rate, 2),
                'average_engagement_score': round(avg_engagement, 2),
                'platform_distribution': platform_counts,
                'content_type_distribution': content_type_counts
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@content_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

