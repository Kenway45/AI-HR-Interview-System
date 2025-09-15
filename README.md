# 🤖 AI HR Interview System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

A comprehensive, **zero-cost** AI-powered HR interview platform that conducts technical interviews, evaluates candidates, and provides detailed reports using open-source AI models.

![AI HR Interview System](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🚀 **Live Demo**

```bash
# One-command setup
git clone https://github.com/Kenway45/AI-HR-Interview-System.git
cd AI-HR-Interview-System
./start_system.sh
```

**Then visit:** `http://localhost:3000`

## ✨ **Key Features**

### 🎤 **Speech-First Interface**
- Real-time speech-to-text with OpenAI Whisper
- Natural conversation flow
- Multi-language support

### 🧠 **AI-Powered Interviewer**
- Context-aware question generation
- Dynamic follow-up questions
- Skill-specific technical assessments

### 💻 **Live Coding Environment**
- Monaco Editor integration
- Real-time code execution
- AI-powered code analysis and hints
- Multiple programming languages

### 👁️ **Smart Proctoring**
- Webcam-based monitoring
- Face detection and tracking
- Suspicious activity detection

### 📊 **Comprehensive Analytics**
- Detailed performance reports
- Skill-based scoring
- Comparative analysis
- Export capabilities

## 🏗️ **Architecture**

### **Tech Stack**

| Component | Technology | Purpose |
|-----------|------------|----------|
| **Frontend** | React + Vite + MUI | User interface & interactions |
| **Backend** | FastAPI + Python | API server & business logic |
| **AI Models** | Whisper + Transformers | Speech recognition & evaluation |
| **Code Execution** | Judge0 + Docker | Sandboxed code running |
| **Database** | PostgreSQL | Data persistence |
| **Storage** | MinIO | File storage |
| **Monitoring** | Face-API.js | Proctoring system |

## 🚀 **Quick Start Options**

### Option 1: **Full AI System** (Recommended)

```bash
# Clone repository
git clone https://github.com/Kenway45/AI-HR-Interview-System.git
cd AI-HR-Interview-System

# Start complete system with all AI features
./start_system.sh
```

**Features:**
- ✅ Real AI speech-to-text
- ✅ Local LLM for evaluation
- ✅ Real code execution
- ✅ Complete interview workflow

### Option 2: **Docker Deployment**

```bash
# Full production setup
./setup_and_start.sh
```

**Features:**
- ✅ All AI models (Whisper, LLaMA)
- ✅ Judge0 code execution
- ✅ Complete infrastructure
- ⏳ Longer startup time

### Option 3: **Development Mode**

```bash
# Quick development setup
./quick_start.sh
```

**Features:**
- ✅ Fast startup
- ✅ Mock AI services
- ✅ Full UI workflow
- ✅ Perfect for testing

## 📋 **Usage Guide**

### 1. **Setup Interview**
```bash
# Upload job description and resume
curl -X POST "http://localhost:8000/upload/jd" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@job_description.pdf"
```

### 2. **Start Interview Session**
- Upload documents via web interface
- AI generates contextual questions
- Begin recorded interview

### 3. **Coding Assessment**
- Live coding environment
- Real-time AI feedback
- Code execution and testing

### 4. **Generate Report**
- Comprehensive analysis
- Scoring and recommendations
- Export options

## 🔧 **Configuration**

### Environment Setup

Create `.env` file:

```bash
# AI Configuration
STT_ENGINE=whisper          # whisper, mock
LLM_ENGINE=textgen          # textgen, mock
WHISPER_MODEL=base          # base, small, medium

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_hr_interview

# Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Services
JUDGE0_URL=http://localhost:2358
TEXTGEN_URL=http://localhost:5000
```

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| MinIO Console | 9001 | http://localhost:9001 |
| Judge0 API | 2358 | http://localhost:2358 |
| Text Generation | 5000 | http://localhost:5000 |

## 🛠️ **Development**

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main_simple:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Project Structure

```
AI-HR-Interview-System/
├── 📁 backend/              # FastAPI application
│   ├── 📁 app/
│   │   ├── 📁 api/          # API endpoints
│   │   ├── 📁 models/       # Database models
│   │   ├── 📁 utils/        # Utilities
│   │   ├── main_simple.py   # Simple backend
│   │   ├── main_ai.py       # Full AI backend
│   │   └── main_enhanced.py # Enhanced demo
│   └── requirements.txt
├── 📁 frontend/             # React application
│   ├── 📁 src/
│   │   ├── 📁 components/   # React components
│   │   ├── 📁 pages/        # Page components
│   │   └── App.jsx
│   └── package.json
├── 📁 infra/                # Infrastructure
│   ├── docker-compose.yml  # Full system
│   ├── docker-compose-simple.yml # Simple setup
│   └── 📁 scripts/
├── 📁 data/                 # Sample data
└── 📄 start_system.sh      # One-click startup
```

## 🚀 **API Reference**

### Core Endpoints

```bash
# Health check
GET /health

# File upload
POST /upload/jd
POST /upload/resume

# Session management
POST /session/create
GET /session/{id}/questions
POST /session/{id}/answer
GET /session/{id}/report

# Speech-to-text
POST /stt/transcribe

# Coding assessment
WS /ws/session/{id}/coding/{task_id}
GET /session/{id}/coding/tasks
```

### Interactive Documentation
Visit `http://localhost:8000/docs` for complete API documentation.

## 🐳 **Docker Deployment**

### Production Deployment

```bash
# Production setup
docker-compose -f infra/docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=3
```

## 📊 **Performance & Monitoring**

### System Requirements

| Mode | RAM | CPU | Storage |
|------|-----|-----|----------|
| Development | 4GB | 2 cores | 10GB |
| Production | 8GB | 4 cores | 50GB |
| Full AI | 16GB | 8 cores | 100GB |

### Health Checks

```bash
# System status
./check_status.sh

# Service health
curl http://localhost:8000/health
```

## 🧪 **Testing**

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/
```

## 🛡️ **Security**

- 🔒 CORS protection
- 🔐 Input validation
- 🏗️ Sandboxed code execution
- 📁 Secure file handling
- 👁️ Proctoring monitoring

## 🚨 **Troubleshooting**

### Common Issues

| Issue | Solution |
|-------|-----------|
| Port in use | Change ports in config |
| Memory errors | Increase Docker memory |
| AI models failing | Check internet connection |
| Audio not working | Enable browser permissions |
| Upload fails | Check file encoding |

### Debug Commands

```bash
# Stop all services
pkill -f 'uvicorn|vite'

# Clean restart
./start_system.sh

# Check logs
tail -f backend/app.log
```

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Add tests for new features
- Update documentation

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI Whisper** - Speech recognition
- **Hugging Face Transformers** - AI models
- **Judge0** - Code execution
- **Face-API.js** - Facial recognition
- **Monaco Editor** - Code editing
- **React** - Frontend framework
- **FastAPI** - Backend framework

---

<div align="center">

**🚀 Ready to revolutionize your HR interview process?**

[Get Started](./start_system.sh) • [Documentation](http://localhost:8000/docs) • [Issues](https://github.com/Kenway45/AI-HR-Interview-System/issues)

</div>
