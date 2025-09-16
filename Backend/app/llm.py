import os
import json
import re
import groq
import threading
from typing import Optional, Dict, List
from dotenv import load_dotenv
from groq import APIError

from .parsing import preprocess_resume_text, clean_json_response
from .schemas import JDModel, CVModel

load_dotenv()

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemma2-9b-it")

client = None
_client_lock = threading.Lock()

def get_groq_client():
    global client
    if client is not None:
        return client
    
    with _client_lock:
        if client is None:
            GROK_API_KEY = os.getenv('GROK_API_KEY')
            if not GROK_API_KEY:
                raise ValueError("GROK_API_KEY environment variable is not set. Please set it in your .env file or environment.")
            client = groq.Groq(api_key=GROK_API_KEY)
    return client

class LLMJsonError(Exception):
    """Custom exception for errors related to LLM JSON processing."""
    pass

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
  ],
  "age_filter": {
      "min_age": "Optional[integer]",
      "max_age": "Optional[integer]"
  },
  "gender_filter": "Optional[string]"
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
        },
        "age": "Optional[integer]",
        "gender": "Optional[string]"
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

def convert_resume_to_json(resume_text: str, jd_skill_categories: Optional[Dict[str, List[str]]] = None) -> dict:
    local_client = get_groq_client()
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
- Extract age and gender if available.
- For the fields "age_filter.min_age", "age_filter.max_age", "Analytics.education_gap.gap_duration_years" only use an integer value or null. Do not use strings like "Unknown", "N/A", or any non-integer value. If the value is not specified or not a number, set it to null.
- Do not make up or infer information that is not explicitly stated.
{skill_presence_instruction}
Schema:
{schema}
Resume Text:
{cleaned_text}
NOTE: Output only valid JSON matching the exact schema structure.
"""
        response = local_client.chat.completions.create(
            model=LLM_MODEL_NAME,
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
        except json.JSONDecodeError:
            raise LLMJsonError("Could not parse the response from the AI service as JSON.")
    except APIError as e:
        # Explicitly catch and re-raise APIError as LLMJsonError for consistent error handling by the caller
        raise LLMJsonError(f"The AI service returned an error: {e.message}") from e
    except Exception as e:
        # Catch any other unexpected errors (e.g., network issues, Groq library errors) and wrap them
        raise LLMJsonError(f"An unexpected error occurred while processing the resume: {e}") from e

def convert_jd_to_json(jd_text: str) -> dict:
    local_client = get_groq_client()
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
- For 'applicationInfo.contactEmail', if no valid email address is found, return null.
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
- Extract age and gender filters if specified.
- For the fields "age_filter.min_age" and "age_filter.max_age", only use an integer value or null. Do not use strings like "Unknown", "N/A", or any non-integer value. If the value is not specified or not a number, set it to null.
- Do not format the response in Markdown or any other format. Just output raw JSON.
Schema:
{schema}
Job Description Text:
{jd_text}
NOTE: Please output only a valid JSON matching the EXACT schema.
"""
        response = local_client.chat.completions.create(
            model=LLM_MODEL_NAME,
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
        except json.JSONDecodeError:
            raise LLMJsonError("Could not parse the response from the AI service as JSON.")
    except APIError as e:
        # Explicitly catch and re-raise APIError as LLMJsonError for consistent error handling by the caller
        raise LLMJsonError(f"The AI service returned an error: {e.message}") from e
    except Exception as e:
        # Catch any other unexpected errors (e.g., network issues, Groq library errors) and wrap them
        raise LLMJsonError(f"An unexpected error occurred while processing the job description: {e}") from e

def generate_interview_questions(jd: JDModel, cv: CVModel) -> list:
    local_client = get_groq_client()
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
    try:
        response = local_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert HR interviewer. Generate only interview questions as a JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        content = response.choices[0].message.content.strip()
        questions = json.loads(clean_json_response(content))
        if isinstance(questions, list):
            return [str(q) for q in questions if isinstance(q, str)]
    except (APIError, json.JSONDecodeError) as e:
        # Catch API errors and JSON parsing errors, re-raise as LLMJsonError
        raise LLMJsonError(f"Could not generate interview questions: {e}") from e
    except Exception as e:
        # Catch any other unexpected errors and wrap them in LLMJsonError
        raise LLMJsonError(f"An unexpected error occurred while generating interview questions: {e}") from e
