import os
import json
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.media import MediaRecord
from app.models.user import User
from app.models.audit import AuditLog
from app.ai_engine.preprocessing.media_loader import (
    compute_sha256,
    detect_media_type,
    extract_media_metadata
)


class MediaService:
    @staticmethod
    def save_upload(db: Session, file: UploadFile, current_user: User) -> MediaRecord:
        # 1. Sanitize original filename and check extension
        original_filename = Path(file.filename or "uploaded_media").name
        content_type = file.content_type or "application/octet-stream"
        
        try:
            media_type = detect_media_type(original_filename, content_type)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # 2. Generate secure unguessable stored filename
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".jpg" if media_type == "image" else (".mp4" if media_type == "video" else ".wav")
        stored_filename = f"{uuid.uuid4()}{ext}"
        target_path = settings.UPLOADS_DIR / stored_filename

        # 3. Stream file safely and check file size limit
        bytes_written = 0
        try:
            with open(target_path, "wb") as buffer:
                while chunk := file.file.read(1024 * 1024):  # 1MB chunks
                    bytes_written += len(chunk)
                    if bytes_written > settings.MAX_UPLOAD_SIZE_BYTES:
                        buffer.close()
                        if target_path.exists(): os.remove(target_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Uploaded file exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB."
                        )
                    buffer.write(chunk)
        except HTTPException:
            raise
        except Exception as e:
            if target_path.exists(): os.remove(target_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded file: {str(e)}"
            )

        if bytes_written == 0:
            if target_path.exists(): os.remove(target_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        # 4. Compute cryptographic SHA256 checksum
        sha256 = compute_sha256(str(target_path))

        # 5. Extract metadata safely
        metadata = extract_media_metadata(str(target_path), media_type)

        # 6. Store record in database
        media_record = MediaRecord(
            user_id=current_user.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(target_path),
            file_size_bytes=bytes_written,
            mime_type=content_type,
            media_type=media_type,
            sha256_hash=sha256,
            metadata_json=json.dumps(metadata)
        )
        db.add(media_record)
        db.commit()
        db.refresh(media_record)

        # 7. Audit log
        audit = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action="MEDIA_UPLOADED",
            resource_type="media",
            resource_id=media_record.id,
            details=f"Type: {media_type}, Size: {bytes_written} bytes, SHA256: {sha256[:16]}..."
        )
        db.add(audit)
        db.commit()

        return media_record

    @staticmethod
    def get_media(db: Session, media_id: str, current_user: User) -> MediaRecord:
        media = db.query(MediaRecord).filter(MediaRecord.id == media_id).first()
        if not media:
            raise HTTPException(status_code=404, detail="Media not found.")

        # User isolation: users can only view their own media unless reviewer or admin
        if media.user_id != current_user.id and current_user.role not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this media.")

        return media

    @staticmethod
    def delete_media(db: Session, media_id: str, current_user: User) -> bool:
        media = MediaService.get_media(db, media_id, current_user)
        
        # Remove physical file if exists
        if os.path.exists(media.file_path):
            try:
                os.remove(media.file_path)
            except Exception:
                pass

        audit = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action="MEDIA_DELETED",
            resource_type="media",
            resource_id=media.id,
            details=f"Filename: {media.original_filename}"
        )
        db.add(audit)
        db.delete(media)
        db.commit()
        return True
