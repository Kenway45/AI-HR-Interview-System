#!/bin/bash

echo "Setting up AI HR Interview System for Development (No Docker)"
echo "============================================================"

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "Please run this script from the ai-hr-interview root directory"
    exit 1
fi

echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Install Python 3.11+ from https://python.org or use Homebrew:"
    echo "brew install python@3.11"
    exit 1
else
    echo "✅ Python 3 found: $(python3 --version)"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Install Node.js 18+ from https://nodejs.org or use Homebrew:"
    echo "brew install node"
    exit 1
else
    echo "✅ Node.js found: $(node --version)"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
else
    echo "✅ npm found: $(npm --version)"
fi

echo ""
echo "Setting up Backend..."

# Setup Python virtual environment
cd backend
if [[ ! -d "venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setting up Frontend..."

# Setup Node.js dependencies
cd ../frontend
if [[ ! -d "node_modules" ]]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node.js dependencies already installed"
fi

echo ""
echo "✅ Development Setup Complete!"
echo ""
echo "To run the system in development mode:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd ~/Documents/ai-hr-interview/backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd ~/Documents/ai-hr-interview/frontend"
echo "  npm run dev"
echo ""
echo "Then access the application at: http://localhost:3000"
echo ""
echo "⚠️  Note: In development mode, some features will be limited:"
echo "   - No speech-to-text (requires Whisper.cpp)"
echo "   - No LLM evaluation (requires local AI models)"
echo "   - No code execution (requires Judge0)"
echo "   - No file storage (requires MinIO)"
echo ""
echo "For full functionality, install Docker and use the complete system."
echo ""