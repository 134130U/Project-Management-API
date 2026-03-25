import os
import sys
from sqlalchemy.exc import IntegrityError

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.update import Update
from app.core.security import hash_password


def seed():
    db = SessionLocal()
    try:
        # Create a demo user
        user = db.query(User).filter(User.email == "demo@example.com").first()
        if not user:
            user = User(email="demo@example.com", password=hash_password("password123"))
            db.add(user)
            db.flush()

        # Create a demo project
        project = (
            db.query(Project)
            .filter(Project.name == "Demo Project", Project.owner_id == user.id)
            .first()
        )
        if not project:
            project = Project(
                name="Demo Project",
                description="A sample project for development",
                owner_id=user.id,
            )
            db.add(project)
            db.flush()

        # Create a demo update
        upd = (
            db.query(Update)
            .filter(Update.project_id == project.id, Update.title == "Initial update")
            .first()
        )
        if not upd:
            upd = Update(
                project_id=project.id,
                title="Initial update",
                description="Project created and initial setup complete.",
            )
            db.add(upd)

        db.commit()
        print("Seed data inserted/ensured.")
    except IntegrityError:
        db.rollback()
        print("Seeding encountered integrity errors; rolled back conflicting ops.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
