#!/bin/bash
# Startup script for Quality Evaluation Web App

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Quality Evaluation Web App${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Setting up...${NC}"
    ./setup_build_env.sh
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Flask if not already installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Installing Flask...${NC}"
    pip install flask>=2.3.0
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if config-editor.html exists
if [ ! -f "config-editor.html" ]; then
    echo -e "${YELLOW}Warning: config-editor.html not found${NC}"
    exit 1
fi

# Check if web_app.py exists
if [ ! -f "src/web_app.py" ]; then
    echo -e "${YELLOW}Warning: src/web_app.py not found${NC}"
    exit 1
fi

# Start the web server
echo -e "${GREEN}Starting web server...${NC}"
echo -e "${BLUE}Open your browser to: http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Try to open browser (macOS)
if command -v open &> /dev/null; then
    sleep 2 && open http://localhost:5000 &
fi

# Run the Flask app
python3 src/web_app.py
