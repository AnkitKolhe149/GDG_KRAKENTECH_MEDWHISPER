"""Application routes and API endpoints"""
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.firebase_auth import require_auth, FirebaseAuthService
from app.services.data_pipeline import HealthDataPipeline
from app.services.feature_engineering import HealthFeatureEngineer
from app.models.risk_model import MultiDiseaseRiskModel
from app.services.scoring_engine import RiskScoringEngine
from app.utils.preprocess import (
    validate_lab_data, validate_lifestyle_data,
    validate_mental_health_data, sanitize_input
)
import logging

logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


# ============== Main Routes (Frontend) ==============

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')


@main_bp.route('/data-input')
def data_input():
    """Health data input form"""
    return render_template('data_input.html')


@main_bp.route('/risk-report')
def risk_report():
    """Risk assessment report view"""
    return render_template('risk_report.html')


# ============== API Routes ==============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Silent Disease Detection Engine',
        'version': '1.0.0'
    })


# ========== Authentication Endpoints ==========

@api_bp.route('/auth/verify', methods=['POST'])
def verify_token():
    """
    Verify Firebase authentication token
    
    Request body:
    {
        "token": "firebase_id_token"
    }
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        auth_service = FirebaseAuthService()
        decoded_token = auth_service.verify_token(token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get or create user
        user = auth_service.get_or_create_user(decoded_token)
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return jsonify({'error': 'Authentication failed'}), 500


@api_bp.route('/user/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """Get user profile"""
    try:
        auth_service = FirebaseAuthService()
        profile = auth_service.get_user_profile(current_user['uid'])
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500


@api_bp.route('/user/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """Update user profile"""
    try:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        
        auth_service = FirebaseAuthService()
        success = auth_service.update_user_profile(current_user['uid'], sanitized_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Profile updated'})
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500


# ========== Health Data Endpoints ==========

@api_bp.route('/data/lab', methods=['POST'])
@require_auth
def submit_lab_data(current_user):
    """
    Submit laboratory test data
    
    Request body:
    {
        "test_date": "2026-01-01",
        "glucose": 95,
        "hba1c": 5.4,
        "cholesterol": 180,
        ...
    }
    """
    try:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        
        # Validate data
        is_valid, error_msg = validate_lab_data(sanitized_data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Store data
        pipeline = HealthDataPipeline()
        success = pipeline.store_lab_data(current_user['uid'], sanitized_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Lab data stored successfully'})
        else:
            return jsonify({'error': 'Failed to store lab data'}), 500
        
    except Exception as e:
        logger.error(f"Error submitting lab data: {e}")
        return jsonify({'error': 'Failed to submit lab data'}), 500


@api_bp.route('/data/lifestyle', methods=['POST'])
@require_auth
def submit_lifestyle_data(current_user):
    """
    Submit lifestyle and activity data
    
    Request body:
    {
        "date": "2026-01-01",
        "sleep_hours": 7.5,
        "exercise_minutes": 30,
        ...
    }
    """
    try:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        
        # Validate data
        is_valid, error_msg = validate_lifestyle_data(sanitized_data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Store data
        pipeline = HealthDataPipeline()
        success = pipeline.store_lifestyle_data(current_user['uid'], sanitized_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Lifestyle data stored successfully'})
        else:
            return jsonify({'error': 'Failed to store lifestyle data'}), 500
        
    except Exception as e:
        logger.error(f"Error submitting lifestyle data: {e}")
        return jsonify({'error': 'Failed to submit lifestyle data'}), 500


@api_bp.route('/data/mental-health', methods=['POST'])
@require_auth
def submit_mental_health_data(current_user):
    """
    Submit mental health indicators
    
    Request body:
    {
        "date": "2026-01-01",
        "stress_level": 5,
        "mood": "neutral",
        ...
    }
    """
    try:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        
        # Validate data
        is_valid, error_msg = validate_mental_health_data(sanitized_data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Store data
        pipeline = HealthDataPipeline()
        success = pipeline.store_mental_health_data(current_user['uid'], sanitized_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Mental health data stored successfully'})
        else:
            return jsonify({'error': 'Failed to store mental health data'}), 500
        
    except Exception as e:
        logger.error(f"Error submitting mental health data: {e}")
        return jsonify({'error': 'Failed to submit mental health data'}), 500


@api_bp.route('/data/family-history', methods=['POST'])
@require_auth
def submit_family_history(current_user):
    """
    Submit family medical history
    
    Request body:
    {
        "diabetes": ["father", "grandmother"],
        "hypertension": ["mother"],
        ...
    }
    """
    try:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        
        # Store data
        pipeline = HealthDataPipeline()
        success = pipeline.store_family_history(current_user['uid'], sanitized_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Family history stored successfully'})
        else:
            return jsonify({'error': 'Failed to store family history'}), 500
        
    except Exception as e:
        logger.error(f"Error submitting family history: {e}")
        return jsonify({'error': 'Failed to submit family history'}), 500


@api_bp.route('/data/history', methods=['GET'])
@require_auth
def get_health_history(current_user):
    """Get all health data history for the user"""
    try:
        pipeline = HealthDataPipeline()
        health_data = pipeline.get_all_user_health_data(current_user['uid'])
        
        return jsonify({
            'success': True,
            'data': health_data
        })
        
    except Exception as e:
        logger.error(f"Error getting health history: {e}")
        return jsonify({'error': 'Failed to get health history'}), 500


# ========== Risk Assessment Endpoints ==========

@api_bp.route('/assessment/generate', methods=['POST'])
@require_auth
def generate_risk_assessment(current_user):
    """
    Generate comprehensive risk assessment report
    
    This endpoint:
    1. Retrieves all user health data
    2. Engineers features from the data
    3. Runs ML models for disease prediction
    4. Generates risk scores and recommendations
    5. Stores and returns the report
    """
    try:
        # Get all health data
        pipeline = HealthDataPipeline()
        health_data = pipeline.get_all_user_health_data(current_user['uid'])
        
        if not health_data or not any(health_data.values()):
            return jsonify({
                'error': 'Insufficient data for risk assessment. Please add health data first.'
            }), 400
        
        # Engineer features
        feature_engineer = HealthFeatureEngineer()
        features = feature_engineer.engineer_features(health_data)
        
        if features.empty:
            return jsonify({'error': 'Failed to process health data'}), 500
        
        # Load ML model
        model_path = current_app.config['MODEL_PATH']
        risk_model = MultiDiseaseRiskModel(model_path=model_path)
        
        # Predict risk scores
        risk_scores = risk_model.predict_risk_scores(features)
        
        # Generate comprehensive report
        scoring_engine = RiskScoringEngine(current_app.config['RISK_THRESHOLDS'])
        
        # Convert features to dictionary for report generation
        features_dict = features.iloc[0].to_dict()
        
        risk_report = scoring_engine.generate_risk_report(
            risk_scores=risk_scores,
            features=features_dict,
            user_profile=current_user
        )
        
        # Store report
        pipeline.store_risk_report(current_user['uid'], risk_report)
        
        logger.info(f"Risk assessment generated for user: {current_user['uid']}")
        
        return jsonify({
            'success': True,
            'report': risk_report
        })
        
    except Exception as e:
        logger.error(f"Error generating risk assessment: {e}")
        return jsonify({'error': 'Failed to generate risk assessment'}), 500


@api_bp.route('/assessment/latest', methods=['GET'])
@require_auth
def get_latest_assessment(current_user):
    """Get user's most recent risk assessment report"""
    try:
        pipeline = HealthDataPipeline()
        latest_report = pipeline.get_latest_risk_report(current_user['uid'])
        
        if latest_report:
            return jsonify({
                'success': True,
                'report': latest_report
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No risk assessment found. Generate your first assessment.'
            }), 404
        
    except Exception as e:
        logger.error(f"Error getting latest assessment: {e}")
        return jsonify({'error': 'Failed to get assessment'}), 500


