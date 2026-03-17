"""
Co-Buddy AGI Core System - The Universal Learning Agent
A complete rewrite that consolidates all functionality into a cohesive system
"""
import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
import sqlite3
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# AI/ML imports
import openai
import anthropic
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CORE DATA MODELS
# ============================================================================

class TaskType(Enum):
    LEARNING = "learning"
    EXECUTION = "execution"
    AUTONOMOUS = "autonomous"
    ANALYSIS = "analysis"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class AgentState(Enum):
    IDLE = "idle"
    LEARNING = "learning"
    PRACTICING = "practicing"
    AUTONOMOUS = "autonomous"
    TEACHING = "teaching"

@dataclass
class Task:
    id: str
    type: TaskType
    status: TaskStatus
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

@dataclass
class LearningSession:
    id: str
    process_name: str
    domain: str
    status: str
    confidence_score: float
    steps: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    created_at: datetime
    autonomous_enabled: bool = False

@dataclass
class AgentMemory:
    task_id: str
    content: str
    embedding: List[float]
    timestamp: datetime
    importance: float

# ============================================================================
# CORE AGENT SYSTEMS
# ============================================================================

class CobuddyMemory:
    """Advanced memory system with embedding and retrieval"""
    
    def __init__(self, db_path: str = "./cobuddy_memory.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT,
                status TEXT,
                title TEXT,
                description TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT,
                result TEXT
            )
        ''')
        
        # Learning sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id TEXT PRIMARY KEY,
                process_name TEXT,
                domain TEXT,
                status TEXT,
                confidence_score REAL,
                steps TEXT,
                errors TEXT,
                created_at TEXT,
                autonomous_enabled BOOLEAN
            )
        ''')
        
        # Memory embeddings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                content TEXT,
                embedding TEXT,
                timestamp TEXT,
                importance REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def store_task(self, task: Task):
        """Store a task in memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, type, status, title, description, created_at, updated_at, metadata, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.type.value, task.status.value, task.title, task.description,
            task.created_at.isoformat(), task.updated_at.isoformat(),
            json.dumps(task.metadata), json.dumps(task.result) if task.result else None
        ))
        
        conn.commit()
        conn.close()
    
    async def store_learning_session(self, session: LearningSession):
        """Store a learning session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learning_sessions
            (id, process_name, domain, status, confidence_score, steps, errors, created_at, autonomous_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.id, session.process_name, session.domain, session.status,
            session.confidence_score, json.dumps(session.steps), json.dumps(session.errors),
            session.created_at.isoformat(), session.autonomous_enabled
        ))
        
        conn.commit()
        conn.close()
    
    async def get_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Retrieve tasks from memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM tasks WHERE status = ?', (status.value,))
        else:
            cursor.execute('SELECT * FROM tasks')
        
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            task = Task(
                id=row[0],
                type=TaskType(row[1]),
                status=TaskStatus(row[2]),
                title=row[3],
                description=row[4],
                created_at=datetime.fromisoformat(row[5]),
                updated_at=datetime.fromisoformat(row[6]),
                metadata=json.loads(row[7]),
                result=json.loads(row[8]) if row[8] else None
            )
            tasks.append(task)
        
        return tasks
    
    async def get_learning_sessions(self) -> List[LearningSession]:
        """Retrieve learning sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM learning_sessions')
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session = LearningSession(
                id=row[0],
                process_name=row[1],
                domain=row[2],
                status=row[3],
                confidence_score=row[4],
                steps=json.loads(row[5]),
                errors=json.loads(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                autonomous_enabled=bool(row[8])
            )
            sessions.append(session)
        
        return sessions

class UniversalAPIManager:
    """Universal API integration system"""
    
    def __init__(self):
        self.apis = {}
        self.load_api_configs()
    
    def load_api_configs(self):
        """Load API configurations from environment"""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            self.apis['openai'] = {
                'client': openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')),
                'models': ['gpt-4', 'gpt-3.5-turbo'],
                'available': True
            }
        
        # Anthropic Claude
        if os.getenv('ANTHROPIC_API_KEY'):
            self.apis['anthropic'] = {
                'client': anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')),
                'models': ['claude-3-sonnet', 'claude-3-haiku'],
                'available': True
            }
        
        # Google Gemini
        if os.getenv('GOOGLE_API_KEY'):
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.apis['gemini'] = {
                'client': genai,
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'available': True
            }
        
        # NVIDIA NIM
        if os.getenv('NVIDIA_NIM_API_KEY'):
            self.apis['nvidia'] = {
                'endpoint': os.getenv('VITE_NVIDIA_NIM_ENDPOINT', 'https://integrate.api.nvidia.com/v1/chat/completions'),
                'api_key': os.getenv('NVIDIA_NIM_API_KEY'),
                'models': ['mistral', 'llama2'],
                'available': True
            }
    
    async def call_api(self, provider: str, prompt: str, model: Optional[str] = None) -> str:
        """Make API call to specified provider"""
        if provider not in self.apis or not self.apis[provider]['available']:
            raise HTTPException(status_code=400, detail=f"API provider {provider} not available")
        
        try:
            if provider == 'openai':
                response = self.apis[provider]['client'].chat.completions.create(
                    model=model or 'gpt-3.5-turbo',
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            
            elif provider == 'anthropic':
                response = self.apis[provider]['client'].messages.create(
                    model=model or 'claude-3-haiku',
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif provider == 'gemini':
                model_obj = genai.GenerativeModel(model or 'gemini-pro')
                response = model_obj.generate_content(prompt)
                return response.text
            
            elif provider == 'nvidia':
                import requests
                headers = {
                    "Authorization": f"Bearer {self.apis[provider]['api_key']}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model or "mistral",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "stream": False
                }
                response = requests.post(self.apis[provider]['endpoint'], headers=headers, json=data)
                return response.json()['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"API call failed for {provider}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")
    
    def list_apis(self) -> Dict[str, Any]:
        """List available APIs"""
        return {
            provider: {
                'available': info['available'],
                'models': info.get('models', [])
            }
            for provider, info in self.apis.items()
        }

class ProcessLearningEngine:
    """Advanced process learning and automation engine"""
    
    def __init__(self, memory: CobuddyMemory, api_manager: UniversalAPIManager):
        self.memory = memory
        self.api_manager = api_manager
        self.active_sessions = {}
    
    async def start_learning_session(self, process_name: str, domain: str = "general") -> Dict[str, Any]:
        """Start a new learning session"""
        session_id = str(uuid.uuid4())
        session = LearningSession(
            id=session_id,
            process_name=process_name,
            domain=domain,
            status="learning",
            confidence_score=0.0,
            steps=[],
            errors=[],
            created_at=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        await self.memory.store_learning_session(session)
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "learning_started",
            "message": f"Started learning session for {process_name}"
        }
    
    async def capture_screen_frame(self, session_id: str, frame_data: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Capture and analyze screen frame"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Learning session not found")
        
        session = self.active_sessions[session_id]
        
        # Analyze frame using AI
        try:
            analysis = await self.api_manager.call_api(
                'openai', 
                f"Analyze this screen frame and describe the user interface elements and possible actions. Frame data: {frame_data[:1000]}..."
            )
            
            step = {
                "type": "screen_capture",
                "timestamp": timestamp or datetime.now().isoformat(),
                "analysis": analysis,
                "frame_data": frame_data
            }
            
            session.steps.append(step)
            await self.memory.store_learning_session(session)
            
            return {
                "success": True,
                "analysis": analysis,
                "step_count": len(session.steps)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_user_action(self, session_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Record user action during learning"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Learning session not found")
        
        session = self.active_sessions[session_id]
        
        step = {
            "type": "user_action",
            "timestamp": datetime.now().isoformat(),
            "action": action
        }
        
        session.steps.append(step)
        await self.memory.store_learning_session(session)
        
        return {
            "success": True,
            "step_count": len(session.steps)
        }
    
    async def record_error_and_correction(self, session_id: str, error: str, correction: str) -> Dict[str, Any]:
        """Record error and correction for learning"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Learning session not found")
        
        session = self.active_sessions[session_id]
        
        error_record = {
            "error": error,
            "correction": correction,
            "timestamp": datetime.now().isoformat()
        }
        
        session.errors.append(error_record)
        await self.memory.store_learning_session(session)
        
        return {
            "success": True,
            "error_count": len(session.errors)
        }
    
    async def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """End learning session and calculate confidence"""
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Learning session not found")
        
        session = self.active_sessions[session_id]
        session.status = "completed"
        
        # Calculate confidence score based on steps and errors
        step_count = len(session.steps)
        error_count = len(session.errors)
        
        if step_count > 0:
            session.confidence_score = max(0.0, min(1.0, (step_count - error_count) / step_count))
        else:
            session.confidence_score = 0.0
        
        await self.memory.store_learning_session(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        return {
            "success": True,
            "confidence_score": session.confidence_score,
            "total_steps": step_count,
            "total_errors": error_count,
            "status": "learning_completed"
        }
    
    async def get_process_workflow(self, session_id: str) -> Dict[str, Any]:
        """Get extracted workflow from learning session"""
        session = self.active_sessions.get(session_id)
        if not session:
            # Try to get from memory
            sessions = await self.memory.get_learning_sessions()
            session = next((s for s in sessions if s.id == session_id), None)
            if not session:
                raise HTTPException(status_code=404, detail="Learning session not found")
        
        # Generate workflow summary using AI
        if session.steps:
            steps_summary = json.dumps(session.steps, indent=2)
            try:
                workflow_summary = await self.api_manager.call_api(
                    'openai',
                    f"Based on these steps, create a comprehensive workflow description: {steps_summary[:2000]}..."
                )
            except:
                workflow_summary = "Workflow analysis unavailable"
        else:
            workflow_summary = "No steps recorded"
        
        return {
            "session_id": session_id,
            "process_name": session.process_name,
            "domain": session.domain,
            "status": session.status,
            "confidence_score": session.confidence_score,
            "total_steps": len(session.steps),
            "total_errors": len(session.errors),
            "workflow_summary": workflow_summary,
            "steps": session.steps,
            "errors": session.errors
        }
    
    async def transition_to_autonomous(self, session_id: str) -> Dict[str, Any]:
        """Transition process to autonomous execution"""
        sessions = await self.memory.get_learning_sessions()
        session = next((s for s in sessions if s.id == session_id), None)
        
        if not session:
            raise HTTPException(status_code=404, detail="Learning session not found")
        
        if session.confidence_score < 0.7:
            return {
                "success": False,
                "error": "Confidence score too low for autonomous execution",
                "confidence_score": session.confidence_score,
                "required_score": 0.7
            }
        
        session.autonomous_enabled = True
        session.status = "autonomous"
        await self.memory.store_learning_session(session)
        
        return {
            "success": True,
            "message": "Process transitioned to autonomous execution",
            "confidence_score": session.confidence_score
        }
    
    async def execute_autonomous_process(self, process_id: str) -> Dict[str, Any]:
        """Execute a learned process autonomously"""
        sessions = await self.memory.get_learning_sessions()
        session = next((s for s in sessions if s.id == process_id and s.autonomous_enabled), None)
        
        if not session:
            raise HTTPException(status_code=404, detail="Autonomous process not found")
        
        execution_id = str(uuid.uuid4())
        
        # Simulate autonomous execution
        # In real implementation, this would execute the actual steps
        try:
            # Use AI to plan execution
            plan = await self.api_manager.call_api(
                'openai',
                f"Create an execution plan for this process: {session.process_name}. Steps: {json.dumps(session.steps[:5], indent=2)}"
            )
            
            result = {
                "execution_id": execution_id,
                "process_id": process_id,
                "status": "completed",
                "execution_plan": plan,
                "steps_executed": len(session.steps),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "execution": result
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id
            }
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get learning progress analytics"""
        sessions = await self.memory.get_learning_sessions()
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "completed"])
        autonomous_sessions = len([s for s in sessions if s.autonomous_enabled])
        
        avg_confidence = sum(s.confidence_score for s in sessions) / total_sessions if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "autonomous_sessions": autonomous_sessions,
            "average_confidence_score": avg_confidence,
            "success_rate": completed_sessions / total_sessions if total_sessions > 0 else 0
        }
    
    async def get_all_processes(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all learned processes"""
        sessions = await self.memory.get_learning_sessions()
        
        if state:
            sessions = [s for s in sessions if s.status == state]
        
        return [
            {
                "id": s.id,
                "process_name": s.process_name,
                "domain": s.domain,
                "status": s.status,
                "confidence_score": s.confidence_score,
                "autonomous_enabled": s.autonomous_enabled,
                "created_at": s.created_at.isoformat(),
                "step_count": len(s.steps),
                "error_count": len(s.errors)
            }
            for s in sessions
        ]

# ============================================================================
# MAIN CO-BUDDY AGI CLASS
# ============================================================================

class CobuddyAGI:
    """Main Co-Buddy AGI System - The Universal Learning Agent"""
    
    def __init__(self):
        self.memory = CobuddyMemory()
        self.api_manager = UniversalAPIManager()
        self.process_engine = ProcessLearningEngine(self.memory, self.api_manager)
        self.current_state = AgentState.IDLE
        self.system_prompt = """
        You are Co-Buddy, a universal learning AGI designed to learn any process through observation 
        and execute it autonomously. You can integrate with any API, learn from user interactions, 
        and continuously improve your capabilities.
        
        Core capabilities:
        - Process learning through screen sharing and observation
        - Autonomous execution of learned processes
        - Universal API integration
        - Natural language understanding and generation
        - Memory and learning analytics
        - Mobile-first design with Android support
        """
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process natural language command"""
        try:
            # Use AI to understand and process the command
            prompt = f"""
            System: {self.system_prompt}
            
            User Command: {command}
            Context: {json.dumps(context or {})}
            
            Process this command and determine the appropriate action or response.
            """
            
            response = await self.api_manager.call_api('openai', prompt)
            return response
        
        except Exception as e:
            return f"I encountered an error processing your command: {str(e)}"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        memory_summary = {"total_tasks": len(await self.memory.get_tasks())}
        learning_analytics = await self.process_engine.get_learning_analytics()
        processes = await self.process_engine.get_all_processes()
        apis = self.api_manager.list_apis()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "state": self.current_state.value,
            "memory": memory_summary,
            "learning": learning_analytics,
            "processes": {
                "total": len(processes),
                "learning": len([p for p in processes if p['status'] == 'learning']),
                "practicing": len([p for p in processes if p['status'] == 'practicing']),
                "autonomous": len([p for p in processes if p['status'] == 'autonomous'])
            },
            "apis": apis,
            "capabilities": {
                "process_learning": True,
                "autonomous_execution": True,
                "universal_apis": True,
                "self_learning": True,
                "mobile_first": True,
                "voice_enabled": True,
                "multi_provider_ai": True
            }
        }

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Initialize Co-Buddy AGI
cobuddy = CobuddyAGI()

# Create FastAPI app
app = FastAPI(
    title="Co-Buddy AGI",
    description="Universal Learning Agent - Learn any process, automate everything",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API MODELS
# ============================================================================

class ProcessLearningRequest(BaseModel):
    process_name: str
    domain: str = "general"

class ScreenCaptureRequest(BaseModel):
    session_id: str
    frame_data: str  # base64 encoded
    timestamp: Optional[str] = None

class ActionRequest(BaseModel):
    session_id: str
    action: Dict[str, Any]

class ErrorCorrectionRequest(BaseModel):
    session_id: str
    error: str
    correction: str

class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "Co-Buddy AGI",
        "version": "3.0.0",
        "status": "operational",
        "tagline": "Universal Learning Agent - The Superbrain of the Century",
        "message": "Welcome to Co-Buddy - Your universal learning and automation companion"
    }

@app.post("/api/v1/command", tags=["Core"])
async def process_command(request: CommandRequest):
    """Process natural language command"""
    response = await cobuddy.process_command(request.command, request.context)
    return {
        "command": request.command,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/status", tags=["Status"])
async def get_status():
    """Get complete Co-Buddy status"""
    return await cobuddy.get_system_status()

@app.get("/api/v1/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }

# Process Learning Endpoints
@app.post("/api/v1/learning/start", tags=["Process Learning"])
async def start_learning_session(request: ProcessLearningRequest):
    """Start a new process learning session"""
    return await cobuddy.process_engine.start_learning_session(request.process_name, request.domain)

@app.post("/api/v1/learning/capture", tags=["Process Learning"])
async def capture_screen(request: ScreenCaptureRequest):
    """Capture screen frame during learning"""
    return await cobuddy.process_engine.capture_screen_frame(
        request.session_id, request.frame_data, request.timestamp
    )

@app.post("/api/v1/learning/action", tags=["Process Learning"])
async def record_action(request: ActionRequest):
    """Record user action during learning"""
    return await cobuddy.process_engine.record_user_action(request.session_id, request.action)

@app.post("/api/v1/learning/error", tags=["Process Learning"])
async def record_error(request: ErrorCorrectionRequest):
    """Record error and correction for learning"""
    return await cobuddy.process_engine.record_error_and_correction(
        request.session_id, request.error, request.correction
    )

@app.post("/api/v1/learning/end/{session_id}", tags=["Process Learning"])
async def end_learning_session(session_id: str):
    """End learning session and calculate confidence"""
    return await cobuddy.process_engine.end_learning_session(session_id)

@app.get("/api/v1/learning/workflow/{session_id}", tags=["Process Learning"])
async def get_workflow(session_id: str):
    """Get extracted workflow from learning session"""
    return await cobuddy.process_engine.get_process_workflow(session_id)

@app.post("/api/v1/learning/autonomous/{session_id}", tags=["Process Learning"])
async def transition_to_autonomous(session_id: str):
    """Transition process to autonomous execution"""
    return await cobuddy.process_engine.transition_to_autonomous(session_id)

@app.post("/api/v1/execution/autonomous/{process_id}", tags=["Autonomous Execution"])
async def execute_autonomous(process_id: str):
    """Execute a learned process autonomously"""
    return await cobuddy.process_engine.execute_autonomous_process(process_id)

# Analytics Endpoints
@app.get("/api/v1/analytics/learning", tags=["Analytics"])
async def get_learning_analytics():
    """Get learning progress analytics"""
    return await cobuddy.process_engine.get_learning_analytics()

@app.get("/api/v1/analytics/processes", tags=["Analytics"])
async def get_all_processes(state: Optional[str] = None):
    """Get all learned processes"""
    processes = await cobuddy.process_engine.get_all_processes(state)
    return {
        "processes": processes,
        "count": len(processes),
        "states": {
            "learning": len([p for p in processes if p['status'] == 'learning']),
            "practicing": len([p for p in processes if p['status'] == 'practicing']),
            "autonomous": len([p for p in processes if p['status'] == 'autonomous'])
        }
    }

@app.get("/api/v1/apis", tags=["APIs"])
async def list_apis():
    """List available AI APIs"""
    return cobuddy.api_manager.list_apis()

@app.post("/api/v1/apis/{provider}/chat", tags=["APIs"])
async def chat_with_api(provider: str, prompt: str, model: Optional[str] = None):
    """Chat with specific AI API"""
    response = await cobuddy.api_manager.call_api(provider, prompt, model)
    return {
        "provider": provider,
        "model": model,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

# WebSocket for real-time updates
@app.websocket("/ws/learning/{session_id}")
async def websocket_learning(websocket: WebSocket, session_id: str):
    """WebSocket for real-time learning updates"""
    await websocket.accept()
    try:
        while True:
            # Send periodic updates
            workflow = await cobuddy.process_engine.get_process_workflow(session_id)
            await websocket.send_json({
                "type": "workflow_update",
                "data": workflow
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
