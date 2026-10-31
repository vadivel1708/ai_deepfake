from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AnalysisJobCreate(BaseModel):
    media_id: str
    model_name: Optional[str] = None


class FramePredictionResponse(BaseModel):
    id: str
    frame_index: int
    timestamp_seconds: float
    score: float
    is_suspicious: bool
    face_detected: bool
    face_bbox: Optional[Any] = None
    thumbnail_url: Optional[str] = None
    indicators: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AudioSegmentResponse(BaseModel):
    id: str
    segment_index: int
    start_time_seconds: float
    end_time_seconds: float
    score: float
    is_suspicious: bool
    spectral_flatness: Optional[float] = None
    mfcc_anomaly_score: Optional[float] = None

    class Config:
        from_attributes = True


class AnalysisJobResponse(BaseModel):
    id: str
    media_id: str
    user_id: str
    status: str
    error_message: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    prediction: Optional[str] = None
    confidence_score: Optional[float] = None
    uncertainty_score: Optional[float] = None
    forensic_indicators: Optional[Dict[str, Any]] = None
    processing_time_seconds: Optional[float] = None
    warnings: Optional[List[str]] = None
    recommendations: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    # Enriched media preview info
    media_type: Optional[str] = None
    original_filename: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisJobDetailResponse(AnalysisJobResponse):
    frame_predictions: List[FramePredictionResponse] = []
    audio_segments: List[AudioSegmentResponse] = []
    review_status: Optional[str] = None
    review_notes: Optional[str] = None


class AnalysisFilter(BaseModel):
    media_type: Optional[str] = None
    prediction: Optional[str] = None
    status: Optional[str] = None
    query: Optional[str] = None
    skip: int = 0
    limit: int = 50
