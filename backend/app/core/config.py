import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
THUMBNAILS_DIR = STORAGE_DIR / "thumbnails"
FORENSICS_DIR = STORAGE_DIR / "forensics"
REPORTS_DIR = STORAGE_DIR / "reports"
MODELS_DIR = BASE_DIR / "app" / "ai_engine" / "model_artifacts"

# Ensure runtime directories exist
for path in [STORAGE_DIR, UPLOADS_DIR, THUMBNAILS_DIR, FORENSICS_DIR, REPORTS_DIR, MODELS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


class Settings:
    PROJECT_NAME: str = "AI-Based Deepfake Detection & Media Authenticity Analysis System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "deepfake-authenticity-forensic-secret-key-2026-supersecure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database
    # Default to local SQLite database in storage folder for zero-setup development,
    # or override with DATABASE_URL for PostgreSQL (e.g. postgresql://user:pass@localhost:5432/deepfake_db)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{STORAGE_DIR / 'deepfake_system.db'}")
    
    # File Upload Restrictions
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB limit
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_VIDEO_TYPES: List[str] = ["video/mp4", "video/avi", "video/quicktime", "video/x-matroska"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav", "audio/flac"]
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    THUMBNAILS_DIR: Path = THUMBNAILS_DIR
    FORENSICS_DIR: Path = FORENSICS_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    MODELS_DIR: Path = MODELS_DIR

    # AI Model Settings
    VIDEO_FRAME_SAMPLE_RATE: int = int(os.getenv("VIDEO_FRAME_SAMPLE_RATE", "10")) # Sample every 10 frames
    VIDEO_MAX_FRAMES_TO_ANALYZE: int = int(os.getenv("VIDEO_MAX_FRAMES_TO_ANALYZE", "60"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]


settings = Settings()
