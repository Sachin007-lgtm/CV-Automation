from sentence_transformers import SentenceTransformer,util
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import re
from typing import Dict, List, Any, Tuple, Optional, Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, File, Form, Body
from difflib import SequenceMatcher
import groq
import json
import os
import tempfile
import shutil
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
lemmatizer = WordNetLemmatizer()
STOPWORDS = set(stopwords.words('english'))

# Add a simple normalize_degree function for now
def normalize_degree(degree: str) -> str:
    return degree.lower().strip() if degree else ""

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')
if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY environment variable is not set. Please set it in your .env file or environment.")

client = groq.Groq(api_key=GROK_API_KEY)
model = SentenceTransformer('all-mpnet-base-v2')

CITY_VARIATIONS = {
    'gurgaon': ['gurugram', 'gurgaon'],
    'gurugram': ['gurugram', 'gurgaon'],
    'bengaluru': ['bangalore', 'bengaluru'],
    'bangalore': ['bangalore', 'bengaluru'],
    'mumbai': ['mumbai', 'bombay'],
    'bombay': ['mumbai', 'bombay'],
    'delhi': ['delhi', 'new delhi'],
    'new delhi': ['delhi', 'new delhi'],
    'kolkata': ['kolkata', 'calcutta'],
    'calcutta': ['kolkata', 'calcutta'],
    'chennai': ['chennai', 'madras'],
    'madras': ['chennai', 'madras'],
    'hyderabad': ['hyderabad', 'secunderabad'],
    'secunderabad': ['hyderabad', 'secunderabad'],
    'pune': ['pune', 'poona'],
    'poona': ['pune', 'poona']
}

