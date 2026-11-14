
import os
import sys
from pathlib import Path

# Ensure the backend directory is on Python's import path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.user import User


def create_admin():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not email or not password:
        raise SystemExit(
            "Set ADMIN_EMAIL and ADMIN_PASSWORD before running this script."
        )

    if len(password) < 12:
        raise SystemExit("Admin password must contain at least 12 characters.")

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(User).where(User.email == email)
        )

        if existing:
            raise SystemExit(
                "This email already exists. Choose a new admin email."
            )

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print(f"Admin account created successfully: {email}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
