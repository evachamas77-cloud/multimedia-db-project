
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Frame(Base):
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, index=True)

    # The camera session this frame belongs to
    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False
    )

    # Image storage information
    image_path = Column(String(500), nullable=False)
    image_filename = Column(String(255), nullable=False)

    # Frame metadata
    captured_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    sharpness_score = Column(Float, nullable=True)

    # Relationship with Session
    session = relationship("Session", back_populates="frames")