class CompanyProfile(BaseModel):
    companyName: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class LocationModel(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remoteStatus: Optional[str] = None

class Qualifications(BaseModel):
    required: List[str] = []
    preferred: List[str] = []

class CompensationBenefits(BaseModel):
    salaryRange: Optional[str] = None
    benefits: List[str] = []

class ApplicationInfo(BaseModel):
    howToApply: Optional[str] = None
    applyLink: Optional[str] = None
    contactEmail: Optional[str] = None

class JDModel(BaseModel):
    jobId: Optional[str] = None
    jobTitle: str
    companyProfile: CompanyProfile
    location: LocationModel
    datePosted: str
    employmentType: str
    jobSummary: str
    keyResponsibilities: List[str]
    qualifications: Qualifications
    requiredSkills: Union[List[str], Dict[str, List[str]]] = []  # Accepts both flat and categorized
    educationRequired: List[str] = []
    compensationAndBenefits: CompensationBenefits
    applicationInfo: ApplicationInfo
    extractedKeywords: List[str]

class PersonalData(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    location: LocationModel

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    fieldOfStudy: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None

class Experience(BaseModel):
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    description: List[str] = []
    technologiesUsed: List[str] = []

class Project(BaseModel):
    projectName: Optional[str] = None
    description: Optional[str] = None
    technologiesUsed: List[str] = []
    link: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class Skill(BaseModel):
    category: Optional[str] = None
    skillName: str

class JobStability(BaseModel):
    average_duration_years: Optional[float] = None
    frequent_switching_flag: bool = False

class EducationGap(BaseModel):
    has_gap: bool = False
    gap_duration_years: float = 0

class KeywordAnalysis(BaseModel):
    teamwork: bool = False
    management_experience: bool = False
    geographic_experience: bool = False
    extracted_keywords: List[str] = []

class Analytics(BaseModel):
    job_stability: JobStability
    education_gap: EducationGap
    keyword_analysis: KeywordAnalysis
    suggested_role: str

class CVModel(BaseModel):
    UUID: str
    Personal_Data: PersonalData = Field(alias="Personal Data")
    education_list: List[Education] = Field(alias="Education", default=[])
    experiences_list: List[Experience] = Field(alias="Experiences", default=[])
    projects_list: List[Project] = Field(alias="Projects", default=[])
    skills_list: List[Skill] = Field(alias="Skills", default=[])
    research_work_list: List[Dict[str, Any]] = Field(alias="Research Work", default=[])
    achievements_list: List[str] = Field(alias="Achievements", default=[])
    Analytics: Analytics
    skill_presence: Optional[Dict[str, bool]] = None  # Changed to Dict[str, bool] for boolean skill presence

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True

class MatchRequest(BaseModel):
    jd: JDModel
    cvs: List[CVModel]

def parse_date(date_str: str) -> datetime:
    if not date_str or date_str.lower() == "present":
        return datetime.now()
    
    try:
        if len(date_str) == 4:
            return datetime.strptime(date_str, "%Y")
        elif len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m")
        else:
            return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime.now()

def calculate_experience_years(experiences: List[Experience]) -> float:
    total_days = 0
    for exp in experiences:
        try:
            start_date = parse_date(exp.startDate)
            end_date = parse_date(exp.endDate) if exp.endDate and exp.endDate.lower() != "present" else datetime.now()
            total_days += (end_date - start_date).days
        except (AttributeError, TypeError):
            continue
    return round(max(0, total_days / 365), 1)

def extract_required_experience(qualifications) -> float:
    if not qualifications or not qualifications.required:
        return 0.0

    required_sentences = qualifications.required
    sentence_embeddings = model.encode(required_sentences, convert_to_tensor=True)

    query = "How many years of experience are required?"
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, sentence_embeddings)[0]

    top_idx = int(similarities.argmax())
    best_sentence = required_sentences[top_idx].lower()

    best_sentence = re.sub(r"[–—−]", "-", best_sentence)

    patterns = [
        r'(\d+)\s*[-]\s*(\d+)\s*years?',
        r'(\d+)\s*to\s*(\d+)\s*years?',
        r'(\d+)\+\s*years?',
        r'minimum\s*(\d+)\s*years?',
        r'at least\s*(\d+)\s*years?',
        r'(\d+)\s*years?\s*experience',
    ]

    for pattern in patterns:
        match = re.search(pattern, best_sentence)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return float(groups[0])
            elif len(groups) == 1:
                return float(groups[0])

    return 0.0

def calculate_role_relevance(jd_title: str, cv_suggested_role: str, cv_experiences: List[Experience]) -> float:
    if cv_suggested_role:
        jd_emb = model.encode(jd_title.lower())
        suggested_role_emb = model.encode(cv_suggested_role.lower())
        role_similarity = cosine_similarity([jd_emb], [suggested_role_emb])[0][0]
        return max(0.3, role_similarity)
    
    if not cv_experiences:
        return 0.5
    
    cv_titles = [exp.jobTitle for exp in cv_experiences if exp.jobTitle]
    cv_titles_text = " ".join(cv_titles).lower()
    
    if not cv_titles_text.strip():
        return 0.5
    
    jd_emb = model.encode(jd_title.lower())
    cv_emb = model.encode(cv_titles_text)
    
    similarity = cosine_similarity([jd_emb], [cv_emb])[0][0]
    return max(0.3, similarity)

def calculate_experience_match(cv_exp: float, jd_req: float, role_relevance: float) -> float:
    if jd_req == 0:
        return 0.8
    if role_relevance < 0.5:
        if cv_exp >= jd_req:
            return min(0.6, 0.4 + (cv_exp / jd_req) * 0.2)
        else:
            return max(0.2, (cv_exp / jd_req) * 0.3)
    
    if cv_exp >= jd_req:
        excess = cv_exp - jd_req
        bonus = min(0.2, excess * 0.1)
        return min(1.0, 0.8 + bonus)
    else:
        ratio = cv_exp / jd_req
        return max(0.3, ratio * 0.7)

def fuzzy_match_cities(city1: str, city2: str) -> float:
    if not city1 or not city2:
        return 0.0
    
    city1_lower = city1.lower().strip()
    city2_lower = city2.lower().strip()
    
    if city1_lower == city2_lower:
        return 1.0
    
    city1_variations = CITY_VARIATIONS.get(city1_lower, [city1_lower])
    city2_variations = CITY_VARIATIONS.get(city2_lower, [city2_lower])
    
    for var1 in city1_variations:
        for var2 in city2_variations:
            if var1 == var2:
                return 1.0
    
    similarity = SequenceMatcher(None, city1_lower, city2_lower).ratio()
    return similarity if similarity > 0.7 else 0.0

DEGREE_HIERARCHY = {
    r"\bph\.?d\b|\bdoctor(?:ate)?\b|\bd\.?phil\b": 4,
    r"\bmaster\b|\bms\b|\bm\.?sc?\b|\bm\.?a\b|\bm\.?com\b|\bm\.?tech\b|\bmba\b|\bmca\b|\bl\.?l\.?m\b": 3,
    r"\bbachelor\b|\bbs\b|\bb\.?sc?\b|\bb\.?a\b|\bb\.?com\b|\bb\.?tech\b|\bbca\b|\bbba\b|\bbe\b|\bl\.?l\.?b\b|\bundergrad\b": 2,
    r"\bdiploma\b|\bcertificate\b|\bassociate\b|\badvance diploma\b": 1,
    r"\bhigh school\b|\bhsc\b|\bssc\b|\bsecondary\b|\bcbse\b|\bicse\b|\bgcse\b": 0
}

def extract_highest_degree_level(text: str) -> int:
    if not text:
        return -1
    text_lower = text.lower()
    found_levels = {level for kw, level in DEGREE_HIERARCHY.items() if kw in text_lower}
    return max(found_levels) if found_levels else -1


def extract_field(text: str) -> str:
    if not text:
        return ""
    
    text_lower = text.lower().strip()
    
    # Common field mappings for degree abbreviations
    field_mappings = {
        'b.b.a': 'business administration',
        'bba': 'business administration',
        'm.b.a': 'business administration',
        'mba': 'business administration',
        'b.tech': 'engineering',
        'btech': 'engineering',
        'm.tech': 'engineering',
        'mtech': 'engineering',
        'b.sc': 'science',
        'bsc': 'science',
        'm.sc': 'science',
        'msc': 'science',
        'b.a': 'arts',
        'ba': 'arts',
        'm.a': 'arts',
        'ma': 'arts',
        'b.com': 'commerce',
        'bcom': 'commerce',
        'm.com': 'commerce',
        'mcom': 'commerce',
        'bca': 'computer applications',
        'mca': 'computer applications',
        'phd': 'research',
        'ph.d': 'research',
        'd.phil': 'research'
    }
    
    # Check for exact degree abbreviation matches
    for abbrev, field in field_mappings.items():
        if abbrev in text_lower:
            return field
    
    # Extract field from "in [field]" pattern
    in_pattern = r'in\s+([a-zA-Z\s]+?)(?:\s+from|\s*$|,|\(|\))'
    in_match = re.search(in_pattern, text_lower)
    if in_match:
        field = in_match.group(1).strip()
        if field and len(field) > 2:  # Avoid very short matches
            return field
    
    # Extract field from parentheses
    paren_pattern = r'\(([^)]+)\)'
    paren_match = re.search(paren_pattern, text_lower)
    if paren_match:
        field = paren_match.group(1).strip()
        if field and len(field) > 2:
            return field
    
    # Extract field from "preferably in" pattern
    pref_pattern = r'preferably\s+in\s+([a-zA-Z\s,]+?)(?:\s+or|\s*$|,|\(|\))'
    pref_match = re.search(pref_pattern, text_lower)
    if pref_match:
        field = pref_match.group(1).strip()
        if field and len(field) > 2:
            return field
    
    # If no specific field found, return the cleaned text
    # Remove common degree words and clean up
    cleaned = re.sub(r'\b(bachelor|master|degree|preferably|related|field|or)\b', '', text_lower)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else ""

def calculate_field_similarity(cv_field: str, jd_text: str) -> float:
    if not cv_field or not jd_text:
        return 0.0
    cv_embed = model.encode([cv_field], convert_to_tensor=True)
    jd_embed = model.encode([jd_text], convert_to_tensor=True)
    return util.cos_sim(cv_embed, jd_embed).item()

def calculate_education_match(cv_education: list[Education], jd_education: list[str]) -> float:
    if not jd_education:
        return 1.0
    if not cv_education:
        return 0.0

    jd_requirements = []
    for req in jd_education:
        level = extract_highest_degree_level(req)
        field = extract_field(req)
        jd_requirements.append({
            "text": req,
            "level": level,
            "field": field
        })

    cv_entries = []
    for edu in cv_education:
        degree = normalize_degree(edu.degree) if edu.degree else ""
        level = extract_highest_degree_level(degree)
        field = extract_field(edu.fieldOfStudy or degree or "")
        cv_entries.append({
            "text": " ".join(filter(None, [
                degree,
                f"in {edu.fieldOfStudy}" if edu.fieldOfStudy else "",
                f"from {edu.institution}" if edu.institution else ""
            ])),
            "level": level,
            "field": field
        })

    jd_texts = [req["text"] for req in jd_requirements]
    cv_texts = [entry["text"] for entry in cv_entries]
    jd_embeddings = model.encode(jd_texts, convert_to_tensor=True)
    cv_embeddings = model.encode(cv_texts, convert_to_tensor=True)
    similarity_matrix = util.cos_sim(jd_embeddings, cv_embeddings)

    requirement_scores = []
    for i, jd_req in enumerate(jd_requirements):
        best_match_score = 0
        for j, cv_entry in enumerate(cv_entries):
            base_score = similarity_matrix[i][j].item()
            level_bonus = 0
            if jd_req["level"] >= 0 and cv_entry["level"] > jd_req["level"]:
                level_bonus = 0.25
            field_bonus = 0
            if jd_req["field"] and cv_entry["field"]:
                if jd_req["field"] == cv_entry["field"]:
                    field_bonus = 0.3
                else:
                    field_sim = calculate_field_similarity(cv_entry["field"], jd_req["field"])
                    field_bonus = 0.2 * field_sim
            total_score = min(1.0, base_score + level_bonus + field_bonus)
            if total_score > best_match_score:
                best_match_score = total_score
        requirement_scores.append(best_match_score)

    final_score = min(1.0, max(requirement_scores) if requirement_scores else 0.0)
    return final_score

def calculate_location_match(cv_location: LocationModel, jd_location: LocationModel) -> float:
    cv_city = cv_location.city.lower().strip() if cv_location.city else ""
    jd_city = jd_location.city.lower().strip() if jd_location.city else ""
    
    if jd_location.remoteStatus and 'remote' in jd_location.remoteStatus.lower():
        return 1.0
    
    city_match = fuzzy_match_cities(cv_city, jd_city)
    if city_match >= 0.8:
        return 1.0
    elif city_match >= 0.7:
        return 0.9
    
    cv_state = cv_location.state.lower().strip() if cv_location.state else ""
    jd_state = jd_location.state.lower().strip() if jd_location.state else ""
    if cv_state and cv_state == jd_state:
        return 0.8
    
    cv_country = cv_location.country.lower().strip() if cv_location.country else ""
    jd_country = jd_location.country.lower().strip() if jd_location.country else ""
    if cv_country and cv_country == jd_country:
        return 0.6
    
    return 0.3

def calculate_skills_match(jd_required_skills: List[str], cv_skills: List[Skill]) -> float:
    if not jd_required_skills:
        return 0.7
    
    cv_skill_names = [s.skillName for s in cv_skills]
    
    if not cv_skill_names:
        return 0.3
    
    jd_skills_text = " ".join(jd_required_skills)
    cv_skills_text = " ".join(cv_skill_names)
    
    jd_skills_emb = model.encode(jd_skills_text)
    cv_skills_emb = model.encode(cv_skills_text)
    semantic_similarity = cosine_similarity([jd_skills_emb], [cv_skills_emb])[0][0]
    
    return max(0.3, min(1.0, semantic_similarity))

def calculate_enhanced_sim_resp(jd_responsibilities: List[str], cv_experiences: List[Experience], model) -> float:
    if not jd_responsibilities or not cv_experiences:
        return 0.0

    cv_descriptions = []
    for exp in cv_experiences:
        if exp.description:
            cv_descriptions.extend(exp.description)

    if not cv_descriptions:
        return 0.0

    jd_embeddings = model.encode(jd_responsibilities)
    cv_embeddings = model.encode(cv_descriptions)

    similarity_matrix = cosine_similarity(jd_embeddings, cv_embeddings)

    best_matches = []
    for i in range(similarity_matrix.shape[0]):
        top_similarities = sorted(similarity_matrix[i], reverse=True)[:2]
        if len(top_similarities) == 2:
            weighted = 0.7 * top_similarities[0] + 0.3 * top_similarities[1]
        else:
            weighted = top_similarities[0]
        best_matches.append(weighted)

    final_score = sum(best_matches) / len(best_matches)
    final_score = 0.3 + (final_score * 0.7)
    return float(min(1.0, final_score))

# Adjust the combination logic to remain domain-agnostic

def calculate_combined_sim_resp(jd_responsibilities, cv_experiences, model):
    semantic_score = calculate_enhanced_sim_resp(jd_responsibilities, cv_experiences, model)
    return min(1.0, semantic_score)

def get_match_level(score: float) -> str:
    if score >= 0.8: return "Excellent"
    elif score >= 0.65: return "Good"
    elif score >= 0.5: return "Moderate"
    else: return "Poor"

def generate_match_summary(details: Dict) -> str:
    strengths = []
    if details['experience_suitability'] > 0.8:
        strengths.append(f"Strong experience fit ({details['candidate_exp_years']} yrs vs req {details['required_exp_years']} yrs)")
    if details['skills_similarity'] > 0.85:
        strengths.append("Excellent skills alignment")
    if details['role_relevance'] > 0.8:
        strengths.append("Highly relevant background")
    
    concerns = []
    if details['experience_suitability'] < 0.5:
        concerns.append(f"Experience gap ({details['candidate_exp_years']} yrs vs req {details['required_exp_years']} yrs)")
    if details['education_relevance'] < 0.4:
        concerns.append("Education mismatch")
    if details['location_compatibility'] < 0.5:
        concerns.append("Location incompatibility")
    if details['role_relevance'] < 0.4:
        concerns.append("Role relevance concerns")
    
    summary = "Strengths: " + ", ".join(strengths) if strengths else ""
    if concerns:
        summary += " | Concerns: " + ", ".join(concerns) if summary else "Concerns: " + ", ".join(concerns)
    
    return summary or "No significant strengths or concerns identified"

def compute_similarity(jd: JDModel, cv: CVModel) -> Tuple[float, Dict]:
    suggested_role = cv.Analytics.suggested_role
    
    role_relevance = calculate_role_relevance(jd.jobTitle, suggested_role, cv.experiences_list)
    
    jd_title_emb = model.encode(jd.jobTitle)
    
    cv_experience_years = calculate_experience_years(cv.experiences_list)
    jd_required_years = extract_required_experience(jd.qualifications)
    
    cv_title_text = suggested_role if suggested_role else " ".join([exp.jobTitle for exp in cv.experiences_list if exp.jobTitle])
    
    cv_title_emb = model.encode(cv_title_text if cv_title_text else "")
    
    sim_title = cosine_similarity([jd_title_emb], [cv_title_emb])[0][0] if cv_title_text else 0.0
    sim_resp = calculate_combined_sim_resp(jd.keyResponsibilities, cv.experiences_list, model)
    
    experience_match = calculate_experience_match(cv_experience_years, jd_required_years, role_relevance)
    education_match = calculate_education_match(cv.education_list, jd.educationRequired)
    location_match = calculate_location_match(cv.Personal_Data.location, jd.location)
    skills_match = calculate_skills_match(jd.requiredSkills, cv.skills_list)
    
    final_score = (
        0.23 * sim_title +
        0.31 * sim_resp +
        0.23 * experience_match +
        0.15 * skills_match +
        0.08 * education_match
    )
    
    details = {
        "job_title_similarity": round(float(sim_title), 4),
        "responsibilities_similarity": round(float(sim_resp), 4),
        "experience_suitability": round(float(experience_match), 4),
        "skills_similarity": round(float(skills_match), 4),
        "education_relevance": round(float(education_match), 4),
        "location_compatibility": round(float(location_match), 4),
        "role_relevance": round(float(role_relevance), 4),
        "candidate_exp_years": cv_experience_years,
        "required_exp_years": jd_required_years,
        "suggested_role": suggested_role,
        "match_summary": generate_match_summary({
            "experience_suitability": experience_match,
            "skills_similarity": skills_match,
            "education_relevance": education_match,
            "location_compatibility": location_match,
            "role_relevance": role_relevance,
            "candidate_exp_years": cv_experience_years,
            "required_exp_years": jd_required_years
        })
    }
    
    return round(float(final_score), 4), details

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
        resume_json["Skills"] = [s for s in skills if isinstance(s, dict)]

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
                # Convert value to boolean
                if isinstance(value, bool):
                    cleaned_skill_presence[skill] = value
                elif isinstance(value, str):
                    cleaned_skill_presence[skill] = value.lower() in ['true', '1', 'yes', 'present']
                elif isinstance(value, (int, float)):
                    cleaned_skill_presence[skill] = bool(value)
                else:
                    cleaned_skill_presence[skill] = False
        resume_json["skill_presence"] = cleaned_skill_presence
    else:
        resume_json["skill_presence"] = {}

    return resume_json

def generate_interview_questions(jd: JDModel, cv: CVModel) -> list:
    prompt = f"""
Given the following job description and candidate resume, generate 3-5 specific interview questions that would help assess the candidate's fit for this role. Focus on their experience, skills, and any gaps or strengths.

Job Description:
{jd.jobTitle}
Key Responsibilities: {', '.join(jd.keyResponsibilities)}
Required Skills: {', '.join(jd.requiredSkills)}
Education Required: {', '.join(jd.educationRequired)}

Candidate Resume:
Name: {cv.Personal_Data.firstName or ''} {cv.Personal_Data.lastName or ''}
Experiences: {', '.join([exp.jobTitle or '' for exp in cv.experiences_list])}
Skills: {', '.join([s.skillName for s in cv.skills_list])}
Education: {', '.join([e.degree or '' for e in cv.education_list])}
Suggested Role: {cv.Analytics.suggested_role}

Output only a JSON array of questions.
"""
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {"role": "system", "content": "You are an expert HR interviewer. Generate only interview questions as a JSON array."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=512
    )
    content = response.choices[0].message.content.strip()
    try:
        questions = json.loads(clean_json_response(content))
        if isinstance(questions, list):
            return [str(q) for q in questions if isinstance(q, str)]
    except Exception:
        pass
    return []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/match_enhanced")
async def match_enhanced(data: MatchRequest):
    jd = data.jd
    cvs = data.cvs
    
    results = []
    for cv in cvs:
        score, details = compute_similarity(jd, cv)
        match_level = get_match_level(score)
        
        candidate_name = f"{cv.Personal_Data.firstName or ''} {cv.Personal_Data.lastName or ''}".strip()
        interview_questions = generate_interview_questions(jd, cv)
        
        results.append({
            "candidate_id": cv.UUID,
            "candidate_name": candidate_name,
            "match_score": round(score * 100, 2),
            "match_level": match_level,
            "match_details": details,
            "interview_questions": interview_questions,
            "job_stability": cv.Analytics.job_stability,
            "education_gap": cv.Analytics.education_gap,
            "suggested_role": cv.Analytics.suggested_role
        })
    
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    return {
        "results": results,
        "matching_metadata": {
            "job_id": jd.jobId,
            "job_title": jd.jobTitle,
            "candidates_evaluated": len(cvs),
            "top_match_score": results[0]["match_score"] if results else 0,
            "average_match_score": round(sum(r["match_score"] for r in results) / len(results), 2) if results else 0
        }
    }

def process_json_input(json_data: dict) -> MatchRequest:
    try:
        return MatchRequest(**json_data)
    except Exception as e:
        print(f"Error processing JSON: {e}")
        raise

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

def preprocess_resume_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-\.\,\:\;\@\(\)\[\]\{\}\+\=\&\|\/\?\!]', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r' +', ' ', text)
    if len(text) > 8000:
        text = text[:8000] + "..."
    return text.strip()

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
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        raise

