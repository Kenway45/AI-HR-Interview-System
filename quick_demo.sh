#!/bin/bash

# 🎤 CodeVox Quick Demo - Fast startup for exploration
# Mock AI services for instant startup

set -e

echo "⚡ CodeVox Quick Demo - Fast startup for exploration"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting CodeVox in demo mode (mock AI)...${NC}"
echo -e "${YELLOW}   • Fast startup (no AI model downloads)${NC}"
echo -e "${YELLOW}   • Full UI exploration${NC}"
echo -e "${YELLOW}   • Perfect for trying CodeVox${NC}"
echo ""

# Start backend with demo configuration
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo -e "${GREEN}🎤 Starting demo backend...${NC}"
nohup uvicorn app.main_demo:app --host 0.0.0.0 --port 8000 > ../codevox-demo-backend.log 2>&1 &
BACKEND_PID=$!

cd ../frontend

echo -e "${GREEN}🌐 Starting frontend...${NC}"
npm install --silent
nohup npm run dev > ../codevox-demo-frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

sleep 5

echo ""
echo "🎉 CodeVox Demo is ready!"
echo ""
echo -e "${GREEN}🌐 Open: http://localhost:3000${NC}"
echo -e "${YELLOW}📝 Note: Using mock AI for fast demo${NC}"
echo ""
echo -e "${GREEN}Happy exploring! 🚀${NC}"

# Save PIDs and wait
echo "$BACKEND_PID" > .codevox-demo-backend.pid
echo "$FRONTEND_PID" > .codevox-demo-frontend.pid

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .codevox-demo-*.pid; exit 0' SIGINT SIGTERM
wait