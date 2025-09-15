from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import logging
import asyncio
import random
import time
from typing import Dict, List, Optional
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple data storage
sessions = {}
files = {}

# Sample responses for demo
demo_responses = [
    "That's an excellent answer! Your understanding shows great depth.",
    "I can see you have practical experience. Can you elaborate more?",
    "Interesting perspective! How would you handle edge cases?",
    "Great technical knowledge! Let's explore this further.",
    "Your problem-solving approach is very methodical."
]

def safe_decode(content):
    """Safely decode file content with multiple encoding attempts"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    # If all fail, use utf-8 with error handling
    return content.decode('utf-8', errors='replace')

# Pydantic models
class SessionCreate(BaseModel):
    job_description: str
    resume_text: str

class AnswerSubmission(BaseModel):
    session_id: str
    question_id: int
    audio_text: str

class ReportResponse(BaseModel):
    session_id: str
    overall_score: int
    feedback: str
    question_scores: List[Dict]

app = FastAPI(
    title="AI HR Interview System - Simple Working Version",
    description="Fully functional AI HR interview system",
    version="1.0.0-simple"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI HR Interview System API - Simple Working Version",
        "version": "1.0.0-simple",
        "status": "running",
        "mode": "demo_enhanced",
        "features": [
            "File upload (JD & Resume)",
            "Smart question generation", 
            "Audio transcription simulation",
            "AI-like evaluation",
            "Live coding environment",
            "Comprehensive reports"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-hr-interview", "mode": "simple"}

@app.post("/upload/jd")
async def upload_job_description(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_id = f"jd_{len(files)}"
        
        # Safe decoding
        jd_text = safe_decode(content)
        
        files[file_id] = {
            "filename": file.filename,
            "content": jd_text,
            "type": "job_description"
        }
        
        # Simulate processing
        await asyncio.sleep(1)
        
        # Extract requirements
        requirements = []
        tech_keywords = ['python', 'javascript', 'react', 'aws', 'docker', 'api', 'database']
        
        for tech in tech_keywords:
            if tech.lower() in jd_text.lower():
                requirements.append(tech.title())
        
        # Generate summary
        experience_match = re.search(r'(\d+)\+?\s*years?', jd_text.lower())
        experience_req = experience_match.group(1) + '+ years' if experience_match else '3+ years'
        
        if requirements:
            jd_summary = f"Position requires {experience_req} of experience in {', '.join(requirements)}. Focus on scalable systems and team collaboration."
        else:
            jd_summary = f"Software engineering position requiring {experience_req} of experience. Focus on development best practices."
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "uploaded",
            "jd_summary": jd_summary
        }
        
    except Exception as e:
        logger.error(f"Error uploading job description: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_id = f"resume_{len(files)}"
        
        # Safe decoding
        resume_text = safe_decode(content)
        
        files[file_id] = {
            "filename": file.filename,
            "content": resume_text,
            "type": "resume"
        }
        
        # Simulate processing
        await asyncio.sleep(1.5)
        
        # Extract skills
        skills = []
        tech_keywords = ['python', 'javascript', 'react', 'aws', 'docker', 'api', 'database']
        
        for tech in tech_keywords:
            if tech.lower() in resume_text.lower():
                skills.append(tech.title())
        
        # Extract experience
        experience_match = re.search(r'(\d+)\+?\s*years?', resume_text.lower())
        experience = experience_match.group(1) + ' years' if experience_match else '5+ years'
        
        if skills:
            resume_summary = f"Experienced professional with {experience} in software development. Proficient in {', '.join(skills)}."
        else:
            resume_summary = f"Software professional with {experience} of development experience."
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "uploaded",
            "resume_summary": resume_summary
        }
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/session/create")
async def create_session(jd_summary: str = None, resume_summary: str = None):
    session_id = f"session_{int(time.time())}"
    
    # Generate contextual questions
    questions = [
        "Tell me about yourself and your background.",
        "Why are you interested in this position?",
        "Describe a challenging project you've worked on.",
        "How do you handle tight deadlines and pressure?",
        "Where do you see yourself in 5 years?"
    ]
    
    # Add technical questions based on job description
    if jd_summary:
        if 'python' in jd_summary.lower():
            questions.append("Explain the difference between lists and tuples in Python.")
        if 'javascript' in jd_summary.lower():
            questions.append("What are closures in JavaScript and how do you use them?")
        if 'react' in jd_summary.lower():
            questions.append("How do you manage state in a React application?")
    
    sessions[session_id] = {
        "id": session_id,
        "job_description": jd_summary or "Software Engineer position",
        "resume_text": resume_summary or "Experienced developer",
        "questions": questions,
        "answers": {},
        "status": "active",
        "current_question": 0,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "id": session_id,
        "status": "created",
        "questions": questions
    }

@app.get("/session/{session_id}/questions")
async def get_questions(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "questions": session["questions"],
        "current_question": session["current_question"]
    }

@app.post("/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Simulate transcription processing
    await asyncio.sleep(random.uniform(1, 2))
    
    # Generate realistic transcription
    transcriptions = [
        "I have over 5 years of experience in software development, primarily working with Python and JavaScript. I'm passionate about creating efficient solutions.",
        "I'm excited about this opportunity because it aligns with my career goals. I'm particularly interested in the technical challenges this role offers.",
        "In my previous role, I led the development of a microservices platform that improved performance by 40%. The main challenge was optimizing database queries.",
        "When facing tight deadlines, I prioritize tasks and maintain clear communication with stakeholders about progress and potential blockers.",
        "In 5 years, I see myself in a technical leadership role, mentoring junior developers and contributing to architectural decisions."
    ]
    
    return {
        "text": random.choice(transcriptions),
        "confidence": round(random.uniform(0.85, 0.98), 2),
        "processing_time": round(random.uniform(0.8, 2.1), 2)
    }

@app.post("/session/{session_id}/answer")
async def submit_answer(session_id: str, answer: AnswerSubmission):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Simple but intelligent scoring
    word_count = len(answer.audio_text.split())
    base_score = 75
    
    # Adjust based on answer length and content
    if word_count < 10:
        score = base_score - 15
    elif word_count > 50:
        score = base_score + 10
    else:
        score = base_score + 5
    
    # Check for technical terms
    technical_terms = ['implement', 'optimize', 'design', 'develop', 'solution']
    tech_bonus = sum(3 for term in technical_terms if term in answer.audio_text.lower())
    
    final_score = min(95, max(45, score + tech_bonus))
    
    # Generate feedback
    feedback = random.choice(demo_responses)
    
    session["answers"][answer.question_id] = {
        "text": answer.audio_text,
        "timestamp": datetime.now().isoformat(),
        "score": final_score,
        "feedback": feedback
    }
    
    return {
        "session_id": session_id,
        "question_id": answer.question_id,
        "evaluation": {
            "score": final_score,
            "feedback": feedback,
            "strengths": ["Clear communication", "Relevant experience"],
            "areas_for_improvement": ["Provide more specific examples"]
        },
        "next_question_id": answer.question_id + 1 if answer.question_id < len(session["questions"]) - 1 else None
    }

@app.get("/session/{session_id}/report", response_model=ReportResponse)
async def get_report(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session["answers"]:
        scores = [answer["score"] for answer in session["answers"].values()]
        overall_score = sum(scores) // len(scores)
        
        if overall_score >= 85:
            feedback = f"Excellent interview performance with an average score of {overall_score}%. Strong technical knowledge and communication skills."
        elif overall_score >= 75:
            feedback = f"Good interview performance with an average score of {overall_score}%. Solid technical competency with room for minor improvements."
        else:
            feedback = f"Satisfactory interview performance with an average score of {overall_score}%. Would benefit from more detailed technical explanations."
    else:
        overall_score = 0
        feedback = "No answers submitted yet."
    
    question_scores = []
    for qid, answer in session["answers"].items():
        question_scores.append({
            "question_id": qid,
            "question": session["questions"][qid],
            "score": answer["score"],
            "feedback": answer["feedback"],
            "strengths": ["Clear communication", "Relevant experience"],
            "areas_for_improvement": ["Provide more specific examples"]
        })
    
    return ReportResponse(
        session_id=session_id,
        overall_score=overall_score,
        feedback=feedback,
        question_scores=question_scores
    )

@app.websocket("/ws/session/{session_id}/coding/{task_id}")
async def coding_websocket(websocket: WebSocket, session_id: str, task_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "code_change":
                # Simple code feedback
                code = message.get("code", "")
                
                feedback = "Code looks good!"
                suggestions = []
                
                if 'def ' in code:
                    feedback += " Good use of functions."
                else:
                    suggestions.append("Consider using functions to organize your code")
                
                if not suggestions:
                    suggestions = ["Consider adding comments for clarity"]
                
                response = {
                    "type": "code_feedback",
                    "feedback": feedback,
                    "suggestions": suggestions[:2],
                    "score": 80
                }
                await websocket.send_text(json.dumps(response))
                
            elif message["type"] == "run_code":
                # Simple code execution simulation
                await asyncio.sleep(1)
                
                response = {
                    "type": "execution_result",
                    "output": "Code executed successfully!\nOutput: Hello World!",
                    "status": "success",
                    "execution_time": "0.5s"
                }
                await websocket.send_text(json.dumps(response))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/session/{session_id}/coding/tasks")
async def get_coding_tasks(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    tasks = [
        {
            "id": "task_1",
            "title": "Two Sum Problem",
            "description": "Given an array of integers and a target, return indices of two numbers that add up to target.",
            "difficulty": "Easy",
            "language": "python",
            "starter_code": "def two_sum(nums, target):\n    # Your solution here\n    pass\n\n# Test\nresult = two_sum([2, 7, 11, 15], 9)\nprint(result)  # Expected: [0, 1]"
        }
    ]
    
    return {"session_id": session_id, "tasks": tasks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)