JD_SCHEMA_JSON = '''{
  "jobId": "string",
  "jobTitle": "string",
  "companyProfile": {
    "companyName": "string",
    "industry": "Optional[string]",
    "website": "Optional[string]",
    "description": "Optional[string]"
  },
  "location": {
    "city": "string",
    "state": "string",
    "country": "string",
    "remoteStatus": "string"
  },
  "datePosted": "YYYY-MM-DD",
  "employmentType": "string",
  "jobSummary": "string",
  "keyResponsibilities": [
    "string",
    "..."
  ],
  "qualifications": {
    "required": [
      "string",
      "..."
    ],
    "preferred": [
      "string",
      "..."
    ]
  },
  "requiredSkills": [
    "string",
    "..."
  ],
  "educationRequired": [
    "string",
    "..."
  ],
  "compensationAndBenefits": {
    "salaryRange": "string",
    "benefits": [
      "string",
      "..."
    ]
  },
  "applicationInfo": {
    "howToApply": "string",
    "applyLink": "string",
    "contactEmail": "Optional[string]"
  },
  "extractedKeywords": [
    "string",
    "..."
  ]
}'''

RESUME_SCHEMA_JSON = '''{
    "UUID": "string",
    "Personal Data": {
        "firstName": "string",
        "lastName": "string",
        "email": "string",
        "phone": "string",
        "linkedin": "string",
        "portfolio": "string",
        "location": {
            "state": "string",
            "city": "string",
            "country": "string"
        }
    },
    "Education": [
        {
            "institution": "string",
            "degree": "string",
            "fieldOfStudy": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD",
            "grade": "string",
            "description": "string"
        }
    ],
    "Experiences": [
        {
            "jobTitle": "string",
            "company": "string",
            "location": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD or Present",
            "description": [
                "string",
                "..."
            ],
            "technologiesUsed": [
                "string",
                "..."
            ]
        }
    ],
    "Projects": [
        {
            "projectName": "string",
            "description": "string",
            "technologiesUsed": [
                "string",
                "..."
            ],
            "link": "string",
            "startDate": "YYYY-MM-DD",
            "endDate": "YYYY-MM-DD"
        }
    ],
    "Skills": [
        {
            "category": "string",
            "skillName": "string"
        }
    ],
    "Research Work": [
        {
            "title": "string",
            "publication": "string",
            "date": "YYYY-MM-DD",
            "link": "string",
            "description": "string"
        }
    ],
    "Achievements": [
        "string",
        "..."
    ],
    "Analytics": {
        "job_stability": {
            "average_duration_years": 0,
            "frequent_switching_flag": false
        },
        "education_gap": {
            "has_gap": false,
            "gap_duration_years": 0
        },
        "keyword_analysis": {
            "teamwork": false,
            "management_experience": false,
            "geographic_experience": false,
            "extracted_keywords": [
                "string",
                "..."
            ]
        },
        "suggested_role": "string"
    },
    "skill_presence": {
        "skill_name": true,
        "skill_name": false
    }
}'''

