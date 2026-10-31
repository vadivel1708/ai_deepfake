# AI Model Checkpoints and Artifacts

This folder stores model weights and calibrated checkpoints for deepfake and synthetic speech detection.

## Supported Architectures

1. **MesoInception-4 (Image Backbone)**
   - Target File: `meso_weights.pth`
   - Architecture: Inception-style multi-scale convolutional filters (1x1, 3x3, 5x5) combined with dilated convolutions, designed to detect microscopic pixel interpolation and blending seams.
   - Input: 256x256 RGB tensor normalized to `[-1, 1]`.

2. **Temporal Aggregator (Video Backbone)**
   - Frame-level classification pooled with OpenCV frontal face tracking and inter-frame facial jitter calculation.

3. **Acoustic Vocoder Detector (Audio Backbone)**
   - Short-Time Fourier Transform (STFT) Wiener entropy analyzer, zero-crossing variance, and harmonic continuity evaluator.

## Checkpoint Loading

The detector automatically scans this folder for `meso_weights.pth`. If the file is absent, the system defaults to the calibrated multi-modal forensic ensemble (Error Level Analysis + 2D-FFT Spectral Decomposition + OpenCV Face Seam Analysis), ensuring robust detection without requiring multi-gigabyte external weight downloads.
