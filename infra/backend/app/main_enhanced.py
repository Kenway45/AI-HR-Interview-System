from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, BackgroundTasks
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

# Enhanced demo data storage (in-memory)
demo_sessions = {}
demo_files = {}
demo_responses = [
    "That's an excellent answer! Your understanding of the topic shows great depth. Can you elaborate on how you would implement this in a production environment?",
    "I can see you have practical experience in this area. Your approach demonstrates solid problem-solving skills. How would you handle edge cases?",
    "Interesting perspective! Your technical knowledge is impressive. How would you optimize this for better performance?",
    "Great technical knowledge! Your solution shows good architectural thinking. Let's explore a more complex scenario.",
    "Your problem-solving approach is very methodical. I appreciate the structured way you think about challenges."
]

# Enhanced question generation based on job requirements
def generate_questions(job_description: str, resume_text: str) -> List[str]:
    """Generate contextual questions based on JD and resume"""
    base_questions = [
        "Tell me about yourself and your background.",
        "Why are you interested in this position?",
        "Describe a challenging project you've worked on.",
        "How do you handle tight deadlines and pressure?",
        "Where do you see yourself in 5 years?"
    ]
    
    # Add technical questions based on job description keywords
    technical_keywords = {
        'python': "Explain the difference between lists and tuples in Python. When would you use each?",
        'javascript': "What are closures in JavaScript and how do you use them?",
        'react': "How do you manage state in a React application? Compare different approaches.",
        'docker': "Explain containerization and how Docker helps in deployment.",
        'aws': "What AWS services would you use for a scalable web application?",
        'kubernetes': "How does Kubernetes help with container orchestration?",
        'microservices': "What are the challenges of microservices architecture?",
        'api': "How do you design RESTful APIs? What are the best practices?",
        'database': "Explain the difference between SQL and NoSQL databases.",
        'security': "How do you implement authentication and authorization in web applications?"
    }
    
    job_lower = job_description.lower()
    for keyword, question in technical_keywords.items():
        if keyword in job_lower:
            base_questions.append(question)
            
    return base_questions[:7]  # Limit to 7 questions for reasonable interview length

# Enhanced evaluation with contextual feedback
def evaluate_answer(question: str, answer: str, question_index: int) -> dict:
    """Provide realistic evaluation based on answer content"""
    answer_lower = answer.lower()
    word_count = len(answer.split())
    
    # Base score calculation
    base_score = 70
    
    # Adjust score based on answer length and content
    if word_count < 10:
        score_modifier = -20
        feedback_suffix = "Consider providing more detailed explanations with specific examples."
    elif word_count > 100:
        score_modifier = 15
        feedback_suffix = "Excellent detailed response with good depth of knowledge."
    else:
        score_modifier = 10
        feedback_suffix = "Good response with appropriate level of detail."
    
    # Look for technical keywords and concepts
    technical_terms = ['implement', 'optimize', 'scalable', 'efficient', 'architecture', 'design', 'solution', 'approach']
    technical_score = sum(5 for term in technical_terms if term in answer_lower)
    
    final_score = min(95, max(40, base_score + score_modifier + technical_score))
    
    # Generate contextual feedback
    feedback_templates = [
        "Your answer demonstrates {} understanding of the concept. {}",
        "I appreciate your {} approach to this problem. {}",
        "Your response shows {} technical knowledge. {}",
        "The way you explained this shows {} problem-solving skills. {}"
    ]
    
    quality_adjectives = ['solid', 'strong', 'excellent', 'good', 'thorough'] if final_score > 75 else ['basic', 'adequate', 'developing']
    
    feedback = random.choice(feedback_templates).format(
        random.choice(quality_adjectives),
        feedback_suffix
    )
    
    return {
        'score': final_score,
        'feedback': feedback,
        'strengths': extract_strengths(answer_lower, final_score),
        'areas_for_improvement': extract_improvements(answer_lower, final_score)
    }

def extract_strengths(answer: str, score: int) -> List[str]:
    """Extract strengths from the answer"""
    strengths = []
    
    if 'experience' in answer or 'worked' in answer:
        strengths.append('Relevant experience mentioned')
    if 'team' in answer or 'collaboration' in answer:
        strengths.append('Team collaboration skills')
    if 'problem' in answer and 'solve' in answer:
        strengths.append('Problem-solving approach')
    if 'learn' in answer or 'research' in answer:
        strengths.append('Willingness to learn')
    if len(answer.split()) > 50:
        strengths.append('Detailed explanation')
        
    if not strengths:
        strengths = ['Clear communication']
        
    return strengths[:3]  # Limit to top 3

