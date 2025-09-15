#!/bin/bash

echo "🔍 AI HR Interview System - Status Check"
echo "========================================"
echo ""

# Check Backend
echo "🚀 Backend Status:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
    
    # Get AI model status
    ai_status=$(curl -s http://localhost:8000/health | jq -r '.ai_status')
    whisper_status=$(echo $ai_status | jq -r '.whisper')
    llm_status=$(echo $ai_status | jq -r '.llm')
    
    if [ "$whisper_status" = "true" ]; then
        echo "🎤 Whisper (Speech-to-Text): ✅ Loaded"
    else
        echo "🎤 Whisper (Speech-to-Text): ⚠️  Using fallback (mock)"
    fi
    
    if [ "$llm_status" = "true" ]; then
        echo "🤖 LLM (AI Evaluation): ✅ Loaded"
    else
        echo "🤖 LLM (AI Evaluation): ❌ Failed"
    fi
else
    echo "❌ Backend is not running"
fi

echo ""

# Check Frontend
echo "🌐 Frontend Status:"
if ps aux | grep -E "vite" | grep -v grep > /dev/null 2>&1; then
    echo "✅ Frontend is running on http://localhost:3000"
    echo "🖥️  Open in browser: http://localhost:3000"
else
    echo "❌ Frontend is not running"
fi

echo ""
echo "🎯 Features Available:"
echo "• File upload (Job Description & Resume)"
echo "• AI-powered question generation"
echo "• Speech-to-text transcription"
echo "• Intelligent answer evaluation"
echo "• Real-time coding environment"
echo "• Code execution and feedback"
echo "• Proctoring simulation"
echo "• Comprehensive interview reports"

echo ""
echo "🚦 To stop services:"
echo "pkill -f 'uvicorn|vite'"

echo ""
echo "🔄 To restart:"
echo "./start_backend.sh &"
echo "./start_frontend.sh &"