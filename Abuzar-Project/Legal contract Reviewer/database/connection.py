# SQLAlchemy database connection and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Create all database tables
def init_db():
    Base.metadata.create_all(engine)


# Dependency for FastAPI — yields a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
