"""Local development entry point"""
import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Run application with hot-reload for development
    app.run(host=host, port=port, debug=debug)
