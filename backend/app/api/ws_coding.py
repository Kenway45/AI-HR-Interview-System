from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any
import json
import asyncio
from datetime import datetime

from ..db import engine, CodingTask, CodeSubmission
from ..api.judge import submit_code, get_submission_result, run_code_tests
from ..models import CodeSubmissionRequest

# Database session for WebSocket
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CodingSessionManager:
    """Manages WebSocket connections for coding sessions"""
    
    def __init__(self):
        # session_id -> {websocket, task_id, last_code, user_activity}
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.code_snapshots: Dict[str, list] = {}  # For autosave
    
    async def connect(self, websocket: WebSocket, session_id: str, task_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[session_id] = {
            "websocket": websocket,
            "task_id": task_id,
            "last_code": "",
            "last_activity": datetime.utcnow(),
            "paste_events": [],
            "tab_switches": 0
        }
        
        # Initialize code snapshots
        if session_id not in self.code_snapshots:
            self.code_snapshots[session_id] = []
        
        print(f"WebSocket connected: session {session_id}, task {task_id}")
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        print(f"WebSocket disconnected: session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]["websocket"]
            await websocket.send_json(message)
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        
        if session_id not in self.active_connections:
            return
        
        connection = self.active_connections[session_id]
        message_type = message.get("type")
        
        try:
            if message_type == "code_edit":
                await self._handle_code_edit(session_id, message, connection)
            
            elif message_type == "run_code":
                await self._handle_run_code(session_id, message, connection)
            
            elif message_type == "submit_code":
                await self._handle_submit_code(session_id, message, connection)
            
            elif message_type == "paste_event":
                await self._handle_paste_event(session_id, message, connection)
            
            elif message_type == "tab_switch":
                await self._handle_tab_switch(session_id, message, connection)
                
            else:
                await self.send_message(session_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
        
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "message": f"Error handling message: {str(e)}"
            })
    
    async def _handle_code_edit(self, session_id: str, message: Dict[str, Any], connection: Dict[str, Any]):
        """Handle code editing events"""
        
        code = message.get("code", "")
        cursor_position = message.get("cursor", {})
        timestamp = datetime.utcnow()
        
        # Update last code and activity
        connection["last_code"] = code
        connection["last_activity"] = timestamp
        
        # Auto-save snapshot every 30 seconds or significant changes
        snapshots = self.code_snapshots[session_id]
        
        should_snapshot = (
            len(snapshots) == 0 or  # First snapshot
            len(code) - len(snapshots[-1].get("code", "")) > 50 or  # 50+ char change
            (timestamp - snapshots[-1]["timestamp"]).total_seconds() > 30  # 30+ seconds
        )
        
        if should_snapshot:
            snapshots.append({
                "code": code,
                "timestamp": timestamp,
                "cursor": cursor_position
            })
            
            # Keep only last 20 snapshots
            if len(snapshots) > 20:
                snapshots.pop(0)
        
        # Send acknowledgment
        await self.send_message(session_id, {
            "type": "edit_ack",
            "timestamp": timestamp.isoformat()
        })
    
    async def _handle_run_code(self, session_id: str, message: Dict[str, Any], connection: Dict[str, Any]):
        """Handle code execution request"""
        
        code = message.get("code", "")
        language = message.get("language", "python")
        stdin_input = message.get("input", "")
        
        # Language ID mapping
        language_map = {
            "python": 71,
            "javascript": 63,
            "java": 62,
            "cpp": 54,
            "c": 50
        }
        
        language_id = language_map.get(language.lower())
        if not language_id:
            await self.send_message(session_id, {
                "type": "run_result",
                "success": False,
                "error": f"Unsupported language: {language}"
            })
            return
        
        try:
            # Create database session
            db = SessionLocal()
            
            # Submit code to Judge0
            request = CodeSubmissionRequest(
                source_code=code,
                language_id=language_id,
                stdin=stdin_input
            )
            
            submission = await submit_code(request, db)
            token = submission.token
            
            # Poll for result
            result = None
            max_attempts = 15  # 15 seconds timeout
            
            for _ in range(max_attempts):
                result = await get_submission_result(token)
                
                status_id = result.status.get("id", 0)
                if status_id not in [1, 2]:  # Not processing
                    break
                    
                await asyncio.sleep(1)
            
            db.close()
            
            if result:
                await self.send_message(session_id, {
                    "type": "run_result",
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "time": result.time,
                    "memory": result.memory,
                    "status": result.status
                })
            else:
                await self.send_message(session_id, {
                    "type": "run_result",
                    "success": False,
                    "error": "Execution timeout"
                })
        
        except Exception as e:
            await self.send_message(session_id, {
                "type": "run_result",
                "success": False,
                "error": str(e)
            })
    
    async def _handle_submit_code(self, session_id: str, message: Dict[str, Any], connection: Dict[str, Any]):
        """Handle final code submission with test cases"""
        
        code = message.get("code", "")
        language = message.get("language", "python")
        task_id = connection["task_id"]
        
        try:
            # Create database session
            db = SessionLocal()
            
            # Run tests against the task
            result = await run_code_tests(task_id, code, language, db)
            
            db.close()
            
            await self.send_message(session_id, {
                "type": "submit_result",
                "success": True,
                "score": result["score"],
                "passed_tests": result["passed_tests"],
                "total_tests": result["total_tests"],
                "test_results": result["test_results"]
            })
            
        except Exception as e:
            await self.send_message(session_id, {
                "type": "submit_result",
                "success": False,
                "error": str(e)
            })
    
    async def _handle_paste_event(self, session_id: str, message: Dict[str, Any], connection: Dict[str, Any]):
        """Handle paste detection (potential cheating)"""
        
        pasted_content = message.get("content", "")
        timestamp = datetime.utcnow()
        
        connection["paste_events"].append({
            "content": pasted_content[:200],  # Store first 200 chars
            "timestamp": timestamp,
            "length": len(pasted_content)
        })
        
        # Alert if large paste (potential external code)
        if len(pasted_content) > 100:
            await self.send_message(session_id, {
                "type": "proctor_alert",
                "event": "large_paste",
                "message": "Large code paste detected",
                "severity": "medium"
            })
    
    async def _handle_tab_switch(self, session_id: str, message: Dict[str, Any], connection: Dict[str, Any]):
        """Handle tab switch detection"""
        
        connection["tab_switches"] += 1
        timestamp = datetime.utcnow()
        
        # Alert on excessive tab switching
        if connection["tab_switches"] > 5:
            await self.send_message(session_id, {
                "type": "proctor_alert",
                "event": "excessive_tab_switching",
                "message": f"Multiple tab switches detected ({connection['tab_switches']})",
                "severity": "high"
            })

# Global session manager
coding_session_manager = CodingSessionManager()

async def handle_coding_websocket(websocket: WebSocket, session_id: str, task_id: str):
    """Main WebSocket handler for coding sessions"""
    
    await coding_session_manager.connect(websocket, session_id, task_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await coding_session_manager.handle_message(session_id, message)
                
            except json.JSONDecodeError:
                await coding_session_manager.send_message(session_id, {
                    "type": "error",
                    "message": "Invalid JSON message"
                })
            
    except WebSocketDisconnect:
        coding_session_manager.disconnect(session_id)
    
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        coding_session_manager.disconnect(session_id)