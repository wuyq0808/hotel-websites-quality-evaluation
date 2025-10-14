#!/bin/bash
# Setup build environment for Quality Evaluation Tool
# Run this once to install all build dependencies

set -e

echo "🔧 Setting up build environment for Quality Evaluation Tool..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📍 Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found: quality_evaluation/venv"
    source venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created: quality_evaluation/venv"
fi

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing core dependencies..."
    pip install pyyaml strands tenacity boto3 playwright
fi

# Install PyInstaller
echo ""
echo "📦 Installing PyInstaller..."
pip install pyinstaller

# Install Playwright browsers (needed for browser automation)
echo ""
echo "🌐 Installing Playwright browsers..."
playwright install

# Verify installation
echo ""
echo "✅ Verifying installation..."
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python3 -c "import yaml; import strands; import tenacity; import PyInstaller; print('All imports successful!')"

# Check config exists
if [ ! -f "config.yaml" ]; then
    echo ""
    echo "⚠️  Warning: config.yaml not found"
    echo "   You'll need config.yaml before building"
fi

echo ""
echo "✅ Build environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit config.yaml to customize settings"
echo "   2. Run: ./build.sh"
echo "   3. Test: cd dist && ./quality_evaluation"
echo ""
