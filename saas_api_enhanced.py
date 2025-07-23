import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import uuid
import json

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'social-media-agent-secret-key-2024'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-social-media-agent'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS for all routes
CORS(app, origins=['*'], supports_credentials=True)

# Initialize JWT
jwt = JWTManager(app)

# In-memory storage for demo purposes
users_db = {}
content_db = []
campaigns_db = []
analytics_db = {
    "total_posts": 156,
    "engagement_rate": 8.4,
    "reach": 45000,
    "impressions": 120000
}

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Social Media Agent SaaS API Gateway",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

# Authentication endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        email = data.get('email', 'demo@example.com')
        password = data.get('password', 'demo123')
        name = data.get('name', 'Demo User')
        
        if email in users_db:
            return jsonify({"error": "User already exists"}), 400
            
        user_id = str(uuid.uuid4())
        users_db[email] = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": password,  # In production, hash this!
            "created_at": datetime.utcnow().isoformat(),
            "plan": "free"
        }
        
        access_token = create_access_token(identity=email)
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "plan": "free"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get('email', 'demo@example.com')
        password = data.get('password', 'demo123')
        
        if email not in users_db or users_db[email]['password'] != password:
            return jsonify({"error": "Invalid credentials"}), 401
            
        access_token = create_access_token(identity=email)
        user = users_db[email]
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "plan": user["plan"]
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Content generation endpoints
@app.route('/api/content/suggestions', methods=['GET'])
@jwt_required()
def get_content_suggestions():
    try:
        user_email = get_jwt_identity()
        
        # Generate sample content suggestions
        suggestions = [
            {
                "id": str(uuid.uuid4()),
                "platform": "Facebook",
                "content": "🚀 Exciting news! Our latest AI-powered social media tool is helping businesses increase engagement by 300%. Ready to transform your digital marketing strategy? #AI #SocialMedia #Marketing",
                "engagement_score": 8.5,
                "optimal_time": "2:00 PM",
                "hashtags": ["#AI", "#SocialMedia", "#Marketing"],
                "status": "pending"
            },
            {
                "id": str(uuid.uuid4()),
                "platform": "Twitter",
                "content": "The future of social media marketing is here! 🤖 Our AI agents create, schedule, and optimize content across all platforms. Join 10,000+ happy customers! #SocialMediaAutomation",
                "engagement_score": 7.8,
                "optimal_time": "10:00 AM",
                "hashtags": ["#SocialMediaAutomation", "#AI", "#Marketing"],
                "status": "pending"
            },
            {
                "id": str(uuid.uuid4()),
                "platform": "LinkedIn",
                "content": "Professional insight: Companies using AI-driven social media strategies see 5x better ROI. Our platform combines human creativity with machine efficiency for optimal results.",
                "engagement_score": 9.2,
                "optimal_time": "9:00 AM",
                "hashtags": ["#ProfessionalGrowth", "#AI", "#BusinessStrategy"],
                "status": "pending"
            },
            {
                "id": str(uuid.uuid4()),
                "platform": "Instagram",
                "content": "✨ Behind the scenes: How AI is revolutionizing content creation! Swipe to see the magic happen. #ContentCreation #AI #Innovation",
                "engagement_score": 8.9,
                "optimal_time": "7:00 PM",
                "hashtags": ["#ContentCreation", "#AI", "#Innovation"],
                "status": "pending"
            },
            {
                "id": str(uuid.uuid4()),
                "platform": "TikTok",
                "content": "POV: You discover an AI tool that creates viral content for you 🎯 Watch how our platform generates engaging posts in seconds! #AIContent #Viral #TechTok",
                "engagement_score": 9.5,
                "optimal_time": "8:00 PM",
                "hashtags": ["#AIContent", "#Viral", "#TechTok"],
                "status": "pending"
            }
        ]
        
        # Store suggestions in memory
        for suggestion in suggestions:
            content_db.append(suggestion)
        
        return jsonify({
            "suggestions": suggestions,
            "total": len(suggestions),
            "generated_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Content approval endpoints
@app.route('/api/content/approval', methods=['GET'])
@jwt_required()
def get_content_for_approval():
    try:
        return jsonify({
            "content": content_db,
            "total": len(content_db)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/<content_id>/status', methods=['PATCH'])
@jwt_required()
def update_content_status(content_id):
    try:
        data = request.get_json() or {}
        new_status = data.get('status', 'pending')
        
        # Find and update the content
        for content in content_db:
            if content['id'] == content_id:
                content['status'] = new_status
                content['updated_at'] = datetime.utcnow().isoformat()
                return jsonify({
                    "message": "Content status updated successfully",
                    "content": content
                })
        
        return jsonify({"error": "Content not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Analytics endpoints
@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_analytics_dashboard():
    try:
        dashboard_data = {
            "overview": {
                "total_posts": analytics_db["total_posts"],
                "engagement_rate": analytics_db["engagement_rate"],
                "reach": analytics_db["reach"],
                "impressions": analytics_db["impressions"]
            },
            "platform_performance": [
                {"platform": "LinkedIn", "posts": 24, "engagement": 92},
                {"platform": "Twitter", "posts": 45, "engagement": 78},
                {"platform": "Facebook", "posts": 18, "engagement": 85},
                {"platform": "Instagram", "posts": 32, "engagement": 88},
                {"platform": "TikTok", "posts": 37, "engagement": 94}
            ],
            "error_tracking": [
                {
                    "id": "err_001",
                    "type": "API Rate Limit",
                    "platform": "Twitter",
                    "message": "Rate limit exceeded for posting",
                    "status": "resolved",
                    "impact": "medium",
                    "timestamp": "2024-07-22T10:30:00Z"
                },
                {
                    "id": "err_002", 
                    "type": "Authentication",
                    "platform": "Facebook",
                    "message": "Token expired for page access",
                    "status": "active",
                    "impact": "high",
                    "timestamp": "2024-07-22T14:15:00Z"
                }
            ],
            "system_health": {
                "api_status": "operational",
                "uptime": "99.9%",
                "response_time": "120ms",
                "active_agents": 5
            }
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Campaign management endpoints
@app.route('/api/campaigns', methods=['GET'])
@jwt_required()
def get_campaigns():
    try:
        sample_campaigns = [
            {
                "id": "camp_001",
                "name": "Summer Product Launch",
                "status": "active",
                "platforms": ["Facebook", "Instagram", "Twitter"],
                "start_date": "2024-07-01",
                "end_date": "2024-07-31",
                "posts_scheduled": 45,
                "posts_published": 32,
                "engagement_rate": 8.7,
                "reach": 125000
            },
            {
                "id": "camp_002", 
                "name": "Brand Awareness Q3",
                "status": "paused",
                "platforms": ["LinkedIn", "Twitter"],
                "start_date": "2024-07-15",
                "end_date": "2024-09-30",
                "posts_scheduled": 60,
                "posts_published": 18,
                "engagement_rate": 6.2,
                "reach": 89000
            }
        ]
        
        return jsonify({
            "campaigns": sample_campaigns,
            "total": len(sample_campaigns)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Business profile endpoints
@app.route('/api/generator/business-profile', methods=['POST'])
@jwt_required()
def save_business_profile():
    try:
        data = request.get_json() or {}
        user_email = get_jwt_identity()
        
        profile = {
            "user_email": user_email,
            "company_name": data.get('company_name', ''),
            "industry": data.get('industry', ''),
            "target_audience": data.get('target_audience', ''),
            "brand_voice": data.get('brand_voice', 'professional'),
            "saved_at": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "message": "Business profile saved successfully",
            "profile": profile
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

