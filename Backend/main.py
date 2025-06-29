from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2, docx, io, string, nltk
import numpy as np
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer



# Load sentence transformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Setup NLTK data directory
nltk.data.path.append('C:/Users/sachi/nltk_data')

# Text cleaning function
def clean_text(raw_text):
    text = raw_text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words and word.isalpha()]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(words)

# Initialize FastAPI app
app = FastAPI()

# CORS setup for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PDF and DOCX extraction
def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file_bytes):
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

# Combined text extraction function
def extract_text(file_bytes, file_type):
    if file_type == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif file_type in ['docx', 'doc']:
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

# Upload API endpoint with optional JD
def calculate_similarity(embedding1, embedding2):
    return float(util.cos_sim(embedding1, embedding2)[0][0])

# 🚀 Upload multiple CVs
@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File(...), jd: str = Form(...)):
    try:
        cleaned_jd = clean_text(jd)
        jd_embedding = model.encode(cleaned_jd, convert_to_tensor=True)

        candidates = []

        for file in files:
            try:
                contents = await file.read()
                file_type = file.filename.split(".")[-1].lower()
                raw_text = extract_text(contents, file_type)
                cleaned_resume = clean_text(raw_text)
                resume_embedding = model.encode(cleaned_resume, convert_to_tensor=True)
                score = calculate_similarity(resume_embedding, jd_embedding)

                candidates.append({
                    "filename": file.filename,
                    "similarity_score": round(score, 4),
                    "raw_text": raw_text,
                    "cleaned_resume_text": cleaned_resume[:500] + "..." if len(cleaned_resume) > 500 else cleaned_resume
                })
            except Exception as e:
                candidates.append({
                    "filename": file.filename,
                    "similarity_score": 0.0,
                    "error": str(e),
                    "raw_text": "",
                    "cleaned_resume_text": ""
                })

        # Sort by similarity descending
        sorted_candidates = sorted(candidates, key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "results": sorted_candidates,
            "total_files": len(files),
            "jd_preview": cleaned_jd[:200] + "..." if len(cleaned_jd) > 200 else cleaned_jd
        }
    except Exception as e:
        return {
            "error": str(e),
            "results": [],
            "total_files": 0
        }

# 🚀 Single file upload (for frontend compatibility)
@app.post("/upload")
async def upload_single(file: UploadFile = File(...), jd: str = Form(None)):
    try:
        contents = await file.read()
        file_type = file.filename.split(".")[-1].lower()
        raw_text = extract_text(contents, file_type)
        cleaned_text = clean_text(raw_text)
        
        response_data = {
            "filename": file.filename,
            "type": file.content_type,
            "raw_text": raw_text,
            "cleaned_resume_text": cleaned_text,
        }
        
        # If JD is provided, calculate similarity
        if jd:
            cleaned_jd = clean_text(jd)
            jd_embedding = model.encode(cleaned_jd, convert_to_tensor=True)
            resume_embedding = model.encode(cleaned_text, convert_to_tensor=True)
            similarity = calculate_similarity(resume_embedding, jd_embedding)
            response_data["similarity_score_with_jd"] = round(similarity, 4)
        
        return response_data
        
    except Exception as e:
        return {
            "error": str(e),
            "filename": file.filename,
            "raw_text": "",
            "cleaned_resume_text": "",
            "similarity_score_with_jd": 0.0
        }

# 🚀 Process both JD and CV together
@app.post("/process-match")
async def process_match(jd_file: UploadFile = File(...), cv_file: UploadFile = File(...)):
    try:
        # Process JD file
        jd_contents = await jd_file.read()
        jd_file_type = jd_file.filename.split(".")[-1].lower()
        jd_raw_text = extract_text(jd_contents, jd_file_type)
        cleaned_jd = clean_text(jd_raw_text)
        
        # Process CV file
        cv_contents = await cv_file.read()
        cv_file_type = cv_file.filename.split(".")[-1].lower()
        cv_raw_text = extract_text(cv_contents, cv_file_type)
        cleaned_cv = clean_text(cv_raw_text)
        
        # Calculate similarity
        jd_embedding = model.encode(cleaned_jd, convert_to_tensor=True)
        cv_embedding = model.encode(cleaned_cv, convert_to_tensor=True)
        similarity = calculate_similarity(cv_embedding, jd_embedding)
        
        return {
            "similarity_score": round(similarity, 4),
            "jd_raw_text": jd_raw_text,
            "cv_raw_text": cv_raw_text,
            "jd_text": cleaned_jd,
            "cv_text": cleaned_cv,
            "jd_filename": jd_file.filename,
            "cv_filename": cv_file.filename
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "similarity_score": 0.0
        }

@app.get("/")
def home():
    return {"message": "FastAPI + Sentence Transformers running 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
