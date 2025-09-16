#!/usr/bin/env python3
"""
Script to create or update an admin user in Supabase
"""

import os
from app.database import get_supabase

def _get(o, key, default=None):
    """Safely get attribute/key from object or dict."""
    if o is None:
        return default
    if isinstance(o, dict):
        return o.get(key, default)
    return getattr(o, key, default)

def _iter_users(response):
    """Return iterable of user objects from different client response shapes."""
    # Try common shapes: response.users, response.data, response.get('users'), response.get('data')
    users = _get(response, "users")
    if users:
        return users
    data = _get(response, "data")
    if isinstance(data, dict):
        # maybe { "users": [...] }
        return data.get("users") or data.get("data") or []
    return data or []

def _extract_user(resp):
    """Extract user object from response returned by create/update calls."""
    user = _get(resp, "user")
    if user:
        return user
    user = _get(resp, "data")
    if isinstance(user, dict) and ("user" in user or "id" in user):
        return user.get("user") or user
    if isinstance(resp, dict) and "id" in resp:
        return resp
    return user

def create_admin_user():
    """Create or update an admin user in Supabase and set their role."""
    try:
        supabase = get_supabase()
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@cvautomation.com")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "password123")

        print(f"Ensuring admin user '{admin_email}' exists and has admin role...")

        # Use the admin client to list users and find if the admin exists
        admin_user = None
        try:
            users_response = supabase.auth.admin.list_users()
            for u in _iter_users(users_response):
                email = _get(u, "email")
                if email == admin_email:
                    admin_user = u
                    break
        except Exception as e:
            print(f"Could not list users. Ensure your SUPABASE_KEY is a service_role key. Error: {e}")
            return False

        if admin_user:
            print(f"User '{admin_email}' already exists. Will update role.")
            user_id = _get(admin_user, "id")
        else:
            print(f"User '{admin_email}' not found. Creating new user...")
            try:
                create_payload = {
                    "email": admin_email,
                    "password": admin_password,
                    # some versions expect "email_confirm" or "email_confirmed"; try the common one
                    "email_confirm": True
                }
                create_resp = supabase.auth.admin.create_user(create_payload)
                created_user = _extract_user(create_resp)
                if not created_user:
                    print("Warning: could not parse create_user response; dumping response for debugging:")
                    print(create_resp)
                    return False
                user_id = _get(created_user, "id")
                print("User created successfully.")
            except Exception as e:
                # Be liberal in catching different exception shapes/messages
                msg = getattr(e, "message", None) or str(e)
                if "already registered" in msg or "user already exists" in msg.lower():
                    print("User already registered (create_user returned an error). Trying to lookup again...")
                    # attempt to find user again
                    try:
                        users_response = supabase.auth.admin.list_users()
                        for u in _iter_users(users_response):
                            if _get(u, "email") == admin_email:
                                user_id = _get(u, "id")
                                admin_user = u
                                break
                        if not admin_user:
                            print("Still couldn't find user after 'already registered' error.")
                            return False
                    except Exception as e2:
                        print(f"Second attempt to list users failed: {e2}")
                        return False
                else:
                    print(f"Error creating user: {msg}")
                    return False

        # Update user metadata to set the role to admin
        try:
            update_resp = supabase.auth.admin.update_user_by_id(
                user_id, {"user_metadata": {"role": "admin"}}
            )
            updated_user = _extract_user(update_resp) or admin_user
            email = _get(updated_user, "email") or admin_email
            print(f"Successfully set role for '{email}' to 'admin'.")
            return True
        except Exception as e:
            print(f"Error updating user metadata: {e}")
            return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("Admin user setup completed successfully!")
    else:
        print("Failed to set up admin user. Please check the logs for details.")
