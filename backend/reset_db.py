from app.database import engine, Base
from app.models import Candidate, JobDescription
from sqlalchemy.orm import Session

def reset_database():
    print("Wiping out old data...")
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    print("Database has been reset with no fake data.")

if __name__ == "__main__":
    reset_database()