def convert_resume_to_json(resume_text: str, jd_skill_categories: Optional[Dict[str, List[str]]] = None) -> Optional[dict]:
    try:
        schema = RESUME_SCHEMA_JSON
        cleaned_text = preprocess_resume_text(resume_text)
        skill_presence_instruction = ""
        if jd_skill_categories:
            skill_presence_instruction = f"""
- For the 'skill_presence' field, create a dictionary where each skill from the provided categories (critical, important, extra) is a key with a boolean value.
- Set the value to 'true' if the skill is present in the resume, 'false' if it is not found.
- Check all skills in the provided categories and assign boolean values accordingly.
- Example format: {{"Python": true, "Java": false, "React": true}}
- Use the provided skill categories for this check:
{json.dumps(jd_skill_categories, indent=2)}
"""
        prompt = f"""
You are a JSON extraction engine. Convert the following resume text into precisely the JSON schema specified below.
IMPORTANT INSTRUCTIONS:
- Extract only information that is clearly present in the text
- If a field is not found, use null or empty array/object as appropriate
- For dates, use YYYY-MM-DD format or "Present" for ongoing
- Try to find location information (city, state, country) using phrases like "based in", "located in", prefered location, etc.
- If the **state is not given**, but the **city is**, **infer the state** based on the city (e.g., if city is Gurgaon, assign state as Uttar Pradesh).
- If **neither city nor state** is provided, set both `"city"` and `"state"` to `"Unknown"`.
- For job_stability, calculate average duration if multiple experiences exist
- For education_gap, check for chronological gaps between education entries
- For keyword_analysis, look for teamwork, management, leadership keywords
- For suggested_role, analyze the most prominent skills and experiences
- For extracted_keywords, identify technical skills, tools, technologies, and important terms
- For each education entry, extract the most specific and relevant field of study, even if it appears in the degree name, fieldOfStudy, or description.
- If the field of study is not explicitly provided, infer it from the degree name or description (e.g., 'MBA in Marketing' → fieldOfStudy: 'Marketing').
- Normalize common abbreviations and synonyms (e.g., 'HR' ↔ 'Human Resources', 'CS' ↔ 'Computer Science', 'IT' ↔ 'Information Technology', 'Mgmt' ↔ 'Management').
- If no field can be determined, set fieldOfStudy to null.
- Do not make up or infer information that is not explicitly stated.
{skill_presence_instruction}
Schema:
{schema}
Resume Text:
{cleaned_text}
NOTE: Output only valid JSON matching the exact schema structure.
"""
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are a precise JSON extraction expert. Only extract information that is explicitly stated in the text. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.05,
            max_tokens=6000
        )
        content = response.choices[0].message.content.strip()
        cleaned_content = clean_json_response(content)
        try:
            result = json.loads(cleaned_content)
            if "Analytics" not in result:
                result["Analytics"] = {}
            if "keyword_analysis" not in result["Analytics"]:
                result["Analytics"]["keyword_analysis"] = {}
            
            # Ensure skill_presence is properly initialized
            if "skill_presence" not in result:
                result["skill_presence"] = {}
            elif not isinstance(result["skill_presence"], dict):
                result["skill_presence"] = {}
            
            return result
        except json.JSONDecodeError as e:
            cleaned_content = re.sub(r',\s*}', '}', cleaned_content)
            cleaned_content = re.sub(r',\s*]', ']', cleaned_content)
            try:
                result = json.loads(cleaned_content)
                if "Analytics" not in result:
                    result["Analytics"] = {}
                if "keyword_analysis" not in result["Analytics"]:
                    result["Analytics"]["keyword_analysis"] = {}
                
                # Ensure skill_presence is properly initialized
                if "skill_presence" not in result:
                    result["skill_presence"] = {}
                elif not isinstance(result["skill_presence"], dict):
                    result["skill_presence"] = {}
                
                return result
            except json.JSONDecodeError:
                return None
    except Exception as e:
        print(f"❌ Error converting resume with Grok API: {e}")
        return None

