import pytest
from pydantic import ValidationError
from app import schemas

def test_user_create_schema():
    """Test UserCreate schema validation."""
    # Valid user data
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "role": "recruiter"
    }
    
    user = schemas.UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "testpassword"
    assert user.role == "recruiter"

def test_user_create_schema_invalid_email():
    """Test UserCreate schema with invalid email."""
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "testpassword",
        "role": "recruiter"
    }
    
    with pytest.raises(ValidationError):
        schemas.UserCreate(**user_data)

def test_user_create_schema_missing_fields():
    """Test UserCreate schema with missing required fields."""
    # Missing username
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "role": "recruiter"
    }
    
    with pytest.raises(ValidationError):
        schemas.UserCreate(**user_data)
    
    # Missing email
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "role": "recruiter"
    }
    
    with pytest.raises(ValidationError):
        schemas.UserCreate(**user_data)

def test_jd_model_schema():
    """Test JDModel schema validation."""
    jd_data = {
        "jobId": "JD001",
        "jobTitle": "Software Engineer",
        "companyProfile": {
            "companyName": "Test Company"
        },
        "location": {
            "city": "San Francisco",
            "state": "CA",
            "country": "USA"
        },
        "datePosted": "2023-01-01",
        "jobSummary": "Test job",
        "keyResponsibilities": ["Responsibility 1"],
        "qualifications": {
            "required": ["Requirement 1"],
            "preferred": ["Preference 1"]
        },
        "requiredSkills": ["Python", "FastAPI"],
        "educationRequired": ["Bachelor's in Computer Science"],
        "compensationAndBenefits": {
            "salaryRange": "$100,000 - $150,000",
            "benefits": ["Health Insurance"]
        },
        "applicationInfo": {
            "howToApply": "Apply online",
            "applyLink": "https://test.com/apply",
            "contactEmail": "hr@test.com"
        },
        "extractedKeywords": ["Python", "FastAPI"]
    }
    
    jd = schemas.JDModel(**jd_data)
    assert jd.jobId == "JD001"
    assert jd.jobTitle == "Software Engineer"
    assert jd.companyProfile.companyName == "Test Company"

def test_jd_model_schema_categorized_skills():
    """Test JDModel schema with categorized skills."""
    jd_data = {
        "jobId": "JD001",
        "jobTitle": "Software Engineer",
        "companyProfile": {
            "companyName": "Test Company"
        },
        "location": {
            "city": "San Francisco",
            "state": "CA",
            "country": "USA"
        },
        "datePosted": "2023-01-01",
        "jobSummary": "Test job",
        "keyResponsibilities": ["Responsibility 1"],
        "qualifications": {
            "required": ["Requirement 1"],
            "preferred": ["Preference 1"]
        },
        "requiredSkills": {
            "critical": ["Python", "FastAPI"],
            "important": ["PostgreSQL"],
            "extra": ["Docker"]
        },
        "educationRequired": ["Bachelor's in Computer Science"],
        "compensationAndBenefits": {
            "salaryRange": "$100,000 - $150,000",
            "benefits": ["Health Insurance"]
        },
        "applicationInfo": {
            "howToApply": "Apply online",
            "applyLink": "https://test.com/apply",
            "contactEmail": "hr@test.com"
        },
        "extractedKeywords": ["Python", "FastAPI"]
    }
    
    jd = schemas.JDModel(**jd_data)
    assert jd.jobId == "JD001"
    assert isinstance(jd.requiredSkills, dict)
    assert "Python" in jd.requiredSkills["critical"]

def test_cv_model_schema():
    """Test CVModel schema validation."""
    cv_data = {
        "UUID": "12345",
        "Personal Data": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "phone": "+1-234-567-8900",
            "linkedin": "https://linkedin.com/in/johndoe",
            "portfolio": "https://johndoe.com",
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "country": "USA"
            },
            "age": 30,
            "gender": "Male"
        },
        "Education": [
            {
                "institution": "Test University",
                "degree": "Bachelor of Science",
                "fieldOfStudy": "Computer Science",
                "startDate": "2015-09-01",
                "endDate": "2019-06-01",
                "grade": "3.8",
                "description": "Studied computer science"
            }
        ],
        "Experiences": [
            {
                "jobTitle": "Software Engineer",
                "company": "Test Company",
                "location": "San Francisco, CA",
                "startDate": "2019-07-01",
                "endDate": "2023-01-01",
                "description": ["Developed applications", "Worked with team"],
                "technologiesUsed": ["Python", "FastAPI"]
            }
        ],
        "Projects": [
            {
                "projectName": "Test Project",
                "description": "A test project",
                "technologiesUsed": ["Python", "FastAPI"],
                "link": "https://github.com/test/project",
                "startDate": "2020-01-01",
                "endDate": "2020-06-01"
            }
        ],
        "Skills": [
            {"category": "Programming", "skillName": "Python"},
            {"category": "Web Frameworks", "skillName": "FastAPI"}
        ],
        "Research Work": [
            {
                "title": "Test Research",
                "publication": "Test Journal",
                "date": "2022-01-01",
                "link": "https://research.com/test",
                "description": "Test research work"
            }
        ],
        "Achievements": ["Award 1", "Recognition 2"],
        "Analytics": {
            "job_stability": {
                "average_duration_years": 2.5,
                "frequent_switching_flag": False
            },
            "education_gap": {
                "has_gap": False,
                "gap_duration_years": 0
            },
            "keyword_analysis": {
                "teamwork": True,
                "management_experience": False,
                "geographic_experience": True,
                "extracted_keywords": ["Python", "FastAPI"]
            },
            "suggested_role": "Backend Developer"
        },
        "skill_presence": {
            "Python": True,
            "FastAPI": True,
            "Java": False
        }
    }
    
    cv = schemas.CVModel(**cv_data)
    assert cv.UUID == "12345"
    assert cv.Personal_Data.firstName == "John"
    assert len(cv.education_list) == 1
    assert len(cv.experiences_list) == 1
    assert len(cv.projects_list) == 1
    assert len(cv.skills_list) == 2
    assert len(cv.research_work_list) == 1
    assert len(cv.achievements_list) == 2