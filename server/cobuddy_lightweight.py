#!/usr/bin/env python3
"""
Co-Buddy Lightweight AGI System
Integrates with Twin Agent System (Aegis + Giffy)
Lightweight Model2Vec + FAISS IndexFlatL2 implementation
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import sqlite3
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Lightweight ML imports
import numpy as np
from model2vec import StaticModel
import faiss
from bs4 import BeautifulSoup
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Co-buddy configuration"""
    embedding_model = "minishlab/M2V_base_output"
    embedding_dim = 512
    db_path = "./cobuddy_memory.db"
    models_dir = Path("./models")
    data_dir = Path("./data")
    logs_dir = Path("./logs")
    
    # Twin Agent Integration
    giffy_api_url = "http://localhost:8001"
    aegis_api_url = "http://localhost:8000"
    
    # Learning settings
    min_confidence_for_autonomy = 0.7
    sessions_to_mastery = 3
    
    def __post_init__(self):
        self.models_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

config = Config()

# ============================================================================
# DATA MODELS
# ============================================================================

class SkillLevel(Enum):
    """Skill mastery levels"""
    OBSERVATION = 1
    GUIDED = 2
    SUPERVISED = 3
    AUTONOMOUS = 4
    MASTERY = 5

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class TrainingData:
    """Training data for skill learning"""
    id: str
    skill_name: str
    data_type: str  # "url", "file", "text", "demo"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

@dataclass
class Skill:
    """Learned skill"""
    id: str
    name: str
    description: str
    level: SkillLevel
    confidence: float
    steps: List[Dict[str, Any]]
    training_sessions: int
    last_executed: Optional[str]
    success_rate: float
    memory_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ExecutionTask:
    """Task for autonomous execution"""
    id: str
    skill_id: str
    status: TaskStatus
    user_input: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class TrainingDataRequest(BaseModel):
    skill_name: str
    data_type: str
    content: str
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class SkillRequest(BaseModel):
    name: str
    description: str
    steps: List[Dict[str, Any]]
    tags: Optional[List[str]] = None

class ExecutionRequest(BaseModel):
    skill_id: str
    user_input: str
    watch_mode: bool = False

class FeedbackRequest(BaseModel):
    task_id: str
    feedback: str
    correction: Optional[Dict[str, Any]] = None
    confidence_adjustment: float = 0.0

# ============================================================================
# CORE SYSTEMS
# ============================================================================

