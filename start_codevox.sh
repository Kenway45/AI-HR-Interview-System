#!/bin/bash

# 🎤 CodeVox - Voice-first interviews. Live coding. Honest scores.
# Startup script for CodeVox interview practice system

set -e

echo "🎤 CodeVox - Voice-first interviews. Live coding. Honest scores."
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check system requirements
echo -e "${BLUE}🔍 Checking system requirements...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/app/main_simple.py" ]; then
    echo -e "${RED}❌ Please run this script from the CodeVox root directory${NC}"
    exit 1
fi

echo -e "${GREEN}✅ System requirements met${NC}"
echo ""

# Setup backend
echo -e "${BLUE}🚀 Setting up CodeVox backend...${NC}"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Start backend server
echo -e "${GREEN}🎤 Starting CodeVox backend server...${NC}"
echo -e "${YELLOW}   Backend will run on: http://localhost:8000${NC}"
echo -e "${YELLOW}   API docs available at: http://localhost:8000/docs${NC}"

nohup uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 > ../codevox-backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to start
sleep 3

# Setup frontend
echo -e "${BLUE}🖥️  Setting up CodeVox frontend...${NC}"

cd frontend

# Install Node.js dependencies
echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
npm install --silent

# Start frontend server
echo -e "${GREEN}🌐 Starting CodeVox frontend...${NC}"
echo ""

# Start frontend (this will block)
nohup npm run dev > ../codevox-frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for services to fully start
echo -e "${YELLOW}⏳ Starting CodeVox services...${NC}"
sleep 5

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend failed to start. Check codevox-backend.log${NC}"
    exit 1
fi

# Save PIDs for cleanup
echo "$BACKEND_PID" > .codevox-backend.pid
echo "$FRONTEND_PID" > .codevox-frontend.pid

echo ""
echo "🎉 CodeVox is ready for interview practice!"
echo ""
echo -e "${GREEN}🌐 Open your browser to: http://localhost:3000${NC}"
echo -e "${BLUE}📚 API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}💡 Tips for effective practice:${NC}"
echo "   • Grant microphone permissions when prompted"
echo "   • Upload a real job description for targeted questions"
echo "   • Practice speaking your answers out loud"
echo "   • Use the live coding environment to explain your solutions"
echo ""
echo -e "${YELLOW}🛑 To stop CodeVox:${NC}"
echo "   pkill -f 'uvicorn|vite' && rm -f .codevox-*.pid"
echo ""
echo -e "${GREEN}Happy practicing! 🚀${NC}"

# Keep the script running and monitor services
trap 'echo "Stopping CodeVox..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .codevox-*.pid; exit 0' SIGINT SIGTERM

# Wait for services
wait