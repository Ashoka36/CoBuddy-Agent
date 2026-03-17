# Co-Buddy AGI Integration Guide
## Twin Agent System Integration (Aegis + Giffy + Co-Buddy)

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: March 17, 2026

---

## 🎯 Overview

Co-Buddy is the execution and learning agent in the Twin Agent System. It integrates seamlessly with:
- **Aegis**: Testing and validation agent (port 8000)
- **Giffy**: Memory and knowledge agent (port 8001)
- **Co-Buddy**: Learning and execution agent (port 8002)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/ash/Desktop/Co-buddy- Windsurf/cobuddy_agi_updated
pip3 install -r requirements.txt
```

### 2. Start All Services

```bash
# Terminal 1: Start Giffy (Memory Agent)
cd /home/ash/Desktop/twin\ agent\ system/Giffy
python3 main.py --port 8001

# Terminal 2: Start Aegis (Testing Agent)
cd /home/ash/Desktop/twin\ agent\ system/Aegis
python3 agent_server.py --port 8000

# Terminal 3: Start Co-Buddy (Execution Agent)
cd /home/ash/Desktop/Co-buddy- Windsurf/cobuddy_agi_updated
python3 server/cobuddy_lightweight.py --port 8002
```

### 3. Access the Interface

Open your browser and navigate to:
```
http://localhost:8002
```

---

## 🔌 Plugin Integration

### Adding Twin Agents as Plugins

In the **Plugins** tab:

1. **Add Aegis Agent**
   - Name: `Aegis (Testing Agent)`
   - URL: `http://localhost:8000`
   - Type: `Agent`

2. **Add Giffy Agent**
   - Name: `Giffy (Memory Agent)`
   - URL: `http://localhost:8001`
   - Type: `Memory`

### API Endpoints

#### Aegis (Testing Agent)
```
GET  /health                    - Health check
POST /test/execute              - Execute test
GET  /test/status/{test_id}     - Get test status
POST /test/feedback             - Provide feedback
```

#### Giffy (Memory Agent)
```
GET  /health                    - Health check
POST /memory/add                - Add memory
GET  /memory/search             - Search memories
POST /memory/update/{id}        - Update memory
POST /ingestion/url             - Ingest from URL
GET  /stats                     - Get statistics
```

#### Co-Buddy (Execution Agent)
```
GET  /health                    - Health check
POST /skills/create             - Create skill
GET  /skills/{skill_id}         - Get skill
POST /learn/url                 - Learn from URL
POST /learn/text                - Learn from text
POST /learn/file                - Learn from file
POST /execute/skill             - Execute skill
POST /feedback                  - Provide feedback
GET  /search/memories           - Search memories
WS   /ws/interact               - WebSocket interaction
```

---

## 📚 Training Data Management

### Training Methods

#### 1. From URL
```javascript
POST /learn/url
{
    "skill_name": "Portfolio Rebalancing",
    "content": "https://example.com/portfolio-guide",
    "tags": ["finance", "portfolio", "trading"]
}
```

#### 2. From Text
```javascript
POST /learn/text
{
    "skill_name": "Email Management",
    "content": "Step 1: Open email client...",
    "tags": ["email", "productivity"]
}
```

#### 3. From File
```javascript
POST /learn/file
{
    "skill_name": "Document Processing",
    "file": <binary file data>,
    "tags": ["documents", "processing"]
}
```

#### 4. From Demo
- Record user actions
- Store in episodic memory
- Extract procedures automatically

### Memory Storage

All training data is stored in:
- **SQLite Database**: `./cobuddy_memory.db`
- **FAISS Index**: Local L2 distance index
- **Embeddings**: Model2Vec 512-dimensional vectors

---

## 🧠 Skill Learning Pipeline

### Phase 1: Data Ingestion
```
Training Input → Parse → Clean → Chunk
```

### Phase 2: Embedding
```
Content → Model2Vec → 512d Vector → FAISS Index
```

### Phase 3: Memory Storage
```
Vector + Metadata → SQLite + FAISS
```

### Phase 4: Skill Creation
```
Memories → Pattern Extraction → Skill Definition
```

### Phase 5: Confidence Scoring
```
Training Sessions → Success Rate → Confidence Level
```

---

## ⚙️ Execution Pipeline

### Step 1: Skill Selection
```javascript
{
    "skill_id": "portfolio_rebalancing_v1",
    "user_input": "Rebalance portfolio to 60/40 stocks/bonds"
}
```

### Step 2: Plan Generation
```
Skill Steps + User Input → Execution Plan
```

### Step 3: Step Execution
```
For each step:
  - Execute action
  - Monitor result
  - Handle errors
  - Update progress
```

### Step 4: Result Reporting
```
{
    "status": "completed",
    "results": {...},
    "confidence": 0.95,
    "lessons_learned": [...]
}
```

---

## 🔄 Twin Agent Coordination

### Memory Sharing

Co-Buddy ↔ Giffy:
```
1. Co-Buddy learns skill
2. Stores in Giffy's memory
3. Retrieves for execution
4. Updates confidence scores
```

### Testing & Validation

Co-Buddy ↔ Aegis:
```
1. Co-Buddy executes skill
2. Aegis tests execution
3. Provides feedback
4. Co-Buddy improves
```

### Unified Memory

All agents share:
- Skill definitions
- Training data
- Execution history
- Performance metrics

