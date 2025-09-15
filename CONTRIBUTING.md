# Contributing to CodeVox

> **"Voice-first interviews. Live coding. Honest scores."**

We welcome contributions to CodeVox! This guide will help you contribute effectively to our open-source interview practice platform.

## 🎆 **Mission**

CodeVox helps people prepare for technical interviews through realistic, AI-powered practice sessions. Every contribution helps more people land their dream jobs!

## 🚀 **Quick Start for Contributors**

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/AI-HR-Interview-System.git
cd AI-HR-Interview-System

# 2. Start development environment
./quick_demo.sh

# 3. Make changes and test
# 4. Submit pull request
```

## 🏆 **Ways to Contribute**

### 🎤 **Voice & Speech Features**
- Improve speech recognition accuracy
- Add multi-language support
- Enhance audio quality processing
- Better noise cancellation

### 🧠 **AI Interview Engine**
- More intelligent question generation
- Better answer evaluation
- Industry-specific interview scenarios
- Difficulty adaptation algorithms

### 💻 **Live Coding Experience**
- Additional programming languages
- Better code analysis and hints
- Performance optimization suggestions
- More realistic coding challenges

### 📊 **Scoring & Feedback**
- More accurate scoring algorithms
- Detailed improvement suggestions
- Progress tracking features
- Export and sharing capabilities

### 👁️ **Interview Simulation**
- Enhanced proctoring features
- Better attention tracking
- Realistic interview environments
- Stress simulation features

## 🛠️ **Development Setup**

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Docker (optional, for full AI features)

### Setup Options

#### ⚡ **Quick Demo Setup** (Recommended for Contributors)
```bash
./quick_demo.sh  # Fast startup with mock AI
```

#### 🎤 **Full AI Setup** (For AI/ML Contributors)
```bash
./start_codevox.sh  # Real AI models
```

#### 🐳 **Production Setup** (For Infrastructure Contributors)
```bash
./setup_production.sh  # Complete Docker environment
```

### Manual Development Setup

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

Thank you for your interest in contributing to the AI HR Interview System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Environment Setup

1. **Prerequisites**
   ```bash
   - Docker and Docker Compose
   - Node.js 18+ (for frontend development)
   - Python 3.11+ (for backend development)
   - Git
   ```

2. **Local Development Setup**
   ```bash
   cd ~/Documents/ai-hr-interview
   
   # Backend development
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend development
   cd frontend
   npm install
   ```

3. **Run Services for Development**
   ```bash
   # Start only the required services for development
   cd infra
   docker-compose up -d db minio judge0-db judge0-redis judge0 textgen
   
   # Run backend in development mode
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Run frontend in development mode
   cd frontend
   npm run dev
   ```

## 📝 Code Style and Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Use meaningful variable and function names
- Maximum line length: 100 characters

```python
# Example
from typing import List, Dict, Any

async def process_interview_data(
    session_id: str,
    questions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process interview data and generate evaluation.
    
    Args:
        session_id: Unique session identifier
        questions: List of question dictionaries
    
    Returns:
        Dict containing processed evaluation results
    """
    # Implementation here
    pass
```

### JavaScript/React (Frontend)
- Use ES6+ features
- Follow React functional components with hooks
- Use TypeScript where beneficial
- Use meaningful component and variable names
- Use proper JSX formatting

```jsx
// Example
import React, { useState, useEffect } from 'react';

const InterviewQuestion = ({ question, onAnswer }) => {
  const [isRecording, setIsRecording] = useState(false);
  
  const handleStartRecording = () => {
    setIsRecording(true);
    // Implementation
  };
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{question.text}</Typography>
        <Button 
          onClick={handleStartRecording}
          disabled={isRecording}
        >
          {isRecording ? 'Recording...' : 'Start Recording'}
        </Button>
      </CardContent>
    </Card>
  );
};
```

### API Design
- Follow RESTful conventions
- Use proper HTTP status codes
- Include comprehensive error messages
- Document all endpoints with examples

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Testing
```bash
cd infra
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 📋 Pull Request Process

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-hr-interview.git
   cd ai-hr-interview
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   git checkout -b fix/bug-description
   git checkout -b docs/documentation-update
   ```

3. **Make Your Changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed
   - Ensure all tests pass

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new interview question type"
   git commit -m "fix: resolve WebSocket connection issue"
   git commit -m "docs: update API documentation"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Use conventional commits format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Build process or auxiliary tool changes

## 🏗️ Architecture Guidelines

### Backend Structure
```
backend/app/
├── api/           # API route handlers
├── models/        # Pydantic models
├── utils/         # Utility functions
├── db.py          # Database models
└── main.py        # FastAPI application
```

### Frontend Structure
```
frontend/src/
├── components/    # Reusable React components
├── pages/         # Page components
├── hooks/         # Custom React hooks
├── utils/         # Utility functions
└── App.jsx        # Main application component
```

## 🔧 Adding New Features

### New Interview Question Types
1. Update `backend/app/utils/question_generator.py`
2. Add evaluation logic in `backend/app/api/llm.py`
3. Update frontend components if needed
4. Add tests for the new question type

### New Programming Languages (Judge0)
1. Update `LANGUAGE_MAP` in `backend/app/api/judge.py`
2. Add language-specific templates in `frontend/src/pages/CodingPage.jsx`
3. Test with sample code execution

### New AI Models
1. Update model configuration in `docker-compose.yml`
2. Add model-specific API wrappers
3. Update environment variables
4. Document model setup in README

## 🐛 Bug Reports

When reporting bugs, include:
- **Environment**: OS, Docker version, browser
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

## 💡 Feature Requests

For feature requests, provide:
- **Use case**: Why is this feature needed?
- **Description**: Detailed description of the feature
- **Acceptance criteria**: How to know when it's complete
- **Mockups**: UI mockups if applicable

## 📖 Documentation

### Code Documentation
- Document all functions with docstrings
- Include type hints for Python code
- Add inline comments for complex logic
- Update README for significant changes

### API Documentation
- All endpoints documented in OpenAPI/Swagger
- Include request/response examples
- Document error responses
- Keep API documentation up to date

## 🔒 Security Considerations

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Follow secure coding practices
- Report security issues privately

## 🎯 Performance Guidelines

### Backend Performance
- Use async/await for I/O operations
- Implement proper database indexing
- Cache frequently accessed data
- Monitor API response times

### Frontend Performance
- Use React.memo for expensive components
- Implement proper component re-rendering optimization
- Minimize bundle size
- Use lazy loading where appropriate

## 📊 Code Review Checklist

### For Reviewers
- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No sensitive data in commits
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] API changes are backward compatible

### For Authors
- [ ] All tests pass locally
- [ ] Code is self-documented
- [ ] Breaking changes are documented
- [ ] Dependencies are justified
- [ ] Error handling is comprehensive

## 🆘 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussion
- **Code Review**: Tag maintainers for reviews
- **Documentation**: Check README and API docs first

## 📞 Contact

For questions about contributing:
- Create a GitHub Discussion
- Open a GitHub Issue
- Check existing documentation

Thank you for contributing to making AI-powered interviewing more accessible and effective! 🚀