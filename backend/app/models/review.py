import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analysis_jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Reviewer status options: pending_review, likely_authentic, potentially_manipulated, inconclusive
    status = Column(String(50), default="pending_review", nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("AnalysisJob", back_populates="review")
    reviewer = relationship("User", back_populates="reviews")
    history = relationship("ReviewHistory", back_populates="review", cascade="all, delete-orphan", order_by="ReviewHistory.created_at.desc()")


class ReviewHistory(Base):
    __tablename__ = "review_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("review_records.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    review = relationship("ReviewRecord", back_populates="history")
