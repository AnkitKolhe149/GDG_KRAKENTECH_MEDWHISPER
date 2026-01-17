"""Firebase Authentication Service"""
import firebase_admin
from firebase_admin import auth, firestore
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthService:
    """Handle Firebase authentication and user management"""
    
    def __init__(self):
        self.db = firestore.client() if firebase_admin._apps else None
    
    def verify_token(self, id_token):
        """
        Verify Firebase ID token
        
        Args:
            id_token (str): Firebase ID token from client
            
        Returns:
            dict: Decoded token with user info or None if invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_or_create_user(self, decoded_token):
        """
        Get existing user or create new user in Firestore
        
        Args:
            decoded_token (dict): Decoded Firebase token
            
        Returns:
            dict: User data
        """
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        
        try:
            # Check if user exists
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                # Create new user
                user_data = {
                    'uid': uid,
                    'email': email,
                    'name': name,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'last_login': firestore.SERVER_TIMESTAMP,
                    'profile_complete': False
                }
                user_ref.set(user_data)
                logger.info(f"New user created: {uid}")
                return user_data
                
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            return None
    
    def update_last_login(self, uid):
        """Update user's last login timestamp"""
        try:
            user_ref = self.db.collection('users').document(uid)
            user_ref.update({'last_login': firestore.SERVER_TIMESTAMP})
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
    
    def get_user_profile(self, uid):
        """Get user profile from Firestore"""
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, uid, profile_data):
        """
        Update user profile information
        
        Args:
            uid (str): User ID
            profile_data (dict): Profile data to update
            
        Returns:
            bool: Success status
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_ref.update(profile_data)
            logger.info(f"Profile updated for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False


# Decorator for protected routes
def require_auth(f):
    """
    Decorator to protect routes with Firebase authentication
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route(current_user):
            return jsonify(current_user)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        # Extract token (format: "Bearer <token>")
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Verify token
        auth_service = FirebaseAuthService()
        decoded_token = auth_service.verify_token(token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get or create user
        current_user = auth_service.get_or_create_user(decoded_token)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update last login
        auth_service.update_last_login(decoded_token['uid'])
        
        # Pass current_user to the route function
        return f(current_user, *args, **kwargs)
    
    return decorated_function
