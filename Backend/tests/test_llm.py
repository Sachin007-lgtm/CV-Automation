import pytest
from unittest.mock import patch, MagicMock
from app import llm
from app.schemas import JDModel, CVModel, LocationModel, CompanyProfile, Qualifications, CompensationBenefits, ApplicationInfo, Experience, Education, Skill, JobStability, EducationGap, KeywordAnalysis, Analytics
import json

# Mock data for testing
MOCK_JD_TEXT = """
Job Title: Senior Python Developer
Company: Tech Corp
Location: San Francisco, CA
Job Summary: We are looking for an experienced Python developer.
Key Responsibilities:
- Develop backend services
- Collaborate with frontend team
Required Skills: Python, FastAPI, PostgreSQL
Education: Bachelor's degree in Computer Science or related field
"""

MOCK_RESUME_TEXT = """
John Doe
Email: john@example.com
Location: San Francisco, CA
Experience:
Senior Python Developer, Tech Corp (2020-Present)
- Developed backend services using Python and FastAPI
- Collaborated with frontend team
Education:
Bachelor of Science in Computer Science, University of California (2015-2019)
Skills: Python, FastAPI, PostgreSQL, Docker
"""

MOCK_JD_JSON = {
    "jobId": "JD001",
    "jobTitle": "Senior Python Developer",
    "companyProfile": {
        "companyName": "Tech Corp"
    },
    "location": {
        "city": "San Francisco",
        "state": "CA",
        "country": "USA"
    },
    "datePosted": "2023-01-01",
    "jobSummary": "We are looking for an experienced Python developer.",
    "keyResponsibilities": [
        "Develop backend services",
        "Collaborate with frontend team"
    ],
    "qualifications": {
        "required": [],
        "preferred": []
    },
    "requiredSkills": ["Python", "FastAPI", "PostgreSQL"],
    "educationRequired": ["Bachelor's degree in Computer Science or related field"],
    "compensationAndBenefits": {
        "salaryRange": "",
        "benefits": []
    },
    "applicationInfo": {
        "howToApply": "",
        "applyLink": "",
        "contactEmail": None
    },
    "extractedKeywords": ["Python", "FastAPI", "PostgreSQL"]
}

MOCK_RESUME_JSON = {
    "UUID": "12345",
    "Personal Data": {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "phone": None,
        "linkedin": None,
        "portfolio": None,
        "location": {
            "city": "San Francisco",
            "state": "CA",
            "country": "USA"
        },
        "age": None,
        "gender": None
    },
    "Education": [
        {
            "institution": "University of California",
            "degree": "Bachelor of Science",
            "fieldOfStudy": "Computer Science",
            "startDate": "2015-09-01",
            "endDate": "2019-06-01",
            "grade": None,
            "description": ""
        }
    ],
    "Experiences": [
        {
            "jobTitle": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "",
            "startDate": "2020-01-01",
            "endDate": "Present",
            "description": [
                "Developed backend services using Python and FastAPI",
                "Collaborated with frontend team"
            ],
            "technologiesUsed": []
        }
    ],
    "Projects": [],
    "Skills": [
        {"category": "Programming", "skillName": "Python"},
        {"category": "Web Frameworks", "skillName": "FastAPI"},
        {"category": "Databases", "skillName": "PostgreSQL"},
        {"category": "DevOps", "skillName": "Docker"}
    ],
    "Research Work": [],
    "Achievements": [],
    "Analytics": {
        "job_stability": {"average_duration_years": 3.5, "frequent_switching_flag": False},
        "education_gap": {"has_gap": False, "gap_duration_years": 0},
        "keyword_analysis": {
            "teamwork": False,
            "management_experience": False,
            "geographic_experience": False,
            "extracted_keywords": ["Python", "FastAPI", "PostgreSQL", "Docker"]
        },
        "suggested_role": "Senior Python Developer"
    },
    "skill_presence": {
        "Python": True,
        "FastAPI": True,
        "PostgreSQL": True
    }
}

@patch('app.llm.get_groq_client')
def test_convert_jd_to_json(mock_get_client):
    """Test converting JD text to JSON."""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(MOCK_JD_JSON)))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function
    result = llm.convert_jd_to_json(MOCK_JD_TEXT)
    
    # Verify the result
    assert isinstance(result, dict)
    assert result["jobTitle"] == "Senior Python Developer"
    assert "Python" in result["requiredSkills"]

@patch('app.llm.get_groq_client')
def test_convert_jd_to_json_with_skill_categories(mock_get_client):
    """Test converting JD text to JSON with skill categories."""
    # Setup mock with categorized skills
    jd_json_with_categories = MOCK_JD_JSON.copy()
    jd_json_with_categories["requiredSkills"] = {
        "critical": ["Python", "FastAPI"],
        "important": ["PostgreSQL"],
        "extra": ["Docker"]
    }
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(jd_json_with_categories)))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function
    result = llm.convert_jd_to_json(MOCK_JD_TEXT)
    
    # Verify the result
    assert isinstance(result, dict)
    assert result["jobTitle"] == "Senior Python Developer"
    assert isinstance(result["requiredSkills"], dict)
    assert "Python" in result["requiredSkills"]["critical"]

