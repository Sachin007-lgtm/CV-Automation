from sentence_transformers import util
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import re
import os
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from dotenv import load_dotenv

from .schemas import JDModel, CVModel, Experience, Education, LocationModel, Skill, Qualifications

# Load environment variables
load_dotenv()

# Get weights from environment variables with defaults
TITLE_WEIGHT = float(os.getenv('MATCHING_TITLE_WEIGHT', 0.20))
RESPONSIBILITIES_WEIGHT = float(os.getenv('MATCHING_RESPONSIBILITIES_WEIGHT', 0.25))
EXPERIENCE_WEIGHT = float(os.getenv('MATCHING_EXPERIENCE_WEIGHT', 0.20))
EDUCATION_WEIGHT = float(os.getenv('MATCHING_EDUCATION_WEIGHT', 0.20))
SKILLS_WEIGHT = float(os.getenv('MATCHING_SKILLS_WEIGHT', 0.15))
LOCATION_WEIGHT = float(os.getenv('MATCHING_LOCATION_WEIGHT', 0.0))

# Skill category weights for weighted matching
CRITICAL_SKILLS_WEIGHT = float(os.getenv('CRITICAL_SKILLS_WEIGHT', 0.4))
IMPORTANT_SKILLS_WEIGHT = float(os.getenv('IMPORTANT_SKILLS_WEIGHT', 0.3))
DESIRED_SKILLS_WEIGHT = float(os.getenv('DESIRED_SKILLS_WEIGHT', 0.2))
BASE_SKILL_SCORE = float(os.getenv('BASE_SKILL_SCORE', 0.1))

# Get model name from environment variable with default
SENTENCE_TRANSFORMER_MODEL = os.getenv('SENTENCE_TRANSFORMER_MODEL', 'all-mpnet-base-v2')

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    return _model

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

DEGREE_HIERARCHY = {
    r"\bph\.?d\b|\bdoctor(?:ate)?\b|\bd\.?phil\b": 4,
    r"\bmaster\b|\bms\b|\bm\.?sc?\b|\bm\.?a\b|\bm\.?com\b|\bm\.?tech\b|\bmba\b|\bmca\b|\bl\.?l\.?m\b": 3,
    r"\bbachelor\b|\bbs\b|\bb\.?sc?\b|\bb\.?a\b|\bb\.?com\b|\bb\.?tech\b|\bbca\b|\bbba\b|\bbe\b|\bl\.?l\.?b\b|\bundergrad\b": 2,
    r"\bdiploma\b|\bcertificate\b|\bassociate\b|\badvance diploma\b": 1,
    r"\bhigh school\b|\bhsc\b|\bssc\b|\bsecondary\b|\bcbse\b|\bicse\b|\bgcse\b": 0
}

def normalize_degree(degree: str) -> str:
    return degree.lower().strip() if degree else ""

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

def extract_required_experience(qualifications: Qualifications, model) -> float:
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

def calculate_role_relevance(jd_title: str, cv_suggested_role: str, cv_experiences: List[Experience], model) -> float:
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

def calculate_field_similarity(cv_field: str, jd_text: str, model) -> float:
    if not cv_field or not jd_text:
        return 0.0
    cv_embed = model.encode([cv_field], convert_to_tensor=True)
    jd_embed = model.encode([jd_text], convert_to_tensor=True)
    return util.cos_sim(cv_embed, jd_embed).item()

def calculate_education_match(cv_education: list[Education], jd_education: list[str], model) -> float:
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
                    field_sim = calculate_field_similarity(cv_entry["field"], jd_req["field"], model)
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
    """Legacy function for backward compatibility - uses semantic similarity"""
    model = get_model()
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

def calculate_weighted_skills_match(skill_categories: Dict[str, List[str]], skill_presence: Dict[str, bool], *,
    critical_weight: float = None, important_weight: float = None, desired_weight: float = None, base_skill_score: float = None) -> Tuple[float, Dict]:
    """
    Calculate weighted skill matching score based on categorized skills and their presence in CV.
    
    Args:
        skill_categories: Dict with keys 'critical', 'important', 'extra' containing skill lists
        skill_presence: Dict mapping skill names to boolean presence values
    
    Returns:
        Tuple of (total_score, detailed_breakdown)
    """
    if not skill_categories or not skill_presence:
        return 0.0, {}
    
    # Resolve weights (allow per-call overrides)
    cw = CRITICAL_SKILLS_WEIGHT if critical_weight is None else float(critical_weight)
    iw = IMPORTANT_SKILLS_WEIGHT if important_weight is None else float(important_weight)
    dw = DESIRED_SKILLS_WEIGHT if desired_weight is None else float(desired_weight)
    base = BASE_SKILL_SCORE if base_skill_score is None else float(base_skill_score)

    # Initialize category scores
    category_scores = {}
    category_details = {}
    
    # Process each skill category
    for category, skills in skill_categories.items():
        if not skills:
            category_scores[category] = 0.0
            category_details[category] = {
                'present': [],
                'absent': [],
                'total': 0,
                'present_count': 0,
                'score': 0.0
            }
            continue
            
        present_skills = [skill for skill in skills if skill_presence.get(skill, False)]
        absent_skills = [skill for skill in skills if not skill_presence.get(skill, False)]
        
        # Calculate category score based on presence ratio
        presence_ratio = len(present_skills) / len(skills) if skills else 0.0
        
        # Apply category weight
        if category == 'critical':
            category_score = presence_ratio * cw
        elif category == 'important':
            category_score = presence_ratio * iw
        elif category == 'extra':
            category_score = presence_ratio * dw
        else:
            category_score = presence_ratio * 0.1  # Default weight for unknown categories
        
        category_scores[category] = category_score
        category_details[category] = {
            'present': present_skills,
            'absent': absent_skills,
            'total': len(skills),
            'present_count': len(present_skills),
            'score': category_score,
            'presence_ratio': presence_ratio
        }
    
    # Calculate total weighted score
    total_score = sum(category_scores.values()) + base
    
    # Ensure score is between 0 and 1
    total_score = min(1.0, max(0.0, total_score))
    
    return total_score, category_details

