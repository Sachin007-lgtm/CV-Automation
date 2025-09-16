import pytest
from unittest.mock import Mock, patch
from app.main import app
from fastapi.testclient import TestClient

# Mock Supabase client for testing
@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing"""
    with patch('app.database.get_supabase') as mock_get_supabase:
        mock_client = Mock()
        mock_get_supabase.return_value = mock_client
        yield mock_client

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_current_user():
    """Create a mock current user for testing"""
    return {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "role": "recruiter",
        "is_active": True
    }