@api_bp.route('/assessment/history', methods=['GET'])
@require_auth
def get_assessment_history(current_user):
    """Get all risk assessment reports for the user"""
    try:
        pipeline = HealthDataPipeline()
        reports = pipeline.get_all_risk_reports(current_user['uid'])
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        })
        
    except Exception as e:
        logger.error(f"Error getting assessment history: {e}")
        return jsonify({'error': 'Failed to get assessment history'}), 500


# ========== Analytics Endpoints ==========

@api_bp.route('/analytics/trends', methods=['GET'])
@require_auth
def get_health_trends(current_user):
    """Get health trends over time"""
    try:
        pipeline = HealthDataPipeline()
        
        # Get historical data
        lab_history = pipeline.get_lab_history(current_user['uid'], months=12)
        lifestyle_history = pipeline.get_lifestyle_history(current_user['uid'], days=90)
        
        # Calculate trends
        trends = {
            'glucose_trend': _calculate_metric_trend(lab_history, 'glucose'),
            'bp_trend': _calculate_metric_trend(lab_history, 'blood_pressure_systolic'),
            'exercise_trend': _calculate_metric_trend(lifestyle_history, 'exercise_minutes'),
            'sleep_trend': _calculate_metric_trend(lifestyle_history, 'sleep_hours')
        }
        
        return jsonify({
            'success': True,
            'trends': trends
        })
        
    except Exception as e:
        logger.error(f"Error calculating trends: {e}")
        return jsonify({'error': 'Failed to calculate trends'}), 500


def _calculate_metric_trend(data_list, metric):
    """Helper function to calculate trend for a specific metric"""
    if not data_list or len(data_list) < 2:
        return {'status': 'insufficient_data', 'change': 0}
    
    try:
        values = [d.get(metric, 0) for d in data_list if d.get(metric)]
        if len(values) < 2:
            return {'status': 'insufficient_data', 'change': 0}
        
        # Calculate percentage change from oldest to newest
        oldest = values[-1]
        newest = values[0]
        
        if oldest == 0:
            return {'status': 'stable', 'change': 0}
        
        change = ((newest - oldest) / oldest) * 100
        
        if abs(change) < 5:
            status = 'stable'
        elif change > 0:
            status = 'increasing'
        else:
            status = 'decreasing'
        
        return {
            'status': status,
            'change': round(change, 2),
            'latest': newest,
            'previous': oldest
        }
    except:
        return {'status': 'error', 'change': 0}


# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
