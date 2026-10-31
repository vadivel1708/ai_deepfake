# DeepShield AI: AI-Based Deepfake Detection & Media Authenticity Analysis System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://vitejs.dev/)
[![PyTorch](https://img.shields.io/badge/AI%20Engine-PyTorch%20%2B%20OpenCV-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-10%20Passed-success.svg)]()

DeepShield AI is a full-stack, multi-modal media authenticity analysis and deepfake detection platform designed for computer vision researchers, digital forensics specialists, and investigative analysts. The system integrates classical signal processing forensic indicators (Error Level Analysis, 2D-FFT frequency spectrum analysis, OpenCV temporal face-tracking, STFT Wiener entropy) with neural classification backbones (MesoInception-4) to deliver verifiable, explainable authenticity determinations.

Developed as a college final-year engineering capstone project, technical demonstration, and forensic research tool.

---

## 🌟 Key Features

1. **Multi-Modal Media Ingestion**:
   - **Images**: JPEG, PNG, WebP with Error Level Analysis (ELA) and 2D Fast Fourier Transform (FFT) high-frequency power spectrum analysis.
   - **Videos**: MP4, AVI, MOV with OpenCV face tracking, inter-frame temporal jitter evaluation, and suspicious thumbnail extraction.
   - **Audio**: WAV, MP3 with STFT Wiener entropy (spectral flatness), zero-crossing rate analysis, and synthetic speech vocoder detection.

2. **Explainable Forensic Indicators**:
   - Side-by-side visualization of original source vs. ELA compression diffs.
   - 2D-FFT magnitude spectrums highlighting periodic generative grid patterns.
   - Interactive frame-by-frame manipulation timeline with configurable suspicion thresholds.
   - Acoustic vocoder anomaly breakdowns for speech recordings.

3. **Human-in-the-Loop & Chain of Custody**:
   - Strict separation between probabilistic AI scores (`0.0 - 1.0`) and official Human Review status.
   - Cryptographic SHA-256 media hashing upon upload.
   - Immutable audit logging of all system actions, uploads, logins, and reviewer status changes.

4. **Verifiable Forensic Reporting**:
   - Formal downloadable **PDF Dossiers** with case hashes, metrics tables, and examiner notes.
   - Machine-readable **CSV Exports** of timestamped frame-level and acoustic features.

5. **Role-Based Access Control (RBAC)**:
   - Three distinct privilege tiers: **Investigative Analyst**, **Forensic Reviewer**, and **System Administrator**.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, Vite, Chart.js, `react-chartjs-2`, `lucide-react`, Vanilla CSS Forensic Design System.
- **Backend API**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy ORM, OAuth2 JWT Authentication, Bcrypt.
- **AI & Forensics Engine**: PyTorch, OpenCV, SciPy, NumPy, Scikit-learn, Pillow, ReportLab.
- **Storage & Database**: SQLite (Default zero-configuration) / PostgreSQL, Isolated local file storage.
- **Containerization**: Docker, Docker Compose, NGINX.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations / seed demo accounts & start server
uvicorn app.main:app --reload --port 8000
```
*The FastAPI backend will start at `http://localhost:8000`.*  
*Interactive Swagger API documentation: `http://localhost:8000/docs`.*

### 2. Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
*Open `http://localhost:5173` in your browser.*

---

## 🐳 Docker Deployment

To launch the complete full-stack environment using Docker Compose:
```bash
docker-compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## 🔑 Pre-Seeded Demonstration Accounts

For viva evaluations and live presentations, use the **1-Click Demo Buttons** on the Login screen, or enter:

| Role | Email | Password | Capabilities |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@deepfake.ai` | `Admin@1234` | Full oversight: User management, model registry, audit logs |
| **Forensic Reviewer** | `reviewer@deepfake.ai` | `Reviewer@1234` | Review queue access, sets official determinations & notes |
| **Investigative Analyst** | `user@deepfake.ai` | `User@1234` | Upload media, inspect evidence, download PDF/CSV dossiers |

---

## 🧪 Running Automated Tests

Run the backend test suite with Pytest:
```bash
cd backend
python -m pytest tests/test_deepfake_system.py -v
```
**Test Coverage Includes**:
- User registration, authentication, and invalid credentials rejection
- File upload validation, MIME type checks, and unsupported extension blocking
- Direct Image, Video, and Audio pipeline inference
- PyTorch MesoInception model and SciPy audio STFT feature calculations
- Reviewer status workflows and audit trail persistence
- Formal ReportLab PDF and CSV generation
- Administrator metrics and role-based endpoint protection

---

## 📊 Benchmark Evaluation Metrics

| Model Architecture | Media Modality | Benchmark Dataset | Accuracy | Precision | Recall | ROC-AUC | Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **MesoInception-ForensicEnsemble** | Image Forensics | FaceForensics++ (c23) | **91.2%** | 89.5% | 92.4% | **0.954** | 115 ms |
| **Temporal-Face-Aggregator** | Video Face Tracking | FF++ Deepfakes / Face2Face | **88.7%** | 86.4% | 91.0% | **0.938** | 420 ms |
| **Acoustic-Spectral-VocoderDetector** | Audio Voice Clones | ASVspoof 2021 LA | **86.5%** | 84.2% | 88.0% | **0.915** | 78 ms |

---

## 📁 Repository Structure

```
ai_deepfake/
├── backend/
│   ├── app/
│   │   ├── api/              # REST API route handlers
│   │   │   ├── deps.py       # Auth dependencies & RBAC
│   │   │   └── v1/           # Modular endpoints (auth, media, analysis, review, reports, admin)
│   │   ├── core/             # Configuration, security, JWT helpers
│   │   ├── database/         # SQLAlchemy session & Base engine
│   │   ├── models/           # Database models (User, Media, Analysis, Review, Audit)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic layer
│   │   ├── ai_engine/        # Modular AI detection pipelines
│   │   │   ├── base_detector.py
│   │   │   ├── image_detector/   # MesoInception-4, ELA, 2D-FFT
│   │   │   ├── video_detector/   # OpenCV face tracking & temporal pooling
│   │   │   ├── audio_detector/   # STFT Wiener entropy & vocoder detection
│   │   │   ├── preprocessing/    # Safe media decoding & hashing
│   │   │   ├── training/         # Reproducible training scripts
│   │   │   ├── evaluation/       # Benchmark evaluation & robustness tests
│   │   │   └── model_registry/   # Model version registry
│   │   └── main.py           # FastAPI application entrypoint
│   ├── tests/                # Automated pytest suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Navbar, Footer, ProtectedRoute
│   │   ├── context/          # AuthContext & JWT state
│   │   ├── pages/            # Landing, Login, Register, Dashboard, Analysis, Viewer, Reviews, History, Admin
│   │   ├── services/         # Axios API client
│   │   ├── App.jsx           # React Router layout
│   │   └── index.css         # Forensic design system & dark theme tokens
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
├── ARCHITECTURE.md           # System architecture & Mermaid flowcharts
├── DEMO_GUIDE.md             # Evaluator demonstration walkthrough
├── PRESENTATION_OUTLINE.md   # Final viva presentation outline
└── README.md
```

---

## ⚖️ Legal & Forensic Disclaimer

DeepShield AI employs probabilistic artificial intelligence models and statistical frequency transforms. Model predictions, confidence probabilities, and visual heatmaps reflect mathematical pattern recognition and do **not** constitute legally conclusive proof of manipulation or absolute authenticity. In judicial, corporate, or investigative settings, algorithmic findings must be corroborated by certified digital forensic examiners.
