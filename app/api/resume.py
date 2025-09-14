from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.db import SessionLocal
from app.models.resume import Resume
from app.services.resume_service import ResumeService
from uuid import UUID
from typing import Any
import os
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document as DocxDocument

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_text_from_pdf(file_path: str) -> str:
    return extract_pdf_text(file_path)

def extract_text_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

@router.post("/upload-resume")
async def upload_resume(file: UploadFile, db: Session = Depends(get_db)) -> Any:
    try:
        ResumeService.validate_file_type(file)
        temp_file_path = ResumeService.save_temp_file(file)
        text = ResumeService.extract_text(temp_file_path, file.content_type)
        os.remove(temp_file_path)
        new_resume = ResumeService.save_resume_to_db(db, file.filename, text)
        return {"id": str(new_resume.id), "filename": new_resume.filename, "created_at": new_resume.created_at.isoformat()}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@router.get("/resumes/{resume_id}")
def get_resume(resume_id: UUID, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": str(resume.id),
        "filename": resume.filename,
        "content": resume.content,
        "created_at": resume.created_at.isoformat()
    }
