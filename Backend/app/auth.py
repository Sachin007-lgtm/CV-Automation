from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase
from supabase import Client
from app import schemas
import os
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# Security scheme for token authentication
security = HTTPBearer()

# JWT configuration for internal token generation (if needed)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token (for compatibility with existing frontend)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> schemas.User:
    """Extract user from JWT token (for compatibility with existing frontend)"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # In a real implementation, you would fetch user details from database
        # For now, we'll return a basic user object
        return schemas.User(
            id="temp-id",
            username=username,
            email=f"{username}@example.com",
            role="recruiter",
            is_active=True
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(request: Request, supabase: Client = Depends(get_supabase)) -> schemas.User:
    """Get current user from Supabase Auth token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Handle both "Bearer token" and "token" formats
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_response = supabase.auth.get_user(token)
        user_data = user_response.user.user_metadata or {}
        # Supabase stores user data in a different structure.
        # We need to adapt it to our Pydantic schema.
        user = schemas.User(
            id=user_response.user.id, # Supabase uses UUIDs for user IDs
            username=user_data.get("username", user_data.get("user_name", "")) or user_response.user.email,
            email=user_response.user.email,
            role=user_data.get("role", "recruiter"), # Assumes you have a 'role' in user_metadata
            is_active=True # Supabase users are active by default
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_admin_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def authenticate_user(supabase: Client, email: str, password: str):
    """Authenticate user with Supabase"""
    try:
        # Sign in with email and password
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        return None