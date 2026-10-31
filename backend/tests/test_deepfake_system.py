import io
import os
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np
import wave

from app.main import app
from app.database.session import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import create_access_token
from app.ai_engine.image_detector.detector import ImageDeepfakeDetector
from app.ai_engine.audio_detector.detector import AudioDeepfakeDetector
from app.ai_engine.video_detector.detector import VideoDeepfakeDetector

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def auth_headers(setup_db):
    user = setup_db.query(User).filter(User.email == "user@deepfake.ai").first()
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def reviewer_headers(setup_db):
    reviewer = setup_db.query(User).filter(User.email == "reviewer@deepfake.ai").first()
    token = create_access_token({"sub": reviewer.id, "email": reviewer.email, "role": reviewer.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def admin_headers(setup_db):
    admin = setup_db.query(User).filter(User.email == "admin@deepfake.ai").first()
    token = create_access_token({"sub": admin.id, "email": admin.email, "role": admin.role})
    return {"Authorization": f"Bearer {token}"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "operational" in response.json().get("status")


def test_user_registration_and_login():
    # Register
    email = f"analyst_test_{os.getpid()}@forensics.ai"
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Test Analyst",
        "role": "user"
    })
    assert reg_res.status_code == 201
    assert reg_res.json()["email"] == email

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_login_invalid_credentials():
    res = client.post("/api/auth/login", json={
        "email": "user@deepfake.ai",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401


def test_upload_image_validation(auth_headers):
    # Create sample synthetic test image in memory
    img = Image.new("RGB", (300, 300), color=(120, 150, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    res = client.post(
        "/api/media/upload",
        files={"file": ("test_sample.jpg", buf, "image/jpeg")},
        headers=auth_headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["media_type"] == "image"
    assert "sha256_hash" in data


def test_upload_unsupported_format(auth_headers):
    buf = io.BytesIO(b"malicious_executable_or_unsupported_data")
    res = client.post(
        "/api/media/upload",
        files={"file": ("malware.exe", buf, "application/x-msdownload")},
        headers=auth_headers
    )
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]


def test_direct_image_analysis_pipeline(auth_headers):
    # Upload and analyze
    img = Image.new("RGB", (256, 256), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    res = client.post(
        "/api/analysis/image",
        files={"file": ("sample_face.png", buf, "image/png")},
        headers=auth_headers
    )
    assert res.status_code == 202
    job_data = res.json()
    assert "id" in job_data
    assert job_data["status"] in ["pending", "processing", "completed"]


def test_ai_detectors_inference():
    # Test Image Detector directly
    img_detector = ImageDeepfakeDetector()
    test_img_path = "storage/forensics/unit_test_img.png"
    img = Image.new("RGB", (256, 256), color=(100, 150, 200))
    img.save(test_img_path)

    res = img_detector.predict(test_img_path)
    assert res.prediction in ["likely_authentic", "potentially_manipulated", "inconclusive"]
    assert 0.0 <= res.confidence_score <= 1.0
    assert 0.0 <= res.uncertainty_score <= 1.0
    assert "ela" in res.forensic_indicators
    assert "frequency_analysis" in res.forensic_indicators

    # Test Audio Detector with synthetic PCM WAV
    audio_detector = AudioDeepfakeDetector()
    test_audio_path = "storage/forensics/unit_test_audio.wav"
    sr = 16000
    t = np.linspace(0, 2.0, int(sr * 2.0))
    audio_wave = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
    with wave.open(test_audio_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_wave.tobytes())

    audio_res = audio_detector.predict(test_audio_path)
    assert audio_res.prediction in ["likely_authentic", "potentially_manipulated", "inconclusive"]
    assert 0.0 <= audio_res.confidence_score <= 1.0
    assert len(audio_res.audio_segments) > 0


def test_reviewer_workflow(reviewer_headers, auth_headers):
    # Upload an image to analyze
    img = Image.new("RGB", (256, 256), color=(80, 90, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    upload_res = client.post(
        "/api/analysis/image",
        files={"file": ("review_test.jpg", buf, "image/jpeg")},
        headers=auth_headers
    )
    job_id = upload_res.json()["id"]

    # Reviewer retrieves pending
    pending_res = client.get("/api/reviews/pending", headers=reviewer_headers)
    assert pending_res.status_code == 200

    # Reviewer updates status
    update_res = client.patch(
        f"/api/reviews/{job_id}/status",
        json={"status": "likely_authentic", "notes": "No facial seam artifacts observed."},
        headers=reviewer_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["new_status"] == "likely_authentic"


def test_report_downloads(auth_headers):
    # Create sample job
    img = Image.new("RGB", (256, 256), color=(50, 60, 70))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    upload_res = client.post(
        "/api/analysis/image",
        files={"file": ("report_test.jpg", buf, "image/jpeg")},
        headers=auth_headers
    )
    job_id = upload_res.json()["id"]

    # Download CSV
    csv_res = client.get(f"/api/reports/{job_id}/csv", headers=auth_headers)
    assert csv_res.status_code == 200
    assert "AI Forensic Authenticity Analysis Report" in csv_res.text

    # Download PDF
    pdf_res = client.get(f"/api/reports/{job_id}/pdf", headers=auth_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")


def test_admin_metrics_and_role_control(admin_headers, auth_headers):
    # Admin metrics
    metrics_res = client.get("/api/admin/metrics", headers=admin_headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert "total_users" in metrics
    assert "media_breakdown" in metrics

    # Non-admin access should be forbidden (403)
    forbidden_res = client.get("/api/admin/metrics", headers=auth_headers)
    assert forbidden_res.status_code == 403
