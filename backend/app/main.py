from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import sessions, upload, judge, ws_coding
import os

# Import appropriate STT and LLM modules based on configuration
STT_ENGINE = os.getenv("STT_ENGINE", "whisper")
LLM_ENGINE = os.getenv("LLM_ENGINE", "textgen")

if STT_ENGINE == "mock":
    from .api import stt_mock as stt
else:
    from .api import stt

if LLM_ENGINE == "mock":
    from .api import llm_mock as llm
else:
    from .api import llm
from .db import init_db
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI HR Interview system...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="AI HR Interview System",
    description="Zero-cost, speech-first AI HR interview system with live coding",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(sessions.router, prefix="/session", tags=["sessions"])
app.include_router(stt.router, prefix="/stt", tags=["speech-to-text"])
app.include_router(judge.router, prefix="/judge", tags=["code-execution"])
app.include_router(llm.router, prefix="/llm", tags=["language-model"])

# WebSocket endpoint
@app.websocket("/ws/session/{session_id}/coding/{task_id}")
async def coding_websocket(websocket: WebSocket, session_id: str, task_id: str):
    await ws_coding.handle_coding_websocket(websocket, session_id, task_id)

@app.get("/")
async def root():
    return {
        "message": "AI HR Interview System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-hr-interview"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)