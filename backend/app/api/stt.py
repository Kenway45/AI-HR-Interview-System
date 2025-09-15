from fastapi import APIRouter, UploadFile, File, HTTPException
import subprocess
import uuid
import os
import tempfile
import json
import requests
from ..models import TranscriptResponse

router = APIRouter()

# Configuration
WHISPER_BIN = os.getenv("WHISPER_BIN", "/opt/whispercpp/main")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "/models/ggml-base.en.bin")
VOSK_SERVER_URL = os.getenv("VOSK_SERVER_URL", "http://vosk-server:2700")
STT_ENGINE = os.getenv("STT_ENGINE", "whisper")  # "whisper" or "vosk"

async def transcribe_audio_internal(file_content: bytes, filename: str) -> str:
    """Internal function to transcribe audio - used by other modules"""
    
    if STT_ENGINE == "whisper":
        return await transcribe_with_whisper(file_content, filename)
    elif STT_ENGINE == "vosk":
        return await transcribe_with_vosk(file_content, filename)
    else:
        raise HTTPException(status_code=500, detail=f"Unknown STT engine: {STT_ENGINE}")

async def transcribe_with_whisper(file_content: bytes, filename: str) -> str:
    """Transcribe using Whisper.cpp"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name
    
    try:
        # Convert to WAV if needed (whisper.cpp works best with WAV)
        wav_path = tmp_path
        if not filename.lower().endswith('.wav'):
            wav_path = convert_to_wav(tmp_path)
        
        # Run whisper.cpp
        cmd = [
            WHISPER_BIN,
            "-m", WHISPER_MODEL,
            "-f", wav_path,
            "--output-txt",
            "--no-prints"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Whisper transcription failed: {result.stderr}"
            )
        
        # Read the output txt file
        txt_file = wav_path.replace('.wav', '.txt')
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as f:
                transcript = f.read().strip()
            os.remove(txt_file)
        else:
            # Fallback: parse stdout
            transcript = result.stdout.strip()
        
        return transcript
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Transcription timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if wav_path != tmp_path and os.path.exists(wav_path):
            os.remove(wav_path)

async def transcribe_with_vosk(file_content: bytes, filename: str) -> str:
    """Transcribe using Vosk server"""
    
    try:
        # Send to Vosk server
        files = {'audio': (filename, file_content, 'audio/wav')}
        response = requests.post(f"{VOSK_SERVER_URL}/transcribe", files=files, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Vosk server error: {response.text}"
            )
        
        result = response.json()
        return result.get('text', '').strip()
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Vosk transcription timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Vosk server error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format using ffmpeg"""
    output_path = input_path.replace(os.path.splitext(input_path)[1], '.wav')
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        '-y',  # overwrite output
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Audio conversion failed: {result.stderr}"
        )
    
    return output_path

@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    # Read file content
    file_content = await file.read()
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")
    
    # Transcribe
    transcript = await transcribe_audio_internal(file_content, file.filename)
    
    if not transcript.strip():
        return TranscriptResponse(
            transcript="[No speech detected]",
            confidence=0.0
        )
    
    return TranscriptResponse(
        transcript=transcript,
        confidence=0.95  # Placeholder - real confidence would come from the STT engine
    )

@router.get("/health")
async def stt_health_check():
    """Check if STT service is available"""
    
    try:
        if STT_ENGINE == "whisper":
            # Check if whisper binary exists
            if not os.path.exists(WHISPER_BIN):
                return {"status": "unhealthy", "error": "Whisper binary not found"}
            if not os.path.exists(WHISPER_MODEL):
                return {"status": "unhealthy", "error": "Whisper model not found"}
            return {"status": "healthy", "engine": "whisper"}
            
        elif STT_ENGINE == "vosk":
            # Check if Vosk server is reachable
            response = requests.get(f"{VOSK_SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "engine": "vosk"}
            else:
                return {"status": "unhealthy", "error": "Vosk server not responding"}
                
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    
    return {"status": "unknown", "engine": STT_ENGINE}