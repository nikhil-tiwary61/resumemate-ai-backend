from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.db import SessionLocal
from app.models.resume import JobDescription
from uuid import UUID
from typing import Any
import re

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_keywords(text: str) -> list:
    # Simple frequency-based regex keyword extraction (MVP)
    words = re.findall(r"\b\w{4,}\b", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    # Take top 10 keywords
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in sorted_keywords[:10]]

@router.post("/submit-jd")
async def submit_jd(payload: dict, db: Session = Depends(get_db)) -> Any:
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Job description content is required.")
    keywords = extract_keywords(content)
    jd = JobDescription(content=content, keywords=keywords)
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return {"id": str(jd.id), "created_at": jd.created_at, "keywords": keywords}

@router.get("/jds/{jd_id}")
def get_jd(jd_id: UUID, db: Session = Depends(get_db)):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return {
        "id": str(jd.id),
        "content": jd.content,
        "keywords": jd.keywords,
        "created_at": jd.created_at
    }
