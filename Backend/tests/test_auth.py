#!/usr/bin/env python3
"""
Script to test admin user authentication in Supabase
"""

import os
from app.database import get_supabase

def test_admin_auth():
    """Test admin user authentication"""
    try:
        supabase = get_supabase()
        admin_email = "admin@cvautomation.com"
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "password123")
        
        print(f"Testing authentication for user: {admin_email}")
        
        # Try to sign in the admin user
        response = supabase.auth.sign_in_with_password({
            "email": admin_email,
            "password": admin_password
        })
        
        if response and response.session:
            print(f"Authentication successful!")
            print(f"Access token: {response.session.access_token[:20]}...")
            print(f"User ID: {response.user.id}")
            print(f"Email: {response.user.email}")
            return True
        else:
            print("Authentication failed")
            return False
            
    except Exception as e:
        print(f"Error during authentication: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_auth()
    if success:
        print("Authentication test completed successfully!")
    else:
        print("Authentication test failed!")