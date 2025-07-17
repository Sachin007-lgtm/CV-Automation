# experience_match Calculation in CV-Automation

## What is experience_match?
`experience_match` quantifies how well the candidate's total years of experience align with the required years in the Job Description (JD), adjusted for role relevance. It is a key part of the overall match score.

---

## Where is experience_match Calculated?
- **Function:** `compute_similarity` in `final_main.py`
- **Helper:** `calculate_experience_match`

---

## Step-by-Step Calculation

### 1. Calculate Candidate's Total Experience Years
- **Function:** `calculate_experience_years`
- **How:** Sums the duration of all experiences in `cv.experiences_list` (using start and end dates).
- **Why:** Total experience is a basic requirement for most jobs.

### 2. Extract Required Experience from JD
- **Function:** `extract_required_experience`
- **How:** Uses semantic search and regex to find and extract the number of years required from `jd.qualifications.required`.
- **Why:** Ensures the candidate meets the minimum experience threshold.

### 3. Calculate Role Relevance
- **Function:** `calculate_role_relevance`
- **How:** Compares JD job title with candidate's suggested role or experience titles using embeddings and cosine similarity.
- **Why:** Experience is more valuable if it is in a relevant role.

### 4. Apply Matching Logic
- **Logic:**
  - If JD required years is 0, return 0.8 (default good match).
  - If role relevance < 0.5:
    - If candidate experience >= required, cap at 0.6.
    - If less, scale down.
  - If role relevance >= 0.5:
    - If candidate experience >= required, add a bonus (up to 1.0).
    - If less, scale as a ratio.
- **Why:** This logic rewards both quantity and relevance of experience.

### 5. Use in Final Score
- **Why:** Ensures candidates are not only experienced, but experienced in the right context.

---

## Utility Functions Used
- `calculate_experience_years`: Sums up candidate's experience duration.
- `extract_required_experience`: Extracts required years from JD.
- `calculate_role_relevance`: Computes similarity between roles.

---

## Example
- JD requires 3 years, candidate has 4 years, high role relevance → high match.
- JD requires 5 years, candidate has 2 years, low role relevance → low match.

---

## Summary
Each step ensures the candidate's experience is both sufficient and relevant, using both quantitative and semantic checks. 