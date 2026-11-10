
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    # Unique question ID
    id = Column(Integer, primary_key=True, index=True)

    # Session in which the question was asked
    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
        index=True
    )

    # Original question spoken by the user
    question_text = Column(Text, nullable=False)

    # Language of the question (en, ar, fr, etc.)
    language = Column(String(10), nullable=True)

    # Date and time the question was received
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
