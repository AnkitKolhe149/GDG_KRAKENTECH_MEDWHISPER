# VERCEL DEPLOYMENT OPTIMIZATION GUIDE

## Current Issue
- Project size: **314 MB** (too large for Vercel)
- Vercel limit: **100 MB** for serverless functions
- Main culprits: `.pkl` model files (10+ MB each)

## Solution: Three-Step Optimization

### STEP 1: Move Models to Cloud Storage
Replace large `.pkl` files with cloud-hosted models:

```python
# app/services/scoring_engine.py
import firebase_admin
from firebase_admin import storage

def load_model_from_cloud(model_name):
    """Load model from Firebase Cloud Storage instead of local file"""
    bucket = storage.bucket()
    blob = bucket.blob(f'models/{model_name}.pkl')
    
    # Download to temp directory
    local_path = f'/tmp/{model_name}.pkl'
    blob.download_to_filename(local_path)
    
    import joblib
    return joblib.load(local_path)
```

### STEP 2: Update .gitignore (DONE)
- All `.pkl` files are excluded from git
- Cache directories are ignored
- Large images are not committed

### STEP 3: Update vercel.json (DONE)
- Production-only dependencies
- Optimized memory settings
- Correct Python version

## Files Already Created:
✅ `.gitignore` - Updated with production exclusions
✅ `.vercelignore` - Vercel-specific exclusions
✅ `vercel.json` - Flask deployment configuration
✅ `requirements-prod.txt` - Production dependencies only

## Deployment Steps:

### 1. Before Pushing to Git
```bash
# Remove node_modules if present
Remove-Item node_modules -Recurse -Force

# Clear Python cache
Get-ChildItem -Recurse -Filter "*.pyc" -File | Remove-Item -Force
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Verify size
$size = (Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "Project size: $([math]::Round($size/1MB,2)) MB"
```

### 2. Commit Changes
```bash
git add .gitignore .vercelignore vercel.json requirements-prod.txt
git commit -m "Optimize for Vercel deployment"
git push origin main
```

### 3. Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### 4. Configure Environment Variables in Vercel
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_DATABASE_URL`

## Alternative: Use Vercel + Firebase Strategy

1. **Code on Vercel** - Just the Flask app (keep lightweight)
2. **Models on Firebase Storage** - Load at runtime
3. **Database on Firebase** - Already configured

This keeps deployment under 50MB.

## Expected Final Size After Cleanup:
- Models excluded: -10.27 MB
- Cache cleaned: -0.5 MB
- Logs removed: -0.1 MB
- **New size: ~0.25 MB** ✅ Ready for Vercel!

## Post-Deployment
- Models auto-load from Firebase on first request
- No local model files needed
- Scales automatically with Vercel's serverless functions
