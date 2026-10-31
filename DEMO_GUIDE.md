# Live Demonstration & Evaluator Walkthrough Guide

This guide outlines a seamless step-by-step walkthrough of the DeepShield platform for evaluators, college professors, and technical judges.

---

## 1. Quick Launch Commands

### Option A: Local Development (Recommended for quick testing)

1. **Start Backend API Server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
   *The backend starts at `http://localhost:8000`, automatically creates all database tables, and seeds preset demonstration accounts.*

2. **Start Frontend Client**:
   ```bash
   cd frontend
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

### Option B: Docker Compose
```bash
docker-compose up --build
```

---

## 2. Pre-Seeded Demonstration Accounts

For convenience during presentations, you can use the **1-Click Demo Buttons** on the Login screen, or enter credentials manually:

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@deepfake.ai` | `Admin@1234` | Full access: User management, model registry, audit logs, review queue, analysis tools |
| **Forensic Reviewer** | `reviewer@deepfake.ai` | `Reviewer@1234` | Review queue access, ability to set official verdicts and submit examiner notes |
| **Investigative Analyst** | `user@deepfake.ai` | `User@1234` | Media upload, forensic inspection, PDF/CSV dossier downloads |

---

## 3. Demonstration Flow for Technical Presentations

### Step 1: Landing Page & Capabilities Overview (`/`)
- Point out the defense-grade dark aesthetic and multi-modal architecture.
- Highlight the distinction between **Image Forensics** (ELA & 2D-FFT), **Video Forensics** (Temporal face-tracking), and **Audio Forensics** (STFT Wiener entropy).
- Explain the 4-step pipeline: Decoupled Ingestion &rarr; Multi-Modal Pipeline &rarr; Neural Calibration &rarr; Verifiable Dossier.

### Step 2: 1-Click Login (`/login`)
- Click **"Admin"** or **"Analyst"** on the preset credentials bar.
- Note the instantaneous authentication via JWT access tokens.

### Step 3: Intelligence Dashboard (`/dashboard`)
- Showcase the summary cards: Total Ingested, Likely Authentic, Manipulated, Inconclusive, Latency.
- Explain the **Prediction Classification Ratio** (Doughnut chart) and **Activity Volume** (Bar chart).
- Highlight the **Distinction Banner**: AI outputs are probabilistic statistical metrics; final determinations belong to certified human examiners.

### Step 4: Media Upload & Real-Time Ingestion (`/analyze`)
- Switch between **Image**, **Video**, and **Audio** tabs.
- Demonstrate drag-and-drop file upload.
- Observe the real-time stage progression text:
  1. *Uploading file safely...*
  2. *Decoding media and checking cryptographic checksum...*
  3. *Generating Error Level Analysis (ELA) compression residual map...*
  4. *Computing 2D Fast Fourier Transform high-frequency power spectrum...*
  5. *Executing MesoInception neural inference and uncertainty bounds...*
- Upon completion, the system automatically routes to the **Forensic Evidence Viewer**.

### Step 5: Deep-Dive Forensic Evidence Viewer (`/analysis/:id`)
- **Header**: Review the SHA-256 hash, analysis ID, and model version.
- **Inference Banner**: Show the classification verdict (`POTENTIALLY MANIPULATED` or `LIKELY AUTHENTIC`), manipulation likelihood bar, and uncertainty score.
- **Visual Forensic Tabs**:
  - Click **"Original Source"**: Shows the clean uploaded image.
  - Click **"ELA Compression Diff"**: Demonstrates how resaving reveals compression variance in tampered facial regions.
  - Click **"2D-FFT Spectrum"**: Displays high-frequency concentric and radial power spectrum artifacts.
- For video files: Show the interactive **Frame-by-Frame Timeline** and **Suspicious Frames Carousel** with timestamps.
- For audio files: Show the **Acoustic STFT Flatness Table**.

### Step 6: Human Review Verdict & Audit Trail
- As an Administrator or Reviewer, change the status from **Pending Review** to **Likely Authentic** or **Potentially Manipulated**.
- Enter forensic observations in the Examiner Notes box and click **Save Reviewer Determination**.
- Demonstrate that the human status is maintained separately from the model output.

### Step 7: Export Verifiable Reports
- Click **Download PDF Dossier**: Streams a formal, styled ReportLab PDF containing legal disclaimers, SHA-256 signatures, score breakdowns, and examiner notes.
- Click **Export CSV**: Downloads raw timestamped metrics for programmatic ingestion.

### Step 8: Administrator Oversight & Audit Logs (`/admin`)
- Switch to the **User & Role Access Control** tab: Show real-time role promotion (Analyst &rarr; Reviewer &rarr; Admin).
- Switch to **Registered Model Architectures**: Displays the MesoInception-4, Temporal Face Tracker, and Vocoder detector configurations alongside held-out benchmark metrics.
- Switch to **Immutable System Audit Logs**: Demonstrates full chain-of-custody compliance with timestamped records of every upload, status alteration, and login.
