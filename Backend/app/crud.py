import json
import hashlib
import logging
import os
from typing import Optional, List, Dict, Any
from supabase import Client
from supabase import create_client
from . import schemas
from .database import get_supabase
from .parsing import to_bool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _create_jd_content_hash(jd: schemas.JDModel) -> str:
    """
    Creates a SHA256 hash of the core, identifying content of the JD.
    This provides a unique fingerprint for the job description itself.
    """
    # Use key fields that define the job. 
    # Using .dict() ensures a consistent order for fields.
    # We might exclude fields that are less likely to be core identifiers 
    # or might vary (like datePosted if it's not part of the core posting)
    # For simplicity, we'll hash the whole JD dict, excluding database-specific fields.
    # A more refined approach could select specific fields.
    jd_dict_for_hashing = jd.dict(exclude_unset=True) 
    # Ensure consistent string representation for hashing
    content_str = json.dumps(jd_dict_for_hashing, sort_keys=True, separators=(',', ':'))
    content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    return content_hash

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

# User CRUD operations
def get_user(supabase: Client, user_id: str):
    """Get user by ID from Supabase Auth"""
    try:
        response = supabase.auth.admin.get_user_by_id(user_id)
        # Handle different response formats
        user_data = None
        if hasattr(response, 'user'):
            user_data = response.user
        elif isinstance(response, dict) and 'user' in response:
            user_data = response['user']
        elif hasattr(response, 'data'):
            user_data = response.data
        elif isinstance(response, dict) and 'data' in response:
            user_data = response['data']
        
        if user_data:
            return schemas.User(
                id=user_data.id,
                username=user_data.user_metadata.get("username", user_data.email.split('@')[0]),
                email=user_data.email,
                role=user_data.user_metadata.get("role", "recruiter"),
                is_active=True,
                created_at=user_data.created_at
            )
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
    return None

def get_user_by_email(supabase: Client, email: str):
    """Get user by email from Supabase"""
    try:
        # For now, we'll create a user schema from Supabase auth data
        # In a real implementation, you might want to store additional user data in a separate table
        response = supabase.auth.sign_in_with_otp({"email": email})
        if response:
            # This is a simplified approach - in reality, you'd need to properly query users
            return schemas.User(
                id="temp_id",
                username=email.split('@')[0],
                email=email,
                role="recruiter",
                is_active=True
            )
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
    return None

def get_users(supabase: Client, skip: int = 0, limit: int = 100, username: str = None):
    """Get users from Supabase Auth"""
    try:
        # For admin operations, create a fresh client to ensure proper auth context
        # This can help avoid initialization timing issues
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        if url and key:
            # Create a fresh client for admin operations
            admin_supabase: Client = create_client(url, key)
            response = admin_supabase.auth.admin.list_users()
        else:
            # Fallback to the provided client
            response = supabase.auth.admin.list_users()
        
        # Handle different response formats from Supabase client
        users = []
        if hasattr(response, 'users'):
            users = response.users
        elif isinstance(response, dict) and 'users' in response:
            users = response['users']
        elif isinstance(response, list):
            users = response
        elif hasattr(response, 'data'):
            data = response.data
            if isinstance(data, list):
                users = data
            elif isinstance(data, dict) and 'users' in data:
                users = data['users']
        elif isinstance(response, dict) and 'data' in response:
            data = response['data']
            if isinstance(data, list):
                users = data
            elif isinstance(data, dict) and 'users' in data:
                users = data['users']
        
        # Convert Supabase User objects to your User schema
        schema_users = [
            schemas.User(
                id=u.id,
                username=u.user_metadata.get("username", u.email.split('@')[0]),
                email=u.email,
                role=u.user_metadata.get("role", "recruiter"),
                is_active=True, # Supabase users are active by default
                created_at=u.created_at
            ) for u in users
        ]
        
        if username:
            schema_users = [u for u in schema_users if u.username == username]
            
        return schema_users[skip : skip + limit]
    except Exception as e:
        logger.error(f"Error getting users: {e}", exc_info=True)
        return []

def create_user(supabase: Client, user: schemas.UserCreate):
    """Create user in Supabase Auth"""
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        if response.user:
            user_data = response.user
            return schemas.User(
                id=user_data.id,
                username=user.username,
                email=user_data.email,
                role=user.role,
                is_active=True
            )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
    return None

def delete_user(supabase: Client, user_id: str):
    """Delete user from Supabase Auth"""
    try:
        response = supabase.auth.admin.delete_user(user_id)
        return response
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
    return None

# JobDescription CRUD operations
def get_jd(supabase: Client, jd_id: int):
    """Get job description by ID from Supabase"""
    try:
        response = supabase.table("job_descriptions").select("*").eq("id", jd_id).execute()
        if response.data:
            data = response.data[0]
            return schemas.JobDescription(
                id=data["id"],
                job_id_str=data.get("job_id_str"),
                content_hash=data["content_hash"],
                job_title=data["job_title"],
                company_name=data.get("company_name"),
                location=data.get("location"),
                ctc=data.get("ctc"),
                status=data.get("status", "Active"),
                details=data.get("details", {}),
                created_at=data.get("created_at")
            )
    except Exception as e:
        logger.error(f"Error getting job description: {e}")
    return None

