from fastapi import FastAPI, UploadFile, File, HTTPException
import subprocess
import tempfile
import os
import json

app = FastAPI(title="Whisper.cpp HTTP Server")

WHISPER_BIN = os.getenv("WHISPER_BIN", "/opt/whispercpp/main")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/ggml-base.en.bin")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio using whisper.cpp"""
    
    if not os.path.exists(WHISPER_BIN):
        raise HTTPException(status_code=500, detail="Whisper binary not found")
    
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=500, detail="Whisper model not found")
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Convert to wav if needed using ffmpeg
        wav_path = tmp_path
        if not file.filename.lower().endswith('.wav'):
            wav_path = tmp_path.replace(tmp_path.split('.')[-1], 'wav')
            convert_cmd = [
                'ffmpeg', '-i', tmp_path, 
                '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                '-y', wav_path
            ]
            subprocess.run(convert_cmd, capture_output=True, check=True)
        
        # Run whisper.cpp transcription
        cmd = [
            WHISPER_BIN,
            '-m', MODEL_PATH,
            '-f', wav_path,
            '--output-json',
            '--no-prints'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {result.stderr}")
        
        # Parse JSON output or fallback to text output
        try:
            # Try to find JSON output file
            json_file = wav_path.replace('.wav', '.json')
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    transcript = data.get('text', '').strip()
                os.remove(json_file)
            else:
                # Fallback to stdout
                transcript = result.stdout.strip()
        except:
            transcript = result.stdout.strip()
        
        return {
            "text": transcript,
            "status": "success"
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Transcription timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Cleanup temporary files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if wav_path != tmp_path and os.path.exists(wav_path):
            os.remove(wav_path)

@app.get("/health")
async def health_check():
    """Check if whisper service is healthy"""
    
    whisper_ready = os.path.exists(WHISPER_BIN)
    model_ready = os.path.exists(MODEL_PATH)
    
    return {
        "status": "healthy" if (whisper_ready and model_ready) else "unhealthy",
        "whisper_binary": whisper_ready,
        "model_loaded": model_ready,
        "model_path": MODEL_PATH
    }

@app.get("/")
async def root():
    return {"message": "Whisper.cpp HTTP Server", "version": "1.0.0"}