"""Risk Scoring Engine with Recommendations"""
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskScoringEngine:
    """Generate risk scores and preventive recommendations"""
    
    def __init__(self, risk_thresholds: Dict):
        self.risk_thresholds = risk_thresholds
        self.recommendations_db = self._initialize_recommendations()
    
    def generate_risk_report(self, risk_scores: Dict, features: Dict, user_profile: Dict) -> Dict:
        """
        Generate comprehensive risk report with recommendations
        
        Args:
            risk_scores: Dictionary of disease risk scores (0-1)
            features: Engineered features used for prediction
            user_profile: User profile information
            
        Returns:
            Complete risk assessment report
        """
        try:
            report = {
                'user_id': user_profile.get('uid', ''),
                'user_name': user_profile.get('name', ''),
                'report_date': datetime.now().isoformat(),
                'risk_assessments': {},
                'overall_risk_score': 0,
                'priority_actions': [],
                'detailed_recommendations': {},
                'key_risk_factors': []
            }
            
            # Generate assessment for each disease
            total_risk = 0
            for disease, score in risk_scores.items():
                risk_level = self._get_risk_level(score, disease)
                assessment = {
                    'disease': disease,
                    'risk_score': round(score * 100, 2),  # Convert to percentage
                    'risk_level': risk_level,
                    'confidence': self._calculate_confidence(features),
                    'contributing_factors': self._identify_risk_factors(disease, features),
                    'recommendations': self._get_recommendations(disease, risk_level, features)
                }
                report['risk_assessments'][disease] = assessment
                total_risk += score
            
            # Calculate overall risk
            report['overall_risk_score'] = round((total_risk / len(risk_scores)) * 100, 2)
            
            # Identify priority actions
            report['priority_actions'] = self._prioritize_actions(report['risk_assessments'])
            
            # Get detailed recommendations
            report['detailed_recommendations'] = self._generate_detailed_recommendations(
                report['risk_assessments'], features
            )
            
            # Identify key risk factors across all diseases
            report['key_risk_factors'] = self._identify_key_risk_factors(features)
            
            # Add metadata
            report['data_completeness'] = self._assess_data_completeness(features)
            report['next_assessment_date'] = self._suggest_next_assessment(report['risk_assessments'])
            
            logger.info(f"Risk report generated for user: {user_profile.get('uid', '')}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return {}
    
    def _get_risk_level(self, score: float, disease: str) -> str:
        """Determine risk level from score"""
        thresholds = self.risk_thresholds.get(disease, {'low': 0.3, 'medium': 0.5, 'high': 0.7})
        
        if score < thresholds['low']:
            return 'low'
        elif score < thresholds['medium']:
            return 'medium'
        elif score < thresholds['high']:
            return 'high'
        else:
            return 'very_high'
    
    def _calculate_confidence(self, features: Dict) -> str:
        """Calculate confidence level based on data completeness"""
        # Check how many key features have non-zero values
        key_features = [
            'glucose_latest', 'bp_systolic_latest', 'avg_sleep_hours',
            'avg_exercise_minutes', 'avg_stress_level'
        ]
        
        available = sum(1 for feat in key_features if features.get(feat, 0) > 0)
        completeness = available / len(key_features)
        
        if completeness >= 0.8:
            return 'high'
        elif completeness >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_factors(self, disease: str, features: Dict) -> List[str]:
        """Identify contributing risk factors for a specific disease"""
        risk_factors = []
        
        if disease == 'diabetes':
            if features.get('glucose_latest', 0) >= 100:
                risk_factors.append('Elevated glucose levels')
            if features.get('hba1c_latest', 0) >= 5.7:
                risk_factors.append('Elevated HbA1c')
            if features.get('has_family_diabetes', 0) == 1:
                risk_factors.append('Family history of diabetes')
            if features.get('sedentary_lifestyle', 0) == 1:
                risk_factors.append('Sedentary lifestyle')
            if features.get('diet_quality_score', 0) < 2.5:
                risk_factors.append('Poor diet quality')
        
        elif disease == 'hypertension':
            if features.get('bp_systolic_latest', 0) >= 130:
                risk_factors.append('Elevated blood pressure')
            if features.get('has_family_hypertension', 0) == 1:
                risk_factors.append('Family history of hypertension')
            if features.get('avg_stress_level', 0) >= 7:
                risk_factors.append('High stress levels')
            if features.get('avg_alcohol_units', 0) > 2:
                risk_factors.append('Excessive alcohol consumption')
            if features.get('smoking', 0) == 1:
                risk_factors.append('Smoking')
        
        elif disease == 'liver_disease':
            if features.get('alt_latest', 0) > 30 or features.get('ast_latest', 0) > 30:
                risk_factors.append('Elevated liver enzymes')
            if features.get('avg_alcohol_units', 0) > 2:
                risk_factors.append('Excessive alcohol consumption')
            if features.get('diet_quality_score', 0) < 2.5:
                risk_factors.append('Poor diet')
        
        elif disease == 'cardiac_risk':
            if features.get('cholesterol_latest', 0) > 200:
                risk_factors.append('Elevated cholesterol')
            if features.get('bp_systolic_latest', 0) >= 130:
                risk_factors.append('High blood pressure')
            if features.get('smoking', 0) == 1:
                risk_factors.append('Smoking')
            if features.get('has_family_heart_disease', 0) == 1:
                risk_factors.append('Family history of heart disease')
            if features.get('exercise_frequency', 0) < 0.3:
                risk_factors.append('Insufficient exercise')
        
        elif disease == 'mental_health':
            if features.get('avg_stress_level', 0) >= 7:
                risk_factors.append('Chronic high stress')
            if features.get('avg_mood_score', 0) <= 2.5:
                risk_factors.append('Low mood')
            if features.get('avg_sleep_hours', 0) < 6:
                risk_factors.append('Sleep deprivation')
            if features.get('social_interaction_score', 0) <= 1:
                risk_factors.append('Social isolation')
            if features.get('work_life_balance_score', 0) <= 2:
                risk_factors.append('Poor work-life balance')
        
        return risk_factors if risk_factors else ['No significant risk factors identified']
    
    def _get_recommendations(self, disease: str, risk_level: str, features: Dict) -> List[str]:
        """Get recommendations based on disease and risk level"""
        recommendations = []
        
        # Get base recommendations for disease and risk level
        base_recs = self.recommendations_db.get(disease, {}).get(risk_level, [])
        recommendations.extend(base_recs)
        
        # Add personalized recommendations based on features
        personalized = self._get_personalized_recommendations(disease, features)
        recommendations.extend(personalized)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_personalized_recommendations(self, disease: str, features: Dict) -> List[str]:
        """Generate personalized recommendations based on specific risk factors"""
        recommendations = []
        
        if disease == 'diabetes':
            if features.get('sedentary_lifestyle', 0) == 1:
                recommendations.append('Increase physical activity to at least 150 minutes per week')
            if features.get('diet_quality_score', 0) < 2.5:
                recommendations.append('Consult a nutritionist for a diabetes-prevention diet plan')
        
        elif disease == 'hypertension':
            if features.get('avg_stress_level', 0) >= 7:
                recommendations.append('Practice stress-reduction techniques like meditation or yoga')
            if features.get('avg_alcohol_units', 0) > 2:
                recommendations.append('Reduce alcohol consumption to recommended limits')
        
        elif disease == 'mental_health':
            if features.get('avg_sleep_hours', 0) < 6:
                recommendations.append('Improve sleep hygiene and aim for 7-9 hours of sleep')
            if features.get('social_interaction_score', 0) <= 1:
                recommendations.append('Increase social connections and community engagement')
        
        return recommendations
    
    def _prioritize_actions(self, risk_assessments: Dict) -> List[Dict]:
        """Prioritize actions based on risk levels"""
        priority_actions = []
        
        # Sort diseases by risk score
        sorted_risks = sorted(
            risk_assessments.items(),
            key=lambda x: x[1]['risk_score'],
            reverse=True
        )
        
        # Add high-priority items
        for disease, assessment in sorted_risks:
            if assessment['risk_level'] in ['high', 'very_high']:
                priority_actions.append({
                    'disease': disease,
                    'risk_score': assessment['risk_score'],
                    'action': f'Consult a healthcare provider for {disease.replace("_", " ")} assessment',
                    'urgency': 'high'
                })
        
        # Add medium-priority items
        for disease, assessment in sorted_risks:
            if assessment['risk_level'] == 'medium' and len(priority_actions) < 5:
                priority_actions.append({
                    'disease': disease,
                    'risk_score': assessment['risk_score'],
                    'action': f'Monitor {disease.replace("_", " ")} risk factors',
                    'urgency': 'medium'
                })
        
        return priority_actions
    
    def _generate_detailed_recommendations(self, risk_assessments: Dict, features: Dict) -> Dict:
        """Generate detailed recommendations by category"""
        recommendations = {
            'lifestyle': [],
            'medical': [],
            'monitoring': [],
            'prevention': []
        }
        
        # Lifestyle recommendations
        if features.get('sedentary_lifestyle', 0) == 1:
            recommendations['lifestyle'].append('Engage in regular physical activity (150 min/week)')
        if features.get('avg_sleep_hours', 0) < 7:
            recommendations['lifestyle'].append('Improve sleep duration to 7-9 hours per night')
        if features.get('diet_quality_score', 0) < 3:
            recommendations['lifestyle'].append('Adopt a balanced, nutrient-rich diet')
        
        # Medical recommendations
        high_risk_diseases = [d for d, a in risk_assessments.items() if a['risk_level'] in ['high', 'very_high']]
        for disease in high_risk_diseases:
            recommendations['medical'].append(
                f'Schedule consultation with healthcare provider for {disease.replace("_", " ")}'
            )
        
        # Monitoring recommendations
        if features.get('glucose_latest', 0) >= 100:
            recommendations['monitoring'].append('Monitor blood glucose levels monthly')
        if features.get('bp_systolic_latest', 0) >= 130:
            recommendations['monitoring'].append('Track blood pressure daily')
        
        # Prevention recommendations
        recommendations['prevention'].append('Maintain regular health check-ups')
        recommendations['prevention'].append('Keep detailed health records and symptom diary')
        
        return recommendations
    
    def _identify_key_risk_factors(self, features: Dict) -> List[Dict]:
        """Identify top risk factors across all conditions"""
        risk_factors = []
        
        if features.get('has_family_diabetes', 0) == 1 or features.get('has_family_hypertension', 0) == 1:
            risk_factors.append({
                'factor': 'Genetic predisposition',
                'severity': 'high',
                'modifiable': False
            })
        
        if features.get('sedentary_lifestyle', 0) == 1:
            risk_factors.append({
                'factor': 'Sedentary lifestyle',
                'severity': 'medium',
                'modifiable': True
            })
        
        if features.get('smoking', 0) == 1:
            risk_factors.append({
                'factor': 'Smoking',
                'severity': 'very_high',
                'modifiable': True
            })
        
        if features.get('avg_stress_level', 0) >= 7:
            risk_factors.append({
                'factor': 'Chronic stress',
                'severity': 'high',
                'modifiable': True
            })
        
        return risk_factors
    
    def _assess_data_completeness(self, features: Dict) -> Dict:
        """Assess completeness of health data"""
        categories = {
            'lab_data': ['glucose_latest', 'bp_systolic_latest', 'cholesterol_latest'],
            'lifestyle_data': ['avg_sleep_hours', 'avg_exercise_minutes', 'avg_steps'],
            'mental_health': ['avg_stress_level', 'avg_mood_score'],
            'family_history': ['has_family_diabetes', 'has_family_hypertension']
        }
        
        completeness = {}
        for category, feature_list in categories.items():
            available = sum(1 for feat in feature_list if features.get(feat, 0) > 0)
            completeness[category] = round((available / len(feature_list)) * 100, 2)
        
        return completeness
    
    def _suggest_next_assessment(self, risk_assessments: Dict) -> str:
        """Suggest when next assessment should be done"""
        max_risk = max(a['risk_score'] for a in risk_assessments.values())
        
        if max_risk >= 70:
            return '1 month'
        elif max_risk >= 50:
            return '3 months'
        else:
            return '6 months'
    
    def _initialize_recommendations(self) -> Dict:
        """Initialize recommendation database"""
        return {
            'diabetes': {
                'low': [
                    'Maintain healthy weight through balanced diet',
                    'Exercise regularly (150 minutes per week)',
                    'Monitor blood sugar annually'
                ],
                'medium': [
                    'Consult with healthcare provider for glucose screening',
                    'Adopt low-glycemic diet',
                    'Increase physical activity',
                    'Monitor blood sugar every 6 months'
                ],
                'high': [
                    'Immediate consultation with endocrinologist',
                    'Comprehensive glucose tolerance testing',
                    'Create diabetes prevention plan',
                    'Monitor blood sugar monthly'
                ],
                'very_high': [
                    'Urgent medical evaluation required',
                    'Immediate lifestyle intervention',
                    'Consider medication consultation',
                    'Weekly glucose monitoring'
                ]
            },
            'hypertension': {
                'low': [
                    'Maintain healthy blood pressure through diet',
                    'Regular cardiovascular exercise',
                    'Limit sodium intake'
                ],
                'medium': [
                    'Monitor blood pressure weekly',
                    'Reduce sodium to <2300mg/day',
                    'Consult with healthcare provider',
                    'Manage stress through relaxation techniques'
                ],
                'high': [
                    'Immediate medical consultation',
                    'Daily blood pressure monitoring',
                    'Strict DASH diet adherence',
                    'Medication evaluation'
                ],
                'very_high': [
                    'Emergency medical evaluation',
                    'Immediate blood pressure management',
                    'Comprehensive cardiovascular assessment',
                    'Multiple daily BP measurements'
                ]
            },
            'liver_disease': {
                'low': [
                    'Maintain liver health through balanced diet',
                    'Limit alcohol consumption',
                    'Annual liver function tests'
                ],
                'medium': [
                    'Consult hepatologist for evaluation',
                    'Reduce or eliminate alcohol',
                    'Liver function tests every 6 months',
                    'Consider hepatitis screening'
                ],
                'high': [
                    'Immediate hepatology consultation',
                    'Comprehensive liver assessment',
                    'Abstain from alcohol',
                    'Quarterly liver monitoring'
                ],
                'very_high': [
                    'Urgent hepatology evaluation',
                    'Complete abstinence from alcohol',
                    'Imaging studies (ultrasound/MRI)',
                    'Monthly liver function monitoring'
                ]
            },
            'cardiac_risk': {
                'low': [
                    'Maintain heart-healthy diet',
                    'Regular aerobic exercise',
                    'Annual cardiovascular check-up'
                ],
                'medium': [
                    'Cardiology consultation',
                    'Lipid profile every 6 months',
                    'Increase cardiovascular exercise',
                    'Consider cardiac calcium scoring'
                ],
                'high': [
                    'Immediate cardiology evaluation',
                    'Comprehensive cardiac workup',
                    'Aggressive risk factor management',
                    'Consider stress test'
                ],
                'very_high': [
                    'Emergency cardiac assessment',
                    'Immediate intervention planning',
                    'Medication optimization',
                    'Close cardiac monitoring'
                ]
            },
            'mental_health': {
                'low': [
                    'Practice stress management techniques',
                    'Maintain social connections',
                    'Ensure adequate sleep'
                ],
                'medium': [
                    'Consider counseling or therapy',
                    'Develop coping strategies',
                    'Regular mental health check-ins',
                    'Improve work-life balance'
                ],
                'high': [
                    'Immediate mental health professional consultation',
                    'Comprehensive psychological assessment',
                    'Consider therapy or medication',
                    'Build strong support network'
                ],
                'very_high': [
                    'Urgent mental health intervention',
                    'Immediate psychiatric evaluation',
                    'Crisis support resources',
                    'Intensive treatment consideration'
                ]
            }
        }
