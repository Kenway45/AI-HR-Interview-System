#!/bin/bash
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./app.db"
export STT_ENGINE="mock"
export LLM_ENGINE="mock"
echo "🚀 Starting AI-Powered Backend API on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🤖 Mode: REAL AI (OpenAI Whisper, Local LLM, Real Code Execution)"
echo ""
uvicorn app.main_ai:app --reload --host 0.0.0.0 --port 8000
