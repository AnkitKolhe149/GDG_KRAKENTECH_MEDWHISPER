"""Feature Engineering for Health Data"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class HealthFeatureEngineer:
    """Transform raw health data into ML-ready features"""
    
    def __init__(self):
        self.feature_names = []
    
    def engineer_features(self, health_data: Dict) -> pd.DataFrame:
        """
        Main method to engineer features from all health data sources
        
        Args:
            health_data: Dictionary containing lab_data, lifestyle_data, 
                        mental_health_data, and family_history
        
        Returns:
            DataFrame with engineered features
        """
        try:
            features = {}
            
            # Extract features from each data source
            lab_features = self._extract_lab_features(health_data.get('lab_data', []))
            lifestyle_features = self._extract_lifestyle_features(health_data.get('lifestyle_data', []))
            mental_features = self._extract_mental_health_features(health_data.get('mental_health_data', []))
            family_features = self._extract_family_history_features(health_data.get('family_history', {}))
            
            # Combine all features
            features.update(lab_features)
            features.update(lifestyle_features)
            features.update(mental_features)
            features.update(family_features)
            
            # Create DataFrame
            df = pd.DataFrame([features])
            self.feature_names = df.columns.tolist()
            
            logger.info(f"Engineered {len(features)} features")
            return df
            
        except Exception as e:
            logger.error(f"Error engineering features: {e}")
            return pd.DataFrame()
    
    def _extract_lab_features(self, lab_data: List[Dict]) -> Dict:
        """Extract features from laboratory data with trend analysis"""
        features = {}
        
        if not lab_data:
            return self._get_default_lab_features()
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(lab_data)
        
        # Latest values
        latest = lab_data[0] if lab_data else {}
        features['glucose_latest'] = latest.get('glucose', 0)
        features['hba1c_latest'] = latest.get('hba1c', 0)
        features['cholesterol_latest'] = latest.get('cholesterol', 0)
        features['hdl_latest'] = latest.get('hdl', 0)
        features['ldl_latest'] = latest.get('ldl', 0)
        features['triglycerides_latest'] = latest.get('triglycerides', 0)
        features['bp_systolic_latest'] = latest.get('blood_pressure_systolic', 0)
        features['bp_diastolic_latest'] = latest.get('blood_pressure_diastolic', 0)
        features['heart_rate_latest'] = latest.get('heart_rate', 0)
        
        # Liver enzymes
        liver = latest.get('liver_enzymes', {})
        features['alt_latest'] = liver.get('alt', 0)
        features['ast_latest'] = liver.get('ast', 0)
        
        # Kidney function
        kidney = latest.get('kidney_function', {})
        features['creatinine_latest'] = kidney.get('creatinine', 0)
        features['bun_latest'] = kidney.get('bun', 0)
        
        # Trend features (if multiple records available)
        if len(lab_data) > 1:
            features['glucose_trend'] = self._calculate_trend(df, 'glucose')
            features['hba1c_trend'] = self._calculate_trend(df, 'hba1c')
            features['bp_systolic_trend'] = self._calculate_trend(df, 'blood_pressure_systolic')
            features['cholesterol_trend'] = self._calculate_trend(df, 'cholesterol')
            
            # Variability (standard deviation)
            features['glucose_variability'] = df['glucose'].std() if 'glucose' in df else 0
            features['bp_variability'] = df['blood_pressure_systolic'].std() if 'blood_pressure_systolic' in df else 0
        else:
            features['glucose_trend'] = 0
            features['hba1c_trend'] = 0
            features['bp_systolic_trend'] = 0
            features['cholesterol_trend'] = 0
            features['glucose_variability'] = 0
            features['bp_variability'] = 0
        
        # Derived features
        features['cholesterol_hdl_ratio'] = features['cholesterol_latest'] / features['hdl_latest'] if features['hdl_latest'] > 0 else 0
        features['pulse_pressure'] = features['bp_systolic_latest'] - features['bp_diastolic_latest']
        
        # Risk flags
        features['prediabetes_flag'] = 1 if 100 <= features['glucose_latest'] <= 125 else 0
        features['prehypertension_flag'] = 1 if 120 <= features['bp_systolic_latest'] <= 139 else 0
        
        return features
    
    def _extract_lifestyle_features(self, lifestyle_data: List[Dict]) -> Dict:
        """Extract aggregated lifestyle features"""
        features = {}
        
        if not lifestyle_data:
            return self._get_default_lifestyle_features()
        
        df = pd.DataFrame(lifestyle_data)
        
        # Sleep features
        features['avg_sleep_hours'] = df['sleep_hours'].mean() if 'sleep_hours' in df else 7
        features['sleep_consistency'] = 1 - (df['sleep_hours'].std() / df['sleep_hours'].mean()) if 'sleep_hours' in df and df['sleep_hours'].mean() > 0 else 0.5
        features['poor_sleep_days'] = (df['sleep_quality'] == 'poor').sum() if 'sleep_quality' in df else 0
        
        # Exercise features
        features['avg_exercise_minutes'] = df['exercise_minutes'].mean() if 'exercise_minutes' in df else 0
        features['exercise_frequency'] = (df['exercise_minutes'] > 0).sum() / len(df) if 'exercise_minutes' in df else 0
        features['avg_steps'] = df['steps'].mean() if 'steps' in df else 0
        
        # Hydration
        features['avg_water_intake'] = df['water_intake_ml'].mean() if 'water_intake_ml' in df else 2000
        features['dehydration_risk'] = 1 if features['avg_water_intake'] < 1500 else 0
        
        # Substance use
        features['avg_alcohol_units'] = df['alcohol_units'].mean() if 'alcohol_units' in df else 0
        features['smoking'] = 1 if ('smoking' in df and df['smoking'].any()) else 0
        
        # Diet quality score (encoded)
        diet_quality_map = {'poor': 1, 'fair': 2, 'balanced': 3, 'excellent': 4}
        features['diet_quality_score'] = df['diet_quality'].map(diet_quality_map).mean() if 'diet_quality' in df else 2.5
        
        # Meal regularity
        features['meal_regularity'] = df.apply(
            lambda x: sum([x.get('meals', {}).get('breakfast', False),
                          x.get('meals', {}).get('lunch', False),
                          x.get('meals', {}).get('dinner', False)]) / 3,
            axis=1
        ).mean() if 'meals' in df.columns else 0.8
        
        # Sedentary lifestyle flag
        features['sedentary_lifestyle'] = 1 if features['avg_steps'] < 5000 and features['avg_exercise_minutes'] < 20 else 0
        
        return features
    
    def _extract_mental_health_features(self, mental_health_data: List[Dict]) -> Dict:
        """Extract mental health indicators"""
        features = {}
        
        if not mental_health_data:
            return self._get_default_mental_health_features()
        
        df = pd.DataFrame(mental_health_data)
        
        # Stress and anxiety
        features['avg_stress_level'] = df['stress_level'].mean() if 'stress_level' in df else 5
        features['avg_anxiety_level'] = df['anxiety_level'].mean() if 'anxiety_level' in df else 3
        features['high_stress_frequency'] = (df['stress_level'] >= 7).sum() / len(df) if 'stress_level' in df else 0
        
        # Mood encoding
        mood_map = {'depressed': 1, 'low': 2, 'neutral': 3, 'good': 4, 'excellent': 5}
        features['avg_mood_score'] = df['mood'].map(mood_map).mean() if 'mood' in df else 3
        features['low_mood_frequency'] = (df['mood'].isin(['depressed', 'low'])).sum() / len(df) if 'mood' in df else 0
        
        # Social interaction
        social_map = {'low': 1, 'moderate': 2, 'high': 3}
        features['social_interaction_score'] = df['social_interaction'].map(social_map).mean() if 'social_interaction' in df else 2
        
        # Work-life balance
        balance_map = {'poor': 1, 'fair': 2, 'good': 3, 'excellent': 4}
        features['work_life_balance_score'] = df['work_life_balance'].map(balance_map).mean() if 'work_life_balance' in df else 2.5
        
        # Mental health risk flags
        features['chronic_stress_flag'] = 1 if features['avg_stress_level'] >= 7 else 0
        features['depression_risk_flag'] = 1 if features['low_mood_frequency'] > 0.5 else 0
        
        return features
    
    def _extract_family_history_features(self, family_history: Dict) -> Dict:
        """Extract family history risk factors"""
        features = {}
        
        if not family_history:
            return self._get_default_family_history_features()
        
        # Count relatives with each condition
        features['family_diabetes'] = len(family_history.get('diabetes', []))
        features['family_hypertension'] = len(family_history.get('hypertension', []))
        features['family_heart_disease'] = len(family_history.get('heart_disease', []))
        features['family_liver_disease'] = len(family_history.get('liver_disease', []))
        features['family_mental_health'] = len(family_history.get('mental_health', []))
        
        # Binary flags for any family history
        features['has_family_diabetes'] = 1 if features['family_diabetes'] > 0 else 0
        features['has_family_hypertension'] = 1 if features['family_hypertension'] > 0 else 0
        features['has_family_heart_disease'] = 1 if features['family_heart_disease'] > 0 else 0
        features['has_family_liver_disease'] = 1 if features['family_liver_disease'] > 0 else 0
        features['has_family_mental_health'] = 1 if features['family_mental_health'] > 0 else 0
        
        # Overall genetic risk score
        features['genetic_risk_score'] = sum([
            features['family_diabetes'] * 2,
            features['family_hypertension'] * 1.5,
            features['family_heart_disease'] * 2,
            features['family_liver_disease'] * 1.5,
            features['family_mental_health'] * 1
        ])
        
        return features
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)"""
        try:
            if column not in df.columns or len(df) < 2:
                return 0
            
            values = df[column].dropna()
            if len(values) < 2:
                return 0
            
            # Simple linear trend
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            return float(slope)
        except:
            return 0
    
    def _get_default_lab_features(self) -> Dict:
        """Return default lab features when no data available"""
        return {
            'glucose_latest': 0, 'hba1c_latest': 0, 'cholesterol_latest': 0,
            'hdl_latest': 0, 'ldl_latest': 0, 'triglycerides_latest': 0,
            'bp_systolic_latest': 0, 'bp_diastolic_latest': 0, 'heart_rate_latest': 0,
            'alt_latest': 0, 'ast_latest': 0, 'creatinine_latest': 0, 'bun_latest': 0,
            'glucose_trend': 0, 'hba1c_trend': 0, 'bp_systolic_trend': 0,
            'cholesterol_trend': 0, 'glucose_variability': 0, 'bp_variability': 0,
            'cholesterol_hdl_ratio': 0, 'pulse_pressure': 0,
            'prediabetes_flag': 0, 'prehypertension_flag': 0
        }
    
    def _get_default_lifestyle_features(self) -> Dict:
        """Return default lifestyle features"""
        return {
            'avg_sleep_hours': 7, 'sleep_consistency': 0.5, 'poor_sleep_days': 0,
            'avg_exercise_minutes': 0, 'exercise_frequency': 0, 'avg_steps': 5000,
            'avg_water_intake': 2000, 'dehydration_risk': 0,
            'avg_alcohol_units': 0, 'smoking': 0, 'diet_quality_score': 2.5,
            'meal_regularity': 0.8, 'sedentary_lifestyle': 1
        }
    
    def _get_default_mental_health_features(self) -> Dict:
        """Return default mental health features"""
        return {
            'avg_stress_level': 5, 'avg_anxiety_level': 3, 'high_stress_frequency': 0,
            'avg_mood_score': 3, 'low_mood_frequency': 0,
            'social_interaction_score': 2, 'work_life_balance_score': 2.5,
            'chronic_stress_flag': 0, 'depression_risk_flag': 0
        }
    
    def _get_default_family_history_features(self) -> Dict:
        """Return default family history features"""
        return {
            'family_diabetes': 0, 'family_hypertension': 0, 'family_heart_disease': 0,
            'family_liver_disease': 0, 'family_mental_health': 0,
            'has_family_diabetes': 0, 'has_family_hypertension': 0,
            'has_family_heart_disease': 0, 'has_family_liver_disease': 0,
            'has_family_mental_health': 0, 'genetic_risk_score': 0
        }
