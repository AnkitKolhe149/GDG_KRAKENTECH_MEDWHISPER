#!/bin/bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Verify wsgi.py can be imported
python -c "from wsgi import app; print('✓ WSGI app loaded successfully')"
