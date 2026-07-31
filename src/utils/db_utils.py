from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import pandas as pd

from config.database import get_database_uri, ENGINE_CONFIG

# Create global engine
engine = create_engine(get_database_uri(), **ENGINE_CONFIG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def execute_query(query: str, params: dict = None) -> pd.DataFrame:
    """Executes a raw SQL query and returns the results as a pandas DataFrame."""
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return pd.DataFrame(result.fetchall(), columns=result.keys())
