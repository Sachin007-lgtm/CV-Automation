# Backend

This directory contains the Python-based backend for the CV Automation application, built with FastAPI.

## Overview

The backend service provides a RESTful API to handle:

-   User authentication and management
-   Job description and resume parsing
-   AI-powered candidate matching
-   Database interactions with Supabase

## Documentation

For detailed information, please refer to the central documentation in the `docs` directory at the root of the project:

-   [**Backend Setup Guide**](../../docs/backend_setup.md)
-   [**API Documentation**](../../docs/api_documentation.md)
-   [**Testing Guide**](../../docs/testing.md)

## Scripts

Utility scripts are available in the `scripts` directory. See the [scripts README](./scripts/README.md) for more information.

## Quick Start

1.  **Install dependencies:** `uv sync --all-extras` (for development) or `uv sync` (for production only)
2.  **Configure your environment:** Create a `.env` file (see the setup guide for details).
3.  **Run the server:** `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`