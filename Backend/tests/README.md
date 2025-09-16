# Backend Tests

This directory contains all automated tests for the FastAPI backend application.

For detailed instructions on how to run these tests, generate coverage reports, and write new tests, please refer to the main [Testing Guide](../../docs/testing.md) in the central documentation.

## Test Structure

-   `conftest.py`: Pytest configuration and fixtures, including mocks for the Supabase client.
-   `test_app.py`: Basic application startup and endpoint tests.
-   `test_auth.py`: Tests for user authentication processes.
-   `test_crud.py`: Tests for database CRUD (Create, Read, Update, Delete) operations.
-   `test_llm.py`: Tests for the Large Language Model (LLM) integration, using mocks to simulate API calls.
-   `test_matching.py`: Tests for the core matching and scoring algorithms.
-   `test_models.py`: Tests for the Pydantic data models.
-   `test_parsing.py`: Tests for file parsing and text cleaning utilities.
-   `test_schemas.py`: Tests for Pydantic schema validation.

## Running Tests

To run all tests, navigate to the `Backend` directory and execute:

```bash
../scripts/run_tests.sh
```

Alternatively, you can run pytest directly:

```bash
python -m pytest tests/ -v
```