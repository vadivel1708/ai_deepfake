from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class MediaUploadResponse(BaseModel):
    id: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    media_type: str
    sha256_hash: str
    created_at: datetime

    class Config:
        from_attributes = True


class MediaDetailResponse(BaseModel):
    id: str
    user_id: str
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    mime_type: str
    media_type: str
    sha256_hash: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
