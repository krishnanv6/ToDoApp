import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _build_mssql_url() -> str:
    import pyodbc

    _PREFERRED_DRIVERS = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "SQL Server",
    ]

    def _pick_driver() -> str:
        available = pyodbc.drivers()
        for d in _PREFERRED_DRIVERS:
            if d in available:
                return d
        raise RuntimeError(f"No suitable SQL Server ODBC driver found. Installed: {available}")

    driver = quote_plus(_pick_driver())
    user = quote_plus(os.getenv("MSSQL_USER", "todoapp"))
    password = quote_plus(os.environ["MSSQL_PASSWORD"])
    host = os.getenv("MSSQL_HOST", "localhost")
    port = os.getenv("MSSQL_PORT", "1433")
    db = os.getenv("MSSQL_DB", "claudetodo")
    return (
        f"mssql+pyodbc://{user}:{password}@{host}:{port}/{db}"
        f"?driver={driver}&TrustServerCertificate=yes"
    )


def _get_database_url() -> str:
    """Return the database URL, preferring SQLite when TEST_DATABASE_URL is set."""
    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        return test_url
    if os.getenv("MSSQL_PASSWORD"):
        return _build_mssql_url()
    # Fallback for local dev without SQL Server
    return "sqlite:///./claudetodo.db"


SQLALCHEMY_DATABASE_URL = _get_database_url()

_connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