---

## 🎓 AGI Skills Integration

The AGI_SKILLS.md document is automatically injected into all agents' memory on startup.

### Skill Levels

1. **Observation** (Confidence: 20%)
   - User demonstrates
   - Co-Buddy records

2. **Guided** (Confidence: 40%)
   - Co-Buddy attempts with guidance
   - User provides corrections

3. **Supervised** (Confidence: 60%)
   - Co-Buddy executes with user watching
   - User intervenes if needed

4. **Autonomous** (Confidence: 80%)
   - Co-Buddy executes independently
   - Reports progress

5. **Mastery** (Confidence: 95%+)
   - Co-Buddy optimizes execution
   - Teaches other agents

---

## 🧪 Testing & Validation

### End-to-End Test

```bash
python3 test_cobuddy_e2e.py
```

### Test Scenarios

1. **Plugin Connection**
   - Connect to Aegis
   - Connect to Giffy
   - Verify communication

2. **Training Pipeline**
   - Learn from URL
   - Learn from text
   - Learn from file
   - Verify memory storage

3. **Execution Pipeline**
   - Create skill
   - Execute skill
   - Provide feedback
   - Verify improvement

4. **Memory Operations**
   - Search memories
   - Update memories
   - Export memories
   - Import memories

5. **Real-time Interaction**
   - WebSocket connection
   - Message exchange
   - Command execution
   - Result retrieval

---

## 📊 Monitoring & Metrics

### System Health

```
GET /health
{
    "status": "active",
    "timestamp": "2026-03-17T18:30:00Z",
    "system": "Co-Buddy AGI",
    "version": "1.0.0"
}
```

### Performance Metrics

```
GET /stats
{
    "embedding_model": "minishlab/M2V_base_output",
    "embedding_dim": 512,
    "memory_db": "./cobuddy_memory.db",
    "skills_learned": 5,
    "avg_confidence": 0.78,
    "total_executions": 12
}
```

---

## 🔐 Security Considerations

### Local Operations
- All processing happens locally
- No external API calls for core functions
- Data stored in local SQLite

### Access Control
- WebSocket authentication ready
- API key support available
- CORS configured for development

### Data Privacy
- No data sent to external services
- Local embeddings only
- Encrypted storage available

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8002

# Kill process
kill -9 <PID>
```

### Model Loading Error
```bash
# Clear cache and reload
rm -rf ~/.cache/huggingface
python3 server/cobuddy_lightweight.py
```

### Database Issues
```bash
# Reset database
rm cobuddy_memory.db
python3 server/cobuddy_lightweight.py
```

### Memory Issues
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep cobuddy'

# Reduce batch size in config
```

---

## 📈 Performance Optimization

### Embedding Caching
```python
# Cache embeddings to avoid recomputation
embedding_cache = {}
```

### Batch Processing
```python
# Process multiple items at once
embeddings = model.encode(texts, batch_size=32)
```

### Index Optimization
```python
# Use GPU acceleration if available
index = faiss.index_factory(512, "IVF100,Flat")
```

---

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server/ ./server/
COPY client/ ./client/

EXPOSE 8002

CMD ["python3", "server/cobuddy_lightweight.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  giffy:
    build: ../Giffy
    ports:
      - "8001:8001"
  
  aegis:
    build: ../Aegis
    ports:
      - "8000:8000"
  
  cobuddy:
    build: .
    ports:
      - "8002:8002"
    depends_on:
      - giffy
      - aegis
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cobuddy-agi
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cobuddy-agi
  template:
    metadata:
      labels:
        app: cobuddy-agi
    spec:
      containers:
      - name: cobuddy
        image: cobuddy-agi:1.0.0
        ports:
        - containerPort: 8002
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

---

## 📚 API Examples

### Create a Skill

```bash
curl -X POST http://localhost:8002/skills/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Portfolio Rebalancing",
    "description": "Rebalance investment portfolio",
    "steps": [
      {"action": "analyze", "description": "Analyze current allocation"},
      {"action": "calculate", "description": "Calculate drift"},
      {"action": "execute", "description": "Execute trades"}
    ]
  }'
```

### Learn from URL

```bash
curl -X POST http://localhost:8002/learn/url \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "Portfolio Rebalancing",
    "content": "https://example.com/guide",
    "tags": ["finance", "portfolio"]
  }'
```

### Execute Skill

```bash
curl -X POST http://localhost:8002/execute/skill \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "portfolio_rebalancing_v1",
    "user_input": "Rebalance to 60/40",
    "watch_mode": true
  }'
```

### Search Memories

```bash
curl -X GET "http://localhost:8002/search/memories?query=portfolio&limit=10"
```

---

## 🎯 Next Steps

1. **Start Services**: Launch all three agents
2. **Connect Plugins**: Add Aegis and Giffy as plugins
3. **Train Skills**: Use training panel to teach Co-Buddy
4. **Execute Tasks**: Run autonomous executions
5. **Monitor Performance**: Track metrics and improvements
6. **Iterate**: Provide feedback and improve skills

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f logs/cobuddy.log`
2. Review documentation: See AGI_SKILLS.md
3. Run tests: `python3 test_cobuddy_e2e.py`
4. Check health: `curl http://localhost:8002/health`

---

**Co-Buddy AGI System is ready for production deployment!**
