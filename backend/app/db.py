from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_hr_interview")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jd_text = Column(Text)
    jd_summary = Column(Text)
    resume_text = Column(Text)
    resume_summary = Column(Text)
    questions = Column(JSON)
    status = Column(String, default="created")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True))
    question_text = Column(Text)
    question_type = Column(String)  # 'behavioral', 'technical', 'coding'
    expected_skills = Column(JSON)
    order_index = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True))
    question_id = Column(UUID(as_uuid=True))
    audio_file_path = Column(String)
    transcript = Column(Text)
    evaluation = Column(JSON)
    score = Column(Float)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class CodingTask(Base):
    __tablename__ = "coding_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True))
    title = Column(String)
    description = Column(Text)
    starter_code = Column(Text)
    test_cases = Column(JSON)
    language = Column(String)
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CodeSubmission(Base):
    __tablename__ = "code_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coding_task_id = Column(UUID(as_uuid=True))
    session_id = Column(UUID(as_uuid=True))
    code = Column(Text)
    language = Column(String)
    judge0_token = Column(String)
    result = Column(JSON)
    score = Column(Float)
    submitted_at = Column(DateTime, default=datetime.utcnow)

class ProctorEvent(Base):
    __tablename__ = "proctor_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True))
    event_type = Column(String)  # 'face_not_detected', 'multiple_faces', 'tab_switch', 'copy_paste'
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)
    severity = Column(String, default="low")  # 'low', 'medium', 'high'

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")