import pytest
from app import models, schemas

def test_user_model():
    """Test User model creation"""
    # Create a user instance
    user = models.User(
        id="test-id",
        username="testuser",
        email="test@example.com",
        role="recruiter"
    )
    
    assert user.id == "test-id"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "recruiter"
    assert user.is_active == True

def test_job_description_model():
    """Test JobDescription model creation"""
    # Create a job description instance
    jd = models.JobDescription(
        id=1,
        job_id_str="JD001",
        content_hash="abcdef123456",
        job_title="Software Engineer",
        company_name="Test Company",
        location="San Francisco, CA",
        ctc="$100,000 - $150,000",
        status="Active",
        details={"test": "data"}
    )
    
    assert jd.id == 1
    assert jd.job_id_str == "JD001"
    assert jd.content_hash == "abcdef123456"
    assert jd.job_title == "Software Engineer"
    assert jd.company_name == "Test Company"
    assert jd.location == "San Francisco, CA"
    assert jd.ctc == "$100,000 - $150,000"
    assert jd.status == "Active"
    assert jd.details == {"test": "data"}

def test_candidate_model():
    """Test Candidate model creation"""
    # Create a candidate instance
    candidate = models.Candidate(
        id=1,
        name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        assessment_result="Good",
        recruiter_id="test-user-id"
    )
    
    assert candidate.id == 1
    assert candidate.name == "John Doe"
    assert candidate.email == "john@example.com"
    assert candidate.phone == "123-456-7890"
    assert candidate.assessment_result == "Good"
    assert candidate.recruiter_id == "test-user-id"

def test_analysis_result_model():
    """Test AnalysisResult model creation"""
    # Create an analysis result instance
    result = models.AnalysisResult(
        id=1,
        job_description_id=1,
        candidate_id=1,
        user_id="test-user-id",
        score=85.5,
        match_level="Good",
        details={"test": "data"}
    )
    
    assert result.id == 1
    assert result.job_description_id == 1
    assert result.candidate_id == 1
    assert result.user_id == "test-user-id"
    assert result.score == 85.5
    assert result.match_level == "Good"
    assert result.details == {"test": "data"}