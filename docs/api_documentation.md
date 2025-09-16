# API Documentation

This document provides details on the API endpoints for the CV Automation application.

## Base URL

The API base URL is configured via the `VITE_API_URL` environment variable in the frontend.

## Authentication

Most endpoints require authentication using a JWT Bearer token provided by Supabase. The token should be included in the `Authorization` header of your requests.

### POST `/token`

Authenticates a user and returns an access token.

-   **Request Body:** `application/x-www-form-urlencoded` with `username` (email) and `password`.
-   **Response:** A JWT access token.

    ```json
    {
      "access_token": "your_supabase_access_token",
      "token_type": "bearer"
    }
    ```

## User Management

These endpoints are restricted to users with the `admin` role.

### GET `/users/me`

Retrieves the profile of the currently authenticated user.

### GET `/users/`

Retrieves a list of all users.

-   **Query Parameters:**
    -   `skip` (int, optional): Number of users to skip.
    -   `limit` (int, optional): Maximum number of users to return.
    -   `username` (str, optional): Filter by username.

### GET `/users/{user_id}`

Retrieves a specific user by their ID.

### POST `/users/`

Creates a new user.

-   **Request Body:** A JSON object with `username`, `email`, `password`, and `role`.

### DELETE `/users/{user_id}`

Deletes a user by their ID.

## Job Descriptions (JDs)

### GET `/jds`

Retrieves a list of all job descriptions.

-   **Query Parameters:**
    -   `skip` (int, optional): Number of JDs to skip.
    -   `limit` (int, optional): Maximum number of JDs to return.

### GET `/jds/{jd_id}`

Retrieves a specific job description by its ID.

### POST `/jds/upload`

Uploads a JD file (PDF, DOCX, TXT), extracts its content, converts it to JSON, and saves it to the database.

-   **Request Body:** `multipart/form-data` with a `jd_file`.
-   **Permissions:** `admin` or `backend_team` role required.

### POST `/extract_jd`

Extracts content from a JD file and returns the JSON representation without saving it.

-   **Request Body:** `multipart/form-data` with a `jd_file`.
-   **Permissions:** `admin` or `backend_team` role required.

### POST `/save_jd`

Saves a JD (in JSON format) to the database.

-   **Request Body:** The JD data as a JSON object.
-   **Permissions:** `admin` or `backend_team` role required.

### PUT `/jds/{jd_id}`

Updates the details of a specific job description.

-   **Request Body:** A JSON object containing the `details` to update.
-   **Permissions:** `admin` or `backend_team` role required.

### PATCH `/jds/{jd_id}`

Updates the status of a specific job description.

-   **Request Body:** A JSON object with the new `status`.

### GET `/jds/{jd_id}/results`

Retrieves all analysis results associated with a specific job description.

## CVs and Matching

### POST `/extract_resumes`

Uploads one or more resume files, extracts their content, and returns the JSON representation.

-   **Request Body:** `multipart/form-data` with `resume_files` (one or more files) and `jd_json` (the corresponding JD in JSON format).

### POST `/match`

Performs the matching process between a JD and a list of CVs.

-   **Request Body:** A JSON object containing `jd_json` and a list of `cvs` (in JSON format).
-   **Response:** A detailed match analysis, including scores, insights, and generated interview questions.

## Analyses

### GET `/analyses`

Retrieves all past analyses created by the currently authenticated user.
