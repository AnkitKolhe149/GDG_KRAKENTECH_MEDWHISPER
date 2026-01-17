# Silent Disease Engine - Setup Guide

## Quick Start (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Firebase

1. **Create Firebase Project**: Visit [Firebase Console](https://console.firebase.google.com/)
   - Click "Add Project"
   - Name it (e.g., "silent-disease-engine")
   - Disable Google Analytics (optional)

2. **Enable Authentication**:
   - Go to Authentication → Get Started
   - Click "Sign-in method" tab
   - Enable "Google" provider
   - Click Save

3. **Enable Firestore**:
   - Go to Firestore Database → Create Database
   - Start in test mode
   - Choose location (closest to you)

4. **Get Service Account Key**:
   - Go to Project Settings (⚙️ icon) → Service Accounts
   - Click "Generate new private key"
   - Save JSON file as `firebase-credentials.json` in project root

5. **Get Web Config**:
   - Go to Project Settings → General
   - Scroll to "Your apps" → Add app → Web
   - Register app
   - Copy the `firebaseConfig` object
   - Paste into `app/templates/base.html` (line 91)

### 3. Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and update:
```env
SECRET_KEY=your-random-secret-key-here
FIREBASE_DATABASE_URL=https://YOUR_PROJECT_ID.firebaseio.com
```

### 4. Run Application

```bash
python run.py
```

Visit `http://localhost:5000`

## Detailed Setup

### Firestore Security Rules (Important for Production)

Go to Firestore → Rules and update:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### Test Data

To test the application, you'll need to:
1. Sign in with Google
2. Navigate to "Add Data"
3. Enter sample health data in each tab
4. Click "Generate Assessment" from dashboard

### Sample Lab Data
- Glucose: 95 mg/dL (normal: 70-100)
- HbA1c: 5.4% (normal: <5.7%)
- Blood Pressure: 120/80 (normal: <120/80)
- Cholesterol: 180 mg/dL (normal: <200)

## Troubleshooting

### Firebase Connection Issues

**Error**: "Firebase credentials not found"
- **Solution**: Ensure `firebase-credentials.json` is in the project root
- Check the path in `.env` file

**Error**: "Permission denied" in Firestore
- **Solution**: Update Firestore rules (see above)
- For development, you can start in test mode

### Import Errors

**Error**: "ModuleNotFoundError"
- **Solution**: Activate virtual environment and reinstall:
  ```bash
  pip install -r requirements.txt
  ```

### Port Already in Use

**Error**: "Address already in use"
- **Solution**: Change port in `.env`:
  ```env
  PORT=8000
  ```

## Production Deployment

### 1. Update Configuration

Create production `.env`:
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=generate-a-secure-random-key
```

### 2. Update Firestore Rules

See "Firestore Security Rules" above

### 3. Deploy to Cloud Platform

Choose one:

#### Google Cloud (Recommended)
```bash
gcloud app deploy
```

#### Heroku
```bash
heroku create
git push heroku main
```

#### DigitalOcean/AWS/Azure
Use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Need Help?

- Check [README.md](README.md) for full documentation
- Open an issue on GitHub
- Contact the development team

---

**Next Steps**: After setup, sign in and add your first health data!
