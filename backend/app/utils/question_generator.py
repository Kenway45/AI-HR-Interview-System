from typing import List, Dict, Any
import json
import random
import os

# Import the appropriate LLM client based on configuration
LLM_ENGINE = os.getenv("LLM_ENGINE", "textgen")

if LLM_ENGINE == "mock":
    from ..api.llm_mock import mock_generate_interview_questions
    llm_client = None
else:
    from ..api.llm import llm_client

# Predefined question templates for fallback
BEHAVIORAL_QUESTIONS = [
    {
        "question": "Tell me about your background and what interests you about this role.",
        "type": "behavioral",
        "skills": ["communication", "motivation"],
        "difficulty": "easy"
    },
    {
        "question": "Describe a challenging project you worked on recently. What was your role and how did you overcome obstacles?",
        "type": "behavioral", 
        "skills": ["problem-solving", "leadership", "technical"],
        "difficulty": "medium"
    },
    {
        "question": "Tell me about a time when you had to work with a difficult team member. How did you handle the situation?",
        "type": "behavioral",
        "skills": ["communication", "conflict-resolution", "teamwork"],
        "difficulty": "medium"
    },
    {
        "question": "Describe a situation where you had to learn a new technology or skill quickly. How did you approach it?",
        "type": "behavioral",
        "skills": ["adaptability", "learning", "self-motivation"],
        "difficulty": "medium"
    }
]

TECHNICAL_QUESTIONS = [
    {
        "question": "How would you design a system to handle high traffic and ensure scalability?",
        "type": "technical",
        "skills": ["system-design", "scalability", "architecture"],
        "difficulty": "hard"
    },
    {
        "question": "Explain the differences between SQL and NoSQL databases. When would you use each?",
        "type": "technical",
        "skills": ["databases", "sql", "nosql"],
        "difficulty": "medium"
    },
    {
        "question": "What are the key principles of RESTful API design?",
        "type": "technical",
        "skills": ["api-design", "rest", "web-services"],
        "difficulty": "medium"
    },
    {
        "question": "How do you ensure code quality and maintainability in your projects?",
        "type": "technical",
        "skills": ["code-quality", "testing", "documentation"],
        "difficulty": "medium"
    }
]

SITUATIONAL_QUESTIONS = [
    {
        "question": "How do you handle working under tight deadlines with competing priorities?",
        "type": "situational",
        "skills": ["time-management", "prioritization", "stress-handling"],
        "difficulty": "medium"
    },
    {
        "question": "If you disagreed with a technical decision made by your manager, how would you handle it?",
        "type": "situational",
        "skills": ["communication", "diplomacy", "technical-judgment"],
        "difficulty": "hard"
    }
]

# Coding task templates
CODING_TASKS_TEMPLATES = {
    "easy": [
        {
            "title": "Array Sum",
            "description": "Write a function that takes an array of integers and returns the sum of all elements.",
            "language": "python",
            "starter_code": "def array_sum(arr):\n    # Your code here\n    pass",
            "test_cases": [
                {"input": "[1, 2, 3, 4, 5]", "expected_output": "15"},
                {"input": "[10, -5, 3]", "expected_output": "8"},
                {"input": "[]", "expected_output": "0"}
            ]
        },
        {
            "title": "String Reversal",
            "description": "Write a function that reverses a string without using built-in reverse functions.",
            "language": "python",
            "starter_code": "def reverse_string(s):\n    # Your code here\n    pass",
            "test_cases": [
                {"input": "hello", "expected_output": "olleh"},
                {"input": "world", "expected_output": "dlrow"},
                {"input": "", "expected_output": ""}
            ]
        }
    ],
    "medium": [
        {
            "title": "Two Sum",
            "description": "Given an array of integers and a target sum, return indices of two numbers that add up to the target.",
            "language": "python",
            "starter_code": "def two_sum(nums, target):\n    # Your code here\n    # Return a list of two indices\n    pass",
            "test_cases": [
                {"input": "[2, 7, 11, 15], 9", "expected_output": "[0, 1]"},
                {"input": "[3, 2, 4], 6", "expected_output": "[1, 2]"},
                {"input": "[3, 3], 6", "expected_output": "[0, 1]"}
            ]
        },
        {
            "title": "Valid Parentheses",
            "description": "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
            "language": "python",
            "starter_code": "def is_valid(s):\n    # Your code here\n    # Return True if valid, False otherwise\n    pass",
            "test_cases": [
                {"input": "()", "expected_output": "True"},
                {"input": "()[]{}", "expected_output": "True"},
                {"input": "(]", "expected_output": "False"},
                {"input": "([)]", "expected_output": "False"}
            ]
        }
    ],
    "hard": [
        {
            "title": "Longest Palindromic Substring",
            "description": "Given a string, find the longest palindromic substring.",
            "language": "python",
            "starter_code": "def longest_palindrome(s):\n    # Your code here\n    # Return the longest palindromic substring\n    pass",
            "test_cases": [
                {"input": "babad", "expected_output": "bab"},
                {"input": "cbbd", "expected_output": "bb"},
                {"input": "a", "expected_output": "a"}
            ]
        }
    ]
}

