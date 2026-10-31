from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register(db: Session, data: UserRegister) -> User:
        existing = AuthService.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )
        
        # Normalize role
        role = data.role.lower() if data.role else "user"
        if role not in ["user", "reviewer", "admin"]:
            role = "user"

        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            hashed_password=get_password_hash(data.password),
            role=role,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="USER_REGISTERED",
            resource_type="user",
            resource_id=user.id,
            details=f"Role assigned: {role}"
        )
        db.add(audit)
        db.commit()

        return user

    @staticmethod
    def authenticate(db: Session, data: UserLogin) -> dict:
        user = AuthService.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )

        token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
        
        # Log login
        audit = AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="USER_LOGIN",
            resource_type="auth",
            resource_id=user.id
        )
        db.add(audit)
        db.commit()

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }

    @staticmethod
    def update_role(db: Session, target_user_id: str, new_role: str, admin_user: User) -> User:
        if admin_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only administrators can change user roles.")

        target = AuthService.get_by_id(db, target_user_id)
        if not target:
            raise HTTPException(status_code=404, detail="User not found.")

        if new_role not in ["user", "reviewer", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role specified.")

        old_role = target.role
        target.role = new_role
        target.updated_at = datetime.now(timezone.utc)
        
        audit = AuditLog(
            user_id=admin_user.id,
            user_email=admin_user.email,
            action="ROLE_UPDATED",
            resource_type="user",
            resource_id=target.id,
            details=f"Changed role from {old_role} to {new_role}"
        )
        db.add(audit)
        db.commit()
        db.refresh(target)
        return target

    @staticmethod
    def list_users(db: Session) -> List[User]:
        return db.query(User).order_by(User.created_at.desc()).all()
