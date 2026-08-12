"""
main.py
-------
TaskFlow FastAPI application entrypoint.

Serves the REST API AND the static frontend from a single process,
which is the recommended architecture for a single Render Web Service
(avoids production CORS issues entirely).
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import Base, engine
from backend.middleware import RequestLoggingMiddleware
from backend.routes import users, projects, tasks

# Create tables on startup if they do not already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="Internal task and project management platform.",
    version="1.0.0",
)

# ---------------------------------------------------------------- CORS ---
FRONTEND_URL = os.getenv("FRONTEND_URL")
allowed_origins = ["http://localhost:5500", "http://127.0.0.1:5500"]
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# ------------------------------------------------------------- Routers ---
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------------- Frontend UI ---
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