def convert_jd_to_json(jd_text: str) -> Optional[dict]:
    try:
        schema = JD_SCHEMA_JSON
        prompt = f"""
You are a JSON-extraction engine. Convert the following raw job posting text into exactly the JSON schema below:
— Do not add any extra fields or prose.
- If the **state is not explicitly given**, but the **city is**, **infer the state** based on the city (e.g., if city is Varanasi, assign state as Uttar Pradesh).
- If **neither city nor state** is provided, set both `"city"` and `"state"` to `"Unknown"`.
— Use "YYYY-MM-DD" for all dates.
— Ensure any URLs (website, applyLink) conform to URI format.
— Do not change the structure or key names; output only valid JSON matching the schema.
- For extractedKeywords, identify key technical skills, tools, technologies, and important terms from the job description.
- Extract keywords like: programming languages, frameworks, tools, methodologies, certifications, etc.
- For requiredSkills, extract specific technical and non-technical skills that are mentioned for the role. Look for phrases like "must have", "required", "essential", "mandatory","Hands-on experience", etc.
- For educationRequired, extract all explicit education requirements (degrees, certifications, fields of study, etc.) mentioned in the job description. This should be a list of strings, e.g., ["Bachelor's in Computer Science", "MBA", "PhD in HR"].
- For educationRequired: When education requirements mention multiple fields, degrees, or options together (e.g., 'Bachelor's degree (preferably in HR, Business Administration, or related field)'), split them into separate, specific entries in the educationRequired list.
  - For example, 'Bachelor's degree (preferably in HR, Business Administration, or related field)' should become:
    - 'Bachelor's in Human Resources'
    - 'Bachelor's in Business Administration'
    - 'Bachelor's in related field'
  - For each requirement, extract the most specific degree and field combination possible.
  - Normalize abbreviations and synonyms (e.g., 'HR' ↔ 'Human Resources', 'CS' ↔ 'Computer Science').
  - If a requirement is ambiguous, include each possible interpretation as a separate entry.
  - Do not merge multiple requirements into a single string in the output.
- Differentiate between requiredSkills (specific technical abilities, programming languages, tools, soft skills) and qualifications (education, experience, certifications)
- Do not format the response in Markdown or any other format. Just output raw JSON.
Schema:
{schema}
Job Description Text:
{jd_text}
NOTE: Please output only a valid JSON matching the EXACT schema.
"""
        response = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are a JSON extraction expert. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000 
        )
        content = response.choices[0].message.content.strip()
        cleaned_content = clean_json_response(content)
        try:
            result = json.loads(cleaned_content)
            if "requiredSkills" not in result:
                result["requiredSkills"] = []
            if "educationRequired" not in result:
                result["educationRequired"] = []
            return result
        except json.JSONDecodeError as e:
            cleaned_content = re.sub(r',\s*}', '}', cleaned_content)
            cleaned_content = re.sub(r',\s*]', ']', cleaned_content)
            try:
                result = json.loads(cleaned_content)
                if "requiredSkills" not in result:
                    result["requiredSkills"] = []
                if "educationRequired" not in result:
                    result["educationRequired"] = []
                return result
            except json.JSONDecodeError:
                return None
    except Exception as e:
        print(f"❌ Error converting JD with Grok API: {e}")
        return None