def calculate_match_status(skills_match: float, skills_details: Dict, skills_match_type: str, *,
    pass_min: float = 0.7, reject_below: float = 0.4, critical_min_percent: float = 70.0) -> str:
    """
    Calculate match status based on skill scores.
    
    Args:
        skills_match: Total skills match score (0-1)
        skills_details: Detailed breakdown of skill categories
        skills_match_type: Type of skills matching used ("weighted" or "semantic")
    
    Returns:
        Status string: "Pass", "Rejected", or "Pending"
    """
    # For weighted matching, check critical skills specifically
    if skills_match_type == "weighted" and skills_details:
        critical_details = skills_details.get('critical', {})
        if critical_details:
            critical_presence_ratio = critical_details.get('presence_ratio', 0.0)
            critical_score_percentage = critical_presence_ratio * 100
            
            # Rejected if critical skills less than configured threshold
            if critical_score_percentage < critical_min_percent:
                return "Rejected"
    
    # Pass if total skills score is 70% or higher
    if skills_match >= pass_min:
        return "Pass"
    
    # Rejected if total skills score is less than 40%
    if skills_match < reject_below:
        return "Rejected"
    
    # Pending for all other cases (40% <= skills_match < 70%)
    return "Pending"

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

def compute_similarity(jd: JDModel, cv: CVModel, skill_categories: Dict[str, List[str]] = None, skill_presence: Dict[str, bool] = None) -> Tuple[float, Dict]:
    """
    Compute similarity between JD and CV with optional weighted skill matching.
    
    Args:
        jd: Job Description model
        cv: CV model
        skill_categories: Optional dict with skill categories (critical, important, extra)
        skill_presence: Optional dict with skill presence boolean values
    
    Returns:
        Tuple of (final_score, details_dict)
    """
    model = get_model()
    suggested_role = cv.Analytics.suggested_role
    
    role_relevance = calculate_role_relevance(jd.jobTitle, suggested_role, cv.experiences_list, model)
    
    jd_title_emb = model.encode(jd.jobTitle)
    
    cv_experience_years = calculate_experience_years(cv.experiences_list)
    jd_required_years = extract_required_experience(jd.qualifications, model)
    
    cv_title_text = suggested_role if suggested_role else " ".join([exp.jobTitle for exp in cv.experiences_list if exp.jobTitle])
    
    cv_title_emb = model.encode(cv_title_text if cv_title_text else "")
    
    sim_title = cosine_similarity([jd_title_emb], [cv_title_emb])[0][0] if cv_title_text else 0.0
    sim_resp = calculate_combined_sim_resp(jd.keyResponsibilities, cv.experiences_list, model)
    
    experience_match = calculate_experience_match(cv_experience_years, jd_required_years, role_relevance)
    education_match = calculate_education_match(cv.education_list, jd.educationRequired, model)
    location_match = calculate_location_match(cv.Personal_Data.location, jd.location)
    
    # Calculate skills match - use weighted if categories provided, otherwise legacy
    if skill_categories is not None and skill_presence is not None:
        # Check if skill_categories has any actual skills
        has_skills = any(skills for skills in skill_categories.values() if skills)
        
        if has_skills:
            skills_match, skills_details = calculate_weighted_skills_match(skill_categories, skill_presence)
            skills_match_type = "weighted"
        else:
            # No skills in categories, fall back to semantic
            skills_match = calculate_skills_match(jd.requiredSkills, cv.skills_list)
            skills_details = {}
            skills_match_type = "semantic"
    else:
        # No categories or presence data, fall back to semantic
        skills_match = calculate_skills_match(jd.requiredSkills, cv.skills_list)
        skills_details = {}
        skills_match_type = "semantic"
    
    final_score = (
        TITLE_WEIGHT * sim_title +
        RESPONSIBILITIES_WEIGHT * sim_resp +
        EXPERIENCE_WEIGHT * experience_match +
        EDUCATION_WEIGHT * education_match +
        SKILLS_WEIGHT * skills_match +
        LOCATION_WEIGHT * location_match
    )
    
    # Calculate match status based on skills
    status = calculate_match_status(skills_match, skills_details, skills_match_type)
    
    details = {
        "job_title_similarity": round(float(sim_title), 4),
        "responsibilities_similarity": round(float(sim_resp), 4),
        "experience_suitability": round(float(experience_match), 4),
        "education_relevance": round(float(education_match), 4),
        "skills_match": round(float(skills_match), 4),
        "skills_match_type": skills_match_type,
        "skills_details": skills_details,
        "location_compatibility": round(float(location_match), 4),
        "role_relevance": round(float(role_relevance), 4),
        "candidate_exp_years": cv_experience_years,
        "required_exp_years": jd_required_years,
        "suggested_role": suggested_role,
        "status": status,
        "match_summary": generate_match_summary({
            "experience_suitability": experience_match,
            "education_relevance": education_match,
            "location_compatibility": location_match,
            "role_relevance": role_relevance,
            "candidate_exp_years": cv_experience_years,
            "required_exp_years": jd_required_years,
            "skills_match": skills_match
        })
    }
    
    return round(float(final_score), 4), details