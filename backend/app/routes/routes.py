"""
routes.py — FastAPI endpoint: POST /analyze
Accepts multipart form (PDF file + role + job_description),
extracts text, runs NLP, returns JSON result.
"""

import os
import io
import shutil
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.services.nlp_service import analyze_cv

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PyMuPDF is not installed. Run: pip install PyMuPDF"
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract text from PDF: {str(e)}"
        )


@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    job_description: str = Form(...),
):
    # ── Validation ──────────────────────────────
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5 MB limit.")

    if not role.strip():
        raise HTTPException(status_code=400, detail="Job role cannot be empty.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # ── Save file (optional, for logging/debugging) ──
    safe_name = file.filename.replace(" ", "_")
    with open(f"{UPLOAD_FOLDER}/{safe_name}", "wb") as f:
        f.write(file_bytes)

    # ── Extract text from PDF ────────────────────
    cv_text = extract_text_from_pdf(file_bytes)

    if len(cv_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from this PDF. Make sure it is not a scanned image-only file."
        )

    # ── Run NLP analysis ────────────────────────
    try:
        result = analyze_cv(
            cv_text=cv_text,
            job_role=role.strip(),
            job_description=job_description.strip(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return JSONResponse(content=result)
