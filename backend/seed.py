"""
seed.py
-------
Optional helper to populate the database with demo data for local
testing. Run with:

    python -m backend.seed
"""

from backend.database import Base, engine, SessionLocal
from backend import models

def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.User).first():
            print("Database already has data, skipping seed.")
            return

        user = models.User(name="Alex Morgan", email="alex@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

        project = models.Project(name="Inventory API", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

        tasks = [
            models.Task(title="Design database schema", priority="high", due_date="tomorrow", project_id=project.id),
            models.Task(title="Write API docs", priority="medium", due_date=None, project_id=project.id),
            models.Task(title="Refactor auth module", priority="low", due_date="next friday", project_id=project.id),
        ]
        db.add_all(tasks)
        db.commit()
        print("Seed data created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
