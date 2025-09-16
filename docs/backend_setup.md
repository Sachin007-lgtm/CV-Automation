# Backend Setup

This guide provides instructions for setting up and running the backend service for the CV Automation application.

## Prerequisites

-   Python 3.12 or higher
-   An active Supabase project
-   A Groq API key

You can use either [uv](https://docs.astral.sh/uv/) (recommended) or [conda](https://docs.conda.io/) to manage your Python environment and dependencies.

### Option 1: Using uv (Recommended)

[Install uv](https://docs.astral.sh/uv/getting-started/installation/)

Navigate to the `Backend` directory and install the required Python packages using `uv`:

```bash
cd Backend
# For development (installs all dependencies including test dependencies)
uv sync --all-extras

# For production only (installs only runtime dependencies)
uv sync
```

### Option 2: Using conda

[[Install conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)]

Navigate to the `Backend` directory and create a conda environment:

```bash
cd Backend
# Create a new conda environment with Python 3.12
conda create -n cv-automation python=3.12

# Activate the environment
conda activate cv-automation

# Install dependencies using pip (recommended approach for conda environments)
pip install -e ".[test]"  # For development (includes test dependencies)
# OR
pip install -e "."        # For production only (runtime dependencies only)
```

## 3. Configure Environment Variables

Create a `.env` file in the `Backend` directory by copying the example file if it exists, or by creating a new one. Populate it with the following keys:

```env
# Groq API Key for LLM tasks
GROK_API_KEY="your_groq_api_key"

# Secret key for JWTs (generate a random string)
SECRET_KEY="your_strong_secret_key"

# Default password for the initial admin user
DEFAULT_ADMIN_PASSWORD="your_secure_admin_password"

# Supabase project credentials
SUPABASE_URL="your_supabase_project_url"
SUPABASE_KEY="your_supabase_service_role_key" # Important: Use the service_role key

LLM_MODEL_NAME=gemma2-9b-it
SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2

MATCHING_TITLE_WEIGHT=0.23
MATCHING_RESPONSIBILITIES_WEIGHT=0.31
MATCHING_EXPERIENCE_WEIGHT=0.23
MATCHING_EDUCATION_WEIGHT=0.23
MATCHING_LOCATION_WEIGHT=0.0
```

## 4. Set Up the Database

The application uses Supabase for its database and authentication. You need to set up the required tables and authentication settings.

For detailed instructions, refer to the [Supabase Setup Guide](./supabase_setup.md).

After setting up the tables, you may also need to download NLTK data (not strictly required):

```bash
# If using uv
uv run download_nltk_data.py

# If using conda
python download_nltk_data.py
```

## 5. Create an Initial Admin User

Run the provided script to create the first admin user in your Supabase project. This user can then manage other users through the application's UI.

```bash
# If using uv
uv run create_admin_user.py

# If using conda
python create_admin_user.py
```

**Note:** After creating the user, you may need to confirm their email address in the Supabase dashboard, unless you have disabled email confirmations for development (as described in the Supabase setup guide).

## 6. Run the Application

Once the setup is complete, you can start the FastAPI server.

```bash
# If using uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# If using conda
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables hot-reloading, which is useful for development.

## 7. Accessing the API

With the server running, the API is available at `http://localhost:8000`. (or whichever port you're running the server)

Interactive API documentation (Swagger UI) can be accessed at `http://localhost:8000/docs`.
