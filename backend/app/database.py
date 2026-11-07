
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

# Store the database inside the backend folder
DATABASE_PATH = Path(__file__).parent.parent / "multimedia.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create the database connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database tables
Base = declarative_base()
