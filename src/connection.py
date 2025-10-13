# file: connection.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

Base = declarative_base()
_engine = None
_SessionLocal = None

def _initialize_database():
    """
    This function creates the engine and session factory.
    It's designed to run only once, when first needed.
    """
    global _engine, _SessionLocal

    # Return immediately if already initialized
    if _engine is not None:
        return

    # --- Configuration is now loaded inside the function ---
    load_dotenv()
    POOL_RECYCLE_SECONDS = 540
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set.")

    # --- Engine creation with your pool settings is moved here ---
    _engine = create_engine(
        DATABASE_URL,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_recycle=POOL_RECYCLE_SECONDS,
        pool_pre_ping=True,
    )

    # --- Session factory creation is also moved here ---
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def getEngine():
    """Returns the singleton engine instance, initializing if necessary."""
    _initialize_database() # Ensure initialization has happened
    return _engine


@contextmanager
def get_session():
    """
    Provide a transactional scope around a series of operations.
    Initializes the database connection on the first call.
    """
    _initialize_database() # Ensure initialization has happened

    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()