@app.post("/extract_and_match")
async def extract_and_match(
    jd_file: UploadFile = File(...),
    resume_files: list[UploadFile] = File(...)
):
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, jd_file.filename)
        with open(jd_path, "wb") as f:
            shutil.copyfileobj(jd_file.file, f)
        jd_text = extract_text_from_file(jd_path)
        jd_json = convert_jd_to_json(jd_text)
        if not jd_json:
            return JSONResponse(status_code=400, content={"error": "Failed to extract JD JSON"})
        os.makedirs("debug_outputs", exist_ok=True)
        with open("debug_outputs/jd_extracted.json", "w", encoding="utf-8") as f:
            json.dump(jd_json, f, indent=2, ensure_ascii=False)
        cvs = []
        for i, resume_file in enumerate(resume_files):
            resume_path = os.path.join(tmpdir, resume_file.filename)
            with open(resume_path, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)
            resume_text = extract_text_from_file(resume_path)
            resume_json = convert_resume_to_json(resume_text)
            if not resume_json:
                continue
            resume_json = clean_resume_json(resume_json)
            with open(f"debug_outputs/resume_extracted_{i+1}.json", "w", encoding="utf-8") as f:
                json.dump(resume_json, f, indent=2, ensure_ascii=False)
            try:
                cv_obj = CVModel.parse_obj(resume_json)
                cvs.append(cv_obj)
            except Exception as e:
                print(f"❌ Error parsing extracted resume JSON: {e}")
                continue
        try:
            jd_obj = JDModel.parse_obj(jd_json)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Failed to parse JD JSON: {e}"})
        results = []
        for cv in cvs:
            score, details = compute_similarity(jd_obj, cv)
            match_level = get_match_level(score)
            candidate_name = f"{cv.Personal_Data.firstName or ''} {cv.Personal_Data.lastName or ''}".strip()
            interview_questions = generate_interview_questions(jd_obj, cv)
            results.append({
                "candidate_id": cv.UUID,
                "candidate_name": candidate_name,
                "match_score": round(score * 100, 2),
                "match_level": match_level,
                "match_details": details,
                "interview_questions": interview_questions,
                "job_stability": cv.Analytics.job_stability,
                "education_gap": cv.Analytics.education_gap,
                "suggested_role": cv.Analytics.suggested_role
            })
        results = sorted(results, key=lambda x: x["match_score"], reverse=True)
        return {
            "results": results,
            "matching_metadata": {
                "job_title": jd_obj.jobTitle,
                "candidates_evaluated": len(cvs),
                "top_match_score": results[0]["match_score"] if results else 0,
                "average_match_score": round(sum(r["match_score"] for r in results) / len(results), 2) if results else 0
            }
        }

