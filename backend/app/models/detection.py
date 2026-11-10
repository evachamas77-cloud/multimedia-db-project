
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class Detection(Base):
    __tablename__ = "detections"

    # Unique detection ID
    id = Column(Integer, primary_key=True, index=True)

    # Frame containing the detected object
    frame_id = Column(
        Integer,
        ForeignKey("frames.id"),
        nullable=False,
        index=True
    )

    # Object information returned by YOLO
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)

    # Bounding box coordinates
    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    y_max = Column(Float, nullable=False)

    # Detection timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
