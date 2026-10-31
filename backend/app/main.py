import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import engine, Base, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

# Import API Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.media import router as media_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.review import router as review_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI Media Authenticity Analysis and Deepfake Detection Platform."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage for evidence inspection (thumbnails, ELA maps, FFT spectrograms)
app.mount("/storage/thumbnails", StaticFiles(directory=str(settings.THUMBNAILS_DIR)), name="thumbnails")
app.mount("/storage/forensics", StaticFiles(directory=str(settings.FORENSICS_DIR)), name="forensics")
app.mount("/storage/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")


# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(media_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(review_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    """Initialize database tables and seed demo accounts."""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed default demonstration users
        demo_users = [
            ("admin@deepfake.ai", "Admin User", "Admin@1234", "admin"),
            ("reviewer@deepfake.ai", "Lead Forensic Reviewer", "Reviewer@1234", "reviewer"),
            ("user@deepfake.ai", "Investigative Analyst", "User@1234", "user")
        ]
        for email, name, pwd, role in demo_users:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                u = User(
                    email=email,
                    full_name=name,
                    hashed_password=get_password_hash(pwd),
                    role=role,
                    is_active=True,
                    is_verified=True
                )
                db.add(u)
        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs"
    }
