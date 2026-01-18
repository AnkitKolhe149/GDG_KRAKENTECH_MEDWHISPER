# RENDER DEPLOYMENT - CONFIGURATION GUIDE

## Issue: Render using default `gunicorn app:app`

### Root Cause
Render may be using its own defaults or not reading the startCommand from render.yaml properly.

### Solution: Manual Configuration in Render Dashboard

**Since render.yaml might not override defaults, follow these steps:**

1. **Go to Render Dashboard**
   - Select your service/app
   - Click Settings

2. **Update Build Command**
   ```
   pip install -r requirements.txt
   ```

3. **Update Start Command** ⭐ CRITICAL
   ```
   gunicorn wsgi:app --workers 1 --worker-class sync --timeout 120 --bind 0.0.0.0:10000
   ```

4. **Set Environment Variables**
   - `FLASK_ENV`: production
   - `PYTHON_VERSION`: 3.13
   - `PORT`: 10000
   - Add Firebase credentials

5. **Save and redeploy**

---

## Why This Happens

Render follows this priority:
1. **Render Dashboard Settings** (highest priority) ← UPDATE HERE
2. render.yaml configuration
3. Procfile
4. Defaults

---

## Quick Fix Steps

### On Render Dashboard:

1. Click your service name
2. Go to **Settings** → **Build & Deploy**
3. Find "Start Command"
4. Replace: `gunicorn app:app`
5. With: `gunicorn wsgi:app --workers 1 --worker-class sync --timeout 120 --bind 0.0.0.0:10000`
6. Click **Save Changes**
7. Click **Manual Deploy** → **Deploy latest commit**

---

## Verify It Works

Once deployed:
```bash
# Check logs
- Visit your Render dashboard
- Go to "Logs"
- Should see: "Listening on 0.0.0.0:10000" (NOT an import error)
```

---

## If Still Failing

Try this alternative approach:

### Option 1: Remove app.py entirely
- Delete root `app.py`
- Only keep `wsgi.py`
- Restart deployment

### Option 2: Rename app directory
- Rename `app/` to `medwhisper/`
- Update imports in wsgi.py
- Update routes.py imports

---

## Files Status

✅ **render.yaml** - Created (may need manual override)
✅ **Procfile** - Correct configuration
✅ **wsgi.py** - WSGI entry point ready
✅ **build.sh** - Build verification script

**Next: Go to Render Dashboard and manually set the Start Command!**
