#!/bin/bash

echo "🚀 AI HR Interview System - Quick Start (Development Mode)"
echo "========================================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "❌ Please run this script from the ai-hr-interview root directory"
    echo "   cd ~/Documents/ai-hr-interview"
    echo "   ./quick_start.sh"
    exit 1
fi

echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.11+ from https://python.org or use Homebrew:"
    echo "  brew install python@3.11"
    exit 1
else
    echo "✅ Python 3 found: $(python3 --version)"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js 18+ from https://nodejs.org or use Homebrew:"
    echo "  brew install node"
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
echo "🔧 Setting up Backend..."

# Setup Python virtual environment
cd backend
if [[ ! -d "venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🌐 Setting up Frontend..."

# Setup Node.js dependencies
cd ../frontend
if [[ ! -d "node_modules" ]]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node.js dependencies already installed"
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""

# Create terminal scripts for easy startup
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./app.db"
export STT_ENGINE="mock"
export LLM_ENGINE="mock"
echo "🔧 Starting Backend API on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "🌐 Starting Frontend on http://localhost:3000"
npm run dev
EOF

chmod +x start_backend.sh start_frontend.sh

echo "🎯 To start the system:"
echo ""
echo "Terminal 1 - Backend API:"
echo "  ./start_backend.sh"
echo ""
echo "Terminal 2 - Frontend:"
echo "  ./start_frontend.sh"
echo ""
echo "Then visit: http://localhost:3000"
echo ""
echo "📝 Development Mode Features:"
echo "  ✅ File upload and processing"
echo "  ✅ Mock interview questions"
echo "  ✅ Audio recording (mock transcription)"
echo "  ✅ Mock AI evaluation"
echo "  ✅ Proctoring simulation"
echo "  ✅ Report generation"
echo "  ✅ Live coding interface (no execution)"
echo ""
echo "⚠️  Note: This is DEMO MODE - no database, no real AI services"
echo "   Perfect for testing the UI and workflow!"
echo ""
echo "🚀 Quick start:"
echo "  Open 2 terminal windows and run:"
echo "    Terminal 1: ./start_backend.sh"
echo "    Terminal 2: ./start_frontend.sh"
echo ""