def get_or_create_job_description(supabase: Client, jd: schemas.JDModel):
    """Get or create job description in Supabase"""
    try:
        # First, try to find by the LLM-provided jobId (if it exists and is not empty)
        db_jd_by_job_id = None
        if jd.jobId:
            response = supabase.table("job_descriptions").select("*").eq("job_id_str", jd.jobId).execute()
            if response.data:
                db_jd_by_job_id = response.data[0]
                logger.info(f"Found existing JD by jobId '{jd.jobId}' (ID: {db_jd_by_job_id['id']})")
                return _convert_to_schema(db_jd_by_job_id)

        # If not found by jobId, or jobId was missing/empty, use content hash
        content_hash = _create_jd_content_hash(jd)
        response = supabase.table("job_descriptions").select("*").eq("content_hash", content_hash).execute()
        
        if response.data:
            db_jd_by_hash = response.data[0]
            logger.info(f"Found existing JD by content hash '{content_hash}' (ID: {db_jd_by_hash['id']})")
            # If the found JD doesn't have a job_id_str, but the new one does, update it.
            if not db_jd_by_hash.get("job_id_str") and jd.jobId:
                logger.info(f"Updating existing JD (ID: {db_jd_by_hash['id']}) with jobId: {jd.jobId}")
                update_response = supabase.table("job_descriptions").update({
                    "job_id_str": jd.jobId
                }).eq("id", db_jd_by_hash["id"]).execute()
                if update_response.data:
                    db_jd_by_hash = update_response.data[0]
            return _convert_to_schema(db_jd_by_hash)

        # If not found by either method, create a new one
        logger.info(f"Creating new JD with content hash '{content_hash}'")
        location_str = f"{jd.location.city}, {jd.location.state}" if jd.location else None
        ctc_str = jd.compensationAndBenefits.salaryRange if jd.compensationAndBenefits else None

        insert_data = {
            "job_id_str": jd.jobId,
            "content_hash": content_hash,
            "job_title": jd.jobTitle,
            "company_name": jd.companyProfile.companyName,
            "location": location_str,
            "ctc": ctc_str,
            "details": jd.dict()
        }
        
        response = supabase.table("job_descriptions").insert(insert_data).execute()
        if response.data:
            return _convert_to_schema(response.data[0])
    except Exception as e:
        logger.error(f"Error getting or creating job description: {e}")
    return None

def get_jds(supabase: Client, skip: int = 0, limit: int = 100):
    """Get job descriptions from Supabase"""
    try:
        response = supabase.table("job_descriptions").select("*").range(skip, skip + limit - 1).execute()
        if response.data:
            return [_convert_to_schema(item) for item in response.data]
    except Exception as e:
        logger.error(f"Error getting job descriptions: {e}")
    return []

def update_jd(supabase: Client, jd_id: int, jd_update: schemas.JobDescriptionUpdate):
    """Update job description in Supabase"""
    try:
        update_data = jd_update.dict(exclude_unset=True)
        if update_data:
            response = supabase.table("job_descriptions").update(update_data).eq("id", jd_id).execute()
            if response.data:
                return _convert_to_schema(response.data[0])
    except Exception as e:
        logger.error(f"Error updating job description: {e}")
    return None

def update_jd_details(supabase: Client, jd_id: int, jd_update: schemas.JobDescriptionDetailUpdate):
    """Update job description details in Supabase"""
    try:
        jd_model = jd_update.details
        # Recalculate content_hash based on the new full details
        new_content_hash = _create_jd_content_hash(jd_model)
        
        update_data = {
            "details": jd_model.dict(),
            "job_title": jd_model.jobTitle,
            "company_name": jd_model.companyProfile.companyName,
            "location": f"{jd_model.location.city}, {jd_model.location.state}" if jd_model.location else None,
            "ctc": jd_model.compensationAndBenefits.salaryRange if jd_model.compensationAndBenefits else None,
            "content_hash": new_content_hash
        }
        
        response = supabase.table("job_descriptions").update(update_data).eq("id", jd_id).execute()
        if response.data:
            return _convert_to_schema(response.data[0])
    except Exception as e:
        logger.error(f"Error updating job description details: {e}")
    return None

def get_jd_results(supabase: Client, jd_id: int):
    """Get job description results from Supabase"""
    try:
        response = supabase.table("analysis_results").select("""
            *,
            job_description:job_descriptions(*),
            candidate:candidates(*)
        """).eq("job_description_id", jd_id).execute()
        if response.data:
            results = []
            for item in response.data:
                # Convert to schema (simplified)
                results.append(schemas.AnalysisResult(
                    id=item["id"],
                    score=item["score"],
                    match_level=item["match_level"],
                    details=item.get("details", {}),
                    candidate=schemas.Candidate(
                        id=item["candidate"]["id"],
                        name=item["candidate"]["name"],
                        email=item["candidate"]["email"]
                    ) if item.get("candidate") else None
                ))
            return results
    except Exception as e:
        logger.error(f"Error getting job description results: {e}")
    return []

