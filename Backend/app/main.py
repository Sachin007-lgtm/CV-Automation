from fastapi import FastAPI, UploadFile, File, Form, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import tempfile
import shutil
import os
import json
import nltk
import secrets
import logging
from typing import List
from datetime import timedelta
import pydantic

from app import crud, schemas, auth, llm
from app.database import get_supabase
from app.schemas import JDModel, CVModel
from app.parsing import extract_text_from_file, clean_resume_json, to_bool
from app.llm import convert_jd_to_json, convert_resume_to_json, generate_interview_questions
from app.matching import compute_similarity, get_match_level

logging.basicConfig(level=logging.INFO)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
    "text/plain", # .txt
    "application/msword" # .doc
]

app = FastAPI()

def download_nltk_data():
    """Downloads the necessary NLTK data if not already present."""
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logging.info("Downloading NLTK data: wordnet")
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        logging.info("Downloading NLTK data: omw-1.4")
        nltk.download('omw-1.4')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logging.info("Downloading NLTK data: stopwords")
        nltk.download('stopwords')

@app.on_event("startup")
def startup_event():
    # Skip startup event during testing
    import os
    if os.getenv("TESTING") == "1":
        return
    
    logging.info("Running startup tasks...")
    # download_nltk_data()
    logging.info("Startup tasks completed.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token endpoint for Supabase authentication
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase = Depends(get_supabase)
):
    """Authenticate user with Supabase and return access token"""
    try:
        # Try normal sign in first
        response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if response and response.session:
            # Return the Supabase access token
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer"
            }
    except Exception as e:
        # If email confirmation is required, we can't sign in normally
        # For development, we'll return a more helpful error message
        if "Email not confirmed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not confirmed. Please check your email for confirmation link.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect username or password: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# User routes
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_admin_user)):
    # Only admins can create new users
    logging.info(f"Attempting to create user: {user.email} with role: {user.role}")
    try:
        # Log the Supabase URL and key length for debugging (don't log the actual key)
        supabase_url = os.environ.get("SUPABASE_URL", "NOT SET")
        supabase_key = os.environ.get("SUPABASE_KEY", "NOT SET")
        logging.info(f"Using Supabase URL: {supabase_url}, Key length: {len(supabase_key) if supabase_key != 'NOT SET' else 'N/A'}")
        
        # Create the user in Supabase Auth
        response = supabase.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": True,  # Set to False if you don't want email confirmation
            "user_metadata": {
                "username": user.username,
                "role": user.role
            }
        })
        
        new_user = response.user
        if new_user:
            logging.info(f"Successfully created user: {new_user.email}")
            return schemas.User(
                id=new_user.id,
                username=new_user.user_metadata.get("username", new_user.email),
                email=new_user.email,
                role=new_user.user_metadata.get("role", "recruiter"),
                is_active=True,
                created_at=new_user.created_at
            )
        else:
            logging.error("Could not create user: response.user is None")
            raise HTTPException(status_code=400, detail="Could not create user")
    except Exception as e:
        logging.error(f"Error creating user in Supabase: {e}", exc_info=True)
        # Provide more specific error information
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg or "User not allowed" in error_msg:
            error_msg += " - This indicates the service role key may not have proper permissions. Please verify:" \
                        " 1) SUPABASE_KEY in .env is a service role key (not an anon/public key)" \
                        " 2) The service role key has admin privileges in your Supabase project" \
                        " 3) Your Supabase project settings allow admin user creation"
        raise HTTPException(status_code=400, detail=f"Error creating user: {error_msg}")

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, username: str = None, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_admin_user)):
    users = crud.get_users(supabase, skip=skip, limit=limit, username=username)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: str, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_admin_user)):
    db_user = crud.get_user(supabase, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: str, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_admin_user)):
    db_user = crud.delete_user(supabase, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/extract_jd", response_model=schemas.JDModel)
async def extract_jd(
    jd_file: UploadFile = File(...),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if jd_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {jd_file.content_type}. Allowed types are: pdf, docx, txt, doc")
    
    jd_file.file.seek(0, 2)
    file_size = jd_file.file.tell()
    jd_file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds the limit of 10MB")

    if current_user.role not in ["admin", "backend_team"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action."
        )
    with tempfile.TemporaryDirectory() as tmpdir:
        sanitized_filename = os.path.basename(jd_file.filename)
        jd_path = os.path.join(tmpdir, sanitized_filename)
        with open(jd_path, "wb") as f:
            shutil.copyfileobj(jd_file.file, f)
        
        jd_text = extract_text_from_file(jd_path)
        if not jd_text:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from {jd_file.filename}")
        
        try:
            jd_json = convert_jd_to_json(jd_text)
        except llm.LLMJsonError as e:
            logging.error(f"Failed to process JD from file {jd_file.filename}: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail=f"Failed to process job description: The AI service encountered an error.")
        
        return jd_json

@app.post("/save_jd", response_model=schemas.JobDescription)
async def save_jd(
    jd_json: dict = Body(...),
    supabase = Depends(get_supabase),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if current_user.role not in ["admin", "backend_team"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action."
        )
    
    required_skills = jd_json.get("requiredSkills", [])
    if isinstance(required_skills, dict):
        flat_skills = [s for cat in required_skills.values() for s in cat]
        jd_json_flat = {**jd_json, "requiredSkills": flat_skills}
    else:
        jd_json_flat = jd_json
        
    try:
        jd_obj = JDModel.parse_obj(jd_json_flat)
    except pydantic.ValidationError as e:
        logging.error(f"Pydantic validation error for JD data: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JD data provided. Validation errors: {e.errors()}"
        )
    
    db_jd = crud.get_or_create_job_description(supabase=supabase, jd=jd_obj)
    
    return db_jd

def ensure_complete_skill_presence(skill_presence: dict, skill_categories: dict) -> dict:
    """Ensure all skills from categories are present in skill_presence with boolean values"""
    if not skill_presence:
        skill_presence = {}
    
    all_skills = [skill for category_skills in skill_categories.values() for skill in category_skills]
    
    for skill in all_skills:
        if skill not in skill_presence:
            skill_presence[skill] = False
        else:
            skill_presence[skill] = to_bool(skill_presence[skill])
    
    return skill_presence

@app.post("/extract_resumes", response_model=List[schemas.ExtractedCVResponse])
async def extract_resumes(
    resume_files: list[UploadFile] = File(...),
    jd_json: str = Form(...),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    for resume_file in resume_files:
        if resume_file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type for {resume_file.filename}: {resume_file.content_type}.")

        resume_file.file.seek(0, 2)
        file_size = resume_file.file.tell()
        resume_file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File {resume_file.filename} exceeds size limit of 10MB")

    jd_json = json.loads(jd_json)
    required_skills = jd_json.get("requiredSkills", [])
    skill_categories = None
    if isinstance(required_skills, dict):
        skill_categories = required_skills
    
    results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for resume_file in resume_files:
            sanitized_filename = os.path.basename(resume_file.filename)
            resume_path = os.path.join(tmpdir, sanitized_filename)
            with open(resume_path, "wb") as f:
                shutil.copyfileobj(resume_file.file, f)
                resume_file.file.seek(0) # Reset file pointer after reading

            resume_text = extract_text_from_file(resume_path)
            if not resume_text:
                logging.warning(f"Could not extract text from {resume_file.filename}, skipping.")
                continue
            try:
                resume_json = convert_resume_to_json(resume_text, skill_categories)
            except llm.LLMJsonError as e:
                logging.error(f"Could not process resume {resume_file.filename}: {e}")
                # Continue processing other resumes, but the result will be missing for this one
                continue
            resume_json = clean_resume_json(resume_json)
            # Ensure skill_presence is complete if JD skill categories were provided
            # This guarantees a consistent structure for downstream processing.
            if skill_categories:
                resume_json["skill_presence"] = ensure_complete_skill_presence(
                    resume_json.get("skill_presence", {}), 
                    skill_categories
                )
            else:
                # If no categories were provided, ensure skill_presence is at least a dict
                resume_json["skill_presence"] = resume_json.get("skill_presence", {})
            results.append({
                "cv_json": resume_json,
                "skill_presence": resume_json["skill_presence"] # Use the (now complete) skill_presence from resume_json
            })
    return results

@app.post("/match", response_model=schemas.MatchResponse)
async def match(
    jd_json: dict = Body(...),
    cvs: list = Body(...),
    supabase = Depends(get_supabase),
    current_user: schemas.User = Depends(auth.get_current_user) 
):
    recruiter_id = current_user.id
    
    required_skills = jd_json.get("requiredSkills", [])
    skill_categories = None
    if isinstance(required_skills, dict):
        skill_categories = required_skills
        flat_skills = [s for cat in required_skills.values() for s in cat]
        jd_json_flat = {**jd_json, "requiredSkills": flat_skills}
    else:
        flat_skills = required_skills
        jd_json_flat = jd_json

    jd_obj = JDModel.parse_obj(jd_json_flat)

    # Optional per-JD overrides for skill weights and rejection rules
    skill_weights = (jd_json.get("skillWeights") or {}) if isinstance(jd_json, dict) else {}
    rejection_rules = (jd_json.get("rejectionRules") or {}) if isinstance(jd_json, dict) else {}
    
    # Save JD to DB
    db_jd = crud.get_or_create_job_description(supabase=supabase, jd=jd_obj)

    results = []
    for cv_entry in cvs:
        cv_json = cv_entry["cv_json"]
        skill_presence = cv_entry.get("skill_presence", {})
        cv_obj = CVModel.parse_obj(cv_json)

        # Save candidate to DB
        db_candidate = crud.get_or_create_candidate(supabase=supabase, cv=cv_obj, recruiter_id=recruiter_id)

        # Filtering, matching, etc. (existing logic)
        filter_status = {"passed": True, "reason": ""}
        # ... (rest of the filtering logic)

        # Use weighted skill matching if skill categories are available
        if skill_categories:
            # Pass overrides through context by attaching to details after computation
            score, details = compute_similarity(jd_obj, cv_obj, skill_categories, skill_presence)
            # Recompute skills with custom weights/status if overrides provided
            if skill_weights or rejection_rules:
                from .matching import calculate_weighted_skills_match, calculate_match_status
                skills_match, skills_details = calculate_weighted_skills_match(
                    skill_categories,
                    skill_presence,
                    critical_weight=skill_weights.get("critical"),
                    important_weight=skill_weights.get("important"),
                    desired_weight=skill_weights.get("desired"),
                    base_skill_score=skill_weights.get("base")
                )
                status = calculate_match_status(
                    skills_match,
                    skills_details,
                    "weighted",
                    pass_min=rejection_rules.get("passMin", 0.7),
                    reject_below=rejection_rules.get("rejectBelow", 0.4),
                    critical_min_percent=rejection_rules.get("criticalMinPercent", 70.0)
                )
                details["skills_match"] = round(float(skills_match), 4)
                details["skills_details"] = skills_details
                details["skills_match_type"] = "weighted"
                details["status"] = status
        else:
            score, details = compute_similarity(jd_obj, cv_obj)
        
        # This part reconstructs all the details needed by the frontend
        present = [s for s in flat_skills if skill_presence.get(s, False)]
        absent = [s for s in flat_skills if not skill_presence.get(s, False)]
        critical_skills = skill_categories.get("critical", []) if skill_categories else []
        if not critical_skills:
            critical_skill_status = "Not Applicable"
            critical_present = []
            critical_absent = []
        else:
            critical_present = [s for s in critical_skills if skill_presence.get(s, False)]
            critical_absent = [s for s in critical_skills if not skill_presence.get(s, False)]
        
            if len(critical_absent) == 0 and len(critical_present) > 0:
                critical_skill_status = "All Present"
            elif len(critical_present) == 0 and len(critical_absent) > 0:
                critical_skill_status = "All Absent"
            else:
                critical_skill_status = "Partial Present"
        
        disclaimer = "Disclaimer: None of the critical required skills are present in this CV." if critical_skill_status == "All Absent" else None

        result_data = {
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
            "skill_presence": skill_presence,
            "filter_status": filter_status
        }
        results.append(result_data)

        # Save analysis result to DB, ensuring details are stored
        if db_jd and db_candidate:
            crud.create_analysis_result(
                supabase=supabase,
                jd_db_id=db_jd.id,
                candidate_db_id=db_candidate.id,
                user_id=current_user.id,
                result={
                    "match_score": result_data["match_score"],
                    "match_level": result_data["match_level"],
                    "match_details": result_data["match_details"]
                }
            )

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

@app.get("/jds", response_model=List[schemas.JobDescription])
def read_jds(skip: int = 0, limit: int = 100, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_user)):
    jds = crud.get_jds(supabase, skip=skip, limit=limit)
    return jds

@app.get("/jds/{jd_id}", response_model=schemas.JobDescription)
def read_jd(jd_id: int, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_user)):
    db_jd = crud.get_jd(supabase, jd_id=jd_id)
    if db_jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return db_jd

@app.put("/jds/{jd_id}", response_model=schemas.JobDescription)
def update_jd_details(
    jd_id: int,
    jd_update: schemas.JobDescriptionDetailUpdate,
    supabase = Depends(get_supabase),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if current_user.role not in ["admin", "backend_team"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_jd = crud.update_jd_details(supabase, jd_id=jd_id, jd_update=jd_update)
    if db_jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return db_jd

@app.patch("/jds/{jd_id}", response_model=schemas.JobDescription)
def update_jd(
    jd_id: int,
    jd_update: schemas.JobDescriptionUpdate,
    supabase = Depends(get_supabase),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_jd = crud.update_jd(supabase, jd_id=jd_id, jd_update=jd_update)
    if db_jd is None:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return db_jd

@app.get("/jds/{jd_id}/results", response_model=List[schemas.AnalysisResult])
def read_jd_results(jd_id: int, supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_user)):
    results = crud.get_jd_results(supabase, jd_id=jd_id)
    return results

@app.get("/analyses", response_model=List[schemas.AnalysisResult])
def read_user_analyses(supabase = Depends(get_supabase), current_user: schemas.User = Depends(auth.get_current_user)):
    analyses = crud.get_user_analyses(supabase, user_id=current_user.id)
    return analyses

@app.post("/jds/upload", response_model=schemas.JobDescription)
async def upload_jd(
    jd_file: UploadFile = File(...),
    supabase = Depends(get_supabase),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if jd_file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {jd_file.content_type}. Allowed types are: pdf, docx, txt, doc")

    jd_file.file.seek(0, 2)
    file_size = jd_file.file.tell()
    jd_file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds the limit of 10MB")

    if current_user.role not in ["admin", "backend_team"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload Job Descriptions."
        )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        sanitized_filename = os.path.basename(jd_file.filename)
        jd_path = os.path.join(tmpdir, sanitized_filename)
        with open(jd_path, "wb") as f:
            shutil.copyfileobj(jd_file.file, f)
        
        jd_text = extract_text_from_file(jd_path)
        if not jd_text:
            raise HTTPException(status_code=400, detail=f"Failed to extract text from {jd_file.filename}")

        try:
            jd_json = convert_jd_to_json(jd_text)
        except llm.LLMJsonError as e:
            logging.error(f"Failed to process JD from file {jd_file.filename}: {e}", exc_info=True)
            raise HTTPException(status_code=502, detail=f"Failed to process job description: The AI service encountered an error.")
        
        # Flatten skills if they are categorized
        required_skills = jd_json.get("requiredSkills", [])
        if isinstance(required_skills, dict):
            flat_skills = [s for cat in required_skills.values() for s in cat]
            jd_json_flat = {**jd_json, "requiredSkills": flat_skills}
        else:
            jd_json_flat = jd_json
            
        try:
            jd_obj = JDModel.parse_obj(jd_json_flat)
        except pydantic.ValidationError as e:
            logging.error(f"Pydantic validation error for JD data from file {jd_file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"LLM extracted invalid JD data. Validation errors: {e.errors()}"
            )
        
        db_jd = crud.get_or_create_job_description(supabase=supabase, jd=jd_obj)
        
        return db_jd

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)