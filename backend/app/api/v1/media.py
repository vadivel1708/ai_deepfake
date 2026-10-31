import json
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.media import MediaUploadResponse, MediaDetailResponse
from app.services.media_service import MediaService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/media", tags=["Media Management"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload media file with format and size validation."""
    media = MediaService.save_upload(db, file, current_user)
    return media


@router.get("/{media_id}", response_model=MediaDetailResponse)
def get_media_details(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get metadata for uploaded media."""
    media = MediaService.get_media(db, media_id, current_user)
    return {
        "id": media.id,
        "user_id": media.user_id,
        "original_filename": media.original_filename,
        "stored_filename": media.stored_filename,
        "file_size_bytes": media.file_size_bytes,
        "mime_type": media.mime_type,
        "media_type": media.media_type,
        "sha256_hash": media.sha256_hash,
        "metadata": json.loads(media.metadata_json) if media.metadata_json else None,
        "created_at": media.created_at
    }


@router.delete("/{media_id}", status_code=status.HTTP_200_OK)
def delete_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete uploaded media record and storage file."""
    MediaService.delete_media(db, media_id, current_user)
    return {"message": "Media successfully deleted."}
