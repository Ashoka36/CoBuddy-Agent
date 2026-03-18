#!/bin/bash

# Co-Buddy AGI Startup Script for Render
# Prevents hanging issues and ensures clean startup

set -e

echo "🚀 Starting Co-Buddy AGI System..."

# Set environment variables for production
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export DEBIAN_FRONTEND=noninteractive

# Create necessary directories
mkdir -p logs models data

# Wait a moment to ensure all systems are ready
sleep 2

echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "🧠 Initializing AGI Core..."
# Test imports to catch any issues early
python -c "
try:
    from server.cobuddy_lightweight import app
    print('✅ Server imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "🌐 Starting server on port ${PORT:-8002}..."
exec python server/cobuddy_lightweight.py --host 0.0.0.0 --port ${PORT:-8002}
