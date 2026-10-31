from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ReviewUpdateStatus(BaseModel):
    status: str  # pending_review, likely_authentic, potentially_manipulated, inconclusive
    notes: Optional[str] = None


class ReviewUpdateNotes(BaseModel):
    notes: str


class ReviewHistoryResponse(BaseModel):
    id: str
    changed_by_user_id: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: str
    analysis_id: str
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    history: List[ReviewHistoryResponse] = []

    class Config:
        from_attributes = True
