from fastapi import APIRouter, UploadFile, File
from ..models import TranscriptResponse
import random

router = APIRouter()

# Mock responses for demonstration
MOCK_RESPONSES = [
    "Thank you for the question. I have over 5 years of experience in full-stack development, working with technologies like React, Node.js, and Python. In my current role, I've led several projects involving machine learning integration and microservices architecture.",
    
    "That's a great question. I'm particularly passionate about solving complex technical challenges and building scalable systems. I believe my experience with AI/ML technologies and my track record of mentoring junior developers make me a strong fit for this role.",
    
    "I approach challenging projects by first understanding the requirements thoroughly, then breaking down the problem into manageable components. I collaborate closely with stakeholders and use agile methodologies to ensure we deliver value incrementally.",
    
    "When working with difficult team members, I focus on clear communication and finding common ground. I try to understand their perspective and work together to find solutions that benefit the project and the team.",
    
    "I stay current with technology trends by reading industry publications, participating in online communities, attending conferences, and working on side projects. I'm always eager to learn new technologies that can improve my work."
]

@router.post("/transcribe", response_model=TranscriptResponse)
async def mock_transcribe_audio(file: UploadFile = File(...)):
    """Mock transcribe endpoint for demonstration"""
    
    # Return a random mock response
    transcript = random.choice(MOCK_RESPONSES)
    
    return TranscriptResponse(
        transcript=transcript,
        confidence=0.85
    )

@router.get("/health")
async def mock_stt_health():
    return {
        "status": "healthy", 
        "engine": "mock",
        "note": "Using mock STT service for demonstration"
    }