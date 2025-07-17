# sim_title Calculation in CV-Automation

## What is sim_title?
`sim_title` quantifies how closely the candidate's main job role matches the job title in the Job Description (JD). It is a key part of the overall candidate-job fit score.

---

## Where is sim_title Calculated?
- **Function:** `compute_similarity` in `final_main.py`

---

## Step-by-Step Calculation

### 1. Extract Job Title from JD
- **Code:** `jd.jobTitle`
- **Why:** The job title is the most direct summary of the role the company is hiring for. Matching this with the candidate's background is crucial for relevance.

### 2. Extract Candidate's Main Role
- **Code:**
  - `suggested_role = cv.Analytics.suggested_role`
  - If not present, concatenate all `jobTitle` fields from `cv.experiences_list`.
- **Why:** The candidate's suggested role (from analytics) or their experience titles best represent their professional identity.

### 3. Generate Embeddings
- **Code:**
  - `jd_title_emb = model.encode(jd.jobTitle)`
  - `cv_title_emb = model.encode(cv_title_text if cv_title_text else "")`
- **Why:** Embeddings convert text into numerical vectors that capture semantic meaning, allowing for meaningful similarity comparison.

### 4. Calculate Cosine Similarity
- **Code:**
  - `sim_title = cosine_similarity([jd_title_emb], [cv_title_emb])[0][0] if cv_title_text else 0.0`
- **Why:** Cosine similarity measures how close the two roles are in meaning, regardless of exact wording.

### 5. Use in Final Score
- **Why:** A high sim_title means the candidate's background is highly relevant to the job, which is a strong indicator of fit.

---

## Utility Functions Used
- `model.encode`: Converts text to embeddings.
- `cosine_similarity`: Measures similarity between two vectors.

---

## Example
- JD Title: "Data Scientist"
- Candidate Titles: "Machine Learning Engineer Data Scientist"
- Both are embedded and compared; high similarity means strong match.

---

## Summary
Each step ensures that the candidate's professional focus aligns with the job's requirements, using advanced language understanding (embeddings) for robust matching. 