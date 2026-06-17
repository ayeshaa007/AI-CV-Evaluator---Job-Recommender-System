"""
job_routes.py
POST /recommend-jobs
Accepts PDF upload, returns job recommendations.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import fitz  # PyMuPDF

from app.services.job_recommender import recommend_jobs

job_router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@job_router.post("/recommend-jobs")
async def recommend_jobs_endpoint(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5 MB.")

    # Extract text
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        cv_text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {e}")

    if len(cv_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text. Make sure the PDF is not a scanned image."
        )

    try:
        result = recommend_jobs(cv_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return JSONResponse(content=result)
