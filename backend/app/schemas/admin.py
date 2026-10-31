from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SystemMetricsResponse(BaseModel):
    total_users: int
    total_media: int
    total_analyses: int
    total_likely_authentic: int
    total_potentially_manipulated: int
    total_inconclusive: int
    total_pending_review: int
    avg_processing_time_sec: float
    failure_rate_percent: float
    media_breakdown: Dict[str, int]
    daily_volume: List[Dict[str, Any]]


class ModelRegistryCreate(BaseModel):
    name: str
    version: str
    media_type: str
    architecture: str
    trained_on: Optional[str] = None
    metrics_json: Optional[str] = None
    is_active: bool = True
    artifact_path: Optional[str] = None


class ModelRegistryResponse(BaseModel):
    id: str
    name: str
    version: str
    media_type: str
    architecture: str
    trained_on: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: bool
    artifact_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True