def get_user_analyses(supabase: Client, user_id: str):
    """Get user analyses from Supabase"""
    try:
        response = supabase.table("analysis_results").select("""
            *,
            job_description:job_descriptions(*),
            candidate:candidates(*)
        """).eq("user_id", user_id).execute()
        if response.data:
            results = []
            for item in response.data:
                # Convert to schema (simplified)
                candidate_data = item.get("candidate")
                candidate = None
                if candidate_data:
                    candidate = schemas.Candidate(
                        id=candidate_data["id"],
                        name=candidate_data["name"],
                        email=candidate_data["email"],
                        phone=candidate_data.get("phone"),
                        assessment_result=candidate_data.get("assessment_result"),
                        recruiter_id=candidate_data.get("recruiter_id"),
                        uploaded_at=candidate_data.get("uploaded_at")
                    )
                
                results.append(schemas.AnalysisResult(
                    id=item["id"],
                    score=item["score"],
                    match_level=item["match_level"],
                    details=item.get("details", {}),
                    candidate=candidate
                ))
            return results
    except Exception as e:
        logger.error(f"Error getting user analyses: {e}")
    return []

# Candidate CRUD operations
def get_or_create_candidate(supabase: Client, cv: schemas.CVModel, recruiter_id: str, assessment_result: str = None):
    """Get or create candidate in Supabase"""
    try:
        # First, try to find by email
        response = supabase.table("candidates").select("*").eq("email", cv.Personal_Data.email).execute()
        if response.data:
            # Update existing candidate
            candidate_data = response.data[0]
            update_data = {
                "name": f"{cv.Personal_Data.firstName or ''} {cv.Personal_Data.lastName or ''}".strip(),
                "phone": cv.Personal_Data.phone,
                "recruiter_id": recruiter_id,
                "assessment_result": assessment_result
            }
            update_response = supabase.table("candidates").update(update_data).eq("id", candidate_data["id"]).execute()
            if update_response.data:
                return _convert_candidate_to_schema(update_response.data[0])
        
        # Create new candidate
        insert_data = {
            "name": f"{cv.Personal_Data.firstName or ''} {cv.Personal_Data.lastName or ''}".strip(),
            "email": cv.Personal_Data.email,
            "phone": cv.Personal_Data.phone,
            "recruiter_id": recruiter_id,
            "assessment_result": assessment_result
        }
        response = supabase.table("candidates").insert(insert_data).execute()
        if response.data:
            return _convert_candidate_to_schema(response.data[0])
    except Exception as e:
        logger.error(f"Error getting or creating candidate: {e}")
    return None

# AnalysisResult CRUD operations
def create_analysis_result(supabase: Client, jd_db_id: int, candidate_db_id: int, user_id: str, result: dict):
    """Create analysis result in Supabase"""
    try:
        insert_data = {
            "job_description_id": jd_db_id,
            "candidate_id": candidate_db_id,
            "user_id": user_id,
            "score": result["match_score"],
            "match_level": result["match_level"],
            "details": result["match_details"]
        }
        response = supabase.table("analysis_results").insert(insert_data).execute()
        if response.data:
            return _convert_analysis_result_to_schema(response.data[0])
    except Exception as e:
        logger.error(f"Error creating analysis result: {e}")
    return None

# Helper functions
def _convert_to_schema(data: Dict[str, Any]) -> schemas.JobDescription:
    """Convert database data to JobDescription schema"""
    return schemas.JobDescription(
        id=data["id"],
        job_id_str=data.get("job_id_str"),
        content_hash=data["content_hash"],
        job_title=data["job_title"],
        company_name=data.get("company_name"),
        location=data.get("location"),
        ctc=data.get("ctc"),
        status=data.get("status", "Active"),
        details=data.get("details", {}),
        created_at=data.get("created_at")
    )

def _convert_candidate_to_schema(data: Dict[str, Any]) -> schemas.Candidate:
    """Convert database data to Candidate schema"""
    return schemas.Candidate(
        id=data["id"],
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        assessment_result=data.get("assessment_result"),
        recruiter_id=data.get("recruiter_id"),
        uploaded_at=data.get("uploaded_at")
    )

def _convert_analysis_result_to_schema(data: Dict[str, Any]) -> schemas.AnalysisResult:
    """Convert database data to AnalysisResult schema"""
    return schemas.AnalysisResult(
        id=data["id"],
        job_description_id=data["job_description_id"],
        candidate_id=data["candidate_id"],
        user_id=data["user_id"],
        score=data["score"],
        match_level=data["match_level"],
        details=data.get("details", {}),
        created_at=data.get("created_at")
    )