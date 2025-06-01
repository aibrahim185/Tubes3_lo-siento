import re
from typing import List, Dict

def regex_search(text: str, pattern: str, flags=re.IGNORECASE) -> List[Dict]:
    """
    Perform regex search on text
    Returns list of matches with positions and context
    """
    if not pattern or not text:
        return []
    
    try:
        matches = []
        for match in re.finditer(pattern, text, flags):
            start_pos = match.start()
            end_pos = match.end()
            matched_text = match.group()
            
            # Get context around the match
            context_start = max(0, start_pos - 50)
            context_end = min(len(text), end_pos + 50)
            context = text[context_start:context_end]
            
            matches.append({
                'position': start_pos,
                'end_position': end_pos,
                'match': matched_text,
                'context': context,
                'full_match': match
            })
        
        return matches
        
    except re.error as e:
        print(f"Regex error: {e}")
        return []

def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\(\d{3}\)\s*\d{3}-\d{4}',
        r'\d{3}-\d{3}-\d{4}',
        r'\d{3}\.\d{3}\.\d{4}'
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    return list(set(phone_numbers))  # Remove duplicates

def extract_skills_keywords(text: str, skills_list: List[str]) -> List[str]:
    """Extract programming skills and technologies from text"""
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def extract_education_info(text: str) -> List[str]:
    """Extract education-related information"""
    education_patterns = [
        r'\b(?:Bachelor|Master|PhD|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.Tech|M\.Tech)\b.*?(?:\n|\.)',
        r'\b(?:University|College|Institute)\s+of\s+\w+',
        r'\b\d{4}\s*-\s*\d{4}\b',  # Years
        r'\bGPA\s*:?\s*\d+\.?\d*'
    ]
    
    education_info = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education_info.extend(matches)
    
    return education_info
