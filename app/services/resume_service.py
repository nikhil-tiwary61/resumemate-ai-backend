import os
import logging
from dotenv import load_dotenv
from fastapi import UploadFile
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document as DocxDocument
from app.models.resume import Resume
from sqlalchemy.orm import Session
from datetime import datetime
import shutil

load_dotenv()

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 5)) * 1024 * 1024  # Default 5MB
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain").split(",")

AI_SERVICE_ENDPOINT = os.getenv("AI_SERVICE_ENDPOINT", "http://localhost:8000")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")

class ResumeService:
    @staticmethod
    def validate_file_type(file: UploadFile):
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}")

    @staticmethod
    def save_temp_file(file: UploadFile) -> str:
        temp_file_path = f"/tmp/{datetime.now().timestamp()}_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return temp_file_path

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        if file_type == "application/pdf":
            return extract_pdf_text(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = DocxDocument(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            raise ValueError("Unsupported file type for extraction.")

    @staticmethod
    def save_resume_to_db(db: Session, filename: str, content: str) -> Resume:
        new_resume = Resume(filename=filename, content=content)
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        return new_resume
