import os
from urllib.parse import quote_plus

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

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

_driver = quote_plus(_pick_driver())
_user = quote_plus(os.getenv("MSSQL_USER", "todoapp"))
_password = quote_plus(os.environ["MSSQL_PASSWORD"])  # crash on startup if not set
_host = os.getenv("MSSQL_HOST", "localhost")
_port = os.getenv("MSSQL_PORT", "1433")
_db = os.getenv("MSSQL_DB", "claudetodo")

SQLALCHEMY_DATABASE_URL = (
    f"mssql+pyodbc://{_user}:{_password}@{_host}:{_port}/{_db}"
    f"?driver={_driver}&TrustServerCertificate=yes"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, fast_executemany=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
