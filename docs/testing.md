# Testing Guide

This document provides comprehensive instructions for running tests for both the backend and frontend of the CV Automation application.

**IMPORTANT:** When running backend tests, ensure the `TESTING` environment variable is set to `1`. This prevents certain startup events from running during tests.

## Backend Testing (Python/FastAPI)

### Prerequisites

Ensure you have installed the necessary development dependencies.

```bash
cd Backend
# Install all dependencies including test dependencies
uv sync --all-extras
```

### Running Tests

To run all backend tests, navigate to the `Backend` directory and use one of the following commands:

```bash
# Run tests with verbose output
uv run pytest tests/ -v

# Or use the provided shell script
./run_tests.sh
```

### Test Coverage

To generate a coverage report for the backend code:

```bash
cd Backend
uv run pytest tests/ -v --cov=app --cov-report=html
```

This will create an `htmlcov` directory with a detailed, viewable report.

### Test Structure

The backend tests are located in the `Backend/tests/` directory and cover all major aspects of the application, including authentication, database operations, API endpoints, and business logic.

---

## Frontend Testing (React/Vitest)

### Prerequisites

Ensure you have installed the necessary npm packages.

```bash
cd Frontend
npm install
```

### Running Tests

To run all frontend tests, navigate to the `Frontend` directory and use one of the following commands:

```bash
# Run all tests once
npm test

# Run tests in watch mode for active development
npm run test:watch
```

### Test Coverage

To generate a coverage report for the frontend code:

```bash
cd Frontend
npm run test:coverage
```

This will output a coverage summary in the console and may generate a more detailed report.

### Test Structure

Frontend tests are co-located with the components and hooks they are testing (e.g., `LoginPage.test.jsx`). This makes it easy to find and maintain tests for specific parts of the UI.