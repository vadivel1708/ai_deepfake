import os
import uuid
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, Optional

from app.core.config import settings
from app.ai_engine.base_detector import BaseDetector, DetectionResult
from app.ai_engine.image_detector.forensics import (
    perform_error_level_analysis,
    perform_fft_frequency_analysis,
    detect_face_and_blending_artifacts
)


class MesoInception4(nn.Module):
    """
    MesoInception-4 architecture designed specifically for detecting microscopic
    deepfake compression and mesoscopic facial synthesis artifacts.
    """
    def __init__(self, num_classes=2):
        super(MesoInception4, self).__init__()
        # Inception Block 1
        self.inc1_conv1 = nn.Conv2d(3, 1, 1, padding=0)
        self.inc1_conv2 = nn.Conv2d(3, 4, 3, padding=1)
        self.inc1_conv3 = nn.Conv2d(3, 4, 5, padding=2)
        self.inc1_conv4 = nn.Conv2d(3, 2, 5, padding=2)
        self.inc1_bn = nn.BatchNorm2d(11)
        self.maxpool1 = nn.MaxPool2d(2, 2)

        # Inception Block 2
        self.inc2_conv1 = nn.Conv2d(11, 2, 1, padding=0)
        self.inc2_conv2 = nn.Conv2d(11, 4, 3, padding=1)
        self.inc2_conv3 = nn.Conv2d(11, 4, 5, padding=2)
        self.inc2_conv4 = nn.Conv2d(11, 2, 5, padding=2)
        self.inc2_bn = nn.BatchNorm2d(12)
        self.maxpool2 = nn.MaxPool2d(2, 2)

        # Normal Conv Block 3
        self.conv3 = nn.Conv2d(12, 16, 5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.maxpool3 = nn.MaxPool2d(2, 2)

        # Normal Conv Block 4
        self.conv4 = nn.Conv2d(16, 16, 5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        self.maxpool4 = nn.MaxPool2d(4, 4)

        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(16 * 8 * 8, 16)
        self.fc2 = nn.Linear(16, num_classes)

    def forward(self, x):
        # Inception 1
        x1 = self.inc1_conv1(x)
        x2 = self.inc1_conv2(x)
        x3 = self.inc1_conv3(x)
        x4 = self.inc1_conv4(x)
        x = torch.cat([x1, x2, x3, x4], dim=1)
        x = F.relu(self.inc1_bn(x))
        x = self.maxpool1(x)

        # Inception 2
        x1 = self.inc2_conv1(x)
        x2 = self.inc2_conv2(x)
        x3 = self.inc2_conv3(x)
        x4 = self.inc2_conv4(x)
        x = torch.cat([x1, x2, x3, x4], dim=1)
        x = F.relu(self.inc2_bn(x))
        x = self.maxpool2(x)

        # Conv 3
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.maxpool3(x)

        # Conv 4
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.maxpool4(x)

        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = F.leaky_relu(self.fc1(x), 0.1)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class ImageDeepfakeDetector(BaseDetector):
    def __init__(self, weights_path: Optional[str] = None):
        super().__init__(model_name="MesoInception-ForensicEnsemble", model_version="1.2.0")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MesoInception4(num_classes=2).to(self.device)
        self.model.eval()

        self.weights_loaded = False
        if weights_path and os.path.exists(weights_path):
            try:
                state_dict = torch.load(weights_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.weights_loaded = True
            except Exception as e:
                print(f"[Detector] Note: Could not load weights from {weights_path}: {e}")

    def preprocess_image(self, image_bgr: np.ndarray) -> torch.Tensor:
        """Preprocess image to standard 256x256 tensor normalized to [-1, 1]"""
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(img_rgb, (256, 256))
        tensor = torch.from_numpy(resized).permute(2, 0, 1).float() / 255.0
        # Normalize with standard ImageNet or MesoNet scale [-1, 1]
        tensor = (tensor - 0.5) / 0.5
        return tensor.unsqueeze(0).to(self.device)

    def predict(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> DetectionResult:
        warnings = []
        
        # 1. Verify existence and load with OpenCV
        if not os.path.exists(file_path):
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["File does not exist on disk."],
                recommendations="Verify file upload integrity."
            )

        img_bgr = cv2.imread(file_path)
        if img_bgr is None:
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["Could not decode image file safely."],
                recommendations="Upload an uncorrupted image."
            )

        h, w = img_bgr.shape[:2]
        if h < 256 or w < 256:
            warnings.append(f"Low resolution input ({w}x{h} px). Model reliability is degraded on low-res images.")

        # 2. Forensic Visual Indicators
        unique_id = str(uuid.uuid4())[:8]
        ela_out_path = str(settings.FORENSICS_DIR / f"ela_{unique_id}.png")
        fft_out_path = str(settings.FORENSICS_DIR / f"fft_{unique_id}.png")

        ela_res = perform_error_level_analysis(file_path, ela_out_path)
        fft_res = perform_fft_frequency_analysis(file_path, fft_out_path)
        face_res = detect_face_and_blending_artifacts(img_bgr)

        if not face_res.get("face_detected", False):
            warnings.append("No human face detected. Facial manipulation checks skipped; relying on global frequency/ELA forensic analysis.")

        # 3. Neural Classifier Inference
        input_tensor = self.preprocess_image(img_bgr)
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probs = F.softmax(outputs, dim=1).cpu().numpy()[0]
            # prob[0] = Authentic, prob[1] = Manipulated
            neural_score = float(probs[1])

        # 4. Multi-modal Calibrated Fusion
        # Fuse Neural feature score with ELA and FFT indicators
        ela_score = ela_res.get("ela_suspicion_score", 0.5)
        fft_score = fft_res.get("fft_suspicion_score", 0.5)
        face_score = face_res.get("blending_suspicion_score", 0.2)

        if face_res.get("face_detected"):
            # If face is detected, face blending and neural face weights carry higher weight
            calibrated_score = 0.45 * neural_score + 0.25 * face_score + 0.15 * ela_score + 0.15 * fft_score
        else:
            # Global image forensics
            calibrated_score = 0.40 * neural_score + 0.35 * ela_score + 0.25 * fft_score

        calibrated_score = round(float(np.clip(calibrated_score, 0.01, 0.99)), 3)

        # 5. Uncertainty computation
        # Uncertainty is highest when calibrated score is near decision boundary (0.5)
        distance_from_boundary = abs(calibrated_score - 0.5)
        uncertainty = round(float(1.0 - (distance_from_boundary * 2.0)), 3)
        if len(warnings) > 0:
            uncertainty = min(1.0, round(uncertainty + 0.15, 3))

        # 6. Final Classification
        if uncertainty > 0.70 or (0.42 <= calibrated_score <= 0.58):
            prediction = "inconclusive"
            recommendations = "Results are borderline. Recommend manual forensic inspection of ELA artifacts and original source provenance."
        elif calibrated_score >= 0.58:
            prediction = "potentially_manipulated"
            recommendations = "High likelihood of synthetic generation, face-swapping, or localized editing. Human expert review advised."
        else:
            prediction = "likely_authentic"
            recommendations = "No significant synthetic frequency patterns or compression tampering detected. Appears consistent with authentic camera capture."

        # Relative paths for frontend preview
        ela_relative = f"/storage/forensics/{os.path.basename(ela_out_path)}" if ela_res.get("ela_saved") else None
        fft_relative = f"/storage/forensics/{os.path.basename(fft_out_path)}" if fft_res.get("fft_saved") else None

        forensic_indicators = {
            "neural_confidence": round(neural_score, 3),
            "ela": {
                "score": ela_score,
                "preview_url": ela_relative,
                "mean_error": ela_res.get("mean_error_level"),
                "std_error": ela_res.get("std_error_level")
            },
            "frequency_analysis": {
                "score": fft_score,
                "preview_url": fft_relative,
                "spectral_ratio": fft_res.get("spectral_energy_ratio"),
                "high_freq_energy": fft_res.get("high_freq_energy")
            },
            "facial_forensics": {
                "face_detected": face_res.get("face_detected"),
                "face_count": face_res.get("face_count"),
                "blending_anomaly_score": face_score,
                "faces": face_res.get("faces")
            }
        }

        return DetectionResult(
            prediction=prediction,
            confidence_score=calibrated_score,
            uncertainty_score=uncertainty,
            forensic_indicators=forensic_indicators,
            warnings=warnings,
            recommendations=recommendations,
            model_name=self.model_name,
            model_version=self.model_version
        )
