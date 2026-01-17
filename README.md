# Silent Disease Early Detection Engine

AI-driven early risk detection system for silent diseases including diabetes, hypertension, liver disorders, cardiac risk, and mental health conditions.

## 🎯 Problem Statement

A large percentage of life-threatening diseases remain undiagnosed for years because symptoms are mild, ignored, or fragmented across reports. This application provides predictive prevention rather than reactive diagnosis.

## ✨ Features

- **Multi-Disease Detection**: Predicts risk for diabetes, hypertension, liver disease, cardiac risk, and mental health conditions
- **AI-Powered Analysis**: Uses ensemble ML models (XGBoost, LightGBM, Random Forest, Gradient Boosting)
- **Comprehensive Data Aggregation**: 
  - Lab trends over time
  - Lifestyle data (sleep, activity, nutrition)
  - Stress & mental health indicators
  - Family history patterns
- **Risk Probability Scores**: Generates probability scores (0-100%), not binary outcomes
- **Personalized Recommendations**: Provides preventive action recommendations
- **Firebase Integration**: Secure authentication with Google Sign-In and cloud data storage
- **Beautiful Dashboard**: Modern, responsive UI with real-time risk visualization

## 🏗️ Architecture

```
silent-disease-engine/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── routes.py                # API routes & endpoints
│   ├── models/
│   │   ├── risk_model.py        # ML models for disease prediction
│   ├── services/
│   │   ├── data_pipeline.py     # Data storage/retrieval (Firestore)
│   │   ├── feature_engineering.py  # Feature extraction & transformation
│   │   ├── firebase_auth.py     # Authentication service
│   │   ├── scoring_engine.py    # Risk scoring & recommendations
│   ├── templates/               # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── data_input.html
│   │   ├── risk_report.html
│   ├── utils/
│       ├── logger.py            # Logging configuration
│       ├── preprocess.py        # Data validation & preprocessing
├── data/
│   ├── raw/                     # Raw data storage
│   ├── processed/               # Processed data
├── models_store/                # Trained ML models
├── logs/                        # Application logs
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Firebase account (for authentication and Firestore)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GFGBQ-Team-jumpyrock/silent-disease-engine
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Firebase Setup

#### a. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Enable Google Authentication:
   - Go to Authentication → Sign-in method
   - Enable Google provider
4. Enable Firestore Database:
   - Go to Firestore Database → Create database
   - Start in test mode (for development)

#### b. Download Service Account Key

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save the JSON file as `firebase-credentials.json` in the project root

#### c. Get Firebase Web Config

1. Go to Project Settings → General
2. Scroll to "Your apps" → Web app
3. Copy the Firebase configuration
4. Update the configuration in `app/templates/base.html`:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# Application Settings
HOST=0.0.0.0
PORT=5000
```

### 6. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📊 Data Structure

### Lab Data
```json
{
    "test_date": "2026-01-01",
    "glucose": 95,
    "hba1c": 5.4,
    "cholesterol": 180,
    "hdl": 55,
    "ldl": 100,
    "triglycerides": 125,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "heart_rate": 72,
    "liver_enzymes": {"alt": 25, "ast": 30},
    "kidney_function": {"creatinine": 0.9, "bun": 15}
}
```

### Lifestyle Data
```json
{
    "date": "2026-01-01",
    "sleep_hours": 7.5,
    "sleep_quality": "good",
    "exercise_minutes": 30,
    "steps": 8000,
    "water_intake_ml": 2000,
    "diet_quality": "balanced",
    "smoking": false
}
```

### Mental Health Data
```json
{
    "date": "2026-01-01",
    "stress_level": 5,
    "mood": "neutral",
    "anxiety_level": 3,
    "social_interaction": "moderate",
    "work_life_balance": "fair"
}
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/verify` - Verify Firebase token
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Health Data
- `POST /api/data/lab` - Submit lab results
- `POST /api/data/lifestyle` - Submit lifestyle data
- `POST /api/data/mental-health` - Submit mental health data
- `POST /api/data/family-history` - Submit family history
- `GET /api/data/history` - Get all health data

### Risk Assessment
- `POST /api/assessment/generate` - Generate risk assessment
- `GET /api/assessment/latest` - Get latest assessment
- `GET /api/assessment/history` - Get all assessments

### Analytics
- `GET /api/analytics/trends` - Get health trends

## 🤖 Machine Learning Models

The system uses ensemble learning with multiple algorithms:

- **XGBoost**: Diabetes prediction
- **Gradient Boosting**: Hypertension & mental health
- **LightGBM**: Liver disease
- **Random Forest**: Cardiac risk

### Feature Engineering

The system extracts 50+ features including:
- Lab value trends and variability
- Lifestyle patterns and consistency
- Mental health indicators
- Genetic predisposition scores
- Derived risk factors

## 🎨 User Interface

### Pages

1. **Landing Page** (`/`): Introduction and sign-in
2. **Dashboard** (`/dashboard`): Overview and quick actions
3. **Data Input** (`/data-input`): Multi-tab data entry forms
4. **Risk Report** (`/risk-report`): Comprehensive risk assessment visualization

## 🔒 Security Features

- Firebase Authentication with Google Sign-In
- JWT token-based API authentication
- Input validation and sanitization
- CORS protection
- Secure data storage in Firestore



## 📈 Future Enhancements

- [ ] Integration with wearable devices (Fitbit, Apple Watch)
- [ ] PDF report generation
- [ ] Email notifications for high-risk alerts
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Doctor portal for patient monitoring
- [ ] Historical trend visualization with charts
- [ ] Integration with electronic health records (EHR)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

**This application is for medical reference and educational purposes only. It does not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.**

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

<<<<<<< Updated upstream
GDG_KRAKENTECH
=======
Team KrakenTech
>>>>>>> Stashed changes

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using Flask, Firebase, and Machine Learning**
