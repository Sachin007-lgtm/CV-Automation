# sim_resp Calculation in CV-Automation

## What is sim_resp?
`sim_resp` measures how well the candidate's experience descriptions match the key responsibilities listed in the Job Description (JD). It is a major factor in the overall match score.

---

## Where is sim_resp Calculated?
- **Function:** `compute_similarity` in `final_main.py`
- **Helper:** `calculate_combined_sim_resp` (calls `calculate_enhanced_sim_resp`)

---

## Step-by-Step Calculation

### 1. Extract JD Responsibilities
- **Code:** `jd.keyResponsibilities` (list of strings)
- **Why:** These are the core tasks the candidate is expected to perform. Matching them ensures the candidate has relevant experience.

### 2. Extract Candidate Experience Descriptions
- **Code:** All `description` fields from `cv.experiences_list` are flattened into a single list.
- **Why:** These descriptions detail what the candidate has actually done in previous roles.

### 3. Generate Embeddings
- **Code:**
  - `jd_embeddings = model.encode(jd_responsibilities)`
  - `cv_embeddings = model.encode(cv_descriptions)`
- **Why:** Embeddings allow for semantic comparison between responsibilities and experience descriptions.

### 4. Calculate Cosine Similarity Matrix
- **Code:** `similarity_matrix = cosine_similarity(jd_embeddings, cv_embeddings)`
- **Why:** This matrix shows how well each JD responsibility matches each candidate experience description.

### 5. Weighted Best Matches
- **Code:** For each JD responsibility, take the top 2 similarities, weight them (0.7 for best, 0.3 for second-best), and average across all responsibilities.
- **Why:** This rewards candidates who have strong matches for multiple responsibilities, not just one.

### 6. Scale and Clamp
- **Code:** `final_score = 0.3 + (avg * 0.7)`
- **Why:** Ensures the score is in a reasonable range and not too harsh for partial matches.

### 7. Use in Final Score
- **Why:** A high sim_resp means the candidate has performed similar work to what the job requires.

---

## Utility Functions Used
- `model.encode`: Converts text to embeddings.
- `cosine_similarity`: Computes similarity matrix.
- `calculate_enhanced_sim_resp`: Implements the above logic.

---

## Example
- JD Responsibilities: ["Build ML models", "Deploy data pipelines"]
- Candidate Descriptions: ["Developed ML models", "Built data pipelines"]
- High similarity scores mean strong match.

---

## Summary
Each step ensures the candidate's practical experience aligns with the job's core tasks, using semantic understanding for robust matching. 