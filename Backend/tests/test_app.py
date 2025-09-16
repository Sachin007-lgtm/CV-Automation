import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test that the main endpoint returns a 404 (since we haven't defined a root route)"""
    response = client.get("/")
    assert response.status_code == 404

def test_token_endpoint():
    """Test that the token endpoint returns a 401 for invalid credentials"""
    response = client.post("/token", data={"username": "test", "password": "test"})
    assert response.status_code == 401

def test_app_startup():
    """Test that the app can start without errors"""
    # This test just verifies that the app imports correctly
    assert app is not None