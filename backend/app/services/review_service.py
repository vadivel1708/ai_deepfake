from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.review import ReviewRecord, ReviewHistory
from app.models.analysis import AnalysisJob
from app.models.user import User
from app.models.audit import AuditLog


class ReviewService:
    @staticmethod
    def get_pending_reviews(db: Session, current_user: User) -> List[Dict[str, Any]]:
        if current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Reviewer or administrator privileges required.")

        records = (
            db.query(ReviewRecord)
            .join(AnalysisJob)
            .filter(ReviewRecord.status == "pending_review")
            .order_by(AnalysisJob.created_at.desc())
            .all()
        )

        output = []
        for r in records:
            output.append({
                "id": r.id,
                "analysis_id": r.analysis_id,
                "status": r.status,
                "notes": r.notes,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "media_type": r.job.media.media_type if r.job and r.job.media else None,
                "original_filename": r.job.media.original_filename if r.job and r.job.media else None,
                "ai_prediction": r.job.prediction if r.job else None,
                "ai_confidence": r.job.confidence_score if r.job else None
            })
        return output

    @staticmethod
    def get_review_by_analysis_id(db: Session, analysis_id: str) -> Optional[ReviewRecord]:
        return db.query(ReviewRecord).filter(ReviewRecord.analysis_id == analysis_id).first()

    @staticmethod
    def update_status(db: Session, analysis_id: str, new_status: str, notes: Optional[str], current_user: User) -> ReviewRecord:
        if current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Reviewer or administrator privileges required.")

        valid_statuses = ["pending_review", "likely_authentic", "potentially_manipulated", "inconclusive"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

        review = db.query(ReviewRecord).filter(ReviewRecord.analysis_id == analysis_id).first()
        if not review:
            review = ReviewRecord(analysis_id=analysis_id, status=new_status, notes=notes, reviewer_id=current_user.id)
            db.add(review)
            db.commit()
            db.refresh(review)

        prev_status = review.status
        review.status = new_status
        review.reviewer_id = current_user.id
        if notes:
            review.notes = notes
        review.updated_at = datetime.now(timezone.utc)

        # Record history audit
        history = ReviewHistory(
            review_id=review.id,
            changed_by_user_id=current_user.id,
            previous_status=prev_status,
            new_status=new_status,
            notes=notes
        )
        db.add(history)

        # System audit log
        audit = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action="REVIEW_STATUS_UPDATED",
            resource_type="review",
            resource_id=review.id,
            details=f"Status changed from {prev_status} to {new_status}"
        )
        db.add(audit)
        db.commit()
        db.refresh(review)

        return review

    @staticmethod
    def update_notes(db: Session, analysis_id: str, notes: str, current_user: User) -> ReviewRecord:
        if current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Reviewer or administrator privileges required.")

        review = db.query(ReviewRecord).filter(ReviewRecord.analysis_id == analysis_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review record not found.")

        review.notes = notes
        review.reviewer_id = current_user.id
        review.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(review)
        return review
