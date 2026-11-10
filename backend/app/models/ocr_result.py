
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    # Unique OCR result ID
    id = Column(Integer, primary_key=True, index=True)

    # Frame from which the text was extracted
    frame_id = Column(
        Integer,
        ForeignKey("frames.id"),
        nullable=False,
        index=True
    )

    # Text recognized by EasyOCR
    recognized_text = Column(Text, nullable=False)

    # OCR confidence score
    confidence = Column(Float, nullable=True)

    # Location of the recognized text in the image
    x_min = Column(Float, nullable=True)
    y_min = Column(Float, nullable=True)
    x_max = Column(Float, nullable=True)
    y_max = Column(Float, nullable=True)

    # Date and time of extraction
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
