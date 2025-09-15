from fastapi import APIRouter, HTTPException
import requests
import os
import json
from typing import Dict, Any, List
from ..models import LLMGenerationRequest, LLMEvaluationRequest

router = APIRouter()

# Configuration
TEXTGEN_URL = os.getenv("TEXTGEN_URL", "http://textgen:5000")
LLAMA_CPP_URL = os.getenv("LLAMA_CPP_URL", "http://llama-cpp:8080")
LLM_ENGINE = os.getenv("LLM_ENGINE", "textgen")  # "textgen" or "llama-cpp"

class LLMClient:
    """LLM client abstraction"""
    
    def __init__(self):
        self.engine = LLM_ENGINE
        self.base_url = TEXTGEN_URL if LLM_ENGINE == "textgen" else LLAMA_CPP_URL
    
    async def generate(self, prompt: str, max_tokens: int = 400, temperature: float = 0.7) -> str:
        """Generate text using the configured LLM"""
        
        if self.engine == "textgen":
            return await self._generate_textgen(prompt, max_tokens, temperature)
        elif self.engine == "llama-cpp":
            return await self._generate_llama_cpp(prompt, max_tokens, temperature)
        else:
            raise HTTPException(status_code=500, detail=f"Unknown LLM engine: {self.engine}")
    
    async def _generate_textgen(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using text-generation-webui API"""
        
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True,
            "top_p": 0.9,
            "typical_p": 1,
            "repetition_penalty": 1.1,
            "encoder_repetition_penalty": 1.0,
            "top_k": 40,
            "min_length": 0,
            "no_repeat_ngram_size": 0,
            "num_beams": 1,
            "penalty_alpha": 0,
            "length_penalty": 1,
            "early_stopping": False,
            "seed": -1
        }
        
        try:
            response = requests.post(
                f"{TEXTGEN_URL}/api/v1/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Text-generation-webui error: {response.text}"
                )
            
            result = response.json()
            return result.get("results", [{}])[0].get("text", "").strip()
            
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=500, detail="LLM generation timed out")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"LLM server error: {str(e)}")
    
    async def _generate_llama_cpp(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using llama.cpp server API"""
        
        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{LLAMA_CPP_URL}/completion",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Llama.cpp server error: {response.text}"
                )
            
            result = response.json()
            return result.get("content", "").strip()
            
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=500, detail="LLM generation timed out")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"LLM server error: {str(e)}")

# Global LLM client instance
llm_client = LLMClient()

async def generate_interview_questions(jd_summary: str, resume_summary: str) -> List[Dict[str, Any]]:
    """Generate interview questions based on JD and resume"""
    
    prompt = f"""You are an expert HR interviewer. Generate a comprehensive set of interview questions based on the job description and candidate's resume.

Job Description Summary:
{jd_summary}

Resume Summary:
{resume_summary}

Generate exactly 8 interview questions covering:
- 3 behavioral questions
- 3 technical/role-specific questions  
- 2 situational questions

For each question, identify skill gaps or strengths to evaluate.

Respond in this exact JSON format:
[
  {{
    "question": "Tell me about a time when...",
    "type": "behavioral",
    "skills": ["communication", "problem-solving"],
    "difficulty": "medium"
  }},
  ...
]

JSON:"""

    try:
        response = await llm_client.generate(prompt, max_tokens=600, temperature=0.8)
        
        # Extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[json_start:json_end]
        questions = json.loads(json_str)
        
        return questions
        
    except json.JSONDecodeError as e:
        # Fallback to default questions if JSON parsing fails
        return [
            {
                "question": "Tell me about your background and what interests you about this role.",
                "type": "behavioral",
                "skills": ["communication", "motivation"],
                "difficulty": "easy"
            },
            {
                "question": "Describe a challenging project you worked on recently.",
                "type": "behavioral",
                "skills": ["problem-solving", "technical"],
                "difficulty": "medium"
            },
            {
                "question": "How do you handle working under tight deadlines?",
                "type": "situational",
                "skills": ["time-management", "stress-handling"],
                "difficulty": "medium"
            }
        ]

async def evaluate_transcript(
    jd_summary: str,
    resume_summary: str,
    question: str,
    transcript: str,
    question_type: str
) -> Dict[str, Any]:
    """Evaluate candidate's answer using LLM"""
    
    prompt = f"""You are an expert HR interviewer evaluating a candidate's response. 

Job Requirements:
{jd_summary}

Candidate Background:
{resume_summary}

Question ({question_type}):
{question}

Candidate's Answer:
{transcript}

Evaluate the answer on:
1. Relevance to the question (0-10)
2. Technical accuracy (0-10) 
3. Communication clarity (0-10)
4. Depth of experience (0-10)
5. Overall impression (0-10)

Respond in this exact JSON format:
{{
  "score": 7.5,
  "feedback": "The candidate demonstrated...",
  "strengths": ["clear communication", "relevant experience"],
  "weaknesses": ["lacks technical depth", "could provide more examples"],
  "detailed_scores": {{
    "relevance": 8,
    "technical_accuracy": 7,
    "communication": 8,
    "depth": 6,
    "overall": 7
  }}
}}

JSON:"""

    try:
        response = await llm_client.generate(prompt, max_tokens=400, temperature=0.3)
        
        # Extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[json_start:json_end]
        evaluation = json.loads(json_str)
        
        return evaluation
        
    except json.JSONDecodeError as e:
        # Fallback evaluation
        return {
            "score": 5.0,
            "feedback": "Unable to parse evaluation from AI system.",
            "strengths": ["provided a response"],
            "weaknesses": ["evaluation system error"],
            "detailed_scores": {
                "relevance": 5,
                "technical_accuracy": 5,
                "communication": 5,
                "depth": 5,
                "overall": 5
            }
        }

@router.post("/generate")
async def generate_text(request: LLMGenerationRequest):
    """General text generation endpoint"""
    
    try:
        response = await llm_client.generate(
            request.prompt,
            request.max_tokens,
            request.temperature
        )
        
        return {"text": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate")
async def evaluate_answer(request: LLMEvaluationRequest):
    """Evaluate candidate answer"""
    
    try:
        evaluation = await evaluate_transcript(
            request.jd_summary,
            request.resume_summary,
            request.question,
            request.answer,
            request.question_type
        )
        
        return evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def llm_health_check():
    """Check if LLM service is available"""
    
    try:
        # Test with a simple prompt
        test_prompt = "Say 'Hello, I am working correctly.'"
        response = await llm_client.generate(test_prompt, max_tokens=20, temperature=0.1)
        
        if "working correctly" in response.lower() or "hello" in response.lower():
            return {"status": "healthy", "engine": LLM_ENGINE}
        else:
            return {"status": "degraded", "engine": LLM_ENGINE, "response": response}
            
    except Exception as e:
        return {"status": "unhealthy", "engine": LLM_ENGINE, "error": str(e)}