@patch('app.llm.get_groq_client')
def test_convert_resume_to_json(mock_get_client):
    """Test converting resume text to JSON."""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(MOCK_RESUME_JSON)))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function
    result = llm.convert_resume_to_json(MOCK_RESUME_TEXT)
    
    # Verify the result
    assert isinstance(result, dict)
    assert result["Personal Data"]["firstName"] == "John"
    assert "Python" in [skill["skillName"] for skill in result["Skills"]]

@patch('app.llm.get_groq_client')
def test_convert_resume_to_json_with_skill_categories(mock_get_client):
    """Test converting resume text to JSON with skill categories."""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(MOCK_RESUME_JSON)))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function with skill categories
    skill_categories = {
        "critical": ["Python", "FastAPI"],
        "important": ["PostgreSQL"],
        "extra": ["Docker"]
    }
    
    result = llm.convert_resume_to_json(MOCK_RESUME_TEXT, skill_categories)
    
    # Verify the result
    assert isinstance(result, dict)
    assert result["Personal Data"]["firstName"] == "John"
    assert "skill_presence" in result
    assert isinstance(result["skill_presence"], dict)

@patch('app.llm.get_groq_client')
def test_generate_interview_questions(mock_get_client):
    """Test generating interview questions."""
    # Setup mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='["What is your experience with Python?", "How do you handle database transactions?"]'))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Create mock JD and CV objects
    jd = JDModel(
        jobId="JD001",
        jobTitle="Senior Python Developer",
        companyProfile=CompanyProfile(companyName="Tech Corp"),
        location=LocationModel(city="San Francisco", state="CA", country="USA"),
        datePosted="2023-01-01",
        jobSummary="We are looking for an experienced Python developer.",
        keyResponsibilities=["Develop backend services", "Collaborate with frontend team"],
        qualifications=Qualifications(required=[], preferred=[]),
        requiredSkills=["Python", "FastAPI", "PostgreSQL"],
        educationRequired=["Bachelor's degree in Computer Science or related field"],
        compensationAndBenefits=CompensationBenefits(salaryRange="", benefits=[]),
        applicationInfo=ApplicationInfo(howToApply="", applyLink="", contactEmail=None),
        extractedKeywords=["Python", "FastAPI", "PostgreSQL"]
    )
    
    cv = CVModel(
        UUID="12345",
        Personal_Data={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "phone": None,
            "linkedin": None,
            "portfolio": None,
            "location": LocationModel(city="San Francisco", state="CA", country="USA"),
            "age": None,
            "gender": None
        },
        education_list=[
            Education(
                institution="University of California",
                degree="Bachelor of Science",
                fieldOfStudy="Computer Science",
                startDate="2015-09-01",
                endDate="2019-06-01",
                grade=None,
                description=""
            )
        ],
        experiences_list=[
            Experience(
                jobTitle="Senior Python Developer",
                company="Tech Corp",
                location="",
                startDate="2020-01-01",
                endDate="Present",
                description=["Developed backend services using Python and FastAPI", "Collaborated with frontend team"],
                technologiesUsed=[]
            )
        ],
        projects_list=[],
        skills_list=[
            Skill(category="Programming", skillName="Python"),
            Skill(category="Web Frameworks", skillName="FastAPI"),
            Skill(category="Databases", skillName="PostgreSQL"),
            Skill(category="DevOps", skillName="Docker")
        ],
        research_work_list=[],
        achievements_list=[],
        Analytics=Analytics(
            job_stability=JobStability(average_duration_years=3.5, frequent_switching_flag=False),
            education_gap=EducationGap(has_gap=False, gap_duration_years=0),
            keyword_analysis=KeywordAnalysis(
                teamwork=False,
                management_experience=False,
                geographic_experience=False,
                extracted_keywords=["Python", "FastAPI", "PostgreSQL", "Docker"]
            ),
            suggested_role="Senior Python Developer"
        ),
        skill_presence={"Python": True, "FastAPI": True, "PostgreSQL": True}
    )
    
    # Test the function
    questions = llm.generate_interview_questions(jd, cv)
    
    # Verify the result
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert isinstance(questions[0], str)

def test_get_groq_client():
    """Test getting Groq client."""
    # Test when GROK_API_KEY is not set
    with patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="GROK_API_KEY environment variable is not set"):
            llm.get_groq_client()
    
    # Test when GROK_API_KEY is set
    with patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = "test-api-key"
        with patch('groq.Groq') as mock_groq:
            mock_client = MagicMock()
            mock_groq.return_value = mock_client
            client = llm.get_groq_client()
            assert client == mock_client

