#!/usr/bin/env python3
"""
Application Startup Verification Script

This script verifies that the CV Automation backend application can start correctly
with the Supabase integration.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def verify_environment():
    """Verify that required environment variables are set"""
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file to fully test Supabase integration.")
        return False
    
    print("All required environment variables are set.")
    return True

def verify_imports():
    """Verify that all modules can be imported without errors"""
    try:
        from app import main, database, crud, auth, schemas, models
        print("All modules imported successfully.")
        return True
    except Exception as e:
        print(f"Error importing modules: {e}")
        return False

def verify_supabase_connection():
    """Verify that Supabase client can be created"""
    try:
        from app.database import get_supabase
        supabase = get_supabase()
        print("Supabase client created successfully.")
        return True
    except Exception as e:
        print(f"Warning: Could not create Supabase client: {e}")
        print("This may be expected if Supabase credentials are not set.")
        return False

def main():
    """Main verification function"""
    print("CV Automation Backend - Startup Verification")
    print("=" * 50)
    
    # Verify environment
    env_ok = verify_environment()
    
    # Verify imports
    imports_ok = verify_imports()
    
    # Verify Supabase connection
    supabase_ok = verify_supabase_connection()
    
    print("\n" + "=" * 50)
    if imports_ok:
        print("✅ Application can start successfully!")
        print("✅ All modules imported correctly.")
    else:
        print("❌ Application has import errors.")
        return 1
    
    if env_ok:
        print("✅ Environment variables are properly set.")
    else:
        print("⚠️  Some environment variables are missing.")
    
    if supabase_ok:
        print("✅ Supabase integration is working.")
    else:
        print("⚠️  Supabase integration needs configuration.")
    
    print("\nTo run the application, use: uvicorn app.main:app --reload")
    return 0

if __name__ == "__main__":
    sys.exit(main())
