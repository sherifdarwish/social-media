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

# Import existing route blueprints
from src.routes.auth import auth_bp
from src.routes.generator import generator_bp
from src.routes.payments import payments_bp
from src.routes.social_auth import social_auth_bp
from src.routes.external_integrations import external_integrations_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///social_media_saas.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    db.init_app(app)
    
    # Rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(generator_bp, url_prefix='/api/generator')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(social_auth_bp, url_prefix='/api/social')
    app.register_blueprint(external_integrations_bp, url_prefix='/api/integrations')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Social Media Agent SaaS API Gateway',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'generator': '/api/generator', 
                'payments': '/api/payments',
                'social': '/api/social',
                'integrations': '/api/integrations',
                'health': '/health'
            }
        })
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
