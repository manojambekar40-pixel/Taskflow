"""
dependencies.py
----------------
Central place for FastAPI dependencies shared across every router.
Currently re-exports get_db so all routes import it from one place.
"""

from backend.database import get_db

__all__ = ["get_db"]
