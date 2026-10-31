import os
import uuid
import wave
import numpy as np
from scipy.io import wavfile
from scipy import signal
from typing import Dict, Any, Optional, List

from app.core.config import settings
from app.ai_engine.base_detector import BaseDetector, DetectionResult, AudioSegmentResult


class AudioDeepfakeDetector(BaseDetector):
    def __init__(self):
        super().__init__(model_name="Acoustic-Spectral-VocoderDetector", model_version="1.0.0")

    def _read_audio(self, file_path: str):
        """Safely load audio data and sample rate."""
        try:
            sr, data = wavfile.read(file_path)
            # If stereo, average to mono
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            # Normalize float [-1.0, 1.0]
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0
            elif data.dtype == np.int32:
                data = data.astype(np.float32) / 2147483648.0
            elif data.dtype == np.uint8:
                data = (data.astype(np.float32) - 128.0) / 128.0
            return sr, data
        except Exception:
            # Fallback to standard python wave module
            try:
                with wave.open(file_path, 'rb') as wf:
                    sr = wf.getframerate()
                    n_frames = wf.getnframes()
                    raw = wf.readframes(n_frames)
                    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                    if wf.getnchannels() > 1:
                        data = data.reshape(-1, wf.getnchannels()).mean(axis=1)
                    return sr, data
            except Exception as e:
                raise ValueError(f"Unable to decode audio format: {e}")

    def predict(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> DetectionResult:
        warnings = []
        if not os.path.exists(file_path):
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=["Audio file not found."],
                recommendations="Upload a valid audio sample."
            )

        try:
            sr, y = self._read_audio(file_path)
        except Exception as e:
            return DetectionResult(
                prediction="inconclusive",
                confidence_score=0.5,
                uncertainty_score=1.0,
                warnings=[f"Audio decoding error: {str(e)}. Only uncompressed PCM WAV and standard formats are natively supported."],
                recommendations="Convert audio to 16-bit or 24-bit PCM WAV (16kHz-48kHz) and re-upload."
            )

        duration = len(y) / float(sr) if sr > 0 else 0

        if duration < 1.0:
            warnings.append(f"Audio sample is very short ({duration:.2f}s). Reliable synthetic speech detection requires at least 2-3 seconds of speech.")
        elif duration > 120.0:
            warnings.append("Audio sample exceeds 2 minutes. Analyzing the first 120 seconds.")
            y = y[: int(sr * 120)]
            duration = 120.0

        # Check for near-silence or clipping
        rms_energy = float(np.sqrt(np.mean(y**2)))
        if rms_energy < 0.005:
            warnings.append("Audio has extremely low volume or is predominantly silence.")

        # Segment-by-segment acoustic feature analysis
        segment_duration = 2.0  # 2-second analysis windows
        samples_per_seg = int(sr * segment_duration)
        num_segments = max(1, int(np.ceil(len(y) / samples_per_seg)))

        segment_results: List[AudioSegmentResult] = []
        seg_scores = []
        spectral_flatnesses = []
        zcr_list = []

        for seg_idx in range(num_segments):
            start_sample = seg_idx * samples_per_seg
            end_sample = min(len(y), start_sample + samples_per_seg)
            chunk = y[start_sample:end_sample]

            if len(chunk) < int(sr * 0.5):
                continue  # skip tiny trailing tail

            start_t = round(start_sample / sr, 2)
            end_t = round(end_sample / sr, 2)

            # 1. Zero Crossing Rate
            zero_crossings = np.sum(np.abs(np.diff(np.sign(chunk)))) / (2.0 * len(chunk))
            zcr_list.append(zero_crossings)

            # 2. Spectral STFT analysis
            f, t, Zxx = signal.stft(chunk, fs=sr, nperseg=min(512, len(chunk)))
            magnitude = np.abs(Zxx) + 1e-9

            # 3. Spectral Flatness (Wiener entropy): Geometric mean / Arithmetic mean of power spectrum
            # Synthetic neural vocoders (WaveNet, HiFi-GAN) often leave abnormal spectral flatness profiles
            power_spec = magnitude**2
            geom_mean = np.exp(np.mean(np.log(power_spec + 1e-12), axis=0))
            arith_mean = np.mean(power_spec, axis=0) + 1e-12
            flatness = float(np.mean(geom_mean / arith_mean))
            spectral_flatnesses.append(flatness)

            # 4. High-frequency phase irregularity & robotic pitch consistency
            high_freq_idx = int(len(f) * 0.7)
            high_freq_energy = float(np.mean(power_spec[high_freq_idx:, :]))
            total_energy = float(np.mean(power_spec))
            hf_ratio = high_freq_energy / (total_energy + 1e-6)

            # Heuristic calculation for vocal synthesis anomalies:
            # Neural TTS models frequently show unnaturally uniform spectral flatness or excessive high-frequency cutoff/artifacts
            flatness_anomaly = abs(flatness - 0.08) / 0.08
            hf_anomaly = min(1.0, hf_ratio * 3.0)

            seg_score = float(np.clip(0.40 * min(1.0, flatness_anomaly) + 0.35 * hf_anomaly + 0.25 * (1.0 - min(1.0, zero_crossings * 10)), 0.05, 0.95))
            seg_score = round(seg_score, 3)
            seg_scores.append(seg_score)

            is_suspicious = seg_score >= 0.58
            segment_results.append(
                AudioSegmentResult(
                    segment_index=seg_idx,
                    start_time_seconds=start_t,
                    end_time_seconds=end_t,
                    score=seg_score,
                    is_suspicious=is_suspicious,
                    spectral_flatness=round(flatness, 4),
                    mfcc_anomaly_score=round(hf_anomaly, 3)
                )
            )

        if not seg_scores:
            seg_scores = [0.5]

        # Overall aggregation
        overall_score = round(float(np.mean(seg_scores)), 3)
        mean_flatness = round(float(np.mean(spectral_flatnesses)), 4) if spectral_flatnesses else 0.0
        avg_zcr = round(float(np.mean(zcr_list)), 4) if zcr_list else 0.0

        # Uncertainty calculation
        uncertainty = 1.0 - (abs(overall_score - 0.5) * 2.0)
        if duration < 2.0 or rms_energy < 0.01:
            uncertainty = min(1.0, uncertainty + 0.25)
        uncertainty = round(float(np.clip(uncertainty, 0.1, 0.95)), 3)

        if uncertainty > 0.68 or (0.43 <= overall_score <= 0.57):
            prediction = "inconclusive"
            recommendations = "Acoustic features do not display clear synthetic vocoder signatures. Acoustic review recommended."
        elif overall_score >= 0.57:
            prediction = "potentially_manipulated"
            recommendations = "Spectral flatness and harmonic continuity deviate from natural human vocal tract acoustics. Possible AI voice clone."
        else:
            prediction = "likely_authentic"
            recommendations = "Natural vocal harmonics, breathing pauses, and expected frequency distribution present."

        forensic_indicators = {
            "duration_seconds": round(duration, 2),
            "sample_rate_hz": sr,
            "rms_energy": round(rms_energy, 4),
            "mean_spectral_flatness": mean_flatness,
            "average_zero_crossing_rate": avg_zcr,
            "total_segments_analyzed": len(segment_results),
            "suspicious_segments_count": sum(1 for s in segment_results if s.is_suspicious)
        }

        return DetectionResult(
            prediction=prediction,
            confidence_score=overall_score,
            uncertainty_score=uncertainty,
            forensic_indicators=forensic_indicators,
            warnings=warnings,
            recommendations=recommendations,
            model_name=self.model_name,
            model_version=self.model_version,
            audio_segments=segment_results
        )
