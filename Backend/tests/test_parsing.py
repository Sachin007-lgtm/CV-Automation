import pytest
from app.parsing import to_bool, clean_resume_json, clean_json_response, preprocess_resume_text

def test_to_bool_with_boolean():
    """Test to_bool with boolean values."""
    assert to_bool(True) == True
    assert to_bool(False) == False

def test_to_bool_with_string():
    """Test to_bool with string values."""
    assert to_bool("true") == True
    assert to_bool("1") == True
    assert to_bool("yes") == True
    assert to_bool("present") == True
    assert to_bool("false") == False
    assert to_bool("0") == False
    assert to_bool("no") == False
    assert to_bool("absent") == False
    assert to_bool("random") == False

def test_to_bool_with_number():
    """Test to_bool with numeric values."""
    assert to_bool(1) == True
    assert to_bool(0) == False
    assert to_bool(5) == True
    assert to_bool(-1) == True
    assert to_bool(0.0) == False
    assert to_bool(1.0) == True

def test_to_bool_with_other_types():
    """Test to_bool with other types."""
    assert to_bool(None) == False
    assert to_bool([]) == False
    assert to_bool({}) == False

def test_clean_resume_json():
    """Test cleaning resume JSON."""
    # Test with valid resume data
    resume_data = {
        "Personal Data": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "location": {
                "city": "San Francisco",
                "state": "CA"
            }
        },
        "Education": [
            {
                "institution": "Test University",
                "degree": "Bachelor's",
                "fieldOfStudy": "Computer Science"
            }
        ],
        "Experiences": [
            {
                "jobTitle": "Software Engineer",
                "company": "Test Company",
                "description": ["Developed applications"],
                "technologiesUsed": ["Python", "FastAPI"]
            }
        ],
        "Skills": [
            {"category": "Programming", "skillName": "Python"},
            {"category": "Web Frameworks", "skillName": "FastAPI"}
        ],
        "Analytics": {
            "job_stability": {"average_duration_years": 2.5, "frequent_switching_flag": False},
            "education_gap": {"has_gap": False, "gap_duration_years": 0},
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
            "Java": False
        }
    }
    
    cleaned = clean_resume_json(resume_data)
    
    # Check that the structure is maintained
    assert cleaned["Personal Data"]["firstName"] == "John"
    assert len(cleaned["Education"]) == 1
    assert len(cleaned["Experiences"]) == 1
    assert len(cleaned["Skills"]) == 2
    assert cleaned["skill_presence"]["Python"] == True
    assert cleaned["skill_presence"]["Java"] == False
    
    # Test with malformed data
    malformed_data = {
        "Personal Data": "invalid",
        "Education": "invalid",
        "Experiences": "invalid",
        "Skills": "invalid",
        "Analytics": "invalid",
        "skill_presence": "invalid"
    }
    
    cleaned_malformed = clean_resume_json(malformed_data)
    
    # Check that it's cleaned to proper structure
    assert isinstance(cleaned_malformed["Personal Data"], dict)
    assert isinstance(cleaned_malformed["Education"], list)
    assert isinstance(cleaned_malformed["Experiences"], list)
    assert isinstance(cleaned_malformed["Skills"], list)
    assert isinstance(cleaned_malformed["Analytics"], dict)
    assert isinstance(cleaned_malformed["skill_presence"], dict)

def test_clean_resume_json_edge_cases():
    """Test cleaning resume JSON with edge cases."""
    # Test with empty arrays
    resume_data = {
        "Personal Data": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "location": {
                "city": "San Francisco",
                "state": "CA"
            }
        },
        "Education": [],
        "Experiences": [],
        "Skills": [],
        "Analytics": {
            "job_stability": {"average_duration_years": 0, "frequent_switching_flag": False},
            "education_gap": {"has_gap": False, "gap_duration_years": 0},
            "keyword_analysis": {
                "teamwork": False,
                "management_experience": False,
                "geographic_experience": False,
                "extracted_keywords": []
            },
            "suggested_role": "Developer"
        },
        "skill_presence": {}
    }
    
    cleaned = clean_resume_json(resume_data)
    
    assert cleaned["Education"] == []
    assert cleaned["Experiences"] == []
    assert cleaned["Skills"] == []
    assert cleaned["skill_presence"] == {}
    
    # Test with None values
    resume_data_none = {
        "Personal Data": {
            "firstName": None,
            "lastName": None,
            "email": None,
            "location": None
        },
        "Education": None,
        "Experiences": None,
        "Skills": None,
        "Analytics": None,
        "skill_presence": None
    }
    
    cleaned_none = clean_resume_json(resume_data_none)
    
    assert isinstance(cleaned_none["Personal Data"], dict)
    assert cleaned_none["Education"] == []
    assert cleaned_none["Experiences"] == []
    assert cleaned_none["Skills"] == []
    assert cleaned_none["skill_presence"] == {}

def test_clean_json_response():
    """Test cleaning JSON response."""
    # Test with markdown code block
    response = "```json\n{\"test\": \"data\"}\n```"
    cleaned = clean_json_response(response)
    assert cleaned == "{\"test\": \"data\"}"
    
    # Test with code block without json specifier
    response = "```\n{\"test\": \"data\"}\n```"
    cleaned = clean_json_response(response)
    assert cleaned == "{\"test\": \"data\"}"
    
    # Test with nested JSON objects
    response = "```json\n{\"outer\": {\"inner\": \"data\"}}\n```"
    cleaned = clean_json_response(response)
    assert cleaned == "{\"outer\": {\"inner\": \"data\"}}"
    
    # Test with invalid JSON (should return as is)
    response = "```json\n{\"invalid\": json}\n```"
    cleaned = clean_json_response(response)
    assert cleaned == "{\"invalid\": json}"

def test_preprocess_resume_text():
    """Test preprocessing resume text."""
    # Test with normal text
    text = "John Doe\nSoftware Engineer\nExperience:\n- Python\n- FastAPI"
    processed = preprocess_resume_text(text)
    assert "John Doe" in processed
    assert "Software Engineer" in processed
    assert "\n" not in processed  # Newlines should be removed
    
    # Test with special characters
    text = "John Doe\nSoftware Engineer\nEmail: john@example.com\nPhone: (123) 456-7890"
    processed = preprocess_resume_text(text)
    assert "john@example.com" in processed
    assert "(123) 456-7890" in processed
    
    # Test with very long text (should be truncated)
    long_text = "A" * 9000
    processed = preprocess_resume_text(long_text)
    assert len(processed) <= 8010  # 8000 + 3 for ellipsis
    assert processed.endswith("...")