import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # reads variables from .env into the environment

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Copy .env.example to .env and fill in your credentials."
    )

engine = create_engine(DATABASE_URL)

# Each request gets its own short-lived session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models inherit from this base class so SQLAlchemy knows about them
Base = declarative_base()


def create_tables():
    """Create all tables defined in models.py (safe to call multiple times)."""
    import models  # noqa: F401 — import triggers model registration on Base
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Dependency helper for FastAPI routes
# ---------------------------------------------------------------------------
def get_db():
    """Yield a database session and close it automatically when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
