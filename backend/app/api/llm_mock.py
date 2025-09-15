from fastapi import APIRouter
import random
import json
from typing import Dict, Any, List
from ..models import LLMGenerationRequest, LLMEvaluationRequest

router = APIRouter()

# Mock interview questions
MOCK_QUESTIONS = [
    {
        "question": "Tell me about your background and what interests you about this role.",
        "type": "behavioral",
        "skills": ["communication", "motivation"],
        "difficulty": "easy"
    },
    {
        "question": "Describe a challenging project you worked on recently. What was your role and how did you overcome obstacles?",
        "type": "behavioral",
        "skills": ["problem-solving", "leadership", "technical"],
        "difficulty": "medium"
    },
    {
        "question": "How would you design a scalable system to handle high traffic?",
        "type": "technical",
        "skills": ["system-design", "scalability", "architecture"],
        "difficulty": "hard"
    },
    {
        "question": "Explain your experience with React and modern web frameworks.",
        "type": "technical",
        "skills": ["react", "frontend", "javascript"],
        "difficulty": "medium"
    },
    {
        "question": "How do you handle working under tight deadlines with competing priorities?",
        "type": "situational",
        "skills": ["time-management", "prioritization"],
        "difficulty": "medium"
    },
    {
        "question": "Describe your experience with Python and backend development.",
        "type": "technical",
        "skills": ["python", "backend", "apis"],
        "difficulty": "medium"
    },
    {
        "question": "Tell me about a time when you had to learn a new technology quickly.",
        "type": "behavioral",
        "skills": ["adaptability", "learning"],
        "difficulty": "medium"
    },
    {
        "question": "How would you approach debugging a performance issue in a web application?",
        "type": "technical",
        "skills": ["debugging", "performance", "optimization"],
        "difficulty": "hard"
    }
]

async def mock_generate_interview_questions(jd_summary: str, resume_summary: str) -> List[Dict[str, Any]]:
    """Generate mock interview questions"""
    # Return a random selection of questions
    return random.sample(MOCK_QUESTIONS, 6)

async def mock_evaluate_transcript(
    jd_summary: str,
    resume_summary: str,
    question: str,
    transcript: str,
    question_type: str
) -> Dict[str, Any]:
    """Mock evaluation of candidate transcript"""
    
    # Generate a realistic mock evaluation
    base_score = random.randint(60, 90)
    
    evaluation = {
        "score": base_score,
        "feedback": f"The candidate provided a {['comprehensive', 'detailed', 'thoughtful', 'well-structured'][random.randint(0,3)]} response that demonstrates {['strong technical knowledge', 'good communication skills', 'relevant experience', 'problem-solving abilities'][random.randint(0,3)]}. The answer shows understanding of the key concepts and provides concrete examples.",
        "strengths": random.sample([
            "clear communication",
            "relevant experience",
            "technical depth",
            "problem-solving approach",
            "concrete examples",
            "industry knowledge"
        ], 2),
        "weaknesses": random.sample([
            "could provide more specific examples",
            "might benefit from discussing edge cases",
            "could elaborate on implementation details",
            "opportunity to mention best practices"
        ], 1),
        "detailed_scores": {
            "relevance": random.randint(base_score-10, base_score+10),
            "technical_accuracy": random.randint(base_score-15, base_score+5),
            "communication": random.randint(base_score-5, base_score+10),
            "depth": random.randint(base_score-20, base_score),
            "overall": base_score
        }
    }
    
    return evaluation

@router.post("/generate")
async def mock_generate_text(request: LLMGenerationRequest):
    """Mock text generation"""
    return {
        "text": "This is a mock response from the LLM service. In a full implementation, this would generate intelligent responses based on the prompt.",
        "note": "Using mock LLM service for demonstration"
    }

@router.post("/evaluate")
async def mock_evaluate_answer(request: LLMEvaluationRequest):
    """Mock answer evaluation"""
    evaluation = await mock_evaluate_transcript(
        request.jd_summary,
        request.resume_summary,
        request.question,
        request.answer,
        request.question_type
    )
    return evaluation

@router.get("/health")
async def mock_llm_health():
    return {
        "status": "healthy",
        "engine": "mock",
        "note": "Using mock LLM service for demonstration"
    }