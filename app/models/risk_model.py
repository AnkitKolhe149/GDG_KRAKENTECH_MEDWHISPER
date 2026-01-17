"""Machine Learning Risk Models for Disease Detection"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import logging

logger = logging.getLogger(__name__)


class MultiDiseaseRiskModel:
    """Ensemble model for predicting risk of multiple diseases"""
    
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Initialize models for each disease
        self.disease_types = [
            'diabetes',
            'hypertension',
            'liver_disease',
            'cardiac_risk',
            'mental_health'
        ]
        
        # Try to load pre-trained models, otherwise create new ones
        self._load_or_initialize_models()
    
    def _load_or_initialize_models(self):
        """Load pre-trained models or initialize new ones"""
        for disease in self.disease_types:
            model_file = os.path.join(self.model_path, f'{disease}_model.pkl') if self.model_path else None
            scaler_file = os.path.join(self.model_path, f'{disease}_scaler.pkl') if self.model_path else None
            
            if model_file and os.path.exists(model_file):
                try:
                    with open(model_file, 'rb') as f:
                        self.models[disease] = pickle.load(f)
                    with open(scaler_file, 'rb') as f:
                        self.scalers[disease] = pickle.load(f)
                    logger.info(f"Loaded pre-trained model for {disease}")
                except Exception as e:
                    logger.warning(f"Could not load model for {disease}: {e}")
                    self._initialize_model(disease)
            else:
                self._initialize_model(disease)
    
    def _initialize_model(self, disease):
        """Initialize a new ensemble model for a disease"""
        # Create an ensemble of models
        self.models[disease] = self._create_ensemble_model(disease)
        self.scalers[disease] = StandardScaler()
        logger.info(f"Initialized new model for {disease}")
    
    def _create_ensemble_model(self, disease):
        """
        Create disease-specific ensemble model
        Each disease may have different model configurations
        """
        if disease == 'diabetes':
            return XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        elif disease == 'hypertension':
            return GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif disease == 'liver_disease':
            return LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )
        elif disease == 'cardiac_risk':
            return RandomForestClassifier(
                n_estimators=150,
                max_depth=8,
                random_state=42
            )
        elif disease == 'mental_health':
            return GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def predict_risk_scores(self, features: pd.DataFrame) -> dict:
        """
        Predict risk probability scores for all diseases
        
        Args:
            features: DataFrame with engineered features
            
        Returns:
            Dictionary with risk scores for each disease (0-1 probability)
        """
        risk_scores = {}
        
        for disease in self.disease_types:
            try:
                # Get disease-specific features
                disease_features = self._get_disease_features(features, disease)
                
                # Check if model is trained
                if not hasattr(self.models[disease], 'classes_'):
                    # Use rule-based prediction for untrained models
                    risk_scores[disease] = self._rule_based_prediction(disease_features, disease)
                else:
                    # Use ML model prediction
                    # Scale features
                    scaled_features = self.scalers[disease].transform(disease_features)
                    
                    # Predict probability
                    proba = self.models[disease].predict_proba(scaled_features)
                    risk_scores[disease] = float(proba[0][1])  # Probability of positive class
                
            except Exception as e:
                logger.error(f"Error predicting {disease}: {e}")
                # Fallback to rule-based prediction
                risk_scores[disease] = self._rule_based_prediction(features, disease)
        
        return risk_scores
    
    def _get_disease_features(self, features: pd.DataFrame, disease: str) -> pd.DataFrame:
        """
        Select relevant features for each disease
        This allows different diseases to use different feature subsets
        """
        # For now, return all features
        # In production, you might want disease-specific feature selection
        return features
    
    def _rule_based_prediction(self, features: pd.DataFrame, disease: str) -> float:
        """
        Rule-based prediction when ML model is not available
        Uses clinical thresholds and risk factors
        """
        try:
            risk_score = 0.0
            
            if disease == 'diabetes':
                # Check glucose and HbA1c levels
                glucose = features['glucose_latest'].values[0] if 'glucose_latest' in features else 0
                hba1c = features['hba1c_latest'].values[0] if 'hba1c_latest' in features else 0
                
                if glucose >= 126 or hba1c >= 6.5:
                    risk_score = 0.8
                elif glucose >= 100 or hba1c >= 5.7:
                    risk_score = 0.5
                else:
                    risk_score = 0.2
                
                # Add family history factor
                if features.get('has_family_diabetes', [0])[0] == 1:
                    risk_score = min(risk_score + 0.15, 1.0)
                
                # Add lifestyle factors
                if features.get('sedentary_lifestyle', [0])[0] == 1:
                    risk_score = min(risk_score + 0.1, 1.0)
            
            elif disease == 'hypertension':
                bp_sys = features['bp_systolic_latest'].values[0] if 'bp_systolic_latest' in features else 0
                bp_dia = features['bp_diastolic_latest'].values[0] if 'bp_diastolic_latest' in features else 0
                
                if bp_sys >= 140 or bp_dia >= 90:
                    risk_score = 0.8
                elif bp_sys >= 130 or bp_dia >= 85:
                    risk_score = 0.5
                else:
                    risk_score = 0.2
                
                # Family history
                if features.get('has_family_hypertension', [0])[0] == 1:
                    risk_score = min(risk_score + 0.15, 1.0)
            
            elif disease == 'liver_disease':
                alt = features['alt_latest'].values[0] if 'alt_latest' in features else 0
                ast = features['ast_latest'].values[0] if 'ast_latest' in features else 0
                
                if alt > 40 or ast > 40:
                    risk_score = 0.6
                elif alt > 30 or ast > 30:
                    risk_score = 0.4
                else:
                    risk_score = 0.15
                
                # Alcohol consumption
                alcohol = features['avg_alcohol_units'].values[0] if 'avg_alcohol_units' in features else 0
                if alcohol > 2:
                    risk_score = min(risk_score + 0.2, 1.0)
            
            elif disease == 'cardiac_risk':
                # Multiple risk factors
                cholesterol = features['cholesterol_latest'].values[0] if 'cholesterol_latest' in features else 0
                bp_sys = features['bp_systolic_latest'].values[0] if 'bp_systolic_latest' in features else 0
                smoking = features['smoking'].values[0] if 'smoking' in features else 0
                
                risk_factors = 0
                if cholesterol > 240:
                    risk_factors += 1
                if bp_sys > 140:
                    risk_factors += 1
                if smoking == 1:
                    risk_factors += 1
                if features.get('has_family_heart_disease', [0])[0] == 1:
                    risk_factors += 1
                
                risk_score = min(0.2 + (risk_factors * 0.15), 0.9)
            
            elif disease == 'mental_health':
                stress = features['avg_stress_level'].values[0] if 'avg_stress_level' in features else 5
                mood = features['avg_mood_score'].values[0] if 'avg_mood_score' in features else 3
                
                if stress >= 8 or mood <= 2:
                    risk_score = 0.7
                elif stress >= 6 or mood <= 2.5:
                    risk_score = 0.5
                else:
                    risk_score = 0.25
                
                # Sleep quality
                sleep_hours = features['avg_sleep_hours'].values[0] if 'avg_sleep_hours' in features else 7
                if sleep_hours < 6:
                    risk_score = min(risk_score + 0.15, 1.0)
            
            return float(risk_score)
            
        except Exception as e:
            logger.error(f"Error in rule-based prediction: {e}")
            return 0.5  # Return medium risk as default
    
    def get_risk_level(self, risk_score: float, disease: str, thresholds: dict) -> str:
        """
        Convert risk score to risk level (low/medium/high)
        
        Args:
            risk_score: Probability score (0-1)
            disease: Disease type
            thresholds: Dictionary with low/medium/high thresholds
            
        Returns:
            Risk level string
        """
        disease_thresholds = thresholds.get(disease, {'low': 0.3, 'medium': 0.5, 'high': 0.7})
        
        if risk_score < disease_thresholds['low']:
            return 'low'
        elif risk_score < disease_thresholds['medium']:
            return 'medium'
        elif risk_score < disease_thresholds['high']:
            return 'high'
        else:
            return 'very_high'
    
    def train_model(self, disease: str, X_train, y_train):
        """
        Train a specific disease model
        
        Args:
            disease: Disease type
            X_train: Training features
            y_train: Training labels
        """
        try:
            # Scale features
            X_scaled = self.scalers[disease].fit_transform(X_train)
            
            # Train model
            self.models[disease].fit(X_scaled, y_train)
            
            logger.info(f"Model trained for {disease}")
            
            # Save feature importance if available
            if hasattr(self.models[disease], 'feature_importances_'):
                self.feature_importance[disease] = self.models[disease].feature_importances_
            
        except Exception as e:
            logger.error(f"Error training model for {disease}: {e}")
            raise
    
    def save_models(self):
        """Save trained models to disk"""
        if not self.model_path:
            logger.warning("No model path specified, cannot save models")
            return
        
        os.makedirs(self.model_path, exist_ok=True)
        
        for disease in self.disease_types:
            try:
                model_file = os.path.join(self.model_path, f'{disease}_model.pkl')
                scaler_file = os.path.join(self.model_path, f'{disease}_scaler.pkl')
                
                with open(model_file, 'wb') as f:
                    pickle.dump(self.models[disease], f)
                with open(scaler_file, 'wb') as f:
                    pickle.dump(self.scalers[disease], f)
                
                logger.info(f"Saved model for {disease}")
            except Exception as e:
                logger.error(f"Error saving model for {disease}: {e}")
