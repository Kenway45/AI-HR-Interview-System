#!/bin/bash

echo "🚀 Starting AI HR Interview System"
echo "=================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn|vite" 2>/dev/null || true
sleep 3

# Start Backend
echo "🔧 Starting Backend API..."
cd backend
source venv/bin/activate
python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start Frontend
echo "🌐 Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
sleep 5

echo ""
echo "🎉 System Started Successfully!"
echo "================================"
echo ""
echo "🌐 Frontend: http://localhost:3000 (or the port shown above)"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Features Available:"
echo "  • File Upload (Job Description & Resume)"
echo "  • Smart Question Generation"
echo "  • Audio Recording & Transcription"
echo "  • AI-powered Evaluation"
echo "  • Live Coding Environment"
echo "  • Comprehensive Interview Reports"
echo ""
echo "🛑 To stop the system:"
echo "  pkill -f 'uvicorn|vite'"
echo ""
echo "Press Ctrl+C to stop monitoring..."

# Keep script running to monitor
trap 'echo "Stopping system..."; pkill -f "uvicorn|vite"; exit 0' INT

# Monitor processes
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died"  
        break
    fi
    sleep 10
done