from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import json

from ..db import get_db, Session as SessionModel, Question, Answer, CodingTask, ProctorEvent
from ..models import SessionCreate, SessionResponse, QuestionResponse, CodingTaskResponse, ProctorEventRequest
from ..utils.question_generator import generate_interview_questions, generate_coding_tasks
import os

# Import the appropriate evaluation function based on configuration
LLM_ENGINE = os.getenv("LLM_ENGINE", "textgen")

if LLM_ENGINE == "mock":
    from ..api.llm_mock import mock_evaluate_transcript as evaluate_transcript
else:
    from ..api.llm import evaluate_transcript

router = APIRouter()

@router.post("/create", response_model=SessionResponse)
async def create_session(
    jd_summary: str,
    resume_summary: str,
    db: Session = Depends(get_db)
):
    """Create new interview session from JD and resume"""
    
    # Generate questions using LLM
    questions_data = await generate_interview_questions(jd_summary, resume_summary)
    
    # Create session in database
    session = SessionModel(
        jd_summary=jd_summary,
        resume_summary=resume_summary,
        questions=questions_data,
        status="created"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create individual question records
    for i, q_data in enumerate(questions_data):
        question = Question(
            session_id=session.id,
            question_text=q_data["question"],
            question_type=q_data["type"],
            expected_skills=q_data.get("skills", []),
            order_index=i
        )
        db.add(question)
    
    db.commit()
    
    return SessionResponse(
        id=session.id,
        status=session.status,
        questions=questions_data,
        created_at=session.created_at
    )

@router.get("/{session_id}/questions", response_model=List[QuestionResponse])
async def get_session_questions(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get all questions for a session"""
    questions = db.query(Question).filter(
        Question.session_id == session_id
    ).order_by(Question.order_index).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for session")
    
    return [
        QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            expected_skills=q.expected_skills or [],
            order_index=q.order_index
        )
        for q in questions
    ]

@router.post("/{session_id}/audio")
async def upload_answer_audio(
    session_id: str,
    question_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload audio answer and process it"""
    from ..api.stt import transcribe_audio_internal
    from ..utils.storage import save_file_to_storage
    
    # Save audio file
    file_content = await file.read()
    audio_path = await save_file_to_storage(file_content, file.filename, "audio")
    
    # Transcribe audio
    transcript = await transcribe_audio_internal(file_content, file.filename)
    
    # Get question and session details for evaluation
    question = db.query(Question).filter(Question.id == question_id).first()
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not question or not session:
        raise HTTPException(status_code=404, detail="Question or session not found")
    
    # Evaluate answer using LLM
    evaluation = await evaluate_transcript(
        jd_summary=session.jd_summary,
        resume_summary=session.resume_summary,
        question=question.question_text,
        transcript=transcript,
        question_type=question.question_type
    )
    
    # Save answer to database
    answer = Answer(
        session_id=session_id,
        question_id=question_id,
        audio_file_path=audio_path,
        transcript=transcript,
        evaluation=evaluation,
        score=evaluation.get("score", 0.0)
    )
    db.add(answer)
    db.commit()
    
    return {
        "message": "Audio processed successfully",
        "transcript": transcript,
        "evaluation": evaluation
    }

@router.post("/{session_id}/start_coding")
async def start_coding_session(
    session_id: str,
    difficulty: str = "medium",
    db: Session = Depends(get_db)
):
    """Start coding session and generate tasks"""
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Generate coding tasks based on JD requirements
    tasks = await generate_coding_tasks(session.jd_summary, difficulty)
    
    # Save tasks to database
    coding_tasks = []
    for task_data in tasks:
        task = CodingTask(
            session_id=session_id,
            title=task_data["title"],
            description=task_data["description"],
            starter_code=task_data["starter_code"],
            test_cases=task_data["test_cases"],
            language=task_data["language"],
            difficulty=difficulty
        )
        db.add(task)
        coding_tasks.append(task)
    
    db.commit()
    
    # Update session status
    session.status = "coding"
    db.commit()
    
    return {
        "message": "Coding session started",
        "tasks": [
            CodingTaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                starter_code=task.starter_code,
                language=task.language,
                difficulty=task.difficulty,
                test_cases=task.test_cases
            )
            for task in coding_tasks
        ]
    }

@router.post("/{session_id}/proctor")
async def log_proctor_event(
    session_id: str,
    event: ProctorEventRequest,
    db: Session = Depends(get_db)
):
    """Log proctoring event"""
    
    proctor_event = ProctorEvent(
        session_id=session_id,
        event_type=event.event_type,
        details=event.details,
        severity=event.severity
    )
    db.add(proctor_event)
    db.commit()
    
    return {"message": "Event logged successfully"}

@router.get("/{session_id}/report")
async def get_session_report(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Generate comprehensive session report"""
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all answers
    answers = db.query(Answer).filter(Answer.session_id == session_id).all()
    
    # Get coding submissions
    coding_tasks = db.query(CodingTask).filter(CodingTask.session_id == session_id).all()
    
    # Get proctor events
    proctor_events = db.query(ProctorEvent).filter(ProctorEvent.session_id == session_id).all()
    
    # Calculate overall score
    answer_scores = [answer.score for answer in answers if answer.score is not None]
    avg_answer_score = sum(answer_scores) / len(answer_scores) if answer_scores else 0
    
    # Analyze proctor events
    high_severity_events = [e for e in proctor_events if e.severity == "high"]
    
    return {
        "session_id": session_id,
        "overall_score": avg_answer_score,
        "answers": [
            {
                "question_id": answer.question_id,
                "score": answer.score,
                "evaluation": answer.evaluation,
                "transcript": answer.transcript
            }
            for answer in answers
        ],
        "coding_tasks": [
            {
                "task_id": task.id,
                "title": task.title,
                "difficulty": task.difficulty
            }
            for task in coding_tasks
        ],
        "proctor_summary": {
            "total_events": len(proctor_events),
            "high_severity_events": len(high_severity_events),
            "event_types": list(set([e.event_type for e in proctor_events]))
        },
        "created_at": session.created_at,
        "status": session.status
    }