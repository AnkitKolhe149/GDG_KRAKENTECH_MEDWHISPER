"""Data preprocessing utilities"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def validate_lab_data(data: dict) -> tuple:
    """
    Validate laboratory data
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['test_date']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric ranges
    validations = {
        'glucose': (0, 500),
        'hba1c': (0, 20),
        'cholesterol': (0, 500),
        'hdl': (0, 200),
        'ldl': (0, 400),
        'triglycerides': (0, 1000),
        'blood_pressure_systolic': (50, 250),
        'blood_pressure_diastolic': (30, 150),
        'heart_rate': (30, 200)
    }
    
    for field, (min_val, max_val) in validations.items():
        if field in data:
            value = data[field]
            if not isinstance(value, (int, float)):
                return False, f"{field} must be a number"
            if not (min_val <= value <= max_val):
                return False, f"{field} must be between {min_val} and {max_val}"
    
    return True, ""


def validate_lifestyle_data(data: dict) -> tuple:
    """
    Validate lifestyle data
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['date']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric ranges
    if 'sleep_hours' in data:
        if not (0 <= data['sleep_hours'] <= 24):
            return False, "sleep_hours must be between 0 and 24"
    
    if 'exercise_minutes' in data:
        if not (0 <= data['exercise_minutes'] <= 1440):
            return False, "exercise_minutes must be between 0 and 1440"
    
    if 'steps' in data:
        if not (0 <= data['steps'] <= 100000):
            return False, "steps must be between 0 and 100000"
    
    # Validate categorical fields
    if 'sleep_quality' in data:
        valid_values = ['poor', 'fair', 'good', 'excellent']
        if data['sleep_quality'] not in valid_values:
            return False, f"sleep_quality must be one of: {valid_values}"
    
    if 'diet_quality' in data:
        valid_values = ['poor', 'fair', 'balanced', 'excellent']
        if data['diet_quality'] not in valid_values:
            return False, f"diet_quality must be one of: {valid_values}"
    
    return True, ""


def validate_mental_health_data(data: dict) -> tuple:
    """
    Validate mental health data
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['date']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate scale values
    if 'stress_level' in data:
        if not (1 <= data['stress_level'] <= 10):
            return False, "stress_level must be between 1 and 10"
    
    if 'anxiety_level' in data:
        if not (1 <= data['anxiety_level'] <= 10):
            return False, "anxiety_level must be between 1 and 10"
    
    # Validate categorical fields
    if 'mood' in data:
        valid_values = ['depressed', 'low', 'neutral', 'good', 'excellent']
        if data['mood'] not in valid_values:
            return False, f"mood must be one of: {valid_values}"
    
    return True, ""


def sanitize_input(data: dict) -> dict:
    """Remove any potentially harmful data from input"""
    sanitized = {}
    
    for key, value in data.items():
        # Skip None values
        if value is None:
            continue
        
        # Convert strings and remove scripts
        if isinstance(value, str):
            value = value.strip()
            # Basic XSS prevention
            value = value.replace('<', '&lt;').replace('>', '&gt;')
        
        sanitized[key] = value
    
    return sanitized
