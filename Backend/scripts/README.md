# Backend Scripts

This directory contains utility scripts for the backend application.

## Scripts

-   **`run_tests.sh`**: A shell script to execute the backend test suite using pytest. It ensures that the `TESTING` environment variable is set and provides colored output for readability.

-   **`verify_startup.py`**: A Python script to help developers verify their local setup. It checks for required environment variables, verifies that all necessary modules can be imported, and attempts to create a Supabase client instance.
