import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(String(36), ForeignKey("media_records.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Model details
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    
    # Prediction details (Strictly AI predictions, distinct from ground truth)
    prediction = Column(String(50), nullable=True, index=True)  # likely_authentic, potentially_manipulated, inconclusive
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0 (manipulation probability)
    uncertainty_score = Column(Float, nullable=True) # 0.0 to 1.0
    
    # Detailed forensic indicators (JSON string)
    forensic_indicators = Column(Text, nullable=True)
    
    # Analysis metadata
    processing_time_seconds = Column(Float, nullable=True)
    warnings = Column(Text, nullable=True)  # JSON array of warning strings
    recommendations = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    media = relationship("MediaRecord", back_populates="analysis_jobs")
    user = relationship("User", back_populates="analysis_jobs")
    frame_predictions = relationship("FramePrediction", back_populates="job", cascade="all, delete-orphan", order_by="FramePrediction.frame_index")
    audio_segments = relationship("AudioSegmentPrediction", back_populates="job", cascade="all, delete-orphan", order_by="AudioSegmentPrediction.segment_index")
    review = relationship("ReviewRecord", back_populates="job", uselist=False, cascade="all, delete-orphan")


class FramePrediction(Base):
    __tablename__ = "frame_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    frame_index = Column(Integer, nullable=False)
    timestamp_seconds = Column(Float, nullable=False)
    score = Column(Float, nullable=False)  # Frame manipulation score
    is_suspicious = Column(Boolean, default=False, nullable=False, index=True)
    face_detected = Column(Boolean, default=False, nullable=False)
    face_bbox = Column(Text, nullable=True)  # JSON [x, y, w, h]
    thumbnail_path = Column(String(512), nullable=True)
    indicators = Column(Text, nullable=True)  # JSON indicators

    job = relationship("AnalysisJob", back_populates="frame_predictions")


class AudioSegmentPrediction(Base):
    __tablename__ = "audio_segment_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    segment_index = Column(Integer, nullable=False)
    start_time_seconds = Column(Float, nullable=False)
    end_time_seconds = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    is_suspicious = Column(Boolean, default=False, nullable=False)
    spectral_flatness = Column(Float, nullable=True)
    mfcc_anomaly_score = Column(Float, nullable=True)

    job = relationship("AnalysisJob", back_populates="audio_segments")
