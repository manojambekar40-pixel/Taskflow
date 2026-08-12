"""
database.py
------------
Database engine and session configuration for TaskFlow.

Local development: SQLite (file-based, zero setup).
Production (Render): PostgreSQL, selected automatically when the
DATABASE_URL environment variable is set.

Design goal: the rest of the application (models, crud, routes) never
needs to know which database engine is actually in use.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load .env for local development. In production (Render) the real
# environment variables are injected by the platform, so this is a no-op.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is in requirements.txt
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render's managed Postgres sometimes provides a "postgres://" URL.
    # SQLAlchemy 2.x requires the "postgresql://" scheme.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Local development fallback: SQLite file stored alongside the backend.
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "taskflow.db")
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees
    it is closed after the request finishes, even if an exception is
    raised. Reused across every router in the application.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
