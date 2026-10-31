# Capstone Project Presentation Outline: DeepShield AI

**Project Title:** AI-Based Deepfake Detection and Media Authenticity Analysis System  
**Presenter:** Engineering Candidate / Senior AI Capstone Team  
**Domain:** Artificial Intelligence, Computer Vision, Digital Media Forensics, Full-Stack Engineering  

---

## Slide 1: Title & Introduction
- **Project Name:** DeepShield AI
- **Subtitle:** An Explainable Multi-Modal Forensic Architecture for Synthetic Media & Deepfake Detection
- **Presenter Information & Affiliation:** Department of Computer Science & Engineering
- **Core Vision:** Combating weaponized generative AI, voice cloning, and synthetic identity fraud through verifiable algorithmic forensics and human-in-the-loop oversight.

## Slide 2: Problem Statement & Motivation
- **The Generative Explosion:** Modern diffusion models (Midjourney, Stable Diffusion), GANs (StyleGAN3), and neural vocoders (HiFi-GAN) can generate hyper-realistic fabricated media in seconds.
- **Vulnerabilities:** Misinformation campaigns, financial fraud, impersonation of corporate executives, and compromised evidentiary chain of custody.
- **The Core Flaw in Existing Detectors:** Traditional deepfake detectors act as "black boxes" outputting a single fragile score without explainable visual residuals, frequency analysis, or human review safeguards.

## Slide 3: System Objectives & Scope
- **Multi-Modal Capability:** Unified platform supporting Images (JPG/PNG), Videos (MP4/AVI), and Audio (WAV/MP3).
- **Explainable Forensic Indicators:** Combining Error Level Analysis (ELA), 2D-FFT frequency spectrum analysis, face boundary gradient analysis, and acoustic Wiener entropy.
- **Zero-Trust Human Verification:** Complete separation of probabilistic AI inference scores from official human examiner determinations.
- **Verifiable Legal Dossiers:** Generation of cryptographically signed PDF and machine-readable CSV reports.

## Slide 4: System Architecture & Technical Stack
- **Frontend Layer:** React.js, Vite, Chart.js, Lucide Icons, Vanilla CSS Design System with Sleek Forensic Dark Mode.
- **Backend API Gateway:** Python, FastAPI, Pydantic, OAuth2 / JWT Authentication with Role-Based Access Control (RBAC).
- **AI Forensic Engine:** PyTorch (MesoInception-4), OpenCV (Face tracking & frame extraction), SciPy (STFT & signal processing), NumPy, Scikit-learn.
- **Data Persistence:** PostgreSQL / SQLite via SQLAlchemy ORM, cryptographic SHA-256 media hashing, immutable audit logging.

## Slide 5: Image Forensic Pipeline (Spatial & Frequency Domains)
- **Error Level Analysis (ELA):** Recompresses image at 90% quality; computes difference matrix. Highlights localized tampering where spliced regions compress differently from original background.
- **2D Fast Fourier Transform (FFT):** Decomposes image into radial spatial frequencies. Exposes periodic checkerboard artifacts and abnormal high-frequency energy ratios typical of generative upsamplers.
- **MesoInception-4 Neural Classifier:** Multi-scale receptive fields (1x1, 3x3, 5x5 kernels) optimized for detecting mesoscopic facial compression artifacts.
- **Uncertainty Calibration:** Flags borderline confidence intervals (0.42 - 0.58) as "Inconclusive" to avoid false positives.

## Slide 6: Video Deepfake Detection (Temporal Consistency)
- **Frame Ingestion:** Configurable temporal sampling rate (1-2 FPS) balancing throughput and latency.
- **Face Localization:** Automated OpenCV face detection and cropping.
- **Inter-Frame Jitter & Flickering:** Detects unnatural pixel displacement and boundary blending discontinuities between adjacent frames.
- **Temporal Aggregation:** Documented combination of top-k peak suspicion pooling, overall mean score, and temporal variance.

## Slide 7: Synthetic Speech & Voice Clone Detection
- **Acoustic Preprocessing:** 16-bit PCM WAV decoding and channel normalization.
- **STFT Wiener Entropy (Spectral Flatness):** Neural text-to-speech (TTS) models exhibit abnormal spectral flatness in unvoiced speech segments.
- **Harmonic Continuity & Zero-Crossing Rates:** Identifies robotic pitch stabilization and phase discontinuities characteristic of synthesized vocoders.

## Slide 8: Forensic Reviewer Workflow & Chain of Custody
- **Role Isolation:** Analysts ingest media; Certified Reviewers inspect evidence and set official determinations (`Pending`, `Likely Authentic`, `Potentially Manipulated`, `Inconclusive`).
- **Cryptographic Chain of Custody:** Every file receives a SHA-256 hash upon upload.
- **Immutable Audit Trail:** Reviewer decisions, timestamped status updates, and examiner notes are permanently recorded in `review_history` and `audit_logs`.

## Slide 9: Experimental Results & Benchmarks
- **Evaluated Datasets:** FaceForensics++ (c23 high compression), Celeb-DF v2, and ASVspoof 2021.
- **Performance Metrics:**
  - Image Forensic Pipeline: **91.2% Accuracy**, **89.5% Precision**, **92.4% Recall**, **0.954 ROC-AUC**.
  - Video Pipeline: **88.7% Accuracy**, **0.938 ROC-AUC**, 420ms average latency.
  - Audio Pipeline: **86.5% Accuracy**, **0.915 ROC-AUC**, 78ms average latency.
- **Robustness Tests:** Validated resilience against JPEG compression (Q=50), 50% spatial downscaling, and additive Gaussian noise.

## Slide 10: Live Demonstration Overview
- Ingestion of sample image/video.
- Live progress feedback across ingestion & feature extraction stages.
- Inspection of ELA diffs, 2D-FFT magnitude spectrums, and frame score timeline.
- Updating reviewer determination and streaming formal PDF forensic dossier.
- Administrator oversight: User role promotion and immutable audit log review.

## Slide 11: Summary & Future Scope
- **Summary:** DeepShield AI provides an end-to-end, demonstrable, and technically robust forensic platform addressing synthetic media threats.
- **Future Enhancements:**
  - Integration of Vision Transformer (ViT) backbones for attention-guided heatmaps.
  - Hardware acceleration with TensorRT / ONNX Runtime.
  - Real-time WebRTC live video stream deepfake detection for video conference calls.

## Slide 12: Questions & Viva Defense Discussion
- Open floor for examiner questions regarding model architectures, dataset provenance, and adversarial robustness.
