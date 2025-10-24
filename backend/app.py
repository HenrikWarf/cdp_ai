"""
Main Flask application for AetherSegment AI
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.config import Config
from backend.api.routes import api


def create_app():
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS - Allow all origins in development, specific origins in production
    if Config.FLASK_ENV == 'development':
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    else:
        CORS(app, resources={
            r"/api/*": {
                "origins": Config.ALLOWED_ORIGINS,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'AetherSegment AI',
            'version': '1.0.0',
            'description': 'AI-First Customer Data Platform for Objective-Driven Micro-Segmentation',
            'endpoints': {
                'health': '/api/v1/health',
                'analyze_campaign': 'POST /api/v1/campaigns/analyze',
                'create_segment': 'POST /api/v1/segments/create',
                'get_customers': 'GET /api/v1/segments/{segment_id}/customers',
                'get_metadata': 'GET /api/v1/segments/{segment_id}/metadata',
                'trigger_suggestions': 'POST /api/v1/triggers/suggestions'
            }
        })
    
    return app


def main():
    """Main entry point for the application"""
    try:
        # Validate configuration
        Config.validate()
        print("✓ Configuration validated")
        
        # Create app
        app = create_app()
        
        # Run server
        port = Config.FLASK_PORT
        debug = Config.FLASK_DEBUG
        
        print(f"\n{'='*60}")
        print(f"  AetherSegment AI - Backend Server")
        print(f"{'='*60}")
        print(f"  Running on: http://localhost:{port}")
        print(f"  Debug mode: {debug}")
        print(f"  Environment: {Config.FLASK_ENV}")
        print(f"{'='*60}\n")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please check your .env file and ensure all required variables are set.")
        print("See env_template.txt for reference.")
        exit(1)
    except Exception as e:
        print(f"\n❌ Failed to start server: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()

