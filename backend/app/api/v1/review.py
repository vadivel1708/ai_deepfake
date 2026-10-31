from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.review import ReviewUpdateStatus, ReviewUpdateNotes, ReviewResponse
from app.services.review_service import ReviewService
from app.api.deps import get_current_user, get_current_reviewer_or_admin
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Forensic Review Workflow"])


@router.get("/pending", response_model=List[Dict[str, Any]])
def get_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reviewer_or_admin)
):
    """Retrieve all pending media items requiring human forensic review."""
    return ReviewService.get_pending_reviews(db, current_user)


@router.post("/{analysis_id}/notes")
def update_review_notes(
    analysis_id: str,
    data: ReviewUpdateNotes,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reviewer_or_admin)
):
    """Add or update reviewer notes on an analysis."""
    review = ReviewService.update_notes(db, analysis_id, data.notes, current_user)
    return {"message": "Notes saved successfully.", "review_id": review.id}


@router.patch("/{analysis_id}/status")
def update_review_status(
    analysis_id: str,
    data: ReviewUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_reviewer_or_admin)
):
    """Update human review status (pending_review, likely_authentic, potentially_manipulated, inconclusive)."""
    review = ReviewService.update_status(db, analysis_id, data.status, data.notes, current_user)
    return {
        "message": "Review status updated successfully.",
        "analysis_id": analysis_id,
        "new_status": review.status,
        "updated_at": review.updated_at
    }