@patch('app.llm.get_groq_client')
def test_convert_jd_to_json_api_error(mock_get_client):
    """Test converting JD text to JSON with API error."""
    # Setup mock to raise APIError
    mock_client = MagicMock()
    # Create a proper APIError mock
    api_error = MagicMock()
    api_error.__class__ = llm.APIError
    api_error.message = "Test API error"
    mock_client.chat.completions.create.side_effect = api_error
    mock_get_client.return_value = mock_client
    
    # Test the function
    with pytest.raises(llm.LLMJsonError):
        llm.convert_jd_to_json(MOCK_JD_TEXT)

@patch('app.llm.get_groq_client')
def test_convert_jd_to_json_json_error(mock_get_client):
    """Test converting JD text to JSON with JSON parsing error."""
    # Setup mock to return invalid JSON
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Invalid JSON"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function
    with pytest.raises(llm.LLMJsonError, match=r"Could not parse the response from the AI service as JSON"):
        llm.convert_jd_to_json(MOCK_JD_TEXT)

@patch('app.llm.get_groq_client')
def test_convert_resume_to_json_api_error(mock_get_client):
    """Test converting resume text to JSON with API error."""
    # Setup mock to raise APIError
    mock_client = MagicMock()
    # Create a proper APIError mock
    api_error = MagicMock()
    api_error.__class__ = llm.APIError
    api_error.message = "Test API error"
    mock_client.chat.completions.create.side_effect = api_error
    mock_get_client.return_value = mock_client
    
    # Test the function
    with pytest.raises(llm.LLMJsonError):
        llm.convert_resume_to_json(MOCK_RESUME_TEXT)

@patch('app.llm.get_groq_client')
def test_convert_resume_to_json_json_error(mock_get_client):
    """Test converting resume text to JSON with JSON parsing error."""
    # Setup mock to return invalid JSON
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Invalid JSON"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_get_client.return_value = mock_client
    
    # Test the function
    with pytest.raises(llm.LLMJsonError, match=r"Could not parse the response from the AI service as JSON"):
        llm.convert_resume_to_json(MOCK_RESUME_TEXT)

@patch('app.llm.get_groq_client')
def test_generate_interview_questions_api_error(mock_get_client):
    """Test generating interview questions with API error."""
    # Setup mock to raise APIError
    mock_client = MagicMock()
    # Create a proper APIError mock
    api_error = MagicMock()
    api_error.__class__ = llm.APIError
    api_error.message = "Test API error"
    mock_client.chat.completions.create.side_effect = api_error
    mock_get_client.return_value = mock_client
    
    # Create mock JD and CV objects
    jd = JDModel(
        jobId="JD001",
        jobTitle="Senior Python Developer",
        companyProfile=CompanyProfile(companyName="Tech Corp"),
        location=LocationModel(city="San Francisco", state="CA", country="USA"),
        datePosted="2023-01-01",
        jobSummary="We are looking for an experienced Python developer.",
        keyResponsibilities=["Develop backend services", "Collaborate with frontend team"],
        qualifications=Qualifications(required=[], preferred=[]),
        requiredSkills=["Python", "FastAPI", "PostgreSQL"],
        educationRequired=["Bachelor's degree in Computer Science or related field"],
        compensationAndBenefits=CompensationBenefits(salaryRange="", benefits=[]),
        applicationInfo=ApplicationInfo(howToApply="", applyLink="", contactEmail=None),
        extractedKeywords=["Python", "FastAPI", "PostgreSQL"]
    )
    
    cv = CVModel(
        UUID="12345",
        Personal_Data={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "phone": None,
            "linkedin": None,
            "portfolio": None,
            "location": LocationModel(city="San Francisco", state="CA", country="USA"),
            "age": None,
            "gender": None
        },
        education_list=[
            Education(
                institution="University of California",
                degree="Bachelor of Science",
                fieldOfStudy="Computer Science",
                startDate="2015-09-01",
                endDate="2019-06-01",
                grade=None,
                description=""
            )
        ],
        experiences_list=[
            Experience(
                jobTitle="Senior Python Developer",
                company="Tech Corp",
                location="",
                startDate="2020-01-01",
                endDate="Present",
                description=["Developed backend services using Python and FastAPI", "Collaborated with frontend team"],
                technologiesUsed=[]
            )
        ],
        projects_list=[],
        skills_list=[
            Skill(category="Programming", skillName="Python"),
            Skill(category="Web Frameworks", skillName="FastAPI"),
            Skill(category="Databases", skillName="PostgreSQL"),
            Skill(category="DevOps", skillName="Docker")
        ],
        research_work_list=[],
        achievements_list=[],
        Analytics=Analytics(
            job_stability=JobStability(average_duration_years=3.5, frequent_switching_flag=False),
            education_gap=EducationGap(has_gap=False, gap_duration_years=0),
            keyword_analysis=KeywordAnalysis(
                teamwork=False,
                management_experience=False,
                geographic_experience=False,
                extracted_keywords=["Python", "FastAPI", "PostgreSQL", "Docker"]
            ),
            suggested_role="Senior Python Developer"
        ),
        skill_presence={"Python": True, "FastAPI": True, "PostgreSQL": True}
    )
    
    # Test the function
    with pytest.raises(llm.LLMJsonError):
        llm.generate_interview_questions(jd, cv)