
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func

from app.core.database import Base


class Answer(Base):
    __tablename__ = "answers"

    # Unique answer ID
    id = Column(Integer, primary_key=True, index=True)

    # Question this answer belongs to
    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False,
        index=True
    )

    # AI-generated response
    answer_text = Column(Text, nullable=False)

    # Language used in the answer
    language = Column(String(10), nullable=True)

    # AI model used to generate the answer
    model_name = Column(String(100), nullable=True)

    # Time taken to generate the answer, in seconds
    processing_time = Column(Float, nullable=True)

    # Answer creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