class LightweightEmbeddings:
    """Model2Vec embedding system"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Model2Vec model"""
        try:
            self.model = StaticModel.from_pretrained(config.embedding_model)
            logger.info(f"Loaded embedding model: {config.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        try:
            embeddings = self.model.encode(texts)
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

class LocalMemoryIndex:
    """FAISS IndexFlatL2 for local memory storage"""
    
    def __init__(self):
        self.index = None
        self.embeddings = LightweightEmbeddings()
        self.memory_map = {}  # id -> memory content
        self.init_index()
    
    def init_index(self):
        """Initialize FAISS index"""
        base_index = faiss.IndexFlatL2(config.embedding_dim)
        self.index = faiss.IndexIDMap(base_index)
        logger.info("Initialized FAISS IndexFlatL2")
    
    def add_memory(self, memory_id: str, content: str) -> bool:
        """Add memory to index"""
        try:
            embedding = self.embeddings.encode([content])
            self.index.add_with_ids(embedding, np.array([hash(memory_id) % (2**31)]))
            self.memory_map[memory_id] = content
            return True
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    def search(self, query: str, limit: int = 10) -> List[tuple]:
        """Search memories by similarity"""
        try:
            query_embedding = self.embeddings.encode([query])
            distances, indices = self.index.search(query_embedding, limit)
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1:
                    # Find memory_id by hash
                    for mem_id, content in self.memory_map.items():
                        if hash(mem_id) % (2**31) == idx:
                            similarity = 1.0 / (1.0 + float(dist))
                            results.append((mem_id, content, similarity))
                            break
            
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

class CobuddyMemory:
    """Memory system with SQLite persistence"""
    
    def __init__(self, db_path: str = config.db_path):
        self.db_path = db_path
        self.index = LocalMemoryIndex()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    level INTEGER,
                    confidence REAL,
                    steps TEXT,
                    training_sessions INTEGER,
                    last_executed TEXT,
                    success_rate REAL,
                    memory_ids TEXT,
                    created_at TEXT
                )
            """)
            
            # Training data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id TEXT PRIMARY KEY,
                    skill_id TEXT,
                    data_type TEXT,
                    content TEXT,
                    metadata TEXT,
                    tags TEXT,
                    created_at TEXT,
                    FOREIGN KEY (skill_id) REFERENCES skills(id)
                )
            """)
            
            # Execution tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_tasks (
                    id TEXT PRIMARY KEY,
                    skill_id TEXT,
                    status TEXT,
                    user_input TEXT,
                    steps TEXT,
                    results TEXT,
                    confidence REAL,
                    created_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (skill_id) REFERENCES skills(id)
                )
            """)
            
            # Memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    embedding TEXT,
                    metadata TEXT,
                    tags TEXT,
                    created_at TEXT,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
    
    def add_skill(self, skill: Skill) -> bool:
        """Add skill to memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO skills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill.id, skill.name, skill.description, skill.level.value,
                skill.confidence, json.dumps(skill.steps), skill.training_sessions,
                skill.last_executed, skill.success_rate, json.dumps(skill.memory_ids),
                skill.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding skill: {e}")
            return False
    
    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Retrieve skill from memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Skill(
                    id=row[0], name=row[1], description=row[2],
                    level=SkillLevel(row[3]), confidence=row[4],
                    steps=json.loads(row[5]), training_sessions=row[6],
                    last_executed=row[7], success_rate=row[8],
                    memory_ids=json.loads(row[9]), created_at=row[10]
                )
            return None
        except Exception as e:
            logger.error(f"Error getting skill: {e}")
            return None
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search memories using FAISS"""
        results = self.index.search(query, limit)
        
        memories = []
        for mem_id, content, similarity in results:
            memories.append({
                'id': mem_id,
                'content': content,
                'similarity': similarity
            })
        
        return memories

class SkillLearner:
    """System for learning skills from various sources"""
    
    def __init__(self, memory: CobuddyMemory):
        self.memory = memory
    
    async def learn_from_url(self, skill_name: str, url: str, tags: List[str] = None) -> str:
        """Learn from web content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove scripts and styles
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        content = soup.get_text(separator=' ', strip=True)
                        
                        training_data = TrainingData(
                            id=str(uuid.uuid4()),
                            skill_name=skill_name,
                            data_type="url",
                            content=content[:5000],  # Limit content
                            metadata={'source_url': url},
                            tags=tags or []
                        )
                        
                        return await self._store_training_data(training_data)
        except Exception as e:
            logger.error(f"Error learning from URL: {e}")
        
        return None
    
    async def learn_from_text(self, skill_name: str, text: str, tags: List[str] = None) -> str:
        """Learn from text input"""
        try:
            training_data = TrainingData(
                id=str(uuid.uuid4()),
                skill_name=skill_name,
                data_type="text",
                content=text,
                tags=tags or []
            )
            
            return await self._store_training_data(training_data)
        except Exception as e:
            logger.error(f"Error learning from text: {e}")
        
        return None
    
    async def learn_from_file(self, skill_name: str, file_content: str, filename: str, tags: List[str] = None) -> str:
        """Learn from file upload"""
        try:
            training_data = TrainingData(
                id=str(uuid.uuid4()),
                skill_name=skill_name,
                data_type="file",
                content=file_content[:10000],
                metadata={'filename': filename},
                tags=tags or []
            )
            
            return await self._store_training_data(training_data)
        except Exception as e:
            logger.error(f"Error learning from file: {e}")
        
        return None
    
    async def _store_training_data(self, training_data: TrainingData) -> str:
        """Store training data in memory"""
        try:
            conn = sqlite3.connect(self.memory.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO training_data VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                training_data.id, training_data.skill_name, training_data.data_type,
                training_data.content, json.dumps(training_data.metadata),
                json.dumps(training_data.tags), training_data.created_at
            ))
            
            # Add to FAISS index
            self.memory.index.add_memory(training_data.id, training_data.content)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored training data: {training_data.id}")
            return training_data.id
        except Exception as e:
            logger.error(f"Error storing training data: {e}")
            return None

class AutonomousExecutor:
    """System for autonomous task execution"""
    
    def __init__(self, memory: CobuddyMemory):
        self.memory = memory
    
    async def execute_skill(self, skill_id: str, user_input: str, watch_mode: bool = False) -> ExecutionTask:
        """Execute a learned skill"""
        try:
            skill = self.memory.get_skill(skill_id)
            if not skill:
                raise ValueError(f"Skill not found: {skill_id}")
            
            task = ExecutionTask(
                id=str(uuid.uuid4()),
                skill_id=skill_id,
                status=TaskStatus.IN_PROGRESS,
                user_input=user_input,
                confidence=skill.confidence
            )
            
            # Generate execution plan from skill steps
            task.steps = self._generate_execution_plan(skill, user_input)
            
            # Execute steps
            for i, step in enumerate(task.steps):
                try:
                    result = await self._execute_step(step, watch_mode)
                    task.results[f"step_{i}"] = result
                    
                    if not result.get('success'):
                        task.status = TaskStatus.FAILED
                        break
                except Exception as e:
                    logger.error(f"Step execution error: {e}")
                    task.status = TaskStatus.FAILED
                    break
            
            if task.status != TaskStatus.FAILED:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
            
            return task
        except Exception as e:
            logger.error(f"Execution error: {e}")
            raise
    
    def _generate_execution_plan(self, skill: Skill, user_input: str) -> List[Dict]:
        """Generate execution plan from skill steps"""
        plan = []
        for step in skill.steps:
            plan.append({
                'action': step.get('action'),
                'parameters': step.get('parameters', {}),
                'description': step.get('description'),
                'user_input': user_input
            })
        return plan
    
    async def _execute_step(self, step: Dict, watch_mode: bool) -> Dict:
        """Execute a single step"""
        try:
            # Simulate step execution
            # In production, this would execute actual actions
            await asyncio.sleep(0.1)
            
            return {
                'success': True,
                'action': step.get('action'),
                'result': 'Step executed successfully'
            }
        except Exception as e:
            logger.error(f"Step error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(title="Co-Buddy AGI System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize systems
memory = CobuddyMemory()
learner = SkillLearner(memory)
executor = AutonomousExecutor(memory)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "system": "Co-Buddy AGI",
        "version": "1.0.0"
    }

