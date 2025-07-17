# education_match Calculation in CV-Automation

## What is education_match?
`education_match` measures how well the candidate's education aligns with the education requirements in the Job Description (JD). It is a component of the overall match score.

---

## Where is education_match Calculated?
- **Function:** `compute_similarity` in `final_main.py`
- **Helper:** `calculate_education_match`

---

## Step-by-Step Calculation

### 1. Extract JD Education Requirements
- **Code:** `jd.educationRequired` (list of strings)
- **Why:** These are the minimum academic qualifications for the job.

### 2. Extract Candidate Education
- **Code:** `cv.education_list` (list of Education objects)
- **Why:** Candidate's education shows their academic background and specialization.

### 3. Extract Degree Level and Field
- **Functions:** `extract_highest_degree_level`, `extract_field`
- **Why:** Degree level (e.g., Bachelor, Master) and field (e.g., Computer Science) are key for matching.

### 4. Generate Embeddings
- **Code:**
  - Create text representations for each JD requirement and candidate education entry.
  - Encode all using the transformer model.
- **Why:** Embeddings allow for semantic comparison of education details.

### 5. Calculate Similarity Matrix and Score
- **Code:**
  - Compute similarity matrix between JD and CV education entries.
  - For each JD requirement, find the best matching candidate education.
  - Add bonuses for higher degree level and field match.
  - Average the best matches, clamp to 1.0.
- **Why:** Ensures both degree and field are considered, not just text similarity.

### 6. Use in Final Score
- **Why:** Ensures candidates meet the academic requirements for the job.

---

## Utility Functions Used
- `extract_highest_degree_level`: Determines degree level from text.
- `extract_field`: Extracts field of study from text.
- `calculate_field_similarity`: Computes semantic similarity between fields.
- `model.encode`: Converts text to embeddings.
- `util.cos_sim`: Computes similarity matrix.

---

## Example
- JD requires "Master's in Computer Science"
- Candidate has "Master of Science in Computer Science"
- High degree and field match → high score.

---

## Summary
Each step ensures the candidate's education is both sufficient and relevant, using both semantic and structural checks. 