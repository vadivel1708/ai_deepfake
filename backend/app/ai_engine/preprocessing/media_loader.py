import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple
import cv2
from PIL import Image

from app.core.config import settings


def compute_sha256(file_path: str) -> str:
    """Calculate SHA256 cryptographic hash of a file for audit and tamper verification."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def detect_media_type(filename: str, mime_type: str) -> str:
    """Classify media into 'image', 'video', or 'audio' based on MIME type and extension."""
    ext = Path(filename).suffix.lower()
    
    if mime_type in settings.ALLOWED_IMAGE_TYPES or ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return "image"
    elif mime_type in settings.ALLOWED_VIDEO_TYPES or ext in [".mp4", ".avi", ".mov", ".mkv"]:
        return "video"
    elif mime_type in settings.ALLOWED_AUDIO_TYPES or ext in [".wav", ".mp3", ".flac", ".m4a"]:
        return "audio"
    else:
        raise ValueError(f"Unsupported file format ({mime_type}, {ext})")


def extract_media_metadata(file_path: str, media_type: str) -> Dict[str, Any]:
    """Safely extract technical metadata without trusting user-provided file headers."""
    meta: Dict[str, Any] = {
        "file_size_bytes": os.path.getsize(file_path),
        "media_type": media_type
    }

    if media_type == "image":
        try:
            with Image.open(file_path) as img:
                meta["width"] = img.width
                meta["height"] = img.height
                meta["format"] = img.format
                meta["mode"] = img.mode
                # Check for EXIF metadata safely
                exif = img.getexif()
                if exif:
                    meta["has_exif"] = True
                    # Common camera metadata tags
                    make = exif.get(0x010F)  # Make
                    model = exif.get(0x0110) # Model
                    software = exif.get(0x0131) # Software
                    if make: meta["camera_make"] = str(make)
                    if model: meta["camera_model"] = str(model)
                    if software: meta["software"] = str(software)
                else:
                    meta["has_exif"] = False
        except Exception as e:
            meta["read_error"] = str(e)

    elif media_type == "video":
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                meta["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                meta["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                meta["fps"] = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
                meta["total_frames"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                meta["duration_seconds"] = round(meta["total_frames"] / meta["fps"], 2) if meta["fps"] > 0 else 0
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                meta["codec_fourcc"] = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                cap.release()
        except Exception as e:
            meta["read_error"] = str(e)

    elif media_type == "audio":
        try:
            import wave
            with wave.open(file_path, "rb") as wf:
                meta["channels"] = wf.getnchannels()
                meta["sample_rate"] = wf.getframerate()
                meta["sample_width_bytes"] = wf.getsampwidth()
                n_frames = wf.getnframes()
                meta["duration_seconds"] = round(n_frames / float(meta["sample_rate"]), 2)
        except Exception as e:
            meta["read_error"] = str(e)

    return meta
