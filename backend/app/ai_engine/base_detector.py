from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class FrameResult:
    frame_index: int
    timestamp_seconds: float
    score: float
    is_suspicious: bool
    face_detected: bool = False
    face_bbox: Optional[List[int]] = None
    thumbnail_path: Optional[str] = None
    indicators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioSegmentResult:
    segment_index: int
    start_time_seconds: float
    end_time_seconds: float
    score: float
    is_suspicious: bool
    spectral_flatness: Optional[float] = None
    mfcc_anomaly_score: Optional[float] = None


@dataclass
class DetectionResult:
    prediction: str  # likely_authentic, potentially_manipulated, inconclusive
    confidence_score: float  # 0.0 to 1.0 (manipulation likelihood)
    uncertainty_score: float  # 0.0 to 1.0
    forensic_indicators: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    recommendations: str = ""
    model_name: str = "BaseDetector"
    model_version: str = "1.0.0"
    frame_results: List[FrameResult] = field(default_factory=list)
    audio_segments: List[AudioSegmentResult] = field(default_factory=list)


class BaseDetector(ABC):
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version

    @abstractmethod
    def predict(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> DetectionResult:
        """Run inference pipeline on the input media file."""
        pass

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "architecture": self.__class__.__name__
        }
