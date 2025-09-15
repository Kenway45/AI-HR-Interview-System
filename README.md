# 🎤 CodeVox

> **"Voice-first interviews. Live coding. Honest scores."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Open Source](https://img.shields.io/badge/Open%20Source-❤️-brightgreen)](https://github.com/Kenway45/AI-HR-Interview-System)
[![Self Hosted](https://img.shields.io/badge/Self%20Hosted-🏠-blue)](https://github.com/Kenway45/AI-HR-Interview-System)

CodeVox is an **open-source, self-hosted AI HR interview practice system**: a speech-first interview agent that asks spoken questions, runs proctored sessions (camera + screen events), includes live coding problems in an embedded IDE, auto-judges code in a secure sandbox, and returns a detailed scorecard and feedback so you can **assess and improve before real interviews**.

![CodeVox System](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🚀 **Get Started with CodeVox**

```bash
# One-command setup
git clone https://github.com/Kenway45/AI-HR-Interview-System.git
cd AI-HR-Interview-System
./start_codevox.sh
```

**Then visit:** `http://localhost:3000` and start practicing!

---

## 🏆 **Why CodeVox?**

💯 **Practice makes perfect** — but most people go into technical interviews unprepared. CodeVox gives you a realistic, AI-powered interview environment where you can:

- 🎤 **Practice speaking** your solutions out loud (just like real interviews)
- 💻 **Code in real-time** with an embedded IDE and instant feedback
- 📊 **Get honest scores** and detailed feedback on your performance
- 🔒 **Stay private** — everything runs locally on your machine
- 🆓 **Zero cost** — completely open-source with no subscriptions

## ✨ **What Makes CodeVox Special**

### 🎤 **Voice-First Interview Practice**
- **Talk through your solutions** — practice explaining your thought process
- **Real-time speech-to-text** with OpenAI Whisper — no typing required
- **Natural conversation flow** — just like talking to a real interviewer
- **Multi-language support** — practice in your preferred language

### 🧠 **Intelligent Interview Agent**
- **Adaptive questioning** — asks follow-ups based on your answers
- **Role-specific scenarios** — tailored to your target job
- **Dynamic difficulty** — adjusts based on your skill level
- **Behavioral + technical** — complete interview practice

### 💻 **Embedded Live Coding IDE**
- **Monaco Editor** — the same editor used in VS Code
- **Instant code execution** — run and test your solutions in real-time
- **Multiple languages** — Python, JavaScript, Java, C++, and more
- **AI code analysis** — get hints and optimization suggestions

### 👁️ **Realistic Interview Simulation**
- **Webcam monitoring** — practice being on camera
- **Screen activity tracking** — simulates real proctored interviews
- **Attention detection** — stay focused like in real interviews
- **Integrity monitoring** — honest practice for honest improvement

### 📊 **Honest Feedback & Scoring**
- **Detailed scorecards** — know exactly where you stand
- **Improvement suggestions** — specific areas to work on
- **Progress tracking** — see your improvement over time
- **Export reports** — share your progress with mentors

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

## 🚀 **Setup Options**

### 🏆 **Ready to Practice** (Recommended)

```bash
# Clone and start practicing immediately
git clone https://github.com/Kenway45/AI-HR-Interview-System.git
cd AI-HR-Interview-System
./start_codevox.sh
```

**Perfect for:**
- ✅ **Interview preparation** — full AI-powered practice sessions
- ✅ **Voice practice** — real speech-to-text with Whisper
- ✅ **Live coding** — embedded IDE with code execution
- ✅ **Honest feedback** — detailed scoring and improvement areas

### 🐳 **Full Production Setup**

```bash
# Complete infrastructure with all services
./setup_production.sh
```

**Features:**
- ✅ **Enterprise-grade** — all AI models (Whisper, LLaMA)
- ✅ **Scalable** — microservices architecture
- ✅ **Secure** — sandboxed code execution
- ⏳ **Longer setup** — downloads AI models (~15 minutes)

### ⚡ **Quick Demo Mode**

```bash
# Fast startup for exploration
./quick_demo.sh
```

**Great for:**
- ✅ **Trying CodeVox** — mock AI for instant startup
- ✅ **UI exploration** — see all features without AI setup
- ✅ **Development** — modify and test changes quickly
- ✅ **Low resource** — works on any machine

## 📈 **How to Practice with CodeVox**

### 1. 📄 **Prepare Your Practice Session**
- **Upload target job description** — CodeVox tailors questions to the role
- **Upload your resume** — questions focus on your experience
- **Select interview type** — behavioral, technical, or full interview

### 2. 🎤 **Start Voice Interview**
- **Grant microphone access** — practice speaking your answers
- **Answer questions aloud** — AI transcribes in real-time
- **Get follow-up questions** — just like a real interviewer

### 3. 💻 **Live Coding Practice**
- **Solve coding problems** in the embedded Monaco IDE
- **Explain your approach** — talk through your solution
- **Run and test code** — instant feedback on correctness
- **Get AI hints** — when you're stuck (optional)

### 4. 📊 **Review Your Performance**
- **Detailed scorecard** — technical skills, communication, problem-solving
- **Specific feedback** — areas for improvement with examples
- **Progress tracking** — see improvement over multiple sessions
- **Export report** — share with mentors or keep for reference

### 5. 🔁 **Practice Again & Improve**
- **Retake interviews** — practice makes perfect
- **Try different roles** — upload different job descriptions
- **Focus on weak areas** — target specific skills for improvement

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

### CodeVox Project Structure

```
CodeVox/
├── 🎤 codevox-backend/        # FastAPI interview engine
│   ├── 📁 app/
│   │   ├── 🎤 speech/        # Voice processing
│   │   ├── 🧠 ai/            # Interview AI logic
│   │   ├── 💻 coding/        # Code execution
│   │   ├── 📊 scoring/       # Feedback engine
│   │   └── 👁️ proctoring/    # Monitoring
│   └── requirements.txt
├── 🗺️ codevox-frontend/       # React practice interface
│   ├── 📁 src/
│   │   ├── 🎤 VoiceInterview/  # Speech components
│   │   ├── 💻 LiveCoding/     # IDE components
│   │   ├── 📊 Scorecard/      # Results display
│   │   └── 👁️ ProctorView/     # Monitoring UI
│   └── package.json
├── 🐳 infrastructure/        # Docker & services
│   ├── docker-compose.yml      # Full AI setup
│   ├── docker-compose-demo.yml # Quick demo
│   └── 📁 scripts/
├── 📁 practice-data/           # Sample interviews
└── 🚀 start_codevox.sh        # One-click practice
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
