from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import User
from backend.auth import get_password_hash

def seed_database():
    """
    Initializes database tables and creates the standard user roles.
    Does NOT seed any fake material inspection records or dummy analytics.
    The inventory and inspection history start completely empty for a new deployment.
    """
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if users already seeded
        if db.query(User).count() == 0:
            print("Initializing default site user accounts...")
            users = [
                User(
                    username="admin",
                    email="admin@constructionsite.com",
                    hashed_password=get_password_hash("Admin@123"),
                    full_name="Sarah Jenkins",
                    role="admin",
                    is_active=True
                ),
                User(
                    username="engineer",
                    email="engineer@constructionsite.com",
                    hashed_password=get_password_hash("Engineer@123"),
                    full_name="Marcus Vance, PE",
                    role="site_engineer",
                    is_active=True
                ),
                User(
                    username="inspector",
                    email="inspector@constructionsite.com",
                    hashed_password=get_password_hash("Inspector@123"),
                    full_name="Elena Rostova",
                    role="inspector",
                    is_active=True
                )
            ]
            db.add_all(users)
            db.commit()
            print("Default user accounts initialized successfully.")
        else:
            print("User accounts already exist.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