async def generate_interview_questions(jd_summary: str, resume_summary: str) -> List[Dict[str, Any]]:
    """Generate interview questions using LLM, with fallback to templates"""
    
    # Use mock service if configured
    if LLM_ENGINE == "mock":
        return await mock_generate_interview_questions(jd_summary, resume_summary)
    
    try:
        # Create prompt for LLM
        prompt = f"""You are an expert HR interviewer. Generate exactly 8 comprehensive interview questions based on the job description and candidate's resume.

Job Description Summary:
{jd_summary}

Resume Summary:
{resume_summary}

Generate questions covering:
- 3 behavioral questions (tell me about a time...)
- 3 technical/role-specific questions
- 2 situational questions (how would you handle...)

For each question, identify the key skills being evaluated.

Respond ONLY with a JSON array in this exact format:
[
  {{
    "question": "Tell me about a time when you had to solve a complex technical problem.",
    "type": "behavioral",
    "skills": ["problem-solving", "technical-skills", "analytical-thinking"],
    "difficulty": "medium"
  }},
  {{
    "question": "How would you approach designing a scalable system for...",
    "type": "technical", 
    "skills": ["system-design", "scalability", "architecture"],
    "difficulty": "hard"
  }}
]

JSON:"""

        # Generate using LLM
        response = await llm_client.generate(prompt, max_tokens=800, temperature=0.8)
        
        # Extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            questions = json.loads(json_str)
            
            # Validate questions
            if len(questions) >= 6 and all(
                isinstance(q, dict) and 
                'question' in q and 
                'type' in q and 
                'skills' in q
                for q in questions
            ):
                return questions
        
    except Exception as e:
        print(f"Error generating questions with LLM: {e}")
    
    # Fallback to predefined questions
    return generate_fallback_questions(jd_summary, resume_summary)

def generate_fallback_questions(jd_summary: str, resume_summary: str) -> List[Dict[str, Any]]:
    """Generate fallback questions using templates and context"""
    
    questions = []
    
    # Add behavioral questions
    behavioral = random.sample(BEHAVIORAL_QUESTIONS, min(3, len(BEHAVIORAL_QUESTIONS)))
    questions.extend(behavioral)
    
    # Add technical questions 
    technical = random.sample(TECHNICAL_QUESTIONS, min(3, len(TECHNICAL_QUESTIONS)))
    questions.extend(technical)
    
    # Add situational questions
    situational = random.sample(SITUATIONAL_QUESTIONS, min(2, len(SITUATIONAL_QUESTIONS)))
    questions.extend(situational)
    
    # Customize questions based on context
    for question in questions:
        if "role" in question["question"] and jd_summary:
            # Try to extract role from JD
            role_keywords = ["engineer", "developer", "manager", "analyst", "designer"]
            for keyword in role_keywords:
                if keyword in jd_summary.lower():
                    question["question"] = question["question"].replace("this role", f"a {keyword} role")
                    break
    
    return questions

async def generate_coding_tasks(jd_summary: str, difficulty: str = "medium") -> List[Dict[str, Any]]:
    """Generate coding tasks using LLM, with fallback to templates"""
    
    try:
        # Analyze JD for technical requirements
        tech_context = extract_technical_context(jd_summary)
        
        prompt = f"""You are a technical interviewer. Generate 2 coding problems suitable for a candidate based on the job requirements.

Job Requirements:
{jd_summary}

Technical Context: {tech_context}
Difficulty Level: {difficulty}

Generate coding problems that test relevant skills. Each problem should include:
- Clear problem description
- Example input/output
- Test cases with expected outputs
- Starter code template

Respond ONLY with a JSON array:
[
  {{
    "title": "Problem Name",
    "description": "Clear problem description with examples",
    "language": "python",
    "starter_code": "def solution():\\n    # Your code here\\n    pass",
    "test_cases": [
      {{"input": "example input", "expected_output": "expected result"}},
      {{"input": "test case 2", "expected_output": "result 2"}}
    ]
  }}
]

JSON:"""

        response = await llm_client.generate(prompt, max_tokens=600, temperature=0.7)
        
        # Extract and validate JSON
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            tasks = json.loads(json_str)
            
            if len(tasks) >= 1 and all(
                isinstance(task, dict) and
                'title' in task and
                'description' in task and
                'test_cases' in task
                for task in tasks
            ):
                return tasks
        
    except Exception as e:
        print(f"Error generating coding tasks with LLM: {e}")
    
    # Fallback to templates
    return generate_fallback_coding_tasks(difficulty)

def generate_fallback_coding_tasks(difficulty: str) -> List[Dict[str, Any]]:
    """Generate fallback coding tasks from templates"""
    
    available_tasks = CODING_TASKS_TEMPLATES.get(difficulty, CODING_TASKS_TEMPLATES["medium"])
    
    # Select 1-2 random tasks
    num_tasks = min(2, len(available_tasks))
    selected_tasks = random.sample(available_tasks, num_tasks)
    
    return selected_tasks

def extract_technical_context(jd_summary: str) -> str:
    """Extract technical context from job description"""
    
    if not jd_summary:
        return "general software development"
    
    jd_lower = jd_summary.lower()
    
    contexts = []
    
    # Programming languages
    languages = ["python", "java", "javascript", "go", "rust", "c++"]
    for lang in languages:
        if lang in jd_lower:
            contexts.append(f"{lang} development")
    
    # Domains
    domains = {
        "web": ["web", "frontend", "backend", "api"],
        "data": ["data", "analytics", "machine learning", "ai"],
        "mobile": ["mobile", "ios", "android", "app"],
        "devops": ["devops", "infrastructure", "cloud", "kubernetes"],
        "security": ["security", "cybersecurity", "authentication"]
    }
    
    for domain, keywords in domains.items():
        if any(keyword in jd_lower for keyword in keywords):
            contexts.append(f"{domain} development")
    
    return ", ".join(contexts) if contexts else "general software development"

def customize_question_for_role(question: str, role_type: str) -> str:
    """Customize question based on role type"""
    
    role_customizations = {
        "senior": "As a senior developer, ",
        "lead": "As a technical lead, ",
        "manager": "As a manager, ",
        "junior": "As someone starting their career, "
    }
    
    for role, prefix in role_customizations.items():
        if role in role_type.lower():
            return prefix + question.lower()
    
    return question