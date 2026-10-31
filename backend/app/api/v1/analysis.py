import json
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analysis import (
    AnalysisJobCreate,
    AnalysisJobResponse,
    AnalysisJobDetailResponse,
    AnalysisFilter
)
from app.services.analysis_service import AnalysisService
from app.services.media_service import MediaService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analysis", tags=["AI Media Analysis"])


@router.post("/create", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_analysis_job(
    data: AnalysisJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a background AI analysis job for an uploaded media file."""
    job = AnalysisService.create_job(db, data.media_id, current_user, background_tasks, data.model_name)
    return job


@router.post("/image", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_image_direct(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Direct upload and trigger analysis for an image file."""
    media = MediaService.save_upload(db, file, current_user)
    job = AnalysisService.create_job(db, media.id, current_user, background_tasks)
    return job


@router.post("/video", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_video_direct(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Direct upload and trigger analysis for a video file."""
    media = MediaService.save_upload(db, file, current_user)
    job = AnalysisService.create_job(db, media.id, current_user, background_tasks)
    return job


@router.post("/audio", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_audio_direct(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Direct upload and trigger analysis for an audio file."""
    media = MediaService.save_upload(db, file, current_user)
    job = AnalysisService.create_job(db, media.id, current_user, background_tasks)
    return job


@router.get("/history")
def get_analysis_history(
    media_type: Optional[str] = Query(None),
    prediction: Optional[str] = Query(None),
    job_status: Optional[str] = Query(None, alias="status"),
    query: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated history of analysis jobs with filters."""
    filters = AnalysisFilter(
        media_type=media_type,
        prediction=prediction,
        status=job_status,
        query=query,
        skip=skip,
        limit=limit
    )
    return AnalysisService.list_jobs(db, filters, current_user)


@router.get("/{analysis_id}/status")
def get_job_status(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lightweight polling endpoint to check current processing status."""
    job = AnalysisService.get_job(db, analysis_id, current_user)
    return {
        "id": job.id,
        "status": job.status,
        "prediction": job.prediction,
        "confidence_score": job.confidence_score,
        "error_message": job.error_message
    }


@router.get("/{analysis_id}", response_model=AnalysisJobDetailResponse)
def get_job_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis report including frame-level metrics and reviewer notes."""
    job = AnalysisService.get_job(db, analysis_id, current_user)
    
    # Process frame predictions
    frames = []
    for fp in job.frame_predictions:
        frames.append({
            "id": fp.id,
            "frame_index": fp.frame_index,
            "timestamp_seconds": fp.timestamp_seconds,
            "score": fp.score,
            "is_suspicious": fp.is_suspicious,
            "face_detected": fp.face_detected,
            "face_bbox": json.loads(fp.face_bbox) if fp.face_bbox else None,
            "thumbnail_url": fp.thumbnail_path,
            "indicators": json.loads(fp.indicators) if fp.indicators else None
        })

    # Process audio segments
    audio_segs = []
    for asp in job.audio_segments:
        audio_segs.append({
            "id": asp.id,
            "segment_index": asp.segment_index,
            "start_time_seconds": asp.start_time_seconds,
            "end_time_seconds": asp.end_time_seconds,
            "score": asp.score,
            "is_suspicious": asp.is_suspicious,
            "spectral_flatness": asp.spectral_flatness,
            "mfcc_anomaly_score": asp.mfcc_anomaly_score
        })

    return {
        "id": job.id,
        "media_id": job.media_id,
        "user_id": job.user_id,
        "status": job.status,
        "error_message": job.error_message,
        "model_name": job.model_name,
        "model_version": job.model_version,
        "prediction": job.prediction,
        "confidence_score": job.confidence_score,
        "uncertainty_score": job.uncertainty_score,
        "forensic_indicators": json.loads(job.forensic_indicators) if job.forensic_indicators else None,
        "processing_time_seconds": job.processing_time_seconds,
        "warnings": json.loads(job.warnings) if job.warnings else [],
        "recommendations": job.recommendations,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "completed_at": job.completed_at,
        "media_type": job.media.media_type if job.media else None,
        "original_filename": job.media.original_filename if job.media else None,
        "frame_predictions": frames,
        "audio_segments": audio_segs,
        "review_status": job.review.status if job.review else None,
        "review_notes": job.review.notes if job.review else None
    }


@router.post("/{analysis_id}/retry", response_model=AnalysisJobResponse)
def retry_analysis_job(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry a failed analysis job."""
    job = AnalysisService.retry_job(db, analysis_id, current_user, background_tasks)
    return job
