from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import UserResponse, UserRoleUpdate
from app.schemas.admin import SystemMetricsResponse, AuditLogResponse
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.api.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Administrator Oversight"])


@router.get("/metrics", response_model=SystemMetricsResponse)
def get_system_metrics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Retrieve system analytics, volume trends, and failure rate metrics."""
    return AdminService.get_system_metrics(db)


@router.get("/users", response_model=List[UserResponse])
def list_system_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all registered platform users and their roles."""
    return AuthService.list_users(db)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Assign a new role to a user (user, reviewer, admin)."""
    return AuthService.update_role(db, user_id, data.role, current_admin)


@router.get("/models")
def list_registered_models(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all registered AI detection model versions, architectures, and benchmark metrics."""
    return AdminService.get_registered_models(db)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Review immutable system security audit logs."""
    return AdminService.list_audit_logs(db, limit=limit)
