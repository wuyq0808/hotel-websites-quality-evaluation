#!/bin/bash
# Build script for Quality Evaluation Tool
# Creates a standalone executable using PyInstaller

set -e  # Exit on error

echo "🔨 Building Quality Evaluation Tool..."

# Check if we're in the right directory
if [ ! -d "src" ] || [ ! -f "src/quality_evaluator_agent.py" ]; then
    echo "❌ Error: src/ directory or main script not found. Are you in the right directory?"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment: venv"
    source venv/bin/activate
elif [ -d "../agentcore_env" ]; then
    echo "🔧 Activating virtual environment: agentcore_env"
    source ../agentcore_env/bin/activate
else
    echo "⚠️  Warning: No virtual environment found."
    echo "   Continuing with system Python..."
fi

# Check if config.yaml exists in src
if [ ! -f "src/config.yaml" ]; then
    echo "❌ Error: src/config.yaml not found. Cannot build without configuration."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/

# Install PyInstaller if not already installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Build the executable
echo "🔧 Running PyInstaller..."
pyinstaller quality_evaluation.spec

# Check if build succeeded
if [ -f "dist/quality_evaluation" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📦 Executable location: dist/quality_evaluation"
    echo ""

    # Create release package
    echo "📦 Creating release package..."
    cd dist
    DATE_STAMP=$(date +%Y%m%d)
    RELEASE_DIR="quality_evaluation_release_$DATE_STAMP"
    rm -rf "$RELEASE_DIR" quality_evaluation_release_*.tar.gz
    mkdir -p "$RELEASE_DIR"
    cp quality_evaluation ../src/config.yaml "$RELEASE_DIR/"
    tar -czf "$RELEASE_DIR.tar.gz" "$RELEASE_DIR/"

    # Clean up intermediate files, keep only tarball
    rm -rf "$RELEASE_DIR" quality_evaluation config.yaml

    echo "✅ Release package created: dist/$RELEASE_DIR.tar.gz"
    cd ..

    echo ""
    echo "📝 To test locally:"
    echo "   cd dist/$RELEASE_DIR"
    echo "   ./quality_evaluation"
    echo ""
    echo "📤 To distribute:"
    echo "   Share: dist/$RELEASE_DIR.tar.gz"
    echo ""
    echo "⚙️  Configuration:"
    echo "   - Edit config.yaml to customize settings"
    echo "   - config.yaml is self-documented with inline comments"
    echo ""
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
