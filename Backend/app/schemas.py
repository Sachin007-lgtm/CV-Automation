from pydantic import BaseModel, Field, root_validator, EmailStr, validator
from typing import Dict, List, Any, Tuple, Optional, Union
from datetime import datetime
import phonenumbers

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Database Schemas

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str  # Supabase uses UUIDs
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    assessment_result: Optional[str] = None

class CandidateCreate(CandidateBase):
    recruiter_id: str  # Supabase uses UUIDs

class Candidate(CandidateBase):
    id: Optional[int] = None
    recruiter_id: Optional[str] = None  # Supabase uses UUIDs
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisResultBase(BaseModel):
    score: float
    match_level: str
    details: Dict[str, Any]

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResult(AnalysisResultBase):
    id: Optional[int] = None
    candidate: Optional[Candidate] = None

    class Config:
        from_attributes = True

class JobDescriptionBase(BaseModel):
    job_id_str: Optional[str] = None
    content_hash: str
    job_title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    ctc: Optional[str] = None
    status: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    content_hash: Optional[str] = None  # Backend generates this, make it optional for creation
    details: Dict[str, Any]

class JobDescriptionUpdate(BaseModel):
    status: Optional[str] = None

class JobDescription(JobDescriptionBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    details: Dict[str, Any]
    results: List[AnalysisResult] = Field(default_factory=list)

    class Config:
        from_attributes = True


# LLM and Matching Schemas

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
    required: List[str] = Field(default_factory=list)
    preferred: List[str] = Field(default_factory=list)

class CompensationBenefits(BaseModel):
    salaryRange: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)

class ApplicationInfo(BaseModel):
    howToApply: Optional[str] = None
    applyLink: Optional[str] = None
    contactEmail: Optional[EmailStr] = None

class AgeFilter(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    @root_validator(pre=True)
    def coerce_non_int_to_none(cls, values):
        for field in ['min_age', 'max_age']:
            val = values.get(field)
            if isinstance(val, str):
                if not val.isdigit():
                    values[field] = None
                else:
                    values[field] = int(val)
            elif not (val is None or isinstance(val, int)):
                values[field] = None
        return values

class JDModel(BaseModel):
    jobId: Optional[str] = None
    jobTitle: str
    companyProfile: CompanyProfile
    location: LocationModel
    datePosted: Optional[str] = None
    employmentType: Optional[str] = None
    jobSummary: str
    keyResponsibilities: List[str]
    qualifications: Qualifications
    requiredSkills: Union[List[str], Dict[str, List[str]]] = Field(default_factory=list)  # Accepts both flat and categorized
    educationRequired: List[str] = Field(default_factory=list)
    compensationAndBenefits: CompensationBenefits
    applicationInfo: ApplicationInfo
    extractedKeywords: List[str]
    age_filter: Optional[AgeFilter] = None
    gender_filter: Optional[str] = None

class JobDescriptionDetailUpdate(BaseModel):
    details: JDModel

class PersonalData(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    location: LocationModel
    age: Optional[int] = None
    gender: Optional[str] = None

    @root_validator(pre=True)
    def coerce_non_int_age_to_none(cls, values):
        age = values.get('age')
        if isinstance(age, str):
            if not age.isdigit():
                values['age'] = None
            else:
                values['age'] = int(age)
        elif not (age is None or isinstance(age, int)):
            values['age'] = None
        return values

    @validator('phone')
    def validate_phone_number(cls, v):
        if v is None:
            return None
        try:
            # First try to parse without a default region
            parsed_phone = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(
                parsed_phone, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.phonenumberutil.NumberParseException:
            # If that fails, try to parse with a default region (India as fallback for Indian numbers)
            # This handles cases where the phone number is missing the country code
            try:
                parsed_phone = phonenumbers.parse(v, "IN")  # Assume India as default
                if phonenumbers.is_valid_number(parsed_phone):
                    return phonenumbers.format_number(
                        parsed_phone, phonenumbers.PhoneNumberFormat.E164
                    )
                else:
                    # If still not valid, return the original value or None
                    return v if v else None
            except phonenumbers.phonenumberutil.NumberParseException:
                # If all parsing attempts fail, return the original value or None
                return v if v else None

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
    description: List[str] = Field(default_factory=list)
    technologiesUsed: List[str] = Field(default_factory=list)

class Project(BaseModel):
    projectName: Optional[str] = None
    description: Optional[str] = None
    technologiesUsed: List[str] = Field(default_factory=list)
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
    gap_duration_years: Optional[float] = 0

class KeywordAnalysis(BaseModel):
    teamwork: bool = False
    management_experience: bool = False
    geographic_experience: bool = False
    extracted_keywords: List[str] = Field(default_factory=list)

class Analytics(BaseModel):
    job_stability: JobStability
    education_gap: EducationGap
    keyword_analysis: KeywordAnalysis
    suggested_role: str

class CVModel(BaseModel):
    UUID: Optional[str] = None
    Personal_Data: PersonalData = Field(alias="Personal Data")
    education_list: List[Education] = Field(alias="Education", default_factory=list)
    experiences_list: List[Experience] = Field(alias="Experiences", default_factory=list)
    projects_list: List[Project] = Field(alias="Projects", default_factory=list)
    skills_list: List[Skill] = Field(alias="Skills", default_factory=list)
    research_work_list: List[Dict[str, Any]] = Field(alias="Research Work", default_factory=list)
    achievements_list: List[str] = Field(alias="Achievements", default_factory=list)
    Analytics: Analytics
    skill_presence: Optional[Dict[str, bool]] = None

    class Config:
        validate_by_name = True

class MatchRequest(BaseModel):
    jd: JDModel
    cvs: List[CVModel]

# API Response Models
class ExtractedCVResponse(BaseModel):
    cv_json: CVModel
    skill_presence: Dict[str, bool]

class MatchResult(BaseModel):
    candidate_id: Optional[str]
    candidate_name: str
    match_score: float
    match_level: str
    match_details: Dict[str, Any]
    critical_skill_status: str
    critical_present: List[str]
    critical_absent: List[str]
    present_skills: List[str]
    absent_skills: List[str]
    disclaimer: Optional[str]
    job_stability: JobStability
    education_gap: EducationGap
    suggested_role: str
    interview_questions: List[str]
    skill_presence: Dict[str, bool]
    filter_status: Dict[str, Any]

class MatchingMetadata(BaseModel):
    job_title: str
    candidates_evaluated: int
    top_match_score: float
    average_match_score: float

class MatchResponse(BaseModel):
    results: List[MatchResult]
    matching_metadata: MatchingMetadata