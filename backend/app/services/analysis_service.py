import os
import json
import time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks

from app.models.analysis import AnalysisJob, FramePrediction, AudioSegmentPrediction
from app.models.media import MediaRecord
from app.models.user import User
from app.models.review import ReviewRecord
from app.models.audit import AuditLog
from app.schemas.analysis import AnalysisFilter
from app.ai_engine.model_registry.registry import ModelRegistryService


class AnalysisService:
    @staticmethod
    def create_job(db: Session, media_id: str, current_user: User, background_tasks: BackgroundTasks, model_name: Optional[str] = None) -> AnalysisJob:
        media = db.query(MediaRecord).filter(MediaRecord.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media record not found.")

        if media.user_id != current_user.id and current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Unauthorized to analyze this media.")

        # Instantiate job
        job = AnalysisJob(
            media_id=media.id,
            user_id=current_user.id,
            status="pending",
            model_name=model_name or "Forensic-Ensemble-Pipeline"
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Initialize corresponding human review record
        review = ReviewRecord(
            analysis_id=job.id,
            status="pending_review",
            notes="Awaiting initial forensic assessment by qualified reviewer."
        )
        db.add(review)
        db.commit()

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action="ANALYSIS_JOB_CREATED",
            resource_type="analysis",
            resource_id=job.id,
            details=f"Media: {media.original_filename} ({media.media_type})"
        )
        db.add(audit)
        db.commit()

        # Launch background execution
        background_tasks.add_task(AnalysisService.execute_analysis_worker, job.id)

        return job

    @staticmethod
    def execute_analysis_worker(job_id: str):
        """Background worker that runs the AI detection pipeline independently."""
        from app.database.session import SessionLocal
        db = SessionLocal()
        start_time = time.time()
        try:
            job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
            if not job:
                return

            job.status = "processing"
            db.commit()

            media = db.query(MediaRecord).filter(MediaRecord.id == job.media_id).first()
            if not media or not os.path.exists(media.file_path):
                job.status = "failed"
                job.error_message = "Source media file could not be accessed on the server storage."
                db.commit()
                return

            # Retrieve model detector for the media type
            detector = ModelRegistryService.get_detector(media.media_type)
            metadata = json.loads(media.metadata_json) if media.metadata_json else {}

            # Execute model inference
            result = detector.predict(media.file_path, metadata=metadata)
            elapsed_time = round(time.time() - start_time, 2)

            # Persist frame predictions if video
            if result.frame_results:
                for f in result.frame_results:
                    fp = FramePrediction(
                        analysis_id=job.id,
                        frame_index=f.frame_index,
                        timestamp_seconds=f.timestamp_seconds,
                        score=f.score,
                        is_suspicious=f.is_suspicious,
                        face_detected=f.face_detected,
                        face_bbox=json.dumps(f.face_bbox) if f.face_bbox else None,
                        thumbnail_path=f.thumbnail_path,
                        indicators=json.dumps(f.indicators) if f.indicators else None
                    )
                    db.add(fp)

            # Persist audio segments if audio
            if result.audio_segments:
                for s in result.audio_segments:
                    asp = AudioSegmentPrediction(
                        analysis_id=job.id,
                        segment_index=s.segment_index,
                        start_time_seconds=s.start_time_seconds,
                        end_time_seconds=s.end_time_seconds,
                        score=s.score,
                        is_suspicious=s.is_suspicious,
                        spectral_flatness=s.spectral_flatness,
                        mfcc_anomaly_score=s.mfcc_anomaly_score
                    )
                    db.add(asp)

            # Update job state
            job.status = "completed"
            job.model_name = result.model_name
            job.model_version = result.model_version
            job.prediction = result.prediction
            job.confidence_score = result.confidence_score
            job.uncertainty_score = result.uncertainty_score
            job.forensic_indicators = json.dumps(result.forensic_indicators)
            job.warnings = json.dumps(result.warnings)
            job.recommendations = result.recommendations
            job.processing_time_seconds = elapsed_time
            job.completed_at = datetime.now(timezone.utc)
            job.updated_at = datetime.now(timezone.utc)

            db.commit()

        except Exception as e:
            db.rollback()
            try:
                job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.completed_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()

    @staticmethod
    def get_job(db: Session, job_id: str, current_user: User) -> AnalysisJob:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Analysis job not found.")

        if job.user_id != current_user.id and current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Unauthorized to view this analysis.")

        return job

    @staticmethod
    def list_jobs(db: Session, filters: AnalysisFilter, current_user: User) -> Dict[str, Any]:
        query = db.query(AnalysisJob).join(MediaRecord)

        # Standard users see only their own jobs; reviewers/admins see all
        if current_user.role not in ["reviewer", "admin"]:
            query = query.filter(AnalysisJob.user_id == current_user.id)

        if filters.media_type:
            query = query.filter(MediaRecord.media_type == filters.media_type)
        if filters.status:
            query = query.filter(AnalysisJob.status == filters.status)
        if filters.prediction:
            query = query.filter(AnalysisJob.prediction == filters.prediction)
        if filters.query:
            query = query.filter(
                (MediaRecord.original_filename.ilike(f"%{filters.query}%")) |
                (AnalysisJob.id.ilike(f"%{filters.query}%"))
            )

        total = query.count()
        jobs = query.order_by(AnalysisJob.created_at.desc()).offset(filters.skip).limit(filters.limit).all()

        results = []
        for j in jobs:
            results.append({
                "id": j.id,
                "media_id": j.media_id,
                "user_id": j.user_id,
                "status": j.status,
                "error_message": j.error_message,
                "model_name": j.model_name,
                "model_version": j.model_version,
                "prediction": j.prediction,
                "confidence_score": j.confidence_score,
                "uncertainty_score": j.uncertainty_score,
                "forensic_indicators": json.loads(j.forensic_indicators) if j.forensic_indicators else None,
                "processing_time_seconds": j.processing_time_seconds,
                "warnings": json.loads(j.warnings) if j.warnings else [],
                "recommendations": j.recommendations,
                "created_at": j.created_at,
                "updated_at": j.updated_at,
                "completed_at": j.completed_at,
                "media_type": j.media.media_type if j.media else None,
                "original_filename": j.media.original_filename if j.media else None
            })

        return {"total": total, "items": results}

    @staticmethod
    def retry_job(db: Session, job_id: str, current_user: User, background_tasks: BackgroundTasks) -> AnalysisJob:
        job = AnalysisService.get_job(db, job_id, current_user)
        job.status = "pending"
        job.error_message = None
        job.completed_at = None
        db.commit()

        background_tasks.add_task(AnalysisService.execute_analysis_worker, job.id)
        return job
