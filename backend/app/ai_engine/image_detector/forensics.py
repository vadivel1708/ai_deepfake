import os
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from typing import Dict, Any, Tuple, Optional


def perform_error_level_analysis(
    image_path: str,
    output_ela_path: str,
    quality: int = 90,
    scale: int = 15
) -> Dict[str, Any]:
    """
    Error Level Analysis (ELA) identifies differences in JPEG compression levels.
    Synthetic or edited regions compress at different rates than original backgrounds.
    """
    try:
        original = Image.open(image_path).convert('RGB')
        
        # Save temporary JPEG re-compressed version in memory
        temp_jpeg_path = output_ela_path + ".tmp.jpg"
        original.save(temp_jpeg_path, 'JPEG', quality=quality)
        
        # Re-open and compute difference
        recompressed = Image.open(temp_jpeg_path).convert('RGB')
        ela_im = ImageChops.difference(original, recompressed)
        
        # Calculate statistical variance
        ela_np = np.array(ela_im).astype(np.float32)
        mean_diff = float(np.mean(ela_np))
        std_diff = float(np.std(ela_np))
        max_diff = float(np.max(ela_np))
        
        # Enhance visual difference for forensic inspection
        extrema = ela_im.getextrema()
        max_diff_channel = max([ex[1] for ex in extrema])
        if max_diff_channel == 0:
            max_diff_channel = 1
        scale_factor = 255.0 / max_diff_channel
        enhanced = ImageEnhance.Brightness(ela_im).enhance(scale_factor)
        enhanced.save(output_ela_path, 'PNG')
        
        # Clean up temp file
        if os.path.exists(temp_jpeg_path):
            os.remove(temp_jpeg_path)

        # High variance and localized anomalies indicate potential manipulation
        suspicious_score = min(1.0, (std_diff / 15.0) * 0.5 + (mean_diff / 12.0) * 0.5)
        
        return {
            "ela_saved": True,
            "ela_path": output_ela_path,
            "mean_error_level": round(mean_diff, 2),
            "std_error_level": round(std_diff, 2),
            "max_error_level": round(max_diff, 2),
            "ela_suspicion_score": round(suspicious_score, 3)
        }
    except Exception as e:
        return {
            "ela_saved": False,
            "error": str(e),
            "ela_suspicion_score": 0.5
        }


def perform_fft_frequency_analysis(
    image_path: str,
    output_fft_path: str
) -> Dict[str, Any]:
    """
    2D Fast Fourier Transform analysis detects periodic grid patterns,
    convolution upsampling artifacts, and spectral discrepancies typical of GAN/Diffusion synthesis.
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"fft_saved": False, "fft_suspicion_score": 0.5}
        
        # Resize to standard power-of-two dimension for consistent spectral analysis
        img_resized = cv2.resize(img, (512, 512))
        
        # Compute 2D Fast Fourier Transform
        f = np.fft.fft2(img_resized)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-9)
        
        # High frequency ring analysis (center 512x512, radius > 180)
        h, w = magnitude_spectrum.shape
        cy, cx = h // 2, w // 2
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        high_freq_mask = dist_from_center > 160
        mid_freq_mask = (dist_from_center > 40) & (dist_from_center <= 160)
        
        high_freq_energy = float(np.mean(magnitude_spectrum[high_freq_mask]))
        mid_freq_energy = float(np.mean(magnitude_spectrum[mid_freq_mask]))
        ratio = high_freq_energy / (mid_freq_energy + 1e-5)
        
        # Save normalized magnitude spectrum visualization
        norm_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
        norm_spectrum_color = cv2.applyColorMap(norm_spectrum.astype(np.uint8), cv2.COLORMAP_MAGMA)
        cv2.imwrite(output_fft_path, norm_spectrum_color)
        
        # GAN and diffusion images tend to have abnormal high-frequency energy ratio
        fft_suspicion = min(1.0, max(0.0, (ratio - 0.55) / 0.35))
        
        return {
            "fft_saved": True,
            "fft_path": output_fft_path,
            "high_freq_energy": round(high_freq_energy, 2),
            "mid_freq_energy": round(mid_freq_energy, 2),
            "spectral_energy_ratio": round(ratio, 3),
            "fft_suspicion_score": round(fft_suspicion, 3)
        }
    except Exception as e:
        return {"fft_saved": False, "error": str(e), "fft_suspicion_score": 0.5}


def detect_face_and_blending_artifacts(image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Detects face boundaries using OpenCV Haar cascades and analyzes boundary gradient smoothness.
    Deepfake face-swaps often leave boundary blending artifacts or sharpness mismatches.
    """
    try:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Load OpenCV default frontal face cascade
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
        
        if len(faces) == 0:
            return {
                "face_detected": False,
                "face_count": 0,
                "faces": [],
                "blending_suspicion_score": 0.2  # No face detected
            }
        
        face_list = []
        max_boundary_score = 0.0
        
        for (x, y, w, h) in faces:
            # Analyze face interior Laplacian vs boundary Laplacian
            face_roi = gray[y:y+h, x:x+w]
            face_laplacian_var = float(cv2.Laplacian(face_roi, cv2.CV_64F).var())
            
            # Exterior border
            y1 = max(0, y - 10)
            y2 = min(gray.shape[0], y + h + 10)
            x1 = max(0, x - 10)
            x2 = min(gray.shape[1], x + w + 10)
            surrounding = gray[y1:y2, x1:x2]
            surrounding_var = float(cv2.Laplacian(surrounding, cv2.CV_64F).var())
            
            # Sharpness mismatch ratio
            ratio = abs(face_laplacian_var - surrounding_var) / (face_laplacian_var + surrounding_var + 1e-5)
            suspicion = min(1.0, ratio * 1.5)
            max_boundary_score = max(max_boundary_score, suspicion)
            
            face_list.append({
                "bbox": [int(x), int(y), int(w), int(h)],
                "face_sharpness": round(face_laplacian_var, 2),
                "boundary_sharpness_mismatch": round(ratio, 3)
            })
            
        return {
            "face_detected": True,
            "face_count": len(faces),
            "faces": face_list,
            "blending_suspicion_score": round(max_boundary_score, 3)
        }
    except Exception as e:
        return {
            "face_detected": False,
            "error": str(e),
            "blending_suspicion_score": 0.5
        }
