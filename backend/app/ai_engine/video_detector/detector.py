import os
import uuid
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, Any, Optional, List

from app.core.config import settings
from app.ai_engine.base_detector import BaseDetector, DetectionResult, FrameResult
from app.ai_engine.image_detector.detector import ImageDeepfakeDetector


class VideoDeepfakeDetector(BaseDetector):
    def __init__(self, image_detector: Optional[ImageDeepfakeDetector] = None):
        super().__init__(model_name="Temporal-Face-Aggregator", model_version="1.1.0")
        self.image_detector = image_detector or ImageDeepfakeDetector()
        
        # Load OpenCV Haar cascade for face tracking
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def predict(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> DetectionResult:
        warnings = []
        if not os.path.exists(file_path):
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["Video file not found."],
                recommendations="Upload a valid video."
            )

        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["Could not open video stream. Codec may be unsupported or corrupted."],
                recommendations="Ensure the video is standard H.264 MP4 format."
            )

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if duration < 1.0:
            warnings.append("Video duration is less than 1 second. Temporal consistency analysis has limited confidence.")

        # Configurable frame sampling interval
        sample_step = max(1, int(fps // 2))  # Sample approx 2 frames per second
        max_frames_to_sample = settings.VIDEO_MAX_FRAMES_TO_ANALYZE

        frame_idx = 0
        sampled_count = 0
        frame_results: List[FrameResult] = []
        scores_list = []
        prev_face_crop = None
        temporal_flicker_scores = []

        unique_prefix = str(uuid.uuid4())[:8]

        while cap.isOpened() and sampled_count < max_frames_to_sample:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_step == 0:
                sampled_count += 1
                timestamp = round(frame_idx / fps, 2)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))

                face_detected = len(faces) > 0
                face_bbox = None
                frame_score = 0.5

                if face_detected:
                    # Pick largest face
                    (x, y, w, h) = max(faces, key=lambda b: b[2] * b[3])
                    face_bbox = [int(x), int(y), int(w), int(h)]
                    face_crop = frame[y:y+h, x:x+w]
                    
                    # Temporal jitter/flicker analysis between consecutive face detections
                    if prev_face_crop is not None:
                        try:
                            resized_prev = cv2.resize(prev_face_crop, (w, h))
                            diff = cv2.absdiff(face_crop, resized_prev)
                            flicker = float(np.mean(diff))
                            temporal_flicker_scores.append(min(1.0, flicker / 40.0))
                        except Exception:
                            pass
                    prev_face_crop = face_crop

                    # Run neural model on face crop
                    tensor = self.image_detector.preprocess_image(face_crop)
                    with torch.no_grad():
                        outputs = self.image_detector.model(tensor)
                        probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
                        frame_score = float(probs[1])
                else:
                    # Run on whole frame
                    tensor = self.image_detector.preprocess_image(frame)
                    with torch.no_grad():
                        outputs = self.image_detector.model(tensor)
                        probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
                        frame_score = float(probs[1]) * 0.8  # slightly lower confidence without face

                frame_score = round(float(frame_score), 3)
                scores_list.append(frame_score)
                is_suspicious = frame_score >= 0.60

                # Save thumbnail for suspicious frames or key intervals
                thumb_rel_path = None
                if is_suspicious or (sampled_count <= 5) or (sampled_count % 5 == 0):
                    thumb_filename = f"thumb_{unique_prefix}_f{frame_idx}.jpg"
                    thumb_full_path = str(settings.THUMBNAILS_DIR / thumb_filename)
                    # Resize thumbnail to save space
                    thumb_img = cv2.resize(frame, (320, 180))
                    # If face detected, draw a clean bounding box
                    if face_detected and face_bbox:
                        scale_x = 320.0 / width
                        scale_y = 180.0 / height
                        bx, by, bw, bh = face_bbox
                        cv2.rectangle(
                            thumb_img,
                            (int(bx * scale_x), int(by * scale_y)),
                            (int((bx + bw) * scale_x), int((by + bh) * scale_y)),
                            (0, 0, 255) if is_suspicious else (0, 255, 0),
                            2
                        )
                    cv2.imwrite(thumb_full_path, thumb_img)
                    thumb_rel_path = f"/storage/thumbnails/{thumb_filename}"

                frame_results.append(
                    FrameResult(
                        frame_index=frame_idx,
                        timestamp_seconds=timestamp,
                        score=frame_score,
                        is_suspicious=is_suspicious,
                        face_detected=face_detected,
                        face_bbox=face_bbox,
                        thumbnail_path=thumb_rel_path,
                        indicators={
                            "face_detected": face_detected,
                            "temporal_step": sample_step
                        }
                    )
                )

            frame_idx += 1

        cap.release()

        if len(scores_list) == 0:
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["No frames could be extracted from the video."],
                recommendations="Review file codec and integrity."
            )

        # 7. Aggregation of frame-level outputs:
        # A documented combination of mean score, top-10% peak suspicion, and temporal inconsistency
        sorted_scores = sorted(scores_list, reverse=True)
        top_k_count = max(1, int(len(sorted_scores) * 0.15))
        top_k_mean = float(np.mean(sorted_scores[:top_k_count]))
        overall_mean = float(np.mean(scores_list))
        temporal_variance = float(np.var(scores_list))
        avg_flicker = float(np.mean(temporal_flicker_scores)) if temporal_flicker_scores else 0.0

        # Weighted aggregate score (avoids classifying whole video as fake from 1 noisy outlier frame)
        aggregated_score = 0.50 * top_k_mean + 0.35 * overall_mean + 0.15 * min(1.0, avg_flicker)
        aggregated_score = round(float(np.clip(aggregated_score, 0.02, 0.98)), 3)

        # Uncertainty: higher if temporal variance is high or score near 0.5
        score_uncertainty = 1.0 - (abs(aggregated_score - 0.5) * 2.0)
        uncertainty = round(float(np.clip(score_uncertainty * 0.7 + temporal_variance * 1.5, 0.05, 0.95)), 3)

        # Classification
        suspicious_frames_count = sum(1 for f in frame_results if f.is_suspicious)
        suspicious_ratio = suspicious_frames_count / len(frame_results)

        if uncertainty > 0.72 or (0.44 <= aggregated_score <= 0.56):
            prediction = "inconclusive"
            recommendations = "Temporal indicators show high variance or borderline confidence. Frame-by-frame human review recommended."
        elif aggregated_score >= 0.56 or suspicious_ratio >= 0.30:
            prediction = "potentially_manipulated"
            recommendations = f"{suspicious_frames_count} frames exhibited suspicious facial artifacts or temporal inconsistencies. Expert human review recommended."
        else:
            prediction = "likely_authentic"
            recommendations = "Consistent temporal coherence and natural facial motion patterns observed across sampled frames."

        forensic_indicators = {
            "total_frames_sampled": len(frame_results),
            "video_duration_sec": round(duration, 2),
            "video_fps": round(fps, 1),
            "resolution": f"{width}x{height}",
            "overall_mean_score": round(overall_mean, 3),
            "top_k_peak_score": round(top_k_mean, 3),
            "temporal_variance": round(temporal_variance, 4),
            "temporal_flicker_index": round(avg_flicker, 3),
            "suspicious_frames_count": suspicious_frames_count,
            "suspicious_frame_ratio": round(suspicious_ratio, 3)
        }

        return DetectionResult(
            prediction=prediction,
            confidence_score=aggregated_score,
            uncertainty_score=uncertainty,
            forensic_indicators=forensic_indicators,
            warnings=warnings,
            recommendations=recommendations,
            model_name=self.model_name,
            model_version=self.model_version,
            frame_results=frame_results
        )
