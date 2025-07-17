# 📄 Resume–JD AI 🔍

An intelligent system that:
- ✅ Uploads resumes (PDF or DOCX)
- ✅ Extracts content using NLP
- ✅ (Coming Soon) Matches resumes to job descriptions with AI
- ✅ (Coming Soon) Generates personalized interview questions

Built using **FastAPI (backend)** and **React (frontend)**.

---

## 🚀 Features

- Upload resumes via drag-and-drop or file picker
- Supports `.pdf` and `.docx` formats
- Extracts key resume content on the backend
- Displays file metadata (name, size, type)
- CORS-enabled for frontend integration
- RESTful architecture ready for AI-powered matching

---

## 📦 Tech Stack

| Layer        | Tech                          |
|--------------|-------------------------------|
| Frontend     | React, Axios, Tailwind CSS    |
| Backend      | FastAPI, PyPDF2, python-docx  |
| File Upload  | `multipart/form-data`         |
| Language     | Python 3.11 / JavaScript      |

---

## 📁 Project Structure

```text
📦 project-root
├── backend/
│   ├── main.py               # FastAPI app
│   └── requirements.txt
└── frontend/
    └── src/
        └── components/
            └── FileUpload.jsx


---

### ✅ Backend Setup

```bash
cd backend
conda create -p venv python==3.12
conda activate venv or conda activate ./venv
pip install -r requirements.txt
uvicorn final_main:app --reload

**Ensure these are in requirements.txt:
fastapi
uvicorn
python-multipart
PyPDF2
python-docx


✅ Frontend Setup
cd frontend
npm install
npm run dev

Ensure Axios is installed:
npm install axios
🔗 API Endpoints
Method	Endpoint	Description
GET	/	Health check
POST	/upload	Upload and extract file

🧠 Upcoming Features

Resume vs JD semantic matching (with cosine similarity) [Optional]

NLP-based question generator

PDF export of evaluation report
