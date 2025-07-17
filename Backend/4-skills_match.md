# skills_match Calculation in CV-Automation

## What is skills_match?
`skills_match` measures how well the candidate's listed skills align with the required skills in the Job Description (JD). It is a significant part of the overall match score.

---

## Where is skills_match Calculated?
- **Function:** `compute_similarity` in `final_main.py`
- **Helper:** `calculate_skills_match`

---

## Step-by-Step Calculation

### 1. Extract JD Required Skills
- **Code:** `jd.requiredSkills` (list of strings)
- **Why:** These are the skills the employer considers essential for the role.

### 2. Extract Candidate Skills
- **Code:** `cv.skills_list` (list of Skill objects, use `skillName`)
- **Why:** Candidate's skills show their technical and professional capabilities.

### 3. Generate Embeddings
- **Code:**
  - Join JD required skills and candidate skills into single strings.
  - Encode both using the transformer model.
- **Why:** Embeddings allow for semantic comparison, not just exact matches.

### 4. Calculate Cosine Similarity
- **Code:**
  - `semantic_similarity = cosine_similarity([jd_skills_emb], [cv_skills_emb])[0][0]`
  - Clamp score between 0.3 and 1.0.
- **Why:** Measures how close the candidate's skills are to the JD requirements.

### 5. Use in Final Score
- **Why:** Ensures candidates have the right technical and soft skills for the job.

---

## Utility Functions Used
- `model.encode`: Converts text to embeddings.
- `cosine_similarity`: Measures similarity between two vectors.

---

## Example
- JD Required Skills: ["Python", "Machine Learning"]
- Candidate Skills: ["Python", "Deep Learning", "ML"]
- High overlap and semantic similarity → high match.

---

## Summary
Each step ensures the candidate's skills are relevant and sufficient, using advanced language understanding for robust matching. 