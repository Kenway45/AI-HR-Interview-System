from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import logging
import asyncio
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo data storage (in-memory)
demo_sessions = {}
demo_files = {}
demo_responses = [
    "That's an excellent answer! Your understanding of the topic shows great depth.",
    "I can see you have practical experience in this area. Can you elaborate more?",
    "Interesting perspective! How would you handle this in a high-pressure situation?",
    "Great technical knowledge! Let's move to the next question.",
    "Your problem-solving approach is very methodical. I appreciate that."
]

class SessionCreate(BaseModel):
    job_description: str
    resume_text: str

class SessionResponse(BaseModel):
    session_id: str
    status: str
    questions: List[str]

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
    title="AI HR Interview System - Demo Mode",
    description="Zero-cost AI HR interview system - Demo with mock services",
    version="1.0.0-demo"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI HR Interview System API - Demo Mode",
        "version": "1.0.0-demo",
        "status": "running",
        "mode": "demo"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-hr-interview", "mode": "demo"}

@app.post("/upload/jd")
async def upload_job_description(file: UploadFile = File(...)):
    content = await file.read()
    file_id = f"jd_{len(demo_files)}"
    demo_files[file_id] = {
        "filename": file.filename,
        "content": content.decode('utf-8'),
        "type": "job_description"
    }
    # Mock job description processing
    jd_summary = "Senior Software Engineer position requiring 5+ years experience in Python, React, and cloud technologies. Strong focus on scalable systems and team collaboration."
    
    return {
        "file_id": file_id, 
        "filename": file.filename, 
        "status": "uploaded",
        "jd_summary": jd_summary
    }

@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    file_id = f"resume_{len(demo_files)}"
    demo_files[file_id] = {
        "filename": file.filename,
        "content": content.decode('utf-8'),
        "type": "resume"
    }
    # Mock resume processing  
    resume_summary = "Experienced Software Engineer with 6 years in full-stack development. Proficient in Python, JavaScript, React, and AWS. Led multiple successful projects and teams."
    
    return {
        "file_id": file_id, 
        "filename": file.filename, 
        "status": "uploaded",
        "resume_summary": resume_summary
    }

@app.post("/session/create")
async def create_session(jd_summary: str = None, resume_summary: str = None):
    session_id = f"session_{len(demo_sessions)}"
    
    # Mock questions based on job description
    questions = [
        "Tell me about yourself and your background.",
        "Why are you interested in this position?",
        "Describe a challenging project you've worked on.",
        "How do you handle tight deadlines and pressure?",
        "Where do you see yourself in 5 years?"
    ]
    
    demo_sessions[session_id] = {
        "id": session_id,
        "job_description": jd_summary or "No job description provided",
        "resume_text": resume_summary or "No resume provided",
        "questions": questions,
        "answers": {},
        "status": "active",
        "current_question": 0
    }
    
    return {
        "id": session_id,
        "status": "created",
        "questions": questions
    }

@app.get("/session/{session_id}/questions")
async def get_questions(session_id: str):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = demo_sessions[session_id]
    return {
        "session_id": session_id,
        "questions": session["questions"],
        "current_question": session["current_question"]
    }

@app.post("/stt/transcribe")
async def mock_transcribe(file: UploadFile = File(...)):
    # Mock transcription - simulate processing time
    await asyncio.sleep(1)
    
    # Return mock transcription
    mock_transcriptions = [
        "I have over 5 years of experience in software development, primarily working with Python and JavaScript. I'm passionate about creating efficient and scalable solutions.",
        "I'm excited about this opportunity because it aligns perfectly with my career goals and allows me to work with cutting-edge technologies.",
        "In my previous role, I led a team to develop a complex microservices architecture that improved system performance by 40%.",
        "I prioritize tasks based on business impact and maintain clear communication with stakeholders to manage expectations effectively.",
        "I see myself growing into a technical leadership role, mentoring junior developers and contributing to strategic technology decisions."
    ]
    
    return {
        "text": mock_transcriptions[len(demo_files) % len(mock_transcriptions)],
        "confidence": 0.95,
        "processing_time": 1.2
    }

@app.post("/session/{session_id}/answer")
async def submit_answer(session_id: str, answer: AnswerSubmission):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = demo_sessions[session_id]
    session["answers"][answer.question_id] = {
        "text": answer.audio_text,
        "timestamp": "2024-01-15T10:30:00Z",
        "score": 85  # Mock score
    }
    
    # Mock AI evaluation response
    evaluation = {
        "feedback": demo_responses[answer.question_id % len(demo_responses)],
        "score": 85,
        "strengths": ["Clear communication", "Relevant experience"],
        "areas_for_improvement": ["Could provide more specific examples"]
    }
    
    return {
        "session_id": session_id,
        "question_id": answer.question_id,
        "evaluation": evaluation,
        "next_question_id": answer.question_id + 1 if answer.question_id < len(session["questions"]) - 1 else None
    }

@app.get("/session/{session_id}/report", response_model=ReportResponse)
async def get_report(session_id: str):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = demo_sessions[session_id]
    
    # Calculate mock overall score
    if session["answers"]:
        scores = [answer["score"] for answer in session["answers"].values()]
        overall_score = sum(scores) // len(scores)
    else:
        overall_score = 0
    
    question_scores = []
    for i, (qid, answer) in enumerate(session["answers"].items()):
        question_scores.append({
            "question_id": qid,
            "question": session["questions"][qid],
            "score": answer["score"],
            "feedback": demo_responses[i % len(demo_responses)]
        })
    
    return ReportResponse(
        session_id=session_id,
        overall_score=overall_score,
        feedback=f"Overall performance was strong with an average score of {overall_score}%. The candidate demonstrated good technical knowledge and communication skills.",
        question_scores=question_scores
    )

@app.websocket("/ws/session/{session_id}/coding/{task_id}")
async def coding_websocket(websocket: WebSocket, session_id: str, task_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Wait for code from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "code_change":
                # Mock code analysis
                response = {
                    "type": "code_feedback",
                    "feedback": "Code looks good! Consider adding error handling.",
                    "suggestions": ["Add try-catch blocks", "Validate input parameters"]
                }
                await websocket.send_text(json.dumps(response))
                
            elif message["type"] == "run_code":
                # Mock code execution
                await asyncio.sleep(2)  # Simulate execution time
                response = {
                    "type": "execution_result",
                    "output": "Hello World!\nExecution completed successfully.",
                    "status": "success",
                    "execution_time": "0.02s"
                }
                await websocket.send_text(json.dumps(response))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/session/{session_id}/coding/tasks")
async def get_coding_tasks(session_id: str):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Mock coding tasks
    tasks = [
        {
            "id": "task_1",
            "title": "Two Sum Problem",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "difficulty": "Easy",
            "language": "python",
            "starter_code": "def two_sum(nums, target):\n    # Your solution here\n    pass"
        },
        {
            "id": "task_2",
            "title": "Reverse String",
            "description": "Write a function that reverses a string. The input string is given as an array of characters.",
            "difficulty": "Easy",
            "language": "python",
            "starter_code": "def reverse_string(s):\n    # Your solution here\n    pass"
        }
    ]
    
    return {"session_id": session_id, "tasks": tasks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_demo:app", host="0.0.0.0", port=8000, reload=True)