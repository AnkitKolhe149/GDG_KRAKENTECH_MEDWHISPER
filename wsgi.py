"""WSGI entry point for production servers (Gunicorn, Render, Vercel)"""
import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # This is for local testing only
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    app.run(host=host, port=port, debug=debug)
