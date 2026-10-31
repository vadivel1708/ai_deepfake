"""
Model Evaluation and Robustness Benchmark Script
Evaluates models against test sets and assesses robustness across:
- JPEG compression
- Resizing
- Gaussian Noise
"""
import os
import time
import json
import numpy as np
import cv2
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from app.ai_engine.image_detector.detector import ImageDeepfakeDetector


def evaluate_detector_on_samples(detector, samples):
    """
    samples: list of (file_path, ground_truth_label) where 0=authentic, 1=manipulated
    """
    y_true = []
    y_pred = []
    y_scores = []
    latencies = []

    for path, label in samples:
        if not os.path.exists(path):
            continue
        start_t = time.time()
        result = detector.predict(path)
        latency = (time.time() - start_t) * 1000.0
        latencies.append(latency)

        score = result.confidence_score
        predicted_binary = 1 if score >= 0.55 else 0

        y_true.append(label)
        y_scores.append(score)
        y_pred.append(predicted_binary)

    if len(y_true) == 0:
        return {"error": "No valid samples evaluated."}

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    try:
        auc = float(roc_auc_score(y_true, y_scores))
    except Exception:
        auc = 0.5
    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "samples_evaluated": len(y_true),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "avg_latency_ms": round(float(np.mean(latencies)), 2),
        "confusion_matrix": cm
    }


def evaluate_robustness(detector, image_path, true_label=1):
    """Assess model robustness under common transmission perturbations."""
    if not os.path.exists(image_path):
        return {}

    img = cv2.imread(image_path)
    if img is None:
        return {}

    results = {}
    temp_prefix = image_path + ".benchmark_"

    # 1. Baseline
    base_res = detector.predict(image_path)
    results["baseline_score"] = base_res.confidence_score

    # 2. JPEG Compression Q=50
    jpeg_p = temp_prefix + "q50.jpg"
    cv2.imwrite(jpeg_p, img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    q50_res = detector.predict(jpeg_p)
    results["jpeg_compression_q50_score"] = q50_res.confidence_score
    if os.path.exists(jpeg_p): os.remove(jpeg_p)

    # 3. Downscale 50% & Upscale back
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 2, h // 2))
    restored = cv2.resize(small, (w, h))
    rescale_p = temp_prefix + "rescale.png"
    cv2.imwrite(rescale_p, restored)
    rescale_res = detector.predict(rescale_p)
    results["rescale_50pct_score"] = rescale_res.confidence_score
    if os.path.exists(rescale_p): os.remove(rescale_p)

    # 4. Additive Gaussian noise
    noise = np.random.normal(0, 15, img.shape).astype(np.float32)
    noisy_img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    noise_p = temp_prefix + "noise.png"
    cv2.imwrite(noise_p, noisy_img)
    noise_res = detector.predict(noise_p)
    results["gaussian_noise_score"] = noise_res.confidence_score
    if os.path.exists(noise_p): os.remove(noise_p)

    return results


if __name__ == "__main__":
    detector = ImageDeepfakeDetector()
    print(f"[*] Loaded Detector: {detector.model_name}")
