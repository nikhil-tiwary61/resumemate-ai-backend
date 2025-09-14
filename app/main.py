import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.resume import router as resume_router
from app.api.jd import router as jd_router

# Load environment variables from .env file
load_dotenv()

# Get environment variables with defaults
APP_TITLE = os.getenv("APP_TITLE", "ResumeMate AI")
APP_DESCRIPTION = os.getenv(
    "APP_DESCRIPTION", 
    "AI-powered resume analysis and enhancement service"
)
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOW_CREDENTIALS = os.getenv("ALLOW_CREDENTIALS", "True").lower() == "true"
ALLOW_METHODS = os.getenv("ALLOW_METHODS", "*").split(",")
ALLOW_HEADERS = os.getenv("ALLOW_HEADERS", "*").split(",")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    debug=DEBUG
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=ALLOW_METHODS,
    allow_headers=ALLOW_HEADERS,
)

# Include routers
app.include_router(resume_router, prefix="/api", tags=["resumes"])
app.include_router(jd_router, prefix="/api", tags=["job_descriptions"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {APP_TITLE} API",
        "version": APP_VERSION,
        "docs": "/docs",
        "environment": "development" if DEBUG else "production"
    }
