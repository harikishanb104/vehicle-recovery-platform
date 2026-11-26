"""Engine and schema creation for the plate-scan service.

This module opens Postgres. It does not decide how a scan becomes a case.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATABASE_URL

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Return the one engine for this process, creating it on first use.

    A fresh engine on every health check would open a new pool each
    time and leak connections.
    """
    global _engine
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Copy backend/.env.example to backend/.env.")
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine


def check_connection(engine: Engine) -> None:
    """Run a trivial query so a caller can tell the database is reachable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_session_factory() -> sessionmaker[Session]:
    """Return the session factory bound to the process engine."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _session_factory


def get_session() -> Iterator[Session]:
    """Yield a request session, committing only when the request succeeds.

    An exception rolls the transaction back. A claim that loses its row
    lock therefore does not leave a half-updated case.
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_schema(engine: Engine) -> None:
    """Create any missing tables registered on the model base.

    Importing app.models attaches Tenant, User, Camera, Case, and Scan
    to that registry. Tables that already exist are left alone.
    """
    from app.models import Base

    Base.metadata.create_all(engine)
