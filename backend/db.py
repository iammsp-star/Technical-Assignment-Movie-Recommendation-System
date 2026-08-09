import os
import time
from typing import Generator
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./netflix.db"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NetflixTitle(Base):
    __tablename__ = "netflix_titles"

    show_id = Column(String(50), primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    director = Column(Text, nullable=True)
    cast = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    date_added = Column(String(100), nullable=True)
    release_year = Column(Integer, nullable=False)
    rating = Column(String(50), nullable=True)
    duration = Column(String(100), nullable=True)
    listed_in = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

def init_db() -> None:
    """Initialize the database schema."""
    start_time = time.time()
    Base.metadata.create_all(bind=engine)
    duration = time.time() - start_time
    print(f"[DB] Initialized database in {duration:.4f} seconds.")

def get_db() -> Generator[Session, None, None]:
    """Dependency injection to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
