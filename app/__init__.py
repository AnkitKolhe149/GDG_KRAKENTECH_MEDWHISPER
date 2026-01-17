import os
import firebase_admin
from firebase_admin import credentials
from flask import Flask
from flask_cors import CORS
from app.config import config


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize Firebase Admin SDK
    initialize_firebase(app)
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize logger
    from app.utils.logger import setup_logger
    setup_logger(app)
    
    return app


def initialize_firebase(app):
    """Initialize Firebase Admin SDK"""
    try:
        cred_path = app.config['FIREBASE_CREDENTIALS_PATH']
        
        if not firebase_admin._apps:
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': app.config.get('FIREBASE_DATABASE_URL')
                })
                app.logger.info("Firebase initialized successfully")
            else:
                app.logger.warning(f"Firebase credentials not found at {cred_path}")
                app.logger.warning("Running without Firebase - authentication will be limited")
    except Exception as e:
        app.logger.error(f"Error initializing Firebase: {e}")
        raise
