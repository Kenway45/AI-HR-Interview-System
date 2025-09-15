import re
from typing import List, Set
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Predefined skill databases
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#', 'php', 'ruby',
    'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express', 'nodejs',
    'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'opencv', 'docker', 'kubernetes',
    'aws', 'azure', 'gcp', 'terraform', 'ansible', 'jenkins', 'git', 'github', 'gitlab',
    
    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
    
    # Technologies
    'microservices', 'api', 'rest', 'graphql', 'websockets', 'grpc', 'oauth', 'jwt',
    'blockchain', 'machine-learning', 'artificial-intelligence', 'deep-learning',
    'data-science', 'big-data', 'etl', 'data-warehousing', 'business-intelligence'
}

SOFT_SKILLS = {
    'leadership', 'communication', 'teamwork', 'problem-solving', 'analytical-thinking',
    'creativity', 'adaptability', 'time-management', 'project-management', 'collaboration',
    'mentoring', 'coaching', 'negotiation', 'presentation', 'public-speaking',
    'conflict-resolution', 'decision-making', 'critical-thinking', 'innovation'
}

JOB_TITLES = {
    'software-engineer', 'senior-software-engineer', 'staff-engineer', 'principal-engineer',
    'tech-lead', 'engineering-manager', 'product-manager', 'data-scientist', 'data-engineer',
    'devops-engineer', 'site-reliability-engineer', 'security-engineer', 'mobile-developer',
    'frontend-developer', 'backend-developer', 'fullstack-developer', 'architect',
    'consultant', 'analyst', 'researcher', 'designer', 'ui-designer', 'ux-designer'
}

def extract_skills(text: str, context: str = "general") -> List[str]:
    """
    Extract skills from text using pattern matching and NLP
    
    Args:
        text: Input text (JD or resume)
        context: "job_description" or "resume" for context-aware extraction
    
    Returns:
        List of extracted skills
    """
    
    if not text or not text.strip():
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    # Extract technical skills
    for skill in TECHNICAL_SKILLS:
        # Match whole words and common variations
        patterns = [
            rf'\b{re.escape(skill)}\b',
            rf'\b{re.escape(skill.replace("-", " "))}\b',
            rf'\b{re.escape(skill.replace("-", ""))}\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found_skills.add(skill)
                break
    
    # Extract soft skills (more selective for resumes)
    for skill in SOFT_SKILLS:
        patterns = [
            rf'\b{re.escape(skill)}\b',
            rf'\b{re.escape(skill.replace("-", " "))}\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found_skills.add(skill)
                break
    
    # Extract years of experience patterns
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'experience.*?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in'
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            years = int(match) if match.isdigit() else 0
            if years > 0:
                found_skills.add(f"{years}-years-experience")
    
    # Extract education levels
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'mba', 'ms', 'bs', 'ba', 'ma',
        'computer science', 'software engineering', 'data science', 'mathematics',
        'electrical engineering', 'information technology'
    ]
    
    for keyword in education_keywords:
        if keyword in text_lower:
            found_skills.add(keyword.replace(" ", "-"))
    
    # Extract certifications
    cert_patterns = [
        r'aws\s+certified',
        r'azure\s+certified',
        r'google\s+cloud\s+certified',
        r'certified\s+\w+',
        r'pmp\s+certified',
        r'scrum\s+master'
    ]
    
    for pattern in cert_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            found_skills.add(match.replace(" ", "-"))
    
    return list(found_skills)

def summarize_text(text: str, max_length: int = 500) -> str:
    """
    Summarize text using extractive summarization
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary
    
    Returns:
        Summarized text
    """
    
    if not text or not text.strip():
        return ""
    
    # If text is already short, return as-is
    if len(text) <= max_length:
        return text.strip()
    
    try:
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) <= 3:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Simple extractive summarization
        # Score sentences based on word frequency and position
        
        # Tokenize and clean words
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        
        # Filter and lemmatize words
        filtered_words = []
        for word in words:
            if (word.isalnum() and 
                word not in stop_words and 
                len(word) > 2):
                filtered_words.append(lemmatizer.lemmatize(word))
        
        # Calculate word frequencies
        word_freq = Counter(filtered_words)
        
        # Score sentences
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            sentence_words = word_tokenize(sentence.lower())
            score = 0
            word_count = 0
            
            for word in sentence_words:
                if word in word_freq:
                    score += word_freq[word]
                    word_count += 1
            
            # Normalize by sentence length and add position bonus
            if word_count > 0:
                normalized_score = score / word_count
                # Boost first and last sentences slightly
                if i == 0 or i == len(sentences) - 1:
                    normalized_score *= 1.1
                sentence_scores.append((normalized_score, i, sentence))
        
        # Sort by score and select top sentences
        sentence_scores.sort(reverse=True)
        
        # Select sentences that fit within max_length
        selected_sentences = []
        current_length = 0
        
        # Sort selected by original order
        for score, orig_idx, sentence in sentence_scores:
            if current_length + len(sentence) <= max_length:
                selected_sentences.append((orig_idx, sentence))
                current_length += len(sentence)
            
            if current_length >= max_length * 0.9:  # 90% of max length
                break
        
        # Sort by original order and join
        selected_sentences.sort(key=lambda x: x[0])
        summary = " ".join([sentence for _, sentence in selected_sentences])
        
        return summary if summary else text[:max_length] + "..."
    
    except Exception as e:
        # Fallback to simple truncation
        print(f"Summarization error: {e}")
        return text[:max_length] + "..." if len(text) > max_length else text

def extract_contact_info(text: str) -> dict:
    """Extract contact information from resume text"""
    
    contact_info = {
        'email': None,
        'phone': None,
        'linkedin': None,
        'github': None
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]
    
    # Phone pattern
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
        r'\+\d{1,3}\s*\d{3,4}[-.]?\d{3,4}[-.]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
            break
    
    # LinkedIn pattern
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_matches:
        contact_info['linkedin'] = linkedin_matches[0]
    
    # GitHub pattern
    github_pattern = r'github\.com/[\w-]+'
    github_matches = re.findall(github_pattern, text, re.IGNORECASE)
    if github_matches:
        contact_info['github'] = github_matches[0]
    
    return contact_info

def calculate_skill_match(jd_skills: List[str], resume_skills: List[str]) -> dict:
    """Calculate skill matching score between JD and resume"""
    
    jd_set = set(skill.lower() for skill in jd_skills)
    resume_set = set(skill.lower() for skill in resume_skills)
    
    if not jd_set:
        return {"match_score": 0.0, "matched_skills": [], "missing_skills": []}
    
    matched_skills = list(jd_set.intersection(resume_set))
    missing_skills = list(jd_set - resume_set)
    
    match_score = len(matched_skills) / len(jd_set) * 100
    
    return {
        "match_score": round(match_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_jd_skills": len(jd_set),
        "total_resume_skills": len(resume_set)
    }

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', text)
    
    return text.strip()