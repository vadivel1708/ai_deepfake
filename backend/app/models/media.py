import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base


class MediaRecord(Base):
    __tablename__ = "media_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    media_type = Column(String(50), nullable=False, index=True)  # "image", "video", "audio"
    sha256_hash = Column(String(64), nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded technical metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="media_items")
    analysis_jobs = relationship("AnalysisJob", back_populates="media", cascade="all, delete-orphan")
