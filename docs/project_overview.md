# Project Overview

CV Automation is a comprehensive tool designed to streamline the recruitment process by leveraging AI to match candidate resumes with job descriptions (JDs).

## Key Features

-   **Automated Parsing:** Extracts structured data from resumes and JDs in various formats (PDF, DOCX, TXT).
-   **Intelligent Matching:** Utilizes semantic analysis and configurable weighting to score and rank candidates based on their suitability for a role.
-   **AI-Powered Insights:** Generates actionable insights, including:
    -   Job stability analysis
    -   Education gap detection
    -   Customized interview questions
-   **Role-Based Access Control:** Differentiates between Admins, Recruiters, and Backend Team members with specific permissions.
-   **Web-Based Interface:** A modern and intuitive React frontend for managing JDs, uploading CVs, and reviewing match results.

## Technology Stack

-   **Backend:** Python, FastAPI, Supabase, Groq API for LLM tasks, Sentence Transformers for embeddings.
-   **Frontend:** React, Vite, Tailwind CSS, Axios.
-   **Database:** PostgreSQL (managed by Supabase).
