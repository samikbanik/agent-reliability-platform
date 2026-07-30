"""SQLAlchemy engine and session helpers."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from agent_reliability_common.settings import get_settings

_engine = None
_session_factory: sessionmaker[Session] | None = None


def get_engine():
    """Create (once) and return the shared SQLAlchemy engine."""
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return the shared session factory, initializing the engine if needed."""
    get_engine()
    assert _session_factory is not None
    return _session_factory


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create ORM tables if they do not already exist."""
    from agent_reliability_common.models import Base

    Base.metadata.create_all(bind=get_engine())