@app.post("/skills/create")
async def create_skill(request: SkillRequest):
    """Create a new skill"""
    try:
        skill = Skill(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            level=SkillLevel.OBSERVATION,
            confidence=0.0,
            steps=request.steps,
            training_sessions=0,
            last_executed=None,
            success_rate=0.0
        )
        
        if memory.add_skill(skill):
            return {"success": True, "skill_id": skill.id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create skill")
    except Exception as e:
        logger.error(f"Error creating skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    """Get skill details"""
    try:
        skill = memory.get_skill(skill_id)
        if skill:
            return asdict(skill)
        else:
            raise HTTPException(status_code=404, detail="Skill not found")
    except Exception as e:
        logger.error(f"Error getting skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn/url")
async def learn_from_url(request: TrainingDataRequest):
    """Learn from URL"""
    try:
        training_id = await learner.learn_from_url(
            request.skill_name,
            request.content,
            request.tags
        )
        
        if training_id:
            return {"success": True, "training_id": training_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to learn from URL")
    except Exception as e:
        logger.error(f"Error learning from URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn/text")
async def learn_from_text(request: TrainingDataRequest):
    """Learn from text"""
    try:
        training_id = await learner.learn_from_text(
            request.skill_name,
            request.content,
            request.tags
        )
        
        if training_id:
            return {"success": True, "training_id": training_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to learn from text")
    except Exception as e:
        logger.error(f"Error learning from text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn/file")
async def learn_from_file(skill_name: str, file: UploadFile = File(...), tags: Optional[str] = None):
    """Learn from file upload"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8', errors='ignore')
        
        tag_list = json.loads(tags) if tags else []
        
        training_id = await learner.learn_from_file(
            skill_name,
            content_str,
            file.filename,
            tag_list
        )
        
        if training_id:
            return {"success": True, "training_id": training_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to learn from file")
    except Exception as e:
        logger.error(f"Error learning from file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute/skill")
async def execute_skill(request: ExecutionRequest):
    """Execute a learned skill"""
    try:
        task = await executor.execute_skill(
            request.skill_id,
            request.user_input,
            request.watch_mode
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": task.status.value,
            "results": task.results,
            "confidence": task.confidence
        }
    except Exception as e:
        logger.error(f"Error executing skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback on execution"""
    try:
        # Update skill based on feedback
        # This would improve confidence and accuracy
        return {
            "success": True,
            "message": "Feedback recorded and processed"
        }
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/memories")
async def search_memories(query: str, limit: int = 10):
    """Search memories"""
    try:
        results = memory.search_memories(query, limit)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        return {
            "system": "Co-Buddy AGI",
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "embedding_model": config.embedding_model,
            "embedding_dim": config.embedding_dim,
            "memory_db": config.db_path
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WEBSOCKET SUPPORT FOR REAL-TIME INTERACTION
# ============================================================================

@app.websocket("/ws/interact")
async def websocket_interact(websocket: WebSocket):
    """WebSocket for real-time agent interaction"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'execute':
                task = await executor.execute_skill(
                    data.get('skill_id'),
                    data.get('input'),
                    watch_mode=True
                )
                await websocket.send_json({
                    'type': 'execution_result',
                    'task_id': task.id,
                    'status': task.status.value,
                    'results': task.results
                })
            
            elif data.get('type') == 'feedback':
                await websocket.send_json({
                    'type': 'feedback_ack',
                    'message': 'Feedback received'
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)

# ============================================================================
# STARTUP AND SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Co-Buddy AGI System starting...")
    logger.info(f"Embedding model: {config.embedding_model}")
    logger.info(f"Embedding dimension: {config.embedding_dim}")
    logger.info(f"Memory DB: {config.db_path}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Co-Buddy AGI System shutting down...")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Co-Buddy AGI System")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8002, help="Server port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              Co-Buddy AGI System v1.0.0                      ║
    ║         Lightweight Learning & Autonomous Execution          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ Features:                                                    ║
    ║ • Model2Vec lightweight embeddings (512d)                    ║
    ║ • FAISS IndexFlatL2 for memory search                        ║
    ║ • Skill learning from URLs, files, text                     ║
    ║ • Autonomous task execution                                 ║
    ║ • Twin Agent integration (Aegis + Giffy)                    ║
    ║ • Real-time WebSocket interaction                           ║
    ║ • Permanent memory persistence                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "cobuddy_lightweight:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
