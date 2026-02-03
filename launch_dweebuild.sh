#!/bin/bash
# Dweebuild v31 Setup & Launch Script

set -e

echo "🔧 Dweebuild v31: The Architect Edition"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Navigate to app directory
cd "$(dirname "$0")/dweebuild_app"

# Check for virtual environment
if [ ! -d "../dwee_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../dwee_env
fi

# Activate virtual environment
echo "⚡ Activating environment..."
source ../dwee_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e .

# Install Playwright browsers
echo "🌐 Installing browsers..."
playwright install chromium --with-deps

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: GROQ_API_KEY not set!"
    echo "   Export your key: export GROQ_API_KEY='your-key-here'"
    echo ""
fi

# Launch
echo "🚀 Launching Dweebuild..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python launch.py
