import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from datetime import datetime

# Import database models
from src.models.user import db
from src.models.tenant import Tenant
from src.models.api_key import APIKey

# Import route blueprints
from src.routes.auth import auth_bp
from src.routes.generator import generator_bp
from src.routes.evaluation import evaluation_bp
from src.routes.team_leader import team_leader_bp
from src.routes.platform_agents import platform_agents_bp
from src.routes.external_api import external_api_bp
from src.routes.admin import admin_bp

# Import middleware
from src.middleware.auth_middleware import auth_required, tenant_required
from src.middleware.rate_limiting import setup_rate_limiting
from src.middleware.request_validation import setup_request_validation
from src.middleware.error_handling import setup_error_handling

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'saas-api-gateway-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days

# Database configuration
database_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS configuration for SaaS platform
CORS(app, origins=['*'], supports_credentials=True)

# JWT configuration
jwt = JWTManager(app)

# Rate limiting configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
db.init_app(app)

# Register blueprints with API versioning
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(generator_bp, url_prefix='/api/v1/generator')
app.register_blueprint(evaluation_bp, url_prefix='/api/v1/evaluation')
app.register_blueprint(team_leader_bp, url_prefix='/api/v1/team-leader')
app.register_blueprint(platform_agents_bp, url_prefix='/api/v1/platforms')
app.register_blueprint(external_api_bp, url_prefix='/api/v1/external')
app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')

# Setup middleware
setup_rate_limiting(app, limiter)
setup_request_validation(app)
setup_error_handling(app)

# Health check endpoint
@app.route('/health')
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'SaaS API Gateway'
    })

# API documentation endpoint
@app.route('/api/docs')
def api_docs():
    """API documentation endpoint."""
    return jsonify({
        'title': 'Social Media Agent SaaS API',
        'version': '1.0.0',
        'description': 'Comprehensive API for Social Media Agent SaaS platform',
        'endpoints': {
            'authentication': '/api/v1/auth',
            'generator_agent': '/api/v1/generator',
            'evaluation_agent': '/api/v1/evaluation',
            'team_leader': '/api/v1/team-leader',
            'platform_agents': '/api/v1/platforms',
            'external_integrations': '/api/v1/external',
            'administration': '/api/v1/admin'
        },
        'documentation_url': '/api/v1/docs/swagger'
    })

# Request logging middleware
@app.before_request
def log_request_info():
    """Log incoming requests for monitoring and debugging."""
    if request.endpoint != 'health_check':
        logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response information."""
    if request.endpoint != 'health_check':
        logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

# Tenant context middleware
@app.before_request
def set_tenant_context():
    """Set tenant context for multi-tenant operations."""
    if request.endpoint and not request.endpoint.startswith('auth'):
        # Extract tenant information from headers or JWT token
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            # Store tenant context for use in request processing
            request.tenant_id = tenant_id

# Database initialization
@app.before_first_request
def create_tables():
    """Create database tables on first request."""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested API endpoint was not found',
            'status_code': 404
        }), 404
    else:
        # Serve frontend for non-API routes
        return serve('')

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500

# Frontend serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend application."""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({'error': 'Static folder not configured'}), 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Social Media Agent SaaS API Gateway',
                'version': '1.0.0',
                'documentation': '/api/docs',
                'health': '/health'
            })

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting SaaS API Gateway on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

