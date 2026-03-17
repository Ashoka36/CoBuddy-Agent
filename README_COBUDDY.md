# 🧠 Co-Buddy AGI - Universal Learning Agent

> **The Superbrain of the Century** - Learn any process, automate everything

## ✨ What is Co-Buddy AGI?

Co-Buddy AGI is a revolutionary universal learning agent that can observe any process, learn it through demonstration, and execute it autonomously. It's designed to be the ultimate AI assistant that adapts to any workflow or task.

## 🚀 Key Features

### 🎯 **Process Learning**
- **Screen Observation**: Learn any process by watching your screen
- **Step Recording**: Capture every action, click, and decision
- **Error Correction**: Learn from mistakes and improve
- **Confidence Scoring**: Know when a process is mastered

### 🤖 **Autonomous Execution**
- **Self-Running**: Execute learned processes without human intervention
- **Multi-Provider AI**: Support for OpenAI, Anthropic, Google Gemini, and NVIDIA NIM
- **API Integration**: Connect with any external service
- **Real-time Monitoring**: Track execution progress

### 🧠 **Advanced Intelligence**
- **Memory System**: Persistent learning with SQLite database
- **Multi-Modal**: Text, image, and voice processing
- **Cross-Platform**: Windows, Linux, macOS, and Android support
- **WebSocket Real-time**: Live updates and monitoring

### 🌐 **Universal API Integration**
- **OpenAI GPT-4**: Advanced reasoning and analysis
- **Anthropic Claude**: Natural language understanding
- **Google Gemini**: Multimodal capabilities
- **NVIDIA NIM**: High-performance inference

## 🛠️ Installation

### Prerequisites
- Node.js 18.19.0 or higher
- Python 3.8 or higher
- pnpm package manager

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Ashoka36/Co-Buddy.git
cd Co-Buddy

# Install Node.js dependencies
pnpm install

# Set up Python environment
python3 -m venv cobuddy_env
source cobuddy_env/bin/activate  # On Windows: cobuddy_env\\Scripts\\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file with the following:

```bash
# Application
NODE_ENV=development
PORT=8000
WEB_PORT=3000

# AI API Keys (choose one or more)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
NVIDIA_NIM_API_KEY=your_nvidia_key_here
VITE_NVIDIA_NIM_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:./cobuddy_memory.db

# Optional Features
VITE_ANALYTICS_ENDPOINT=
VITE_ANALYTICS_WEBSITE_ID=
```

## 🎮 Usage

### Start the Full System

```bash
# Start both AGI server and web interface
pnpm run start:full

# Or development mode
pnpm run dev:full
```

### Individual Components

```bash
# Start only the AGI server (Python/FastAPI)
pnpm run start:agi

# Start only the web interface (Node.js/Express)
pnpm run start
```

### Access Points

- **🌐 Web Interface**: http://localhost:3000
- **🤖 AGI Server**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🔗 Health Check**: http://localhost:8000/api/v1/health

## 🧪 Process Learning Workflow

### 1. Start a Learning Session
```bash
curl -X POST "http://localhost:8000/api/v1/learning/start" \
  -H "Content-Type: application/json" \
  -d '{"process_name": "Data Entry", "domain": "office"}'
```

### 2. Capture Screen Frames
```bash
curl -X POST "http://localhost:8000/api/v1/learning/capture" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_id", "frame_data": "base64_image_data"}'
```

### 3. Record User Actions
```bash
curl -X POST "http://localhost:8000/api/v1/learning/action" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_id", "action": {"type": "click", "element": "submit_button"}}'
```

### 4. End Learning & Get Confidence
```bash
curl -X POST "http://localhost:8000/api/v1/learning/end/session_id"
```

### 5. Go Autonomous
```bash
curl -X POST "http://localhost:8000/api/v1/learning/autonomous/session_id"
```

### 6. Execute Autonomously
```bash
curl -X POST "http://localhost:8000/api/v1/execution/autonomous/process_id"
```

## 📱 Mobile App Support

Co-Buddy includes Android support for on-the-go learning:

```bash
# Get mobile configuration
curl "http://localhost:8000/api/v1/mobile/config"

# WebSocket for real-time updates
ws://localhost:8000/ws/learning/session_id
```

## 🔧 API Endpoints

### Core System
- `GET /` - System information
- `GET /api/v1/status` - Complete system status
- `GET /api/v1/health` - Health check
- `POST /api/v1/command` - Process natural language commands

### Process Learning
- `POST /api/v1/learning/start` - Start learning session
- `POST /api/v1/learning/capture` - Capture screen frame
- `POST /api/v1/learning/action` - Record user action
- `POST /api/v1/learning/error` - Record error/correction
- `POST /api/v1/learning/end/{session_id}` - End session
- `GET /api/v1/learning/workflow/{session_id}` - Get workflow
- `POST /api/v1/learning/autonomous/{session_id}` - Enable autonomous

### Autonomous Execution
- `POST /api/v1/execution/autonomous/{process_id}` - Execute process

### Analytics
- `GET /api/v1/analytics/learning` - Learning analytics
- `GET /api/v1/analytics/processes` - All processes

### AI APIs
- `GET /api/v1/apis` - List available APIs
- `POST /api/v1/apis/{provider}/chat` - Chat with specific AI

## 🏗️ Architecture

### Core Components

1. **CobuddyAGI**: Main orchestrator class
2. **CobuddyMemory**: Persistent memory with SQLite
3. **UniversalAPIManager**: Multi-provider AI integration
4. **ProcessLearningEngine**: Learning and automation logic

### Data Flow

```
User Interface → Node.js/Express → Python/FastAPI → Co-Buddy AGI Core
                ↓                    ↓                    ↓
            Static Files        API Gateway        AI Processing
                ↓                    ↓                    ↓
            React Frontend     WebSocket          Memory System
```

## 🧠 Development

### Project Structure
```
Co-Buddy/
├── client/                 # React frontend
│   ├── src/
│   └── public/
├── server/                 # Backend systems
│   ├── cobuddy_agi_unified.py  # Main AGI system
│   ├── _core/             # Node.js integration
│   └── cobuddy_memory.py  # Memory system
├── shared/                # Shared types
├── drizzle/              # Database schemas
├── mobile/               # Android app
└── cobuddy_env/          # Python virtual environment
```

### Adding New AI Providers

1. Update `UniversalAPIManager` in `cobuddy_agi_unified.py`
2. Add API key to `.env`
3. Implement provider-specific logic

### Extending Learning Capabilities

1. Modify `ProcessLearningEngine`
2. Add new step types in learning workflow
3. Enhance confidence scoring algorithms

## 🔒 Security

- API keys stored in environment variables
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Error handling without information leakage

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker build -t cobuddy-agi .
docker run -p 8000:8000 -p 3000:3000 cobuddy-agi
```

### Render/Heroku
1. Connect repository
2. Set environment variables
3. Deploy with build command: `pnpm run build`
4. Start command: `pnpm run start:full`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- Google for Gemini models
- NVIDIA for NIM endpoints
- FastAPI for the Python web framework
- React for the frontend framework

## 📞 Support

- 📧 Email: support@cobuddy.ai
- 💬 Discord: [Join our community](https://discord.gg/cobuddy)
- 📖 Documentation: [docs.cobuddy.ai](https://docs.cobuddy.ai)

---

**🌟 Co-Buddy AGI - Your universal learning and automation companion**

*Learn any process, automate everything, transform your workflow*
