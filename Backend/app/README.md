# Application Logic

This directory contains the core application logic for the FastAPI backend.

-   `main.py`: The main FastAPI application file, containing all API endpoint definitions.
-   `auth.py`: Authentication logic, including JWT handling and user retrieval.
-   `crud.py`: Database Create, Read, Update, and Delete (CRUD) operations.
-   `database.py`: Supabase client initialization.
-   `llm.py`: Integration with the Groq LLM for AI-powered parsing and analysis.
-   `matching.py`: The core matching algorithm for comparing JDs and CVs.
-   `models.py`: Pydantic models for database table structures.
-   `parsing.py`: File parsing and text extraction utilities.
-   `schemas.py`: Pydantic schemas for data validation and API models.

For more detailed information on the backend architecture and setup, please refer to the [Backend Setup Guide](../../docs/backend_setup.md).
