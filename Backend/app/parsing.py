import os
import re
import json
import logging
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'present']
    if isinstance(value, (int, float)):
        return bool(value)
    return False

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".txt":
            return Path(file_path).read_text(encoding="utf-8")
        elif ext == ".docx":
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == ".pdf":
            import PyPDF2
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        else:
            logger.warning(f"Unsupported file type: {ext} for file {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return None

def preprocess_resume_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-\.\,\:\;\@\(\)\[\]\{\}\+\=\&\|\/\?\!]', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r' +', ' ', text)
    if len(text) > 8000:
        text = text[:8000] + "..."
    return text.strip()

def clean_json_response(content: str) -> str:
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    start_idx = None
    stack = []
    largest_json = ''
    max_len = 0
    for i, c in enumerate(content):
        if c == '{':
            if not stack:
                start_idx = i
            stack.append(c)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidate = content[start_idx:i+1]
                    if len(candidate) > max_len:
                        largest_json = candidate
                        max_len = len(candidate)
    if largest_json:
        return largest_json
    return content

def clean_resume_json(resume_json):
    achievements = resume_json.get("Achievements", [])
    if isinstance(achievements, list):
        resume_json["Achievements"] = [str(a) for a in achievements if isinstance(a, (str, int, float))]
    else:
        resume_json["Achievements"] = []

    education = resume_json.get("Education", [])
    if not isinstance(education, list):
        resume_json["Education"] = []
    else:
        resume_json["Education"] = [e for e in education if isinstance(e, dict)]

    experiences = resume_json.get("Experiences", [])
    if not isinstance(experiences, list):
        resume_json["Experiences"] = []
    else:
        for exp in experiences:
            if isinstance(exp, dict):
                desc = exp.get("description", [])
                if isinstance(desc, list):
                    exp["description"] = [str(d) for d in desc if isinstance(d, (str, int, float))]
                else:
                    exp["description"] = []
                techs = exp.get("technologiesUsed", [])
                if isinstance(techs, list):
                    exp["technologiesUsed"] = [str(t) for t in techs if isinstance(t, (str, int, float))]
                else:
                    exp["technologiesUsed"] = []
        resume_json["Experiences"] = [e for e in experiences if isinstance(e, dict)]

    projects = resume_json.get("Projects", [])
    if not isinstance(projects, list):
        resume_json["Projects"] = []
    else:
        for proj in projects:
            if isinstance(proj, dict):
                techs = proj.get("technologiesUsed", [])
                if isinstance(techs, list):
                    proj["technologiesUsed"] = [str(t) for t in techs if isinstance(t, (str, int, float))]
                else:
                    proj["technologiesUsed"] = []
        resume_json["Projects"] = [p for p in projects if isinstance(p, dict)]

    skills = resume_json.get("Skills", [])
    if not isinstance(skills, list):
        resume_json["Skills"] = []
    else:
        # Filter out skills that are not dicts or are missing a truthy 'skillName'
        resume_json["Skills"] = [s for s in skills if isinstance(s, dict) and s.get("skillName")]

    research = resume_json.get("Research Work", [])
    if not isinstance(research, list):
        resume_json["Research Work"] = []
    else:
        resume_json["Research Work"] = [r for r in research if isinstance(r, dict)]

    analytics = resume_json.get("Analytics", {})
    if not isinstance(analytics, dict):
        resume_json["Analytics"] = {}
    else:
        ka = analytics.get("keyword_analysis", {})
        if not isinstance(ka, dict):
            analytics["keyword_analysis"] = {}
        else:
            ek = ka.get("extracted_keywords", [])
            if isinstance(ek, list):
                ka["extracted_keywords"] = [str(e) for e in ek if isinstance(e, (str, int, float))]
            else:
                ka["extracted_keywords"] = []
            analytics["keyword_analysis"] = ka
        resume_json["Analytics"] = analytics

    pd = resume_json.get("Personal Data", {})
    if isinstance(pd, dict):
        loc = pd.get("location", {})
        if not isinstance(loc, dict):
            pd["location"] = {}
        resume_json["Personal Data"] = pd
    else:
        resume_json["Personal Data"] = {"location": {}}

    # Clean skill_presence to ensure it's a dictionary with boolean values
    skill_presence = resume_json.get("skill_presence", {})
    if isinstance(skill_presence, dict):
        cleaned_skill_presence = {}
        for skill, value in skill_presence.items():
            if isinstance(skill, str):
                cleaned_skill_presence[skill] = to_bool(value)
        resume_json["skill_presence"] = cleaned_skill_presence
    else:
        resume_json["skill_presence"] = {}

    return resume_json