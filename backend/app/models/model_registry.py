import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text
from app.database.session import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    media_type = Column(String(50), nullable=False)  # image, video, audio
    architecture = Column(String(100), nullable=False)
    trained_on = Column(String(255), nullable=True)  # Dataset names / benchmark
    metrics_json = Column(Text, nullable=True)  # Accuracy, Precision, Recall, F1, ROC-AUC
    is_active = Column(Boolean, default=True, nullable=False)
    artifact_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
