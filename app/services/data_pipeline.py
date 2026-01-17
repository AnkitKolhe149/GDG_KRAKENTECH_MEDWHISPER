"""Data Pipeline for Health Data Management"""
import firebase_admin
from firebase_admin import firestore
from datetime import datetime, timedelta
import logging
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthDataPipeline:
    """Manage health data storage and retrieval from Firestore"""
    
    def __init__(self):
        self.db = firestore.client() if firebase_admin._apps else None
    
    # ========== Lab Data Methods ==========
    
    def store_lab_data(self, uid: str, lab_data: Dict) -> bool:
        """
        Store laboratory test results for a user
        
        Args:
            uid: User ID
            lab_data: Dictionary containing lab test data
            
        Expected lab_data structure:
        {
            'test_date': '2026-01-01',
            'glucose': 95,
            'hba1c': 5.4,
            'cholesterol': 180,
            'hdl': 55,
            'ldl': 100,
            'triglycerides': 125,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'heart_rate': 72,
            'liver_enzymes': {'alt': 25, 'ast': 30},
            'kidney_function': {'creatinine': 0.9, 'bun': 15}
        }
        """
        try:
            lab_data['timestamp'] = firestore.SERVER_TIMESTAMP
            lab_data['created_at'] = datetime.now().isoformat()
            
            self.db.collection('users').document(uid)\
                .collection('lab_data').add(lab_data)
            
            logger.info(f"Lab data stored for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error storing lab data: {e}")
            return False
    
    def get_lab_history(self, uid: str, months: int = 12) -> List[Dict]:
        """Get user's lab history for specified months"""
        try:
            cutoff_date = datetime.now() - timedelta(days=months*30)
            
            lab_docs = self.db.collection('users').document(uid)\
                .collection('lab_data')\
                .where('created_at', '>=', cutoff_date.isoformat())\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .stream()
            
            return [doc.to_dict() for doc in lab_docs]
        except Exception as e:
            logger.error(f"Error getting lab history: {e}")
            return []
    
    # ========== Lifestyle Data Methods ==========
    
    def store_lifestyle_data(self, uid: str, lifestyle_data: Dict) -> bool:
        """
        Store lifestyle and activity data
        
        Expected lifestyle_data structure:
        {
            'date': '2026-01-01',
            'sleep_hours': 7.5,
            'sleep_quality': 'good',  # poor/fair/good/excellent
            'exercise_minutes': 30,
            'exercise_type': 'cardio',
            'steps': 8000,
            'water_intake_ml': 2000,
            'alcohol_units': 0,
            'smoking': False,
            'diet_quality': 'balanced',  # poor/fair/balanced/excellent
            'meals': {
                'breakfast': True,
                'lunch': True,
                'dinner': True,
                'snacks': 2
            }
        }
        """
        try:
            lifestyle_data['timestamp'] = firestore.SERVER_TIMESTAMP
            lifestyle_data['created_at'] = datetime.now().isoformat()
            
            self.db.collection('users').document(uid)\
                .collection('lifestyle_data').add(lifestyle_data)
            
            logger.info(f"Lifestyle data stored for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error storing lifestyle data: {e}")
            return False
    
    def get_lifestyle_history(self, uid: str, days: int = 30) -> List[Dict]:
        """Get user's lifestyle data for specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            lifestyle_docs = self.db.collection('users').document(uid)\
                .collection('lifestyle_data')\
                .where('created_at', '>=', cutoff_date.isoformat())\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .stream()
            
            return [doc.to_dict() for doc in lifestyle_docs]
        except Exception as e:
            logger.error(f"Error getting lifestyle history: {e}")
            return []
    
    # ========== Mental Health Data Methods ==========
    
    def store_mental_health_data(self, uid: str, mental_health_data: Dict) -> bool:
        """
        Store mental health indicators
        
        Expected mental_health_data structure:
        {
            'date': '2026-01-01',
            'stress_level': 5,  # 1-10 scale
            'mood': 'neutral',  # depressed/low/neutral/good/excellent
            'anxiety_level': 3,  # 1-10 scale
            'social_interaction': 'moderate',  # low/moderate/high
            'work_life_balance': 'fair',  # poor/fair/good/excellent
            'symptoms': ['fatigue', 'irritability'],
            'therapy_sessions': 0
        }
        """
        try:
            mental_health_data['timestamp'] = firestore.SERVER_TIMESTAMP
            mental_health_data['created_at'] = datetime.now().isoformat()
            
            self.db.collection('users').document(uid)\
                .collection('mental_health_data').add(mental_health_data)
            
            logger.info(f"Mental health data stored for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error storing mental health data: {e}")
            return False
    
    def get_mental_health_history(self, uid: str, months: int = 6) -> List[Dict]:
        """Get user's mental health history"""
        try:
            cutoff_date = datetime.now() - timedelta(days=months*30)
            
            mental_docs = self.db.collection('users').document(uid)\
                .collection('mental_health_data')\
                .where('created_at', '>=', cutoff_date.isoformat())\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .stream()
            
            return [doc.to_dict() for doc in mental_docs]
        except Exception as e:
            logger.error(f"Error getting mental health history: {e}")
            return []
    
    # ========== Family History Methods ==========
    
    def store_family_history(self, uid: str, family_history: Dict) -> bool:
        """
        Store family medical history
        
        Expected family_history structure:
        {
            'diabetes': ['father', 'grandmother'],
            'hypertension': ['mother'],
            'heart_disease': ['grandfather'],
            'liver_disease': [],
            'mental_health': ['mother'],
            'cancer': ['grandmother'],
            'notes': 'Father diagnosed at age 45'
        }
        """
        try:
            family_history['updated_at'] = firestore.SERVER_TIMESTAMP
            
            self.db.collection('users').document(uid)\
                .collection('medical_profile').document('family_history')\
                .set(family_history, merge=True)
            
            logger.info(f"Family history stored for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error storing family history: {e}")
            return False
    
    def get_family_history(self, uid: str) -> Optional[Dict]:
        """Get user's family medical history"""
        try:
            doc = self.db.collection('users').document(uid)\
                .collection('medical_profile').document('family_history').get()
            
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Error getting family history: {e}")
            return None
    
    # ========== Risk Reports Methods ==========
    
    def store_risk_report(self, uid: str, risk_report: Dict) -> bool:
        """Store generated risk assessment report"""
        try:
            risk_report['timestamp'] = firestore.SERVER_TIMESTAMP
            risk_report['created_at'] = datetime.now().isoformat()
            
            self.db.collection('users').document(uid)\
                .collection('risk_reports').add(risk_report)
            
            logger.info(f"Risk report stored for user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error storing risk report: {e}")
            return False
    
    def get_latest_risk_report(self, uid: str) -> Optional[Dict]:
        """Get user's most recent risk report"""
        try:
            reports = self.db.collection('users').document(uid)\
                .collection('risk_reports')\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(1)\
                .stream()
            
            for report in reports:
                return report.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting latest risk report: {e}")
            return None
    
    def get_all_risk_reports(self, uid: str) -> List[Dict]:
        """Get all risk reports for a user"""
        try:
            reports = self.db.collection('users').document(uid)\
                .collection('risk_reports')\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .stream()
            
            return [report.to_dict() for report in reports]
        except Exception as e:
            logger.error(f"Error getting risk reports: {e}")
            return []
    
    # ========== Comprehensive Data Retrieval ==========
    
    def get_all_user_health_data(self, uid: str) -> Dict:
        """
        Retrieve all health data for a user for ML prediction
        
        Returns comprehensive data structure with all health signals
        """
        try:
            data = {
                'lab_data': self.get_lab_history(uid, months=12),
                'lifestyle_data': self.get_lifestyle_history(uid, days=90),
                'mental_health_data': self.get_mental_health_history(uid, months=6),
                'family_history': self.get_family_history(uid),
                'latest_report': self.get_latest_risk_report(uid)
            }
            
            logger.info(f"Retrieved comprehensive health data for user: {uid}")
            return data
        except Exception as e:
            logger.error(f"Error getting comprehensive health data: {e}")
            return {}