def extract_improvements(answer: str, score: int) -> List[str]:
    """Extract areas for improvement"""
    improvements = []
    
    if len(answer.split()) < 20:
        improvements.append('Provide more specific examples')
    if 'example' not in answer and 'instance' not in answer:
        improvements.append('Include concrete examples')
    if score < 70:
        improvements.append('Elaborate on technical aspects')
        
    if not improvements:
        improvements = ['Consider discussing potential challenges']
        
    return improvements[:2]  # Limit to top 2

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
    title="AI HR Interview System - Enhanced Demo",
    description="Zero-cost AI HR interview system with enhanced AI-like features",
    version="1.0.0-enhanced"
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
        "message": "AI HR Interview System API - Enhanced Demo Mode",
        "version": "1.0.0-enhanced",
        "status": "running",
        "mode": "enhanced_demo",
        "features": [
            "Contextual question generation",
            "Intelligent answer evaluation",
            "Realistic AI feedback",
            "Live coding environment",
            "Proctoring simulation"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-hr-interview", "mode": "enhanced_demo"}

@app.post("/upload/jd")
async def upload_job_description(file: UploadFile = File(...)):
    content = await file.read()
    file_id = f"jd_{len(demo_files)}"
    
    # Process job description with more realistic parsing
    jd_text = content.decode('utf-8')
    demo_files[file_id] = {
        "filename": file.filename,
        "content": jd_text,
        "type": "job_description"
    }
    
    # Extract key requirements (simulate AI processing)
    await asyncio.sleep(1)  # Simulate processing time
    
    # Generate realistic summary based on common patterns
    requirements = []
    if 'python' in jd_text.lower():
        requirements.append('Python programming')
    if 'javascript' in jd_text.lower() or 'js' in jd_text.lower():
        requirements.append('JavaScript development')
    if 'react' in jd_text.lower():
        requirements.append('React framework')
    if 'aws' in jd_text.lower() or 'cloud' in jd_text.lower():
        requirements.append('Cloud technologies')
    if 'api' in jd_text.lower():
        requirements.append('API development')
        
    experience_match = re.search(r'(\d+)\+?\s*years?', jd_text.lower())
    experience_req = experience_match.group(1) + '+ years' if experience_match else '3+ years'
    
    jd_summary = f"Position requires {experience_req} of experience in {', '.join(requirements) if requirements else 'software development'}. Strong focus on scalable systems, team collaboration, and modern development practices."
    
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
    
    # Process resume with more realistic parsing
    resume_text = content.decode('utf-8')
    demo_files[file_id] = {
        "filename": file.filename,
        "content": resume_text,
        "type": "resume"
    }
    
    # Simulate AI resume processing
    await asyncio.sleep(1.5)  
    
    # Extract skills and experience
    skills = []
    if 'python' in resume_text.lower():
        skills.append('Python')
    if 'javascript' in resume_text.lower():
        skills.append('JavaScript')
    if 'react' in resume_text.lower():
        skills.append('React')
    if 'aws' in resume_text.lower():
        skills.append('AWS')
        
    experience_match = re.search(r'(\d+)\+?\s*years?', resume_text.lower())
    experience = experience_match.group(1) + ' years' if experience_match else '5+ years'
    
    resume_summary = f"Experienced professional with {experience} in software development. Proficient in {', '.join(skills) if skills else 'multiple programming languages'}. Track record of successful project delivery and team leadership."
    
    return {
        "file_id": file_id, 
        "filename": file.filename, 
        "status": "uploaded",
        "resume_summary": resume_summary
    }

@app.post("/session/create")
async def create_session(jd_summary: str = None, resume_summary: str = None):
    session_id = f"session_{int(time.time())}"
    
    # Generate contextual questions
    jd_text = jd_summary or "Software Engineer position"
    resume_text = resume_summary or "Experienced developer"
    questions = generate_questions(jd_text, resume_text)
    
    demo_sessions[session_id] = {
        "id": session_id,
        "job_description": jd_text,
        "resume_text": resume_text,
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
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = demo_sessions[session_id]
    return {
        "session_id": session_id,
        "questions": session["questions"],
        "current_question": session["current_question"]
    }

@app.post("/stt/transcribe")
async def enhanced_transcribe(file: UploadFile = File(...)):
    # Enhanced mock transcription with realistic processing
    await asyncio.sleep(random.uniform(1, 2))  # Realistic processing time
    
    # More diverse and realistic transcriptions
    mock_transcriptions = [
        "I have over 6 years of experience in full-stack development, primarily working with Python and JavaScript. I've led several projects involving microservices architecture and have experience with AWS and Docker. I'm passionate about creating efficient, scalable solutions and enjoy working in collaborative environments.",
        "I'm excited about this opportunity because it aligns perfectly with my career goals in senior software engineering. The company's focus on innovation and the tech stack you're using really appeals to me. I'm particularly interested in the machine learning applications you're developing.",
        "In my previous role, I led the development of a real-time analytics platform that processed over 1 million events per day. The main challenge was optimizing the database queries and implementing proper caching strategies. We used Redis for caching and optimized our PostgreSQL queries, which improved performance by 60%.",
        "When facing tight deadlines, I prioritize tasks based on business impact and break down complex features into smaller, manageable pieces. I maintain clear communication with stakeholders about progress and potential blockers. I also believe in the importance of code reviews and testing, even under pressure.",
        "In 5 years, I see myself in a technical leadership role, possibly as a Staff Engineer or Engineering Manager. I want to continue growing my technical skills while also mentoring junior developers and contributing to architectural decisions. I'm also interested in exploring more about distributed systems and cloud architecture."
    ]
    
    # Add some variability based on file name or content
    transcription = random.choice(mock_transcriptions)
    confidence = random.uniform(0.85, 0.98)
    
    return {
        "text": transcription,
        "confidence": round(confidence, 2),
        "processing_time": round(random.uniform(0.8, 2.1), 2)
    }

@app.post("/session/{session_id}/answer")
async def submit_answer(session_id: str, answer: AnswerSubmission):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = demo_sessions[session_id]
    question_text = session["questions"][answer.question_id] if answer.question_id < len(session["questions"]) else "Unknown question"
    
    # Enhanced evaluation
    evaluation = evaluate_answer(question_text, answer.audio_text, answer.question_id)
    
    session["answers"][answer.question_id] = {
        "text": answer.audio_text,
        "timestamp": datetime.now().isoformat(),
        "score": evaluation['score'],
        "feedback": evaluation['feedback'],
        "strengths": evaluation['strengths'],
        "areas_for_improvement": evaluation['areas_for_improvement']
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
    
    # Calculate comprehensive scores
    if session["answers"]:
        scores = [answer["score"] for answer in session["answers"].values()]
        overall_score = sum(scores) // len(scores)
        
        # Generate performance summary
        high_scores = sum(1 for score in scores if score >= 80)
        total_answers = len(scores)
        
        performance_level = "Excellent" if overall_score >= 85 else "Good" if overall_score >= 75 else "Satisfactory" if overall_score >= 65 else "Needs Improvement"
        
        feedback = f"Overall performance was {performance_level.lower()} with an average score of {overall_score}%. "
        
        if high_scores > total_answers // 2:
            feedback += "The candidate demonstrated strong technical knowledge and excellent communication skills throughout the interview."
        else:
            feedback += "The candidate showed good foundational knowledge with room for improvement in some technical areas."
            
    else:
        overall_score = 0
        feedback = "No answers submitted yet."
    
    question_scores = []
    for i, (qid, answer) in enumerate(session["answers"].items()):
        question_scores.append({
            "question_id": qid,
            "question": session["questions"][qid],
            "score": answer["score"],
            "feedback": answer["feedback"],
            "strengths": answer.get("strengths", []),
            "areas_for_improvement": answer.get("areas_for_improvement", [])
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
                # Enhanced code analysis
                code = message.get("code", "")
                analysis = analyze_code(code)
                
                response = {
                    "type": "code_feedback",
                    "feedback": analysis["feedback"],
                    "suggestions": analysis["suggestions"],
                    "score": analysis["score"]
                }
                await websocket.send_text(json.dumps(response))
                
            elif message["type"] == "run_code":
                # Enhanced code execution simulation
                code = message.get("code", "")
                await asyncio.sleep(random.uniform(1, 3))  # Realistic execution time
                
                result = execute_code_simulation(code)
                response = {
                    "type": "execution_result",
                    "output": result["output"],
                    "status": result["status"],
                    "execution_time": result["execution_time"]
                }
                await websocket.send_text(json.dumps(response))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

def analyze_code(code: str) -> dict:
    """Analyze code and provide realistic feedback"""
    lines = code.split('\n')
    line_count = len([line for line in lines if line.strip()])
    
    score = 70  # Base score
    feedback = "Your code structure looks good. "
    suggestions = []
    
    # Check for common patterns
    if 'def ' in code:
        score += 10
        feedback += "Good use of functions. "
    
    if 'try:' in code and 'except' in code:
        score += 15
        feedback += "Excellent error handling! "
    else:
        suggestions.append("Consider adding error handling with try-except blocks")
    
    if line_count < 5:
        suggestions.append("Try to break down the solution into smaller functions")
    elif line_count > 50:
        suggestions.append("Consider refactoring into smaller, more manageable functions")
        
    if 'return' not in code and 'def ' in code:
        suggestions.append("Don't forget to return values from your functions")
        
    if not suggestions:
        suggestions = ["Consider adding comments to explain complex logic"]
        
    return {
        "feedback": feedback.strip(),
        "suggestions": suggestions[:3],
        "score": min(95, score)
    }

def execute_code_simulation(code: str) -> dict:
    """Simulate code execution with realistic results"""
    if 'print(' in code:
        # Extract print statements and simulate output
        import re
        prints = re.findall(r'print\([^)]*\)', code)
        output_lines = []
        
        for print_stmt in prints:
            if '"hello world"' in print_stmt.lower() or "'hello world'" in print_stmt.lower():
                output_lines.append("Hello World!")
            elif 'range(' in print_stmt:
                output_lines.append("0\n1\n2\n3\n4")
            else:
                output_lines.append("Output from your code")
                
        output = "\n".join(output_lines)
        status = "success"
    elif 'return' in code:
        output = "Function executed successfully\nReturned: [result value]"
        status = "success"
    elif 'def ' in code:
        output = "Function defined successfully\nReady to be called"
        status = "success"
    else:
        output = "Code executed without errors"
        status = "success"
        
    # Occasionally simulate errors for realism
    if random.random() < 0.1:  # 10% chance of error
        output = "NameError: name 'undefined_variable' is not defined\nLine 3: undefined_variable = 5"
        status = "error"
        
    return {
        "output": output,
        "status": status,
        "execution_time": f"{random.uniform(0.01, 0.5):.3f}s"
    }

@app.get("/session/{session_id}/coding/tasks")
async def get_coding_tasks(session_id: str):
    if session_id not in demo_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # More sophisticated coding tasks
    tasks = [
        {
            "id": "task_1",
            "title": "Two Sum Problem",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
            "difficulty": "Easy",
            "language": "python",
            "starter_code": "def two_sum(nums, target):\n    \"\"\"\n    Find two numbers that add up to target\n    Args:\n        nums: List of integers\n        target: Target sum\n    Returns:\n        List of two indices\n    \"\"\"\n    # Your solution here\n    pass\n\n# Test case\n# nums = [2, 7, 11, 15], target = 9\n# Expected output: [0, 1]",
            "test_cases": [
                {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
                {"input": "[3, 2, 4], 6", "expected": "[1, 2]"}
            ]
        },
        {
            "id": "task_2",
            "title": "Palindrome Check",
            "description": "Write a function to check if a string is a palindrome. A palindrome reads the same forwards and backwards.",
            "difficulty": "Easy",
            "language": "python",
            "starter_code": "def is_palindrome(s):\n    \"\"\"\n    Check if string is a palindrome\n    Args:\n        s: Input string\n    Returns:\n        Boolean indicating if string is palindrome\n    \"\"\"\n    # Your solution here\n    pass\n\n# Test cases\n# is_palindrome('racecar') should return True\n# is_palindrome('hello') should return False",
            "test_cases": [
                {"input": "'racecar'", "expected": "True"},
                {"input": "'hello'", "expected": "False"}
            ]
        },
        {
            "id": "task_3",
            "title": "Binary Search",
            "description": "Implement binary search algorithm to find the index of a target value in a sorted array. Return -1 if target is not found.",
            "difficulty": "Medium",
            "language": "python",
            "starter_code": "def binary_search(arr, target):\n    \"\"\"\n    Binary search implementation\n    Args:\n        arr: Sorted array of integers\n        target: Value to search for\n    Returns:\n        Index of target or -1 if not found\n    \"\"\"\n    # Your solution here\n    pass",
            "test_cases": [
                {"input": "[1, 3, 5, 7, 9], 5", "expected": "2"},
                {"input": "[1, 3, 5, 7, 9], 6", "expected": "-1"}
            ]
        }
    ]
    
    return {"session_id": session_id, "tasks": tasks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_enhanced:app", host="0.0.0.0", port=8000, reload=True)