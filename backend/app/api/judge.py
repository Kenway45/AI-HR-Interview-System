from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import requests
import os
import time
import base64
from typing import Dict, Any, Optional

from ..db import get_db, CodeSubmission, CodingTask
from ..models import CodeSubmissionRequest, CodeSubmissionResponse, CodeResultResponse

router = APIRouter()

JUDGE0_URL = os.getenv("JUDGE0_URL", "http://judge0:2358")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY", "")

# Language ID mappings (Judge0 standard)
LANGUAGE_MAP = {
    "python": 71,
    "javascript": 63,
    "java": 62,
    "cpp": 54,
    "c": 50,
    "go": 60,
    "rust": 73,
    "typescript": 74
}

def get_headers():
    """Get request headers for Judge0 API"""
    headers = {"Content-Type": "application/json"}
    if JUDGE0_API_KEY:
        headers["X-RapidAPI-Key"] = JUDGE0_API_KEY
    return headers

@router.post("/submit", response_model=CodeSubmissionResponse)
async def submit_code(
    request: CodeSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Submit code to Judge0 for execution"""
    
    # Prepare submission data
    submission_data = {
        "source_code": base64.b64encode(request.source_code.encode()).decode(),
        "language_id": request.language_id,
        "stdin": base64.b64encode(request.stdin.encode()).decode() if request.stdin else "",
        "expected_output": "",
        "cpu_time_limit": 2,  # 2 seconds
        "cpu_extra_time": 0.5,
        "wall_time_limit": 5,  # 5 seconds
        "memory_limit": 128000,  # 128MB
        "stack_limit": 64000,  # 64MB
        "enable_per_process_and_thread_time_limit": True,
        "enable_per_process_and_thread_memory_limit": True
    }
    
    try:
        # Submit to Judge0
        response = requests.post(
            f"{JUDGE0_URL}/submissions?base64_encoded=true&wait=false",
            json=submission_data,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=500,
                detail=f"Judge0 submission failed: {response.text}"
            )
        
        result = response.json()
        token = result.get("token")
        
        if not token:
            raise HTTPException(status_code=500, detail="No token received from Judge0")
        
        return CodeSubmissionResponse(token=token)
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Judge0 submission timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Judge0 error: {str(e)}")

@router.get("/result/{token}", response_model=CodeResultResponse)
async def get_submission_result(token: str):
    """Get execution result from Judge0"""
    
    try:
        response = requests.get(
            f"{JUDGE0_URL}/submissions/{token}?base64_encoded=true",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Judge0 result fetch failed: {response.text}"
            )
        
        result = response.json()
        
        # Decode base64 encoded fields
        if result.get("stdout"):
            result["stdout"] = base64.b64decode(result["stdout"]).decode('utf-8', errors='ignore')
        if result.get("stderr"):
            result["stderr"] = base64.b64decode(result["stderr"]).decode('utf-8', errors='ignore')
        if result.get("compile_output"):
            result["compile_output"] = base64.b64decode(result["compile_output"]).decode('utf-8', errors='ignore')
        
        return CodeResultResponse(
            status=result.get("status", {}),
            stdout=result.get("stdout"),
            stderr=result.get("stderr"),
            compile_output=result.get("compile_output"),
            time=result.get("time"),
            memory=result.get("memory")
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Judge0 result fetch timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Judge0 error: {str(e)}")

@router.post("/run_tests/{task_id}")
async def run_code_tests(
    task_id: str,
    source_code: str,
    language: str,
    db: Session = Depends(get_db)
):
    """Run code against predefined test cases"""
    
    # Get coding task
    task = db.query(CodingTask).filter(CodingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Coding task not found")
    
    language_id = LANGUAGE_MAP.get(language.lower())
    if not language_id:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}. Supported: {list(LANGUAGE_MAP.keys())}"
        )
    
    test_results = []
    passed_tests = 0
    total_tests = len(task.test_cases)
    
    # Run each test case
    for i, test_case in enumerate(task.test_cases):
        test_input = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "").strip()
        
        # Submit code with test input
        submission_request = CodeSubmissionRequest(
            source_code=source_code,
            language_id=language_id,
            stdin=test_input
        )
        
        # Submit and wait for result
        submission_response = await submit_code(submission_request, db)
        token = submission_response.token
        
        # Poll for result (with timeout)
        result = None
        max_attempts = 30  # 30 seconds timeout
        
        for attempt in range(max_attempts):
            try:
                result = await get_submission_result(token)
                
                # Check if execution is complete
                status_id = result.status.get("id", 0)
                if status_id not in [1, 2]:  # Not "In Queue" or "Processing"
                    break
                    
            except Exception:
                pass
                
            time.sleep(1)
        
        if not result:
            test_results.append({
                "test_case": i + 1,
                "passed": False,
                "error": "Execution timeout",
                "expected": expected_output,
                "actual": None
            })
            continue
        
        # Check result
        status_id = result.status.get("id", 0)
        actual_output = (result.stdout or "").strip()
        
        if status_id == 3:  # Accepted
            passed = actual_output == expected_output
            if passed:
                passed_tests += 1
                
            test_results.append({
                "test_case": i + 1,
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output,
                "execution_time": result.time,
                "memory_used": result.memory
            })
            
        else:
            # Execution error
            error_msg = result.stderr or result.compile_output or "Unknown error"
            test_results.append({
                "test_case": i + 1,
                "passed": False,
                "error": error_msg,
                "expected": expected_output,
                "actual": actual_output
            })
    
    # Calculate score
    score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Save submission to database
    code_submission = CodeSubmission(
        coding_task_id=task_id,
        session_id=task.session_id,
        code=source_code,
        language=language,
        result={
            "test_results": test_results,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "score": score
        },
        score=score
    )
    db.add(code_submission)
    db.commit()
    
    return {
        "submission_id": code_submission.id,
        "score": score,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "test_results": test_results
    }

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    
    try:
        response = requests.get(
            f"{JUDGE0_URL}/languages",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            languages = response.json()
            return {"languages": languages}
        else:
            # Return our predefined language mapping
            return {
                "languages": [
                    {"id": lang_id, "name": lang_name}
                    for lang_name, lang_id in LANGUAGE_MAP.items()
                ]
            }
            
    except Exception:
        # Fallback to predefined languages
        return {
            "languages": [
                {"id": lang_id, "name": lang_name}
                for lang_name, lang_id in LANGUAGE_MAP.items()
            ]
        }

@router.get("/health")
async def judge0_health_check():
    """Check if Judge0 service is available"""
    
    try:
        response = requests.get(
            f"{JUDGE0_URL}/system_info",
            headers=get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            return {"status": "healthy", "judge0_url": JUDGE0_URL}
        else:
            return {"status": "unhealthy", "error": f"Judge0 returned {response.status_code}"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}