@app.post("/extract_jd")
async def extract_jd(jd_file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = os.path.join(tmpdir, jd_file.filename)
        with open(jd_path, "wb") as f:
            shutil.copyfileobj(jd_file.file, f)
        jd_text = extract_text_from_file(jd_path)
        jd_json = convert_jd_to_json(jd_text)
        if not jd_json:
            return JSONResponse(status_code=400, content={"error": "Failed to extract JD JSON"})
        return jd_json

@app.post("/extract_resumes")
async def extract_resumes(
    resume_files: list[UploadFile] = File(...),
    jd_json: str = Form(...)
):
    import json
    jd_json = json.loads(jd_json)
    # Flatten requiredSkills if dict
    required_skills = jd_json.get("requiredSkills", [])
    skill_categories = None
    if isinstance(required_skills, dict):
        skill_categories = required_skills
        flat_skills = [s for cat in required_skills.values() for s in cat]
    else:
        flat_skills = required_skills
    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for resume_file in resume_files:
            resume_path = os.path.join(tmpdir, resume_file.filename)
            with open(resume_path, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)
            resume_text = extract_text_from_file(resume_path)
            resume_json = convert_resume_to_json(resume_text, skill_categories)
            if not resume_json:
                continue
            resume_json = clean_resume_json(resume_json)
            
            # Ensure all skills from categories are present in skill_presence
            if skill_categories:
                resume_json["skill_presence"] = ensure_complete_skill_presence(
                    resume_json.get("skill_presence", {}), 
                    skill_categories
                )
            
            results.append({
                "cv_json": resume_json,
                "skill_presence": resume_json.get("skill_presence", {})
            })
    return results

@app.post("/match")
async def match(
    jd_json: dict = Body(...),
    cvs: list = Body(...)
):
    # Flatten requiredSkills if dict
    required_skills = jd_json.get("requiredSkills", [])
    skill_categories = None
    if isinstance(required_skills, dict):
        skill_categories = required_skills
        flat_skills = [s for cat in required_skills.values() for s in cat]
        jd_json = {**jd_json, "requiredSkills": flat_skills}
    else:
        flat_skills = required_skills
    jd_obj = JDModel.parse_obj(jd_json)
    results = []
    for cv_entry in cvs:
        cv_json = cv_entry["cv_json"]
        skill_presence = cv_entry.get("skill_presence", {})
        cv_obj = CVModel.parse_obj(cv_json)
        # For each skill, present if in skill_presence, else absent
        present = [s for s in flat_skills if skill_presence.get(s, False)]
        absent = [s for s in flat_skills if not skill_presence.get(s, False)]
        # For critical skills, check status
        critical_skills = skill_categories["critical"] if skill_categories and "critical" in skill_categories else []
        critical_present = [s for s in critical_skills if skill_presence.get(s, False)]
        critical_absent = [s for s in critical_skills if not skill_presence.get(s, False)]
        if len(critical_absent) == 0 and len(critical_present) > 0:
            critical_skill_status = "All Present"
        elif len(critical_present) == 0 and len(critical_absent) > 0:
            critical_skill_status = "All Absent"
        else:
            critical_skill_status = "Partial Present"
        disclaimer = None
        if critical_skill_status == "All Absent":
            disclaimer = "Disclaimer: None of the critical required skills are present in this CV."
        score, details = compute_similarity(jd_obj, cv_obj)
        results.append({
            "candidate_id": cv_obj.UUID,
            "candidate_name": f"{cv_obj.Personal_Data.firstName or ''} {cv_obj.Personal_Data.lastName or ''}".strip(),
            "match_score": round(score * 100, 2),
            "match_level": get_match_level(score),
            "match_details": details,
            "critical_skill_status": critical_skill_status,
            "critical_present": critical_present,
            "critical_absent": critical_absent,
            "present_skills": present,
            "absent_skills": absent,
            "disclaimer": disclaimer,
            "job_stability": cv_obj.Analytics.job_stability,
            "education_gap": cv_obj.Analytics.education_gap,
            "suggested_role": cv_obj.Analytics.suggested_role,
            "interview_questions": generate_interview_questions(jd_obj, cv_obj),
            "skill_presence": skill_presence
        })
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)
    return {
        "results": results,
        "matching_metadata": {
            "job_title": jd_obj.jobTitle,
            "candidates_evaluated": len(results),
            "top_match_score": results[0]["match_score"] if results else 0,
            "average_match_score": round(sum(r["match_score"] for r in results) / len(results), 2) if results else 0
        }
    }

def ensure_complete_skill_presence(skill_presence: dict, skill_categories: dict) -> dict:
    """Ensure all skills from categories are present in skill_presence with boolean values"""
    if not skill_presence:
        skill_presence = {}
    
    # Get all skills from all categories
    all_skills = []
    for category_skills in skill_categories.values():
        all_skills.extend(category_skills)
    
    # Ensure each skill has a boolean value
    for skill in all_skills:
        if skill not in skill_presence:
            skill_presence[skill] = False
        elif not isinstance(skill_presence[skill], bool):
            # Convert to boolean if not already
            skill_presence[skill] = bool(skill_presence[skill])
    
    return skill_presence

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
