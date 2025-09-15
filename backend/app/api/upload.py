from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import PyPDF2
import docx
import os
import uuid
from ..db import get_db
from ..models import JDUploadResponse, ResumeUploadResponse
from ..utils.storage import save_file_to_storage
from ..utils.text_processing import extract_skills, summarize_text

router = APIRouter()

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX files"""
    try:
        if filename.lower().endswith('.pdf'):
            # Handle PDF
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif filename.lower().endswith('.docx'):
            # Handle DOCX
            import io
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif filename.lower().endswith('.txt'):
            # Handle plain text
            return file_content.decode('utf-8')
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

@router.post("/jd", response_model=JDUploadResponse)
async def upload_job_description(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process job description"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    file_content = await file.read()
    
    # Extract text from file
    jd_text = extract_text_from_file(file_content, file.filename)
    
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="No text found in file")
    
    # Save original file
    file_path = await save_file_to_storage(file_content, file.filename, "jd")
    
    # Process text
    jd_summary = summarize_text(jd_text, max_length=500)
    extracted_skills = extract_skills(jd_text, context="job_description")
    
    # Store in session cache or database
    # This will be linked to session creation later
    
    return JDUploadResponse(
        message="Job description processed successfully",
        jd_summary=jd_summary,
        extracted_skills=extracted_skills
    )

@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process resume"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    file_content = await file.read()
    
    # Extract text from file
    resume_text = extract_text_from_file(file_content, file.filename)
    
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="No text found in file")
    
    # Save original file
    file_path = await save_file_to_storage(file_content, file.filename, "resume")
    
    # Process text
    resume_summary = summarize_text(resume_text, max_length=500)
    candidate_skills = extract_skills(resume_text, context="resume")
    
    return ResumeUploadResponse(
        message="Resume processed successfully",
        resume_summary=resume_summary,
        candidate_skills=candidate_skills
    )