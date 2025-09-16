from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# Pydantic models for Supabase data structures
class User(BaseModel):
    id: str  # Supabase uses UUIDs
    username: str
    email: str
    role: str = "recruiter"
    is_active: bool = True
    created_at: Optional[datetime] = None

class JobDescription(BaseModel):
    id: Optional[int] = None
    job_id_str: Optional[str] = None
    content_hash: str
    job_title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    ctc: Optional[str] = None
    status: str = "Active"
    details: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

class Candidate(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = None
    assessment_result: Optional[str] = None
    recruiter_id: Optional[str] = None  # Supabase uses UUIDs
    uploaded_at: Optional[datetime] = None

class AnalysisResult(BaseModel):
    id: Optional[int] = None
    job_description_id: int
    candidate_id: int
    user_id: str  # Supabase uses UUIDs
    score: float
    match_level: str
    details: Dict[str, Any] = {}
    created_at: Optional[datetime] = None