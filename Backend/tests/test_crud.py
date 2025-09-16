import pytest
from unittest.mock import Mock
from app import crud, schemas

def test_create_jd_content_hash():
    """Test that the content hash function works correctly"""
    # Create a simple JD model for testing
    jd_data = {
        "jobId": "test-123",
        "jobTitle": "Test Job",
        "companyProfile": {
            "companyName": "Test Company"
        },
        "location": {
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "remoteStatus": "Remote"
        },
        "datePosted": "2023-01-01",
        "employmentType": "Full-time",
        "jobSummary": "This is a test job",
        "keyResponsibilities": ["Responsibility 1", "Responsibility 2"],
        "qualifications": {
            "required": ["Requirement 1"],
            "preferred": ["Preference 1"]
        },
        "requiredSkills": ["Skill 1", "Skill 2"],
        "educationRequired": ["Bachelor's Degree"],
        "compensationAndBenefits": {
            "salaryRange": "$50,000 - $70,000",
            "benefits": ["Health Insurance"]
        },
        "applicationInfo": {
            "howToApply": "Apply online",
            "applyLink": "https://test.com/apply"
        },
        "extractedKeywords": ["keyword1", "keyword2"],
    }
    
    jd_model = schemas.JDModel(**jd_data)
    content_hash = crud._create_jd_content_hash(jd_model)
    
    # Verify that we get a hash back
    assert isinstance(content_hash, str)
    assert len(content_hash) == 64  # SHA256 hashes are 64 characters long

def test_ensure_complete_skill_presence():
    """Test that skill presence is properly ensured"""
    skill_presence = {"Python": True, "Java": False}
    skill_categories = {
        "critical": ["Python", "JavaScript"],
        "important": ["Java", "C++"]
    }
    
    result = crud.ensure_complete_skill_presence(skill_presence, skill_categories)
    
    # Verify that all skills are present in the result
    assert "Python" in result
    assert "Java" in result
    assert "JavaScript" in result
    assert "C++" in result
    
    # Verify that existing values are preserved
    assert result["Python"] == True
    assert result["Java"] == False
    
    # Verify that missing skills are set to False
    assert result["JavaScript"] == False
    assert result["C++"] == False