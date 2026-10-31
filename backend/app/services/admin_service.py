import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.media import MediaRecord
from app.models.analysis import AnalysisJob
from app.models.review import ReviewRecord
from app.models.audit import AuditLog
from app.models.model_registry import ModelRegistry
from app.ai_engine.model_registry.registry import ModelRegistryService


class AdminService:
    @staticmethod
    def get_system_metrics(db: Session) -> Dict[str, Any]:
        total_users = db.query(User).count()
        total_media = db.query(MediaRecord).count()
        total_analyses = db.query(AnalysisJob).count()

        total_likely_authentic = db.query(AnalysisJob).filter(AnalysisJob.prediction == "likely_authentic").count()
        total_potentially_manipulated = db.query(AnalysisJob).filter(AnalysisJob.prediction == "potentially_manipulated").count()
        total_inconclusive = db.query(AnalysisJob).filter(AnalysisJob.prediction == "inconclusive").count()
        total_pending_review = db.query(ReviewRecord).filter(ReviewRecord.status == "pending_review").count()

        # Average processing time
        avg_time = db.query(func.avg(AnalysisJob.processing_time_seconds)).filter(AnalysisJob.status == "completed").scalar() or 0.0

        # Failure rate
        total_failed = db.query(AnalysisJob).filter(AnalysisJob.status == "failed").count()
        failure_rate = (total_failed / total_analyses * 100.0) if total_analyses > 0 else 0.0

        # Media breakdown
        img_count = db.query(MediaRecord).filter(MediaRecord.media_type == "image").count()
        vid_count = db.query(MediaRecord).filter(MediaRecord.media_type == "video").count()
        aud_count = db.query(MediaRecord).filter(MediaRecord.media_type == "audio").count()

        # 7-day activity volume trend
        daily_volume = []
        now = datetime.now(timezone.utc)
        for i in range(6, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            cnt = db.query(AnalysisJob).filter(
                AnalysisJob.created_at >= day_start,
                AnalysisJob.created_at < day_end
            ).count()
            daily_volume.append({
                "date": day_start.strftime("%b %d"),
                "analyses": cnt
            })

        return {
            "total_users": total_users,
            "total_media": total_media,
            "total_analyses": total_analyses,
            "total_likely_authentic": total_likely_authentic,
            "total_potentially_manipulated": total_potentially_manipulated,
            "total_inconclusive": total_inconclusive,
            "total_pending_review": total_pending_review,
            "avg_processing_time_sec": round(float(avg_time), 2),
            "failure_rate_percent": round(failure_rate, 2),
            "media_breakdown": {
                "image": img_count,
                "video": vid_count,
                "audio": aud_count
            },
            "daily_volume": daily_volume
        }

    @staticmethod
    def list_audit_logs(db: Session, limit: int = 100) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_registered_models(db: Session) -> List[Dict[str, Any]]:
        # Sync with ModelRegistryService defaults
        default_models = ModelRegistryService.list_registered_models()
        return default_models
