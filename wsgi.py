"""WSGI entry point for production servers (Gunicorn, Render, Vercel)"""
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    app.run()
