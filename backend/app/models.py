

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from app.database import Base


class Frame(Base):
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    # Link this analysis to its original image
    frame_id = Column(
        Integer,
        ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type of AI analysis: OCR or object_detection
    analysis_type = Column(String, nullable=False)

    # Store the complete AI results as JSON
    results = Column(JSON, nullable=False)

    # Date and time of the